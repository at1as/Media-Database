(function() {
  const root = document.documentElement;
  const storageKey = 'catalogView';
  const isFile = window.location.protocol === 'file:';
  const requested = new URLSearchParams(window.location.search).get('view');
  let view = readView(requested) || readSavedView() || 'table';
  let storageAvailable = saveView();

  function readView(value) {
    return value === 'tiles' || value === 'table' ? value : null;
  }

  function readSavedView() {
    try {
      return readView(localStorage.getItem(storageKey));
    } catch {
      return null;
    }
  }

  function saveView() {
    try {
      localStorage.setItem(storageKey, view);
      return true;
    } catch {
      return false;
    }
  }

  function updateNavigationLinks() {
    document.querySelectorAll('#navbarSupportedContent a.nav-link').forEach(link => {
      const destination = new URL(link.href);
      if (isFile || !storageAvailable) {
        destination.searchParams.set('view', view);
      } else {
        destination.searchParams.delete('view');
      }
      link.href = destination.href;
    });
  }

  function updatePageUrl() {
    const url = new URL(window.location.href);
    if (storageAvailable) {
      url.searchParams.delete('view');
    } else {
      url.searchParams.set('view', view);
    }
    if (url.href !== window.location.href) {
      try {
        history.replaceState(history.state, '', url);
      } catch {
        // Navigation links can still carry the view on restricted file URLs.
      }
    }
  }

  function applyView() {
    root.dataset.catalogView = view;
    updateNavigationLinks();
    document.dispatchEvent(new Event('catalogviewchange'));
  }

  root.dataset.catalogView = view;
  if (readView(requested)) {
    updatePageUrl();
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateNavigationLinks();
    document.querySelectorAll('.catalog-view-toggle button[data-view]').forEach(button => {
      button.addEventListener('click', () => {
        if (view === button.dataset.view) {
          return;
        }
        view = button.dataset.view;
        storageAvailable = saveView();
        updatePageUrl();
        applyView();
      });
    });
  });

  window.addEventListener('pageshow', event => {
    if (event.persisted) {
      const saved = readSavedView();
      if (saved && saved !== view) {
        view = saved;
        applyView();
      }
    }
  });
})();
