(function() {
  const root = document.documentElement;
  const viewStorageKey = 'catalogView';
  const filtersStorageKey = 'catalogFilters';
  const isFile = window.location.protocol === 'file:';
  const params = new URLSearchParams(window.location.search);
  const requestedView = readView(params.get('view'));
  const requestedFilters = readFilters(params.get('filters'));
  let view = requestedView || readView(readPreference(viewStorageKey)) || 'table';
  let filters = requestedFilters || readFilters(readPreference(filtersStorageKey)) || 'open';
  let viewStorageAvailable = savePreference(viewStorageKey, view);
  let filtersStorageAvailable = savePreference(filtersStorageKey, filters);

  function readView(value) {
    return value === 'tiles' || value === 'table' ? value : null;
  }

  function readFilters(value) {
    return value === 'open' || value === 'closed' ? value : null;
  }

  function readPreference(key) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }

  function savePreference(key, value) {
    try {
      localStorage.setItem(key, value);
      return true;
    } catch {
      return false;
    }
  }

  function updateUrlParams(url, carryPreferences) {
    if (carryPreferences || !viewStorageAvailable) {
      url.searchParams.set('view', view);
    } else {
      url.searchParams.delete('view');
    }
    if (carryPreferences || !filtersStorageAvailable) {
      url.searchParams.set('filters', filters);
    } else {
      url.searchParams.delete('filters');
    }
  }

  function updateNavigationLinks() {
    document.querySelectorAll('#navbarSupportedContent a.nav-link').forEach(link => {
      const destination = new URL(link.href);
      updateUrlParams(destination, isFile);
      link.href = destination.href;
    });
  }

  function updatePageUrl() {
    const url = new URL(window.location.href);
    updateUrlParams(url, false);
    if (url.href !== window.location.href) {
      try {
        history.replaceState(history.state, '', url);
      } catch {
        // Navigation links can still carry preferences on restricted file URLs.
      }
    }
  }

  function applyView() {
    root.dataset.catalogView = view;
    updateNavigationLinks();
    document.dispatchEvent(new Event('catalogviewchange'));
  }

  root.dataset.catalogView = view;
  root.dataset.catalogFilters = filters;
  if (requestedView || requestedFilters) {
    updatePageUrl();
  }

  document.addEventListener('toggle', event => {
    if (event.target.id !== 'advanced-filters') {
      return;
    }
    const next = event.target.open ? 'open' : 'closed';
    if (next === filters) {
      return;
    }
    filters = next;
    root.dataset.catalogFilters = filters;
    filtersStorageAvailable = savePreference(filtersStorageKey, filters);
    updatePageUrl();
    updateNavigationLinks();
  }, true);

  document.addEventListener('DOMContentLoaded', () => {
    updateNavigationLinks();
    document.querySelectorAll('.catalog-view-toggle button[data-view]').forEach(button => {
      button.addEventListener('click', () => {
        if (view === button.dataset.view) {
          return;
        }
        view = button.dataset.view;
        viewStorageAvailable = savePreference(viewStorageKey, view);
        updatePageUrl();
        applyView();
      });
    });
  });

  window.addEventListener('pageshow', event => {
    if (event.persisted) {
      const saved = readView(readPreference(viewStorageKey));
      if (saved && saved !== view) {
        view = saved;
        applyView();
      }

      const savedFilters = readFilters(readPreference(filtersStorageKey));
      if (savedFilters && savedFilters !== filters) {
        filters = savedFilters;
        root.dataset.catalogFilters = filters;
        const panel = document.getElementById('advanced-filters');
        if (panel) {
          panel.open = filters === 'open';
        }
        updateNavigationLinks();
      }
    }
  });
})();
