(() => {
  'use strict';
  const root = document.documentElement;
  const THEME_KEY = 'samsyn-theme';
  const MATRIX_KEY = 'samsyn-matrix';

  let storedTheme = null;
  let storedMatrix = null;
  try {
    storedTheme = localStorage.getItem(THEME_KEY);
    storedMatrix = localStorage.getItem(MATRIX_KEY);
  } catch (e) {
    // Storage can be disabled; defaults still apply.
  }

  root.dataset.theme = storedTheme === 'light' ? 'light' : 'dark';
  if (storedMatrix === 'off') root.dataset.matrix = 'off';

  function updateThemeColor() {
    const meta = document.getElementById('theme-color');
    if (meta) meta.setAttribute('content', root.dataset.theme === 'light' ? '#f4f7fc' : '#070b14');
  }

  function updateThemeButton(button) {
    const isDark = root.dataset.theme === 'dark';
    button.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    button.setAttribute('title', isDark ? 'Switch to light theme' : 'Switch to dark theme');
  }

  function updateMatrixButton(button) {
    const enabled = root.dataset.matrix !== 'off';
    button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    button.setAttribute('title', enabled ? 'Turn matrix background off' : 'Turn matrix background on');
    button.setAttribute('aria-label', enabled ? 'Turn matrix background off' : 'Turn matrix background on');
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateThemeColor();

    const themeButton = document.getElementById('theme-toggle');
    if (themeButton) {
      updateThemeButton(themeButton);
      themeButton.addEventListener('click', () => {
        root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem(THEME_KEY, root.dataset.theme); } catch (e) {}
        updateThemeColor();
        updateThemeButton(themeButton);
      });
    }

    const matrixButton = document.getElementById('matrix-toggle');
    if (matrixButton) {
      updateMatrixButton(matrixButton);
      matrixButton.addEventListener('click', () => {
        const enabled = root.dataset.matrix !== 'off';
        if (enabled) {
          root.dataset.matrix = 'off';
          try { localStorage.setItem(MATRIX_KEY, 'off'); } catch (e) {}
        } else {
          delete root.dataset.matrix;
          try { localStorage.setItem(MATRIX_KEY, 'on'); } catch (e) {}
        }
        updateMatrixButton(matrixButton);
      });
    }

    const menuButton = document.getElementById('menu-toggle');
    const mobileNav = document.getElementById('mobile-nav');
    if (menuButton && mobileNav) {
      const close = () => {
        menuButton.setAttribute('aria-expanded', 'false');
        mobileNav.hidden = true;
      };
      menuButton.addEventListener('click', () => {
        const expanded = menuButton.getAttribute('aria-expanded') === 'true';
        menuButton.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        mobileNav.hidden = expanded;
      });
      mobileNav.addEventListener('click', (event) => {
        if (event.target.closest('a')) close();
      });
      document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') close();
      });
    }
  });
})();
