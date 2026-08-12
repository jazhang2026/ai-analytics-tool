import { render, navigate, showLoading } from './ui.js';
import { api, setToken, clearToken, getToken } from './api.js';

const routes = {};
export function register(path, handler) { routes[path] = handler; }

export function registerRoutes(currentPath) {
  const handler = routes[currentPath];
  if (handler) { handler(); }
  else { render('<div class="error"><h2>404</h2><p>Page not found</p></div>'); }
}

// ---- Root redirect ----
register('/', () => {
  if (getToken()) {
    navigate('/dashboard');
  } else {
    navigate('/login');
  }
});

// ---- Register ----
register('/register', () => {
  render(`
    <h1>Register Tenant</h1>
    <form id="f">
      <label>Tenant Name</label><input name="tenant_name" required />
      <label>Admin Email</label><input name="admin_email" type="email" required />
      <label>Admin Password</label><input name="admin_password" type="password" required minlength="8" maxlength="12" />
      <p style="font-size:0.8rem;color:#64748b">8-12 chars, must include uppercase, lowercase, and number</p>
      <button type="submit">Create Tenant</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
  `);
  document.getElementById('f').addEventListener('submit', async (e) => {
    e.preventDefault(); const fd = new FormData(e.target);
    try { showLoading(); const d = await api.post('/tenants', { tenant_name: fd.get('tenant_name'), admin_email: fd.get('admin_email'), admin_password: fd.get('admin_password') }); setToken(d.token); navigate('/dashboard'); }
    catch (err) { render(`<div class="error"><p>${err.message}</p><a href="/register">Try again</a></div>`); }
  });
});

// ---- Login ----
register('/login', () => {
  render(`
    <h1>Login</h1>
    <form id="f">
      <label>Email</label><input name="email" type="email" required />
      <label>Password</label><input name="password" type="password" required />
      <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="/register">Register</a></p>
  `);
  document.getElementById('f').addEventListener('submit', async (e) => {
    e.preventDefault(); const fd = new FormData(e.target);
    try { showLoading(); const d = await api.post('/auth/login', { email: fd.get('email'), password: fd.get('password') }); setToken(d.token); navigate('/dashboard'); }
    catch (err) { render(`<div class="error"><p>${err.message}</p><a href="/login">Try again</a></div>`); }
  });
});

// ---- Dashboard ----
register('/dashboard', async () => {
  if (!getToken()) { navigate('/login'); return; }
  try {
    const me = await api.get('/me');
    const reqs = await api.get('/analytics-requests');
    import('./main.js').then(m => m.setCurrentUser(me));
    const rows = reqs.map(r => `<tr><td><a href="/requests/${r.id}">${r.title}</a></td><td><span class="badge badge-${r.status === 'succeeded' ? 'active' : r.status === 'failed' ? 'error' : 'pending'}">${r.status}</span></td><td>${r.selected_method || '-'}</td></tr>`).join('');
    render(`<h1>Dashboard</h1><div class="card"><p>Welcome, ${me.email} (${me.role})</p></div><h2>Recent Requests</h2><table><thead><tr><th>Title</th><th>Status</th><th>Method</th></tr></thead><tbody>${rows || '<tr><td colspan="3">No requests yet</td></tr>'}</tbody></table>`);
  } catch { clearToken(); navigate('/login'); }
});

// ---- Tenant Users (admin) ----
register('/tenant/users', async () => {
  if (!getToken()) { navigate('/login'); return; }
  try {
    const me = await api.get('/me');
    if (me.role !== 'admin') { navigate('/dashboard'); return; }
    const users = await api.get('/tenant/users');
    const rows = users.map(u => `<tr><td>${u.email}</td><td>${u.role}</td></tr>`).join('');
    render(`
      <h1>Tenant Users</h1>
      <div class="card">
        <h2>Add User</h2>
        <form id="add-user">
          <label>Email</label><input name="email" type="email" required />
          <label>Password</label><input name="password" type="password" required minlength="8" maxlength="12" />
          <label>Role</label><select name="role"><option value="user">User</option><option value="admin">Admin</option></select>
          <button type="submit">Create User</button>
        </form>
      </div>
      <table><thead><tr><th>Email</th><th>Role</th></tr></thead><tbody>${rows}</tbody></table>
    `);
    document.getElementById('add-user').addEventListener('submit', async (e) => {
      e.preventDefault(); const fd = new FormData(e.target);
      try { await api.post('/tenant/users', { email: fd.get('email'), password: fd.get('password'), role: fd.get('role') }); navigate('/tenant/users'); }
      catch (err) { alert(err.message); }
    });
  } catch { clearToken(); navigate('/login'); }
});

