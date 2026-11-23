document.addEventListener('DOMContentLoaded', () => {
  const table = document.querySelector('#results[data-sortable]');
  if (!table) {
    return;
  }

  const body = table.tBodies[0];
  const head = table.tHead;
  let sortedHeader;

  for (const header of head.querySelectorAll('th[data-sort]')) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'catalog-sort-button';
    button.textContent = header.textContent.trim();
    header.replaceChildren(button);
  }

  head.addEventListener('click', event => {
    const header = event.target.closest('th[data-sort]');
    if (!header || table.hasAttribute('aria-busy')) {
      return;
    }

    table.setAttribute('aria-busy', 'true');
    header.dataset.sorting = '';

    // Let the busy indicator paint before reordering the table.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      try {
        const reverse = header === sortedHeader;
        const direction = header.getAttribute('aria-sort') === 'ascending' ? 'descending' : 'ascending';
        const rows = Array.from(body.rows);
        const orderedRows = reverse ? rows.reverse() : sortRows(rows, header);

        const nextSibling = body.nextSibling;
        const fragment = document.createDocumentFragment();
        body.remove();
        for (const row of orderedRows) {
          fragment.append(row);
        }
        body.append(fragment);
        table.insertBefore(body, nextSibling);

        sortedHeader?.removeAttribute('aria-sort');
        header.setAttribute('aria-sort', direction);
        sortedHeader = header;
      } finally {
        delete header.dataset.sorting;
        table.removeAttribute('aria-busy');
      }
    }));
  });
});

function sortRows(rows, header) {
  const column = header.cellIndex;
  const numeric = header.dataset.sort === 'number';
  const entries = rows.map(row => {
    const cell = row.cells[column];
    const text = cell.dataset.sortKey ?? cell.textContent.trim();
    const key = numeric ? parseFloat(text.replace(/[^0-9.-]/g, '')) || 0 : text.toLowerCase();
    return {row, key};
  });

  entries.sort((first, second) => {
    if (numeric) {
      return first.key - second.key;
    }
    if (first.key === second.key) {
      return 0;
    }
    return first.key < second.key ? -1 : 1;
  });
  return entries.map(entry => entry.row);
}
