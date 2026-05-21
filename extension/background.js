chrome.action.onClicked.addListener((tab) => {
  // 1. Inject script to read the page
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: scrapePageText,
  }, (results) => {
      // 2. Grab the text and send it to Python
      if (results && results[0]) {
        const pageText = results[0].result;
        sendToPythonBrain(tab.url, pageText);
      }
  });
});

// Runs inside the webpage to get readable text
function scrapePageText() {
  return document.body.innerText;
}

// Sends the data to your Python Flask server
function sendToPythonBrain(url, text) {
  console.log("Sending memory to AI...");
  
  fetch('http://127.0.0.1:5000/silentsave', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: url, text: text })
  })
  .then(response => response.json())
  .then(data => console.log("✅ Success! Memory saved."))
  .catch(error => console.error("❌ Error sending to AI:", error));
}