// ---- Password Change ----
register('/account/password', () => {
  if (!getToken()) { navigate('/login'); return; }
  render(`
    <h1>Change Password</h1>
    <form id="f">
      <label>Current Password</label><input name="current_password" type="password" required />
      <label>New Password</label><input name="new_password" type="password" required minlength="8" maxlength="12" />
      <p style="font-size:0.8rem;color:#64748b">8-12 chars, must include uppercase, lowercase, and number</p>
      <button type="submit">Change Password</button>
    </form>
  `);
  document.getElementById('f').addEventListener('submit', async (e) => {
    e.preventDefault(); const fd = new FormData(e.target);
    try { await api.patch('/me/password', { current_password: fd.get('current_password'), new_password: fd.get('new_password') }); alert('Password changed'); navigate('/dashboard'); }
    catch (err) { alert(err.message); }
  });
});

// ---- Data Sources ----
register('/data-sources', async () => {
  if (!getToken()) { navigate('/login'); return; }
  try {
    const sources = await api.get('/data-sources');
    const rows = sources.map(s => `<tr><td>${s.name}</td><td>${s.source_type}</td><td><span class="badge badge-${s.status === 'active' ? 'active' : 'pending'}">${s.status}</span></td></tr>`).join('');
    render(`
      <h1>Data Sources</h1>
      <div class="card">
        <h2>Upload File</h2>
        <form id="upload-form" enctype="multipart/form-data">
          <label>File</label><input name="file" type="file" accept=".txt,.pdf,.docx,.xlsx" required />
          <button type="submit">Upload</button>
        </form>
      </div>
      <table><thead><tr><th>Name</th><th>Type</th><th>Status</th></tr></thead><tbody>${rows || '<tr><td colspan="3">No data sources</td></tr>'}</tbody></table>
    `);
  } catch { clearToken(); navigate('/login'); }
});

// ---- New Request ----
register('/requests/new', async () => {
  if (!getToken()) { navigate('/login'); return; }
  try {
    const sources = await api.get('/data-sources');
    const opts = sources.filter(s => s.status === 'active').map(s => `<option value="${s.id}">${s.name} (${s.source_type})</option>`).join('');
    render(`
      <h1>New Analytics Request</h1>
      <form id="f">
        <label>Title</label><input name="title" required />
        <label>Objective</label><textarea name="objective" required></textarea>
        <label>Data Sources</label><select name="data_source_ids" multiple style="height:120px">${opts}</select>
        <button type="submit">Submit Request</button>
      </form>
    `);
    document.getElementById('f').addEventListener('submit', async (e) => {
      e.preventDefault(); const fd = new FormData(e.target);
      try {
        const ids = [...fd.getAll('data_source_ids')];
        const d = await api.post('/analytics-requests', { title: fd.get('title'), objective: fd.get('objective'), data_source_ids: ids });
        navigate(`/requests/${d.id}`);
      } catch (err) { alert(err.message); }
    });
  } catch { clearToken(); navigate('/login'); }
});

// ---- Request Detail ----
register('/requests/:id', async () => {
  if (!getToken()) { navigate('/login'); return; }
  const id = window.location.pathname.split('/').pop();
  try {
    const req = await api.post('/analytics-requests/detail', { request_id: id });
    render(`
      <h1>${req.title}</h1>
      <div class="card">
        <p><strong>Status:</strong> <span class="badge badge-${req.status === 'succeeded' ? 'active' : req.status === 'failed' ? 'error' : 'pending'}">${req.status}</span></p>
        <p><strong>Method:</strong> ${req.selected_method || 'N/A'}</p>
        <p><strong>Rationale:</strong> ${req.method_rationale || 'N/A'}</p>
        ${req.status === 'succeeded' ? `<p><a href="/results/${id}">View Results</a></p>` : ''}
        ${req.error_message ? `<p class="error">${req.error_message}</p>` : ''}
      </div>
      <a href="/dashboard">Back to Dashboard</a>
    `);
  } catch (err) { render(`<div class="error"><p>${err.message}</p></div>`); }
});

// ---- Results ----
register('/results/:id', async () => {
  if (!getToken()) { navigate('/login'); return; }
  const id = window.location.pathname.split('/').pop();
  try {
    const result = await api.post('/analytics-requests/result', { request_id: id });
    render(`
      <h1>Results</h1>
      <div class="card"><p><strong>Summary:</strong> ${result.summary_text || 'N/A'}</p></div>
      ${result.metrics_payload ? `<div class="card"><h2>Metrics</h2><pre>${JSON.stringify(result.metrics_payload, null, 2)}</pre></div>` : ''}
      <p>
        <button onclick="window._download('${id}','csv')">Download CSV</button>
        <button onclick="window._download('${id}','xlsx')">Download Excel</button>
      </p>
      <a href="/dashboard">Back to Dashboard</a>
    `);
  } catch (err) { render(`<div class="error"><p>${err.message}</p></div>`); }
});

