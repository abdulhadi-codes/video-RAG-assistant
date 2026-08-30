// ============================================================
// CourseMind AI — frontend logic
// Talks to Flask's POST /query endpoint, which is expected to return:
//   { question, answer, context, response_time }
// Every number shown on this page comes from a real response or a
// real session counter — nothing here is a placeholder statistic.
// ============================================================

// --- Inject the waveform signature into its slot -----------------
document.querySelectorAll('[data-waveform]').forEach((slot) => {
  const tpl = document.getElementById('waveform-template');
  slot.appendChild(tpl.content.cloneNode(true));
});

// --- TODO: set this to your real chunk count from embeddings.joblib
// e.g. len(df) from your Python pipeline. Left as null until you set
// it, so the UI shows "—" instead of a fabricated number.
// --- Pull the real chunk count from Flask's /health route on load ---
const chunkEls = [
  document.getElementById('hero-chunk-count'),
  document.getElementById('stat-chunks'),
];

async function loadChunkCount() {
  try {
    const res = await fetch('/health');
    const data = await res.json();
    if (data.chunks_loaded !== undefined) {
      chunkEls.forEach((el) => { if (el) el.textContent = data.chunks_loaded; });
    }
  } catch (err) {
    // Server not reachable yet — leave the "—" placeholder as-is.
  }
}

loadChunkCount();

// --- Session state (real counters, not fake stats) ----------------
let queryCount = 0;

const chatThread = document.getElementById('chat-thread');
const chatEmpty = document.getElementById('chat-empty');
const input = document.getElementById('question-input');
const askBtn = document.getElementById('ask-btn');
const askBtnText = askBtn.querySelector('.ask-btn-text');
const askBtnSpinner = askBtn.querySelector('.ask-btn-spinner');
const statResponseTime = document.getElementById('stat-response-time');
const statQueryCount = document.getElementById('stat-query-count');

// Auto-grow the textarea a little as the user types
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
});

// Enter submits, Shift+Enter makes a newline
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
});

askBtn.addEventListener('click', ask);

// Suggestion chips fill the input and ask immediately
document.querySelectorAll('.suggestion').forEach((btn) => {
  btn.addEventListener('click', () => {
    input.value = btn.dataset.q;
    ask();
  });
});

function appendUserMessage(text) {
  if (chatEmpty) chatEmpty.remove();
  const div = document.createElement('div');
  div.className = 'msg msg-user';
  div.textContent = text;
  chatThread.appendChild(div);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function appendTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'msg msg-ai';
  div.id = 'typing-indicator';
  div.innerHTML = `
    <div class="typing-indicator">
      <span></span><span></span><span></span>
    </div>`;
  chatThread.appendChild(div);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function removeTypingIndicator() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

function appendAiMessage({ answer, context, response_time, sources, error }) {
  const div = document.createElement('div');
  div.className = 'msg msg-ai';

  if (error) {
    div.innerHTML = `<span class="answer-text">Something went wrong: ${escapeHtml(error)}</span>`;
    chatThread.appendChild(div);
    chatThread.scrollTop = chatThread.scrollHeight;
    return;
  }

  let html = `<div class="answer-text">${escapeHtml(answer || '')}</div>`;

  if (context) {
    html += `<div class="context-block">${escapeHtml(context)}</div>`;
  }

  const metaParts = [];
  if (response_time) metaParts.push(`Response time: ${response_time}`);
  if (Array.isArray(sources)) {
    sources.forEach((s) => {
      metaParts.push(`Video ${s.video_number} · ${s.start}s–${s.end}s`);
    });
  }
  if (metaParts.length) {
    html += `<div class="msg-meta">${metaParts.map((p) => `<span>${escapeHtml(p)}</span>`).join('')}</div>`;
  }

  div.innerHTML = html;
  chatThread.appendChild(div);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function setLoading(isLoading) {
  askBtn.disabled = isLoading;
  askBtnText.hidden = isLoading;
  askBtnSpinner.hidden = !isLoading;
}

async function ask() {
  const question = input.value.trim();
  if (!question) return;

  appendUserMessage(question);
  input.value = '';
  input.style.height = 'auto';
  setLoading(true);
  appendTypingIndicator();

  const start = performance.now();

  try {
    const res = await fetch('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    const elapsedMs = Math.round(performance.now() - start);

    removeTypingIndicator();

    if (data.error) {
      appendAiMessage({ error: data.error });
    } else {
      const responseTime = data.response_time || `${elapsedMs}ms`;
      appendAiMessage({
        answer: data.answer,
        context: data.context,
        response_time: responseTime,
        sources: data.sources,
      });
      statResponseTime.textContent = responseTime;
    }

    queryCount += 1;
    statQueryCount.textContent = queryCount;
  } catch (err) {
    removeTypingIndicator();
    appendAiMessage({ error: err.message });
  } finally {
    setLoading(false);
  }
}
// --- Copy-to-clipboard for the visible email address ---
const copyBtn = document.getElementById('copy-email-btn');
const emailText = document.getElementById('email-text');

if (copyBtn && emailText) {
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(emailText.textContent);
      copyBtn.textContent = 'Copied';
      copyBtn.classList.add('copied');
      setTimeout(() => {
        copyBtn.textContent = 'Copy';
        copyBtn.classList.remove('copied');
      }, 1800);
    } catch (err) {
      // Clipboard API can fail on non-HTTPS/non-localhost origins —
      // the visible email text is still there as a manual fallback.
    }
  });
}