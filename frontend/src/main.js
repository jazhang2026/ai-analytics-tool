import { api, getToken, clearToken } from './api.js';
import { render, navigate } from './ui.js';
import { registerRoutes } from './routes.js';

let currentUser = null;

export function getCurrentUser() { return currentUser; }
export function setCurrentUser(u) { currentUser = u; }

export function navBar() {
  const token = getToken();
  if (!token) return '';
  if (currentUser?.role === 'operator') {
    return `<nav>
      <a href="/operator/dashboard">Dashboard</a>
      <a href="/operator/tenants">Tenants</a>
      <a href="/operator/backup">Backup</a>
      <span class="spacer"></span>
      <span>${currentUser.email}</span>
      <button onclick="window._logout()">Logout</button>
    </nav>`;
  }
  return `<nav>
    <a href="/dashboard">Dashboard</a>
    <a href="/data-sources">Data Sources</a>
    <a href="/requests/new">New Request</a>
    ${currentUser?.role === 'admin' ? '<a href="/tenant/users">Users</a>' : ''}
    <a href="/account/password">Password</a>
    <span class="spacer"></span>
    <span>${currentUser.email}</span>
    <button onclick="window._logout()">Logout</button>
  </nav>`;
}

window._logout = async () => {
  try { await api.post('/auth/logout'); } catch {}
  clearToken();
  setCurrentUser(null);
  navigate('/login');
};

async function refreshPage() {
  const path = window.location.pathname;
  if (getToken() && !currentUser) {
    try {
      const me = await api.get('/me');
      setCurrentUser(me);
    } catch {
      clearToken();
      navigate('/login');
      return;
    }
  }
  const nav = navBar();
  const app = document.getElementById('app');
  registerRoutes(path);
  if (nav) {
    setTimeout(() => {
      const el = document.getElementById('app');
      if (el && !el.querySelector('nav')) {
        el.insertAdjacentHTML('afterbegin', nav);
      }
    }, 0);
  }
}

window.addEventListener('popstate', refreshPage);
refreshPage();
