(function() {
  const root = document.documentElement;
  const storageKey = 'darkMode';
  const isFile = window.location.protocol === 'file:';
  const requested = new URLSearchParams(window.location.search).get('dark');
  let dark = requested === '1' || (requested !== '0' && readPreference() !== 'false');
  let storageAvailable = false;

  function readPreference() {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  }

  function savePreference() {
    try {
      localStorage.setItem(storageKey, String(dark));
      return true;
    } catch {
      return false;
    }
  }

  function applyTheme(animateToggle = false) {
    root.classList.toggle('theme-toggle-animated', animateToggle);
    root.classList.toggle('dark-theme', dark);
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
      toggle.checked = dark;
      document.querySelectorAll('#navbarSupportedContent a.nav-link, .navbar-about').forEach(link => {
        const destination = new URL(link.href);
        if (isFile || !storageAvailable) {
          destination.searchParams.set('dark', dark ? '1' : '0');
        } else {
          destination.searchParams.delete('dark');
        }
        link.href = destination.href;
      });
    }
  }

  function updatePageUrl() {
    const url = new URL(window.location.href);
    if (storageAvailable) {
      url.searchParams.delete('dark');
    } else {
      url.searchParams.set('dark', dark ? '1' : '0');
    }
    if (url.href !== window.location.href) {
      try {
        history.replaceState(history.state, '', url);
      } catch {
        // Some browsers restrict history changes to pages opened from disk.
      }
    }
  }

  if (window.parent === window) {
    storageAvailable = savePreference();
    if (requested === '0' || requested === '1') {
      updatePageUrl();
    }
  }
  applyTheme();

  document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    document.getElementById('darkModeToggle')?.addEventListener('change', event => {
      dark = event.target.checked;
      storageAvailable = savePreference();
      updatePageUrl();
      applyTheme(true);
    });
  });

  window.addEventListener('storage', event => {
    if (event.key === storageKey && event.newValue !== null) {
      dark = event.newValue === 'true';
      applyTheme();
    }
  });

  window.addEventListener('pageshow', event => {
    if (event.persisted && window.parent === window) {
      const saved = readPreference();
      if (saved !== null) {
        dark = saved === 'true';
      }
    }
    // Browsers may restore the checkbox value after firing pageshow.
    requestAnimationFrame(() => applyTheme());
  });
})();
