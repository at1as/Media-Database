if (window.parent !== window) {
  document.addEventListener('keydown', event => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey ||
        !['Escape', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
      return;
    }
    if (event.key !== 'Escape' && (event.target.closest('video, audio, input, select, textarea') ||
        event.target.isContentEditable)) {
      return;
    }
    // File URLs have opaque origins. The parent checks this frame's window.
    const origin = window.location.origin;
    window.parent.postMessage({detailKey: event.key}, origin === 'null' || window.location.protocol === 'file:' ? '*' : origin);
  });
}
