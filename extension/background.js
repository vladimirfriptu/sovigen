const BRIDGE = 'http://127.0.0.1:8765';

async function pollJob() {
  try {
    const response = await fetch(`${BRIDGE}/job`);
    if (response.status !== 200) return null;
    return await response.json();
  } catch (err) {
    return null;
  }
}

async function postResult(result) {
  try {
    await fetch(`${BRIDGE}/result`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result),
    });
  } catch (err) {
    console.warn('sovigen: bridge unreachable', err);
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'poll') {
    pollJob().then(sendResponse);
    return true;
  }
  if (message.type === 'result') {
    postResult(message.result).then(() => sendResponse(true));
    return true;
  }
  return false;
});
