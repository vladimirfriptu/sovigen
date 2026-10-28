// Set to true to fill the form without pressing Create.
const DRY_RUN = false;

const POLL_MS = 3000;
const FORM_TIMEOUT_MS = 30000;
const CLIPS_TIMEOUT_MS = 120000;
const CAPTCHA_TIMEOUT_MS = 300000;
const NEW_CLIPS_EXPECTED = 2;

const LYRICS_SELECTOR = '[aria-label="Lyrics editor"]';
const EXCLUDE_SELECTOR = 'input[placeholder="Exclude styles"]';
const CREATE_SELECTOR = 'button[aria-label="Create song"]';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitFor(check, timeoutMs, what) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const value = check();
    if (value) return value;
    await sleep(500);
  }
  throw new Error(`timed out waiting for ${what}`);
}

function findMoreOptions() {
  const buttons = document.querySelectorAll('div[role=button]');
  return [...buttons].find((el) => el.textContent.trim() === 'More Options');
}

// The placeholder of the Styles textarea rotates, so it is found by elimination.
function findStyleTextarea() {
  const areas = [...document.querySelectorAll('textarea')];
  return areas.find((el) => {
    const visible = el.offsetParent !== null;
    return visible && !el.getAttribute('aria-label') && !el.placeholder.startsWith('Describe');
  });
}

function setReactValue(el, value) {
  const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
  setter.call(el, value);
  el.dispatchEvent(new Event('input', { bubbles: true }));
}

function setLyrics(el, text) {
  el.focus();
  document.execCommand('selectAll');
  document.execCommand('insertText', false, text);
}

function selectAdvancedTab() {
  const tabs = document.querySelectorAll('button[role=tab]');
  const advanced = [...tabs].find((el) => el.textContent.trim() === 'Advanced');
  if (advanced && advanced.getAttribute('aria-selected') !== 'true') advanced.click();
}

async function fillForm(job) {
  selectAdvancedTab();
  const lyricsEl = await waitFor(() => document.querySelector(LYRICS_SELECTOR), FORM_TIMEOUT_MS, 'lyrics editor');
  const more = await waitFor(findMoreOptions, FORM_TIMEOUT_MS, 'More Options');
  if (!document.querySelector(EXCLUDE_SELECTOR)) more.click();

  const styleEl = await waitFor(findStyleTextarea, FORM_TIMEOUT_MS, 'styles textarea');
  const excludeEl = await waitFor(() => document.querySelector(EXCLUDE_SELECTOR), FORM_TIMEOUT_MS, 'exclude styles');

  setLyrics(lyricsEl, job.lyrics);
  setReactValue(styleEl, job.style);
  setReactValue(excludeEl, job.exclude);

  await waitFor(() => {
    const button = document.querySelector(CREATE_SELECTOR);
    return button && !button.disabled;
  }, FORM_TIMEOUT_MS, 'enabled Create button');
}

function songHrefs() {
  const links = document.querySelectorAll('a[href^="/song/"]');
  return new Set([...links].map((a) => a.getAttribute('href')));
}

function captchaVisible() {
  const frames = document.querySelectorAll('iframe[src*="hcaptcha"], iframe[src*="recaptcha"]');
  return [...frames].some((f) => f.offsetParent !== null);
}

async function waitForNewClips(before) {
  let deadline = Date.now() + CLIPS_TIMEOUT_MS;
  let captchaSeen = false;
  while (Date.now() < deadline) {
    const fresh = [...songHrefs()].filter((href) => !before.has(href));
    if (fresh.length >= NEW_CLIPS_EXPECTED) return fresh.length;
    if (!captchaSeen && captchaVisible()) {
      captchaSeen = true;
      deadline = Date.now() + CAPTCHA_TIMEOUT_MS;
    }
    await sleep(2000);
  }
  throw new Error(captchaSeen ? 'captcha was not solved in time' : 'no new clips appeared');
}

async function runJob(job) {
  await fillForm(job);
  if (DRY_RUN) return 0;
  const before = songHrefs();
  document.querySelector(CREATE_SELECTOR).click();
  return waitForNewClips(before);
}

let busy = false;

async function tick() {
  if (busy) return;
  const job = await chrome.runtime.sendMessage({ type: 'poll' });
  if (!job) return;
  busy = true;
  const result = { id: job.id, ok: true, clips: 0, error: '' };
  try {
    result.clips = await runJob(job);
  } catch (err) {
    result.ok = false;
    result.error = String(err.message || err);
  }
  await chrome.runtime.sendMessage({ type: 'result', result });
  busy = false;
}

setInterval(tick, POLL_MS);
