/* ===== CSRF ===== */
function getCsrfToken() {
  const name = 'csrftoken=';
  for (const c of document.cookie.split(';')) {
    const t = c.trim();
    if (t.startsWith(name)) return t.substring(name.length);
  }
  return '';
}

/* ===== API CLIENT ===== */
const api = {
  async request(method, path, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      credentials: 'same-origin',
    };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch('/api' + path, opts);
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data === 'object'
        ? Object.values(data).flat().join(' ')
        : String(data);
      throw new Error(msg);
    }
    return data;
  },
  get:    (path)       => api.request('GET', path),
  post:   (path, body) => api.request('POST', path, body),
  patch:  (path, body) => api.request('PATCH', path, body),
  del:    (path)       => api.request('DELETE', path),

  users:    {
    list:   ()     => api.get('/users/'),
    create: (d)    => api.post('/users/', d),
    get:    (id)   => api.get(`/users/${id}/`),
  },
  songs:    {
    list:   ()     => api.get('/songs/'),
    get:    (id)   => api.get(`/songs/${id}/`),
    delete: (id)   => api.del(`/songs/${id}/`),
  },
  requests: {
    list:    ()    => api.get('/requests/'),
    create:  (d)   => api.post('/requests/', d),
    refresh: (id)  => api.post(`/requests/${id}/refresh_generation/`, {}),
  },
  shares:   {
    list:    ()         => api.get('/shares/'),
    create:  (d)        => api.post('/shares/', d),
    update:  (id, d)    => api.patch(`/shares/${id}/`, d),
    delete:  (id)       => api.del(`/shares/${id}/`),
  },
  libraries: {
    list:       ()        => api.get('/libraries/'),
    get:        (id)      => api.get(`/libraries/${id}/`),
    create:     (d)       => api.post('/libraries/', d),
    update:     (id, d)   => api.patch(`/libraries/${id}/`, d),
    delete:     (id)      => api.del(`/libraries/${id}/`),
    addSong:    (id, sid) => api.post(`/libraries/${id}/add_song/`, { song_id: sid }),
    removeSong: (id, sid) => api.post(`/libraries/${id}/remove_song/`, { song_id: sid }),
  },
};

/* ===== AUTH ===== */
const auth = {
  get user() {
    try { return JSON.parse(localStorage.getItem('cithai_user')); } catch { return null; }
  },
  set user(u) {
    if (u) localStorage.setItem('cithai_user', JSON.stringify(u));
    else localStorage.removeItem('cithai_user');
  },
  logout() { this.user = null; location.href = '/'; },
  require() { if (!this.user) { location.href = '/'; return false; } return true; },
};

/* ===== TOAST ===== */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => { el.style.transition = 'opacity 0.3s'; el.style.opacity = '0'; }, 2600);
  setTimeout(() => el.remove(), 2900);
}

/* ===== HELPERS ===== */
function statusBadge(status) {
  const s = (status || '').toLowerCase();
  const map = {
    pending:    { cls: 'pending',    dot: '○', label: 'Pending' },
    processing: { cls: 'processing', dot: '◉', label: 'Processing' },
    complete:   { cls: 'complete',   dot: '●', label: 'Complete' },
    failed:     { cls: 'failed',     dot: '✕', label: 'Failed' },
  };
  const m = map[s] || { cls: 'pending', dot: '○', label: status };
  return `<span class="badge badge-${m.cls}">${m.dot} ${m.label}</span>`;
}

function formatDate(dt) {
  if (!dt) return '--';
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDuration(secs) {
  if (!secs && secs !== 0) return '--';
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function escHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(String(str || '')));
  return d.innerHTML;
}
