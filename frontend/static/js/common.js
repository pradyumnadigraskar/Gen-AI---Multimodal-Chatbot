// frontend/static/js/common.js

// ---------- Logout ----------
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
  logoutBtn.onclick = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    location.href = '/login';
  };
}

// ---------- Dropdowns (Models & Profile) ----------
function setupDropdownByTrigger(triggerEl) {
  if (!triggerEl) return;
  const dropdown = triggerEl.closest('.dropdown');
  const menu = dropdown ? dropdown.querySelector('.dropdown-menu, .dropdown-content') : null;
  if (!dropdown || !menu) return;

  const open = () => dropdown.classList.add('open');
  const close = () => dropdown.classList.remove('open');
  const toggle = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropdown.classList.toggle('open');
  };

  triggerEl.addEventListener('click', toggle);

  // Close on click outside
  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) close();
  });

  // Close on Esc
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') close();
  });
}

// Models trigger is the button with data-dropdown-toggle inside data-dropdown="models"
setupDropdownByTrigger(document.querySelector('[data-dropdown="models"] [data-dropdown-toggle]'));

// Profile trigger (your button already has id="profileBtn")
setupDropdownByTrigger(document.querySelector('#profileBtn'));

// ---------- History Drawer ----------
const historyBtn = document.getElementById('historyBtn');
const historyDrawer = document.getElementById('historyDrawer');
const closeHistory = document.getElementById('closeHistory');
const historyList = document.getElementById('historyList');

function openHistory() {
  if (historyDrawer) historyDrawer.classList.add('open');
}
function hideHistory() {
  if (historyDrawer) historyDrawer.classList.remove('open');
}

if (historyBtn) historyBtn.addEventListener('click', openHistory);
if (closeHistory) closeHistory.addEventListener('click', hideHistory);

// Click outside drawer to close
document.addEventListener('click', (e) => {
  if (!historyDrawer) return;
  if (!historyDrawer.classList.contains('open')) return;
  const clickedInside = historyDrawer.contains(e.target) || (historyBtn && historyBtn.contains(e.target));
  if (!clickedInside) hideHistory();
});

// ---------- History fetching & rendering ----------
async function fetchHistory() {
  try {
    const r = await fetch('/api/history/', { credentials: 'include' });
    if (!r.ok) throw new Error(await r.text());
    return await r.json(); // [{id,title,modality,created_at}]
  } catch (err) {
    console.error('History load failed:', err);
    return [];
  }
}

function renderHistory(items) {
  if (!historyList) return;
  if (!Array.isArray(items) || items.length === 0) {
    historyList.innerHTML = `<div class="empty">No history yet.</div>`;
    return;
  }
  historyList.innerHTML = items.map(i => `
    <div class="history-item" data-id="${i.id}" data-modality="${(i.modality || '').toLowerCase()}">
      <div class="title"><b>[${i.modality}]</b> ${i.title || '(untitled)'} </div>
      <div class="time">${new Date(i.created_at).toLocaleString()}</div>
      <div class="actions">
        <a class="btn sm" href="/chat?chat_id=${i.id}">Open</a>
      </div>
    </div>
  `).join('');
}

function applyHistoryFilter(modality) {
  if (!historyList) return;
  const nodes = [...historyList.querySelectorAll('.history-item')];
  nodes.forEach(n => {
    const m = (n.getAttribute('data-modality') || '').toLowerCase();
    const show = modality === 'all' || modality === m;
    n.style.display = show ? '' : 'none';
  });
}

function setupHistoryFilters() {
  const chips = document.querySelectorAll('.filters .chip');
  if (!chips.length) return;
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const modality = (chip.getAttribute('data-modality') || 'all').toLowerCase();
      applyHistoryFilter(modality);
    });
  });
}

// Prefetch history on page load (so drawer is instant)
window.addEventListener('DOMContentLoaded', async () => {
  const items = await fetchHistory();
  renderHistory(items);
  setupHistoryFilters();
});
