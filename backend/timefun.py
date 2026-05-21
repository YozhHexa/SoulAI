import datetime
import re

def extract_date_from_file(filename, filepath):
    match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        
    return datetime.date.today().strftime("%Y-%m-%d")