window._download = async (id, fmt) => {
  try {
    const res = await fetch('/api/analytics-requests/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
      body: JSON.stringify({ request_id: id, format: fmt }),
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `result_${id}.${fmt}`; a.click();
  } catch (err) { alert(err.message); }
};

// ---- Operator Login ----
register('/operator/login', () => {
  render(`
    <h1>Operator Login</h1>
    <form id="f">
      <label>Email</label><input name="email" type="email" required />
      <label>Password</label><input name="password" type="password" required />
      <button type="submit">Login</button>
    </form>
  `);
  document.getElementById('f').addEventListener('submit', async (e) => {
    e.preventDefault(); const fd = new FormData(e.target);
    try { showLoading(); const d = await api.post('/operator/login', { email: fd.get('email'), password: fd.get('password') }); setToken(d.token); import('./main.js').then(m => { m.setCurrentUser({ role: 'operator', email: fd.get('email') }); navigate('/operator/dashboard'); }); }
    catch (err) { render(`<div class="error"><p>${err.message}</p><a href="/operator/login">Try again</a></div>`); }
  });
});

// ---- Operator Dashboard ----
register('/operator/dashboard', async () => {
  if (!getToken()) { navigate('/operator/login'); return; }
  try {
    const tenants = await api.get('/operator/tenants');
    const rows = tenants.map(t => `<tr><td><a href="/operator/tenants/${t.id}">${t.name}</a></td><td>${t.status}</td></tr>`).join('');
    render(`<h1>Operator Dashboard</h1><table><thead><tr><th>Tenant</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>`);
  } catch { clearToken(); navigate('/operator/login'); }
});

// ---- Operator Tenant Detail ----
register('/operator/tenants/:id', async () => {
  if (!getToken()) { navigate('/operator/login'); return; }
  const id = window.location.pathname.split('/').pop();
  try {
    const d = await api.post('/operator/tenants/detail', { tenant_id: id });
    const urows = d.users.map(u => `<tr><td>${u.email}</td><td>${u.role}</td></tr>`).join('');
    render(`<h1>${d.tenant.name}</h1><h2>Users</h2><table><thead><tr><th>Email</th><th>Role</th></tr></thead><tbody>${urows}</tbody></table><h2>Data Sources</h2><ul>${d.data_sources.map(s => `<li>${s.name} (${s.source_type}) - ${s.status}</li>`).join('')}</ul><a href="/operator/dashboard">Back</a>`);
  } catch (err) { render(`<div class="error"><p>${err.message}</p></div>`); }
});

// ---- Operator Backup ----
register('/operator/backup', async () => {
  if (!getToken()) { navigate('/operator/login'); return; }
  try {
    const backups = await api.get('/operator/backups');
    const rows = backups.map(b => `<tr><td>${b.id}</td><td>${b.file_size || '?'} bytes</td><td>${b.created_at}</td><td><button onclick="window._restore('${b.id}')">Restore</button></td></tr>`).join('');
    render(`
      <h1>Backup & Restore</h1>
      <div class="card"><button id="backup-btn">Create Backup</button></div>
      <table><thead><tr><th>ID</th><th>Size</th><th>Created</th><th>Actions</th></tr></thead><tbody>${rows || '<tr><td colspan="4">No backups</td></tr>'}</tbody></table>
      <a href="/operator/dashboard">Back</a>
    `);
    document.getElementById('backup-btn').addEventListener('click', async () => {
      try { await api.post('/operator/backup'); navigate('/operator/backup'); }
      catch (err) { alert(err.message); }
    });
  } catch { clearToken(); navigate('/operator/login'); }
});

window._restore = async (id) => {
  if (!confirm('Restore database from this backup? This cannot be undone.')) return;
  try { await api.post('/operator/restore', { backup_id: id }); alert('Restore completed'); navigate('/operator/dashboard'); }
  catch (err) { alert(err.message); }
};

// ---- Operator Tenants list ----
register('/operator/tenants', async () => {
  if (!getToken()) { navigate('/operator/login'); return; }
  try {
    const tenants = await api.get('/operator/tenants');
    const rows = tenants.map(t => `<tr><td><a href="/operator/tenants/${t.id}">${t.name}</a></td><td>${t.status}</td></tr>`).join('');
    render(`<h1>All Tenants</h1><table><thead><tr><th>Name</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table><a href="/operator/dashboard">Back</a>`);
  } catch { clearToken(); navigate('/operator/login'); }
});
