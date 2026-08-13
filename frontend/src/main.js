import { api, getToken, clearToken } from './api.js';
import { render, navigate } from './ui.js';
import { registerRoutes } from './routes.js';

let currentUser = null;

export function getCurrentUser() { return currentUser; }
export function setCurrentUser(u) { currentUser = u; }

export function headerBar() {
  const token = getToken();
  const email = currentUser?.email || '';
  const role = currentUser?.role || '';
  const userMenu = token
    ? `<div class="user-menu">
        <button class="user-email-btn" onclick="window._toggleMenu(event)">${email} <span class="caret">&#9662;</span></button>
        <div class="user-dropdown" id="user-dropdown" hidden>
          <a href="/account/password" onclick="window._closeMenu()">Change Password</a>
          <a href="#" onclick="event.preventDefault(); window._logout()">Logout</a>
        </div>
      </div>`
    : '';
  return `
    <header class="app-header">
      <div class="brand">AI Analytics Tool</div>
      ${userMenu}
    </header>
    ${token ? navBar(role) : ''}
  `;
}

export function navBar(role) {
  const token = getToken();
  if (!token) return '';
  if (role === 'operator') {
    return `<nav class="app-nav">
      <a href="/operator/dashboard">Dashboard</a>
      <a href="/operator/tenants">Tenants</a>
      <a href="/operator/backup">Backup</a>
    </nav>`;
  }
  return `<nav class="app-nav">
    <a href="/dashboard">Dashboard</a>
    <a href="/data-sources">Data Sources</a>
    <a href="/analytics">Data Analytics</a>
    ${role === 'admin' ? '<a href="/tenant/users">Users</a>' : ''}
  </nav>`;
}

window._toggleMenu = (e) => {
  e.stopPropagation();
  const dd = document.getElementById('user-dropdown');
  if (dd) dd.hidden = !dd.hidden;
};

window._closeMenu = () => {
  const dd = document.getElementById('user-dropdown');
  if (dd) dd.hidden = true;
};

document.addEventListener('click', (e) => {
  if (!e.target.closest('.user-menu')) window._closeMenu();
});

export function isOperatorPath(path) {
  return path === '/operator/login' || path.startsWith('/operator/');
}

window._logout = async () => {
  try { await api.post('/auth/logout'); } catch {}
  clearToken();
  setCurrentUser(null);
  navigate('/login');
};

function renderHeader() {
  const el = document.getElementById('app-header');
  if (el) el.innerHTML = headerBar();
}

async function refreshPage() {
  const path = window.location.pathname;
  if (getToken() && !currentUser) {
    try {
      const me = await api.get('/me');
      setCurrentUser(me);
    } catch {
      clearToken();
      navigate(isOperatorPath(path) ? '/operator/login' : '/login');
      return;
    }
  }
  // Unauthenticated visitor on an operator page → operator login
  if (!getToken() && isOperatorPath(path) && path !== '/operator/login') {
    navigate('/operator/login');
    return;
  }
  renderHeader();
  registerRoutes(path);
}

window.addEventListener('popstate', refreshPage);
refreshPage();
