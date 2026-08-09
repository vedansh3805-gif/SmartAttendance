/* ═══════════════════════════════════════════════════════════════
   SmartAttend – main.js
   Clock · Sidebar · Toasts · Flash dismiss · AJAX helpers
═══════════════════════════════════════════════════════════════ */

/* ── Live Clock ─────────────────────────────────────────────── */
function updateClock() {
  const now   = new Date();
  const clock = document.getElementById('topbarClock');
  const dateEl= document.getElementById('topbarDate');
  if (clock)  clock.textContent  = now.toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' });
  if (dateEl) dateEl.textContent = now.toLocaleDateString('en-IN', { weekday:'short', day:'numeric', month:'short', year:'numeric' });
}
updateClock();
setInterval(updateClock, 1000);

/* ── Sidebar Toggle ─────────────────────────────────────────── */
function toggleSidebar() {
  document.getElementById('sidebar')?.classList.toggle('open');
  document.getElementById('sidebarOverlay')?.classList.toggle('show');
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('show');
}

/* ── Toast Notifications ────────────────────────────────────── */
(function() {
  const c = document.createElement('div');
  c.id = 'toastContainer';
  document.body.appendChild(c);
})();

function showToast(message, type = 'info', duration = 3500) {
  const icons = {
    success: 'fa-circle-check',
    error:   'fa-circle-xmark',
    info:    'fa-circle-info',
    warning: 'fa-triangle-exclamation'
  };
  const container = document.getElementById('toastContainer');
  const toast     = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ── Flash Auto-dismiss (4s) ────────────────────────────────── */
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => {
    f.style.transition = 'opacity .4s';
    f.style.opacity = '0';
    setTimeout(() => f.remove(), 400);
  }, 4000);
});

/* ── AJAX Helpers ───────────────────────────────────────────── */
async function postJSON(url, data) {
  const res = await fetch(url, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(data)
  });
  return res.json();
}

async function getJSON(url) {
  return (await fetch(url)).json();
}

/* ── Student Search Autocomplete ────────────────────────────── */
function setupStudentSearch(inputId, resultsId, onSelect) {
  const input   = document.getElementById(inputId);
  const results = document.getElementById(resultsId);
  if (!input || !results) return;

  let debounce;
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = input.value.trim();
    if (q.length < 2) { results.style.display = 'none'; return; }

    debounce = setTimeout(async () => {
      const data = await getJSON(`/api/students/search?q=${encodeURIComponent(q)}`);
      results.innerHTML = '';
      if (!data.length) { results.style.display = 'none'; return; }

      data.forEach(s => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.style.cssText = `
          padding:10px 14px; cursor:pointer; border-bottom:1px solid rgba(255,255,255,.06);
          display:flex; flex-direction:column; gap:2px;
          transition:background .1s;
        `;
        item.innerHTML = `
          <strong style="font-size:.875rem;color:#e8e8f0;">${s.name}</strong>
          <span style="font-size:.72rem;color:#9999b3;">${s.student_id} · ${s.department} · ${s.year}</span>
        `;
        item.addEventListener('mouseenter', () => item.style.background = 'rgba(108,99,255,.1)');
        item.addEventListener('mouseleave', () => item.style.background = '');
        item.addEventListener('click', () => {
          input.value = s.student_id;
          results.style.display = 'none';
          if (onSelect) onSelect(s);
        });
        results.appendChild(item);
      });

      Object.assign(results.style, {
        display: 'block',
        position: 'absolute',
        zIndex: '500',
        width: '100%',
        background: '#13131f',
        border: '1px solid rgba(255,255,255,.1)',
        borderRadius: '10px',
        boxShadow: '0 8px 24px rgba(0,0,0,.4)',
        overflow: 'hidden',
        top: '100%',
        marginTop: '4px'
      });
    }, 260);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !results.contains(e.target)) {
      results.style.display = 'none';
    }
  });
}

/* ── Confirm delete on forms ────────────────────────────────── */
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

/* ── Copy to clipboard ──────────────────────────────────────── */
function copyText(text, label = 'Copied') {
  navigator.clipboard.writeText(text).then(() => showToast(`${label} copied`, 'success'));
}
