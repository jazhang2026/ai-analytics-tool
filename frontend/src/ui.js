// UI helpers for rendering and navigation
const app = document.getElementById('app');

export function render(html) {
  app.innerHTML = html;
}

export function navigate(path) {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
}

export function showLoading() {
  app.innerHTML = '<div class="loading">Loading...</div>';
}

export function showError(msg) {
  app.innerHTML = `<div class="error"><p>${msg}</p><button onclick="location.reload()">Retry</button></div>`;
}
