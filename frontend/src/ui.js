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

export function initPasswordToggles() {
  document.querySelectorAll('input[type="password"]').forEach(input => {
    if (input.parentElement?.classList.contains('pw-wrapper')) return; // already wrapped
    const wrapper = document.createElement('span');
    wrapper.className = 'pw-wrapper';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pw-toggle';
    btn.textContent = 'Show';
    btn.addEventListener('click', () => {
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      btn.textContent = isPassword ? 'Hide' : 'Show';
    });
    wrapper.appendChild(btn);
  });
}
