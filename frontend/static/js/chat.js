// const form = document.getElementById('chatForm');
// const chatWindow = document.getElementById('chatWindow');
// let chatId = null;
// form.addEventListener('submit', async (e)=>{
//   e.preventDefault();
//   const msg = new FormData(form).get('message');
//   if(!msg) return;
//   chatWindow.innerHTML += `<div class="msg user">${msg}</div>`;
//   form.reset();
//   const r = await fetch('/api/chat/text', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({chat_id: chatId, message: msg}), credentials:'include'});
//   const data = await r.json();
//   chatId = data.chat_id;
//   chatWindow.innerHTML += `<div class="msg assistant">${marked.parse(data.answer)}</div>`;
//   chatWindow.scrollTop = chatWindow.scrollHeight;
// });


let currentChatId = null;

// helper to render markdown safely (marked already loaded in base.html)
function renderMarkdown(text) {
  try { return marked.parse(text || ''); } catch { return text; }
}

// load chat list into sidebar
async function loadChatList() {
  const r = await fetch('/api/history/', { credentials: 'include' });
  const items = await r.json();
  const list = document.getElementById('chatList');
  list.innerHTML = '';
  items.forEach(i => {
    const el = document.createElement('div');
    el.className = 'chat-list-item';
    el.textContent = i.title || `[${i.modality}] Chat #${i.id}`;
    el.onclick = () => loadChat(i.id);
    list.appendChild(el);
  });
}

// load chat messages into main window
async function loadChat(id) {
  currentChatId = id;
  const rr = await fetch(`/api/history/${id}`, { credentials: 'include' });
  const data = await rr.json();
  const box = document.getElementById('chatWindow');
  box.innerHTML = (data.messages || []).map(m =>
    `<div class="msg ${m.role}"><b>${m.role}:</b> ${renderMarkdown(m.content)}</div>`
  ).join('');
  box.scrollTop = box.scrollHeight;
}

// handle new chat
function newChat() {
  currentChatId = null;
  const box = document.getElementById('chatWindow');
  box.innerHTML = '';
}

document.addEventListener('DOMContentLoaded', async () => {
  // if history page redirected here with chat_id
  const params = new URLSearchParams(window.location.search);
  const jumpId = params.get('chat_id');

  // buttons
  const newChatBtn = document.getElementById('newChatBtn');
  if (newChatBtn) newChatBtn.onclick = newChat;

  // submit handler
  const form = document.getElementById('chatForm');
  const input = form.querySelector('input[name="message"]');
  const box = document.getElementById('chatWindow');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;

    // show user message immediately
    box.innerHTML += `<div class="msg user"><b>user:</b> ${msg}</div>`;
    box.scrollTop = box.scrollHeight;
    input.value = '';

    // send to backend
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      credentials: 'include',
      body: JSON.stringify({ chat_id: currentChatId, message: msg })
    });

    const data = await r.json();

    // track chat_id
    if (data.chat_id) currentChatId = data.chat_id;

    // render assistant reply (markdown)
    box.innerHTML += `<div class="msg assistant"><b>assistant:</b> ${renderMarkdown(data.reply || '')}</div>`;
    box.scrollTop = box.scrollHeight;

    // refresh sidebar titles (first message becomes title)
    loadChatList();
  });

  // initial loads
  await loadChatList();
  if (jumpId) {
    loadChat(parseInt(jumpId, 10));
  }
});
