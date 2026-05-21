import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from timefun import extract_date_from_file

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# ==========================================
# ⚙️ LOAD CONFIGURATION
# ==========================================
load_dotenv()
CWD = "D://WorKBench//SoulOSv2"
DB_DIR = os.path.join(CWD, "db")

MEMORY_SOURCES_LIST = [
    {"path": os.getenv("DIARY_PATH"), "type": "diary"},
    {"path": os.getenv("CHATS_PATH"), "type": "chat_history"}
]

def extract_documents_from_folder(folder_path, memory_type):
    """Reads text files, chops them up, and tags them with the specific memory type."""
    if not folder_path or not os.path.exists(folder_path):
        print(f"⚠️ Skipping '{memory_type}' - Directory '{folder_path}' not found.")
        return []

    print(f"📂 Scanning '{memory_type}' directory: {folder_path}...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_docs_to_save = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") or filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            
            real_date_str = extract_date_from_file(filename, file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                
                chunks = text_splitter.split_text(content)
                docs = [
                    Document(
                        page_content=chunk, 
                        metadata={"date": real_date_str, "source": filename, "type": memory_type}
                    ) for chunk in chunks
                ]
                
                all_docs_to_save.extend(docs)
                print(f"📄 Extracted {len(docs)} chunks from '{filename}'")
                
            except Exception as e:
                print(f"⚠️ Could not process '{filename}'. Error: {e}")

    return all_docs_to_save


def save_documents_to_db(docs_to_save):
    """Takes a list of prepared Documents and saves them directly to the Vector DB."""
    if not docs_to_save:
        print("⚠️ No documents were provided to save.")
        return

    print(f"🧠 Connecting to database to save {len(docs_to_save)} total memories...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    db.add_documents(docs_to_save)
    
    print("🎉 Import Complete! All chunks saved to Vector DB.")


def sync_all_memories():
    """
    The Master Helper: Loops through the .env configuration and imports everything.
    You can call this from anywhere in your app to refresh the AI's brain.
    """
    all_extracted_docs = []
    
    for source in MEMORY_SOURCES_LIST:
        docs = extract_documents_from_folder(source["path"], source["type"])
        all_extracted_docs.extend(docs) 
        
    if all_extracted_docs:
        save_documents_to_db(all_extracted_docs)
    else:
        print("⚠️ No new memories found to sync.")


sync_all_memories()