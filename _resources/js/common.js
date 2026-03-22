function get_filter_fields() {
  return document.querySelectorAll('#filters input:not([type="checkbox"]):not([type="radio"]):not([type="hidden"]), #filters select');
}

function get_filter_field_value(field_id) {
  var field = document.getElementById(field_id);
  if (!field) {
    return '';
  }

  if (field.tomselect) {
    function normalize_select_value(value) {
      return String(value || '').replace(/\s\(\d+\)$/, '');
    }

    function normalize_select_values(values) {
      if (Array.isArray(values)) {
        return values.map(normalize_select_value).join(', ');
      }

      if (field.multiple) {
        return String(values || '')
          .split(',')
          .map(function(part) { return normalize_select_value(part.trim()); })
          .filter(function(part) { return part !== ''; })
          .join(', ');
      }

      return normalize_select_value(values);
    }

    var select_value = field.tomselect.getValue();
    return normalize_select_values(select_value);
  }

  return field.value || '';
}

function get_filter_field_values(field_id) {
  var field = document.getElementById(field_id);
  if (!field) {
    return [];
  }

  if (field.tomselect && field.multiple) {
    return (field.tomselect.items || []).map(function(value) {
      return String(value || '').replace(/\s\(\d+\)$/, '').trim();
    }).filter(function(value) {
      return value !== '';
    });
  }

  var single_value = get_filter_field_value(field_id).trim();
  return single_value === '' ? [] : [single_value];
}

function clear_filter_field(field_id) {
  var field = document.getElementById(field_id);
  if (!field) {
    return;
  }

  if (field.tomselect) {
    field.tomselect.clear(true);
    update_clear_button_visibility(field_id);
    return;
  }

  field.value = '';
  update_clear_button_visibility(field_id);
}

function update_clear_button_visibility(field_id) {
  var field = document.getElementById(field_id);
  if (!field) {
    return;
  }

  var clear_btn = field.parentElement.querySelector('.filter-clear-btn');
  if (clear_btn) {
    if (field.value.trim() === '') {
      clear_btn.style.display = 'none';
      field.parentElement.classList.remove('has-clear-visible');
    } else {
      clear_btn.style.display = 'flex';
      field.parentElement.classList.add('has-clear-visible');
    }
  }
}

function setup_search_clear_buttons() {
  var search_inputs = document.querySelectorAll('.filter-title-input, #cast-search, #director-search, #vote-search');
  forEach(search_inputs, function(input) {
    // Set initial visibility
    update_clear_button_visibility(input.id);

    // Add input event listener
    input.addEventListener('input', function() {
      update_clear_button_visibility(input.id);
    });
  });
}

function detect_results_table_type() {
  var results_table = document.getElementById('results');
  if (!results_table) {
    return null;
  }

  if (results_table.querySelector('th[name="genre_data"]')) {
    return 'series';
  }

  if (results_table.querySelector('th[name="genres_data"]')) {
    return 'movie';
  }

  return null;
}

function trigger_page_search() {
  var table_type = detect_results_table_type();

  log_filter_debug('trigger_page_search', {
    table_type: table_type
  });

  if (table_type === 'series') {
    try {
      search_series_table('results');
    } catch(err) {
      // no action
    }
    return;
  }

  if (table_type === 'movie') {
    try{
      search_movie_table('results');
    } catch(err) {
      // no action
    }
  }
}

function filter_debug_enabled() {
  try {
    if (window.location && window.location.search.indexOf('debug_filters=1') !== -1) {
      return true;
    }

    return window.localStorage && window.localStorage.getItem('debug_filters') === '1';
  } catch (err) {
    return false;
  }
}

function log_filter_debug(label, payload) {
  if (!filter_debug_enabled()) {
    return;
  }

  console.log('[Filter Debug] ' + label, payload);
}

function parse_list_tokens(value) {
  return String(value || '')
    .replace(/\n/g, ',')
    .split(',')
    .map(function(part) {
      return part.replace(/\s+/g, ' ').trim().toLowerCase();
    })
    .filter(function(part) {
      return part !== '';
    });
}

function selected_values_in_list(selected_values, item) {
  var item_list = parse_list_tokens(item);
  var normalized_selected_values = selected_values.map(function(value) {
    return String(value || '').replace(/\s+/g, ' ').trim().toLowerCase();
  }).filter(function(value) {
    return value !== '';
  });

  for (var i = 0; i < normalized_selected_values.length; i++) {
    var selected_value = normalized_selected_values[i];
    var matched = false;

    for (var j = 0; j < item_list.length; j++) {
      if (item_list[j] === selected_value) {
        matched = true;
        break;
      }
    }

    if (!matched) {
      log_filter_debug('selected_values_in_list:no_match', {
        selected_values: normalized_selected_values,
        raw_item: item,
        item_list: item_list
      });
      return false;
    }
  }

  return true;
}

function count_active_filters() {
  var filter_inputs = get_filter_fields();
  var count = 0;

  forEach(filter_inputs, function(input) {
    if (get_filter_field_value(input.id).trim() !== '') {
      count += 1;
    }
  });

  return count;
}

function update_clear_all_filters_button() {
  var button = document.getElementById('clear_all_filters_btn');
  if (!button) {
    return;
  }

  var label = button.querySelector('.media-action-btn-label');
  if (!label) {
    return;
  }

  var active_filter_count = count_active_filters();

  label.textContent = 'Clear All Filters (' + active_filter_count + ')';
  button.classList.toggle('is-disabled', active_filter_count === 0);
  button.disabled = active_filter_count === 0;
}

function update_results_empty_state(count) {
  var results_message = document.getElementById('results-message');
  var results_container = document.getElementById('results-container');

  if (results_message) {
    results_message.style.display = count === 0 ? 'block' : 'none';
  }

  if (results_container) {
    results_container.style.display = count === 0 ? 'none' : '';
  }
}

function update_results_count_display(count) {
  var current_count = document.getElementById('results_num');
  var total_count = document.getElementById('total_num');
  var count_spacer = document.getElementById('mv_seperator');
  var page_current_count = document.getElementById('page_results_num');
  var page_total_count = document.getElementById('page_total_num');
  var page_count_spacer = document.getElementById('page_mv_seperator');

  if (current_count) {
    current_count.innerHTML = count;
  }

  if (page_current_count) {
    page_current_count.innerHTML = count;
  }

  if (!total_count) {
    return;
  }

  var total_value = total_count.innerHTML;
  var show_filtered_count = String(count) !== String(total_value);

  if (current_count) {
    current_count.style.display = show_filtered_count ? '' : 'none';
    if (show_filtered_count) {
      current_count.style.color = '#45d234';
    }
  }

  if (count_spacer) {
    count_spacer.style.display = show_filtered_count ? '' : 'none';
  }

  if (page_current_count) {
    page_current_count.style.display = show_filtered_count ? '' : 'none';
  }

  if (page_count_spacer) {
    page_count_spacer.style.display = show_filtered_count ? '' : 'none';
  }

  if (page_total_count) {
    page_total_count.innerHTML = total_value;
  }

  var page_results_summary = document.querySelector('.filters-results-summary');
  if (page_results_summary) {
    page_results_summary.classList.toggle('is-filtered', show_filtered_count);
    page_results_summary.classList.toggle('is-empty', count === 0);
  }
}

function sanitize_numeric_filter_value(input) {
  var filter_type = input.getAttribute('data-numeric-filter');
  var original_value = input.value;
  var sanitized_value = original_value;

  if (filter_type === 'decimal') {
    sanitized_value = sanitized_value.replace(/[^0-9.]/g, '');

    var first_decimal_index = sanitized_value.indexOf('.');
    if (first_decimal_index !== -1) {
      sanitized_value = sanitized_value.substring(0, first_decimal_index + 1) + sanitized_value.substring(first_decimal_index + 1).replace(/\./g, '');
    }
  } else {
    sanitized_value = sanitized_value.replace(/[^0-9]/g, '');
  }

  if (sanitized_value !== original_value) {
    input.value = sanitized_value;
    input.classList.add('filter-input-invalid');

    window.clearTimeout(input.invalidFilterTimeout);
    input.invalidFilterTimeout = window.setTimeout(function() {
      input.classList.remove('filter-input-invalid');
    }, 900);
  } else {
    input.classList.remove('filter-input-invalid');
  }
}

function initialize_numeric_filter_inputs() {
  var numeric_inputs = document.querySelectorAll('.numeric-filter-input');

  forEach(numeric_inputs, function(input) {
    input.addEventListener('keydown', function(event) {
      if (event.key === 'e' || event.key === 'E' || event.key === '+' || event.key === '-') {
        event.preventDefault();
        input.classList.add('filter-input-invalid');

        window.clearTimeout(input.invalidFilterTimeout);
        input.invalidFilterTimeout = window.setTimeout(function() {
          input.classList.remove('filter-input-invalid');
        }, 900);
      }
    });

    input.addEventListener('input', function() {
      sanitize_numeric_filter_value(input);
    });

    input.addEventListener('paste', function() {
      window.setTimeout(function() {
        sanitize_numeric_filter_value(input);
      }, 0);
    });
  });
}

function populate_select_options(select, values, include_empty_option) {
  select.innerHTML = '';
  if (include_empty_option) {
    select.appendChild(new Option('', ''));
  }

  forEach(values, function(value) {
    select.appendChild(new Option(value, value));
  });
}

function collect_table_values(cell_name) {
  var cells = document.getElementsByName(cell_name);
  var values = {};

  forEach(cells, function(cell) {
    if (cell.tagName === 'TH') {
      return;
    }

    var raw_values = cell.textContent.replace(/\n/g, ',').split(',');
    forEach(raw_values, function(raw_value) {
      var value = raw_value.trim();
      if (value !== '') {
        values[value] = true;
      }
    });
  });

  return Object.keys(values).sort(function(a, b) {
    return a.localeCompare(b);
  });
}

function get_filter_option_cell_name(field_id) {
  if (field_id === 'genre-search') {
    if (document.getElementsByName('genres_data').length > 0) {
      return 'genres_data';
    }
    return 'genre_data';
  }

  if (field_id === 'language-search') {
    return 'languages_data';
  }

  return null;
}

function collect_visible_table_value_counts(cell_name) {
  var cells = document.getElementsByName(cell_name);
  var counts = {};

  forEach(cells, function(cell) {
    if (cell.tagName === 'TH') {
      return;
    }

    if (!cell.parentElement || cell.parentElement.style.display === 'none') {
      return;
    }

    var seen_in_row = {};
    var raw_values = cell.textContent.replace(/\n/g, ',').split(',');
    forEach(raw_values, function(raw_value) {
      var value = raw_value.trim();
      if (value === '' || seen_in_row[value]) {
        return;
      }

      seen_in_row[value] = true;
      counts[value] = (counts[value] || 0) + 1;
    });
  });

  return counts;
}

function refresh_filter_select_for_visible_rows(field_id) {
  var select = document.getElementById(field_id);
  if (!select || !select.tomselect) {
    return;
  }

  var cell_name = get_filter_option_cell_name(field_id);
  if (!cell_name) {
    return;
  }

  var counts = collect_visible_table_value_counts(cell_name);
  var selected_values = select.tomselect.getValue();
  if (!Array.isArray(selected_values)) {
    selected_values = selected_values ? [selected_values] : [];
  }

  forEach(selected_values, function(value) {
    if (!(value in counts)) {
      counts[value] = 0;
    }
  });

  var option_values = Object.keys(counts).sort(function(a, b) {
    var count_delta = (counts[b] || 0) - (counts[a] || 0);
    if (count_delta !== 0) {
      return count_delta;
    }

    return a.localeCompare(b);
  });

  select.tomselect.clearOptions();

  forEach(option_values, function(value) {
    var count = counts[value];
    select.tomselect.addOption({
      value: value,
      text: value,
      count: count
    });
  });

  select.tomselect.setValue(selected_values, true);
  select.tomselect.refreshOptions(false);
  select.tomselect.refreshItems();

  log_filter_debug('refresh_filter_select_for_visible_rows', {
    field_id: field_id,
    selected_values: selected_values,
    option_values_sample: option_values.slice(0, 20),
    counts_sample: option_values.slice(0, 20).map(function(value) {
      return { value: value, count: counts[value] };
    })
  });
}

function collect_year_values() {
  var cells = document.getElementsByName('year_data');
  var values = {};
  var current_year = new Date().getFullYear();

  forEach(cells, function(cell) {
    var matches = cell.textContent.match(/\d{4}/g) || [];
    forEach(matches, function(match) {
      values[match] = true;
    });
  });

  for (var year = current_year; year >= 1900; year--) {
    if (values[String(year)]) {
      break;
    }
    values[String(year)] = true;
  }

  return Object.keys(values).sort(function(a, b) {
    return parseInt(a, 10) - parseInt(b, 10);
  });
}

function collect_rating_values() {
  var values = [];
  var rating = 0;

  while (rating <= 100) {
    values.push((rating / 10).toFixed(1));
    rating += 1;
  }

  return values;
}

function collect_visible_rating_threshold_counts() {
  var results_table = document.getElementById('results');
  var rows = results_table ? results_table.querySelectorAll('tbody tr') : [];
  var thresholds = collect_rating_values();
  var counts = {};
  var visible_ratings = [];

  forEach(thresholds, function(threshold) {
    counts[threshold] = 0;
  });

  forEach(rows, function(row) {
    if (row.style.display === 'none') {
      return;
    }

    var rating_cell = row.querySelector('[name="rating_data"]');
    if (!rating_cell) {
      return;
    }

    var rating_value = parseFloat((rating_cell.textContent || '').trim());
    if (!isNaN(rating_value)) {
      visible_ratings.push(rating_value);
    }
  });

  forEach(thresholds, function(threshold) {
    var threshold_value = parseFloat(threshold);

    forEach(visible_ratings, function(rating_value) {
      if (rating_value >= threshold_value) {
        counts[threshold] += 1;
      }
    });
  });

  return counts;
}

function refresh_rating_select_options() {
  var rating_select = document.getElementById('rating-search');
  if (!rating_select || rating_select.tomselect) {
    return;
  }

  var selected_value = rating_select.value;
  var rating_values = collect_rating_values();
  var counts = collect_visible_rating_threshold_counts();

  rating_select.innerHTML = '';
  rating_select.appendChild(new Option('', ''));

  forEach(rating_values, function(value) {
    rating_select.appendChild(new Option(value + ' (' + counts[value] + ')', value));
  });

  rating_select.value = selected_value;
}

function format_selected_rating_option() {
  var rating_select = document.getElementById('rating-search');
  if (!rating_select || rating_select.tomselect || !rating_select.value) {
    return;
  }

  var selected_option = rating_select.options[rating_select.selectedIndex];
  if (selected_option) {
    selected_option.text = rating_select.value + '+';
  }
}

function format_selected_year_options() {
  forEach(['year-min-search', 'year-max-search'], function(field_id) {
    var year_select = document.getElementById(field_id);
    if (!year_select || year_select.tomselect || !year_select.value) {
      return;
    }

    var selected_option = year_select.options[year_select.selectedIndex];
    if (selected_option) {
      selected_option.text = year_select.value;
    }
  });
}

function collect_visible_year_range_values() {
  var results_table = document.getElementById('results');
  var rows = results_table ? results_table.querySelectorAll('tbody tr') : [];
  var table_type = detect_results_table_type();
  var ranges = [];

  forEach(rows, function(row) {
    if (row.style.display === 'none') {
      return;
    }

    var year_cell = row.querySelector('[name="year_data"]');
    if (!year_cell) {
      return;
    }

    var year_text = (year_cell.textContent || '').trim();
    var matches = year_text.match(/\d{4}/g) || [];

    if (matches.length === 0) {
      return;
    }

    if (table_type === 'series') {
      var start_year = parseInt(matches[0], 10);
      var end_year = null;

      if (matches.length > 1) {
        end_year = parseInt(matches[1], 10);
      } else if (year_text.indexOf('-') === -1) {
        end_year = start_year;
      }

      ranges.push({
        min: start_year,
        max: end_year
      });
      return;
    }

    var year_value = parseInt(matches[0], 10);
    ranges.push({
      min: year_value,
      max: year_value
    });
  });

  return ranges;
}

function build_year_option_counts(year_values) {
  var ranges = collect_visible_year_range_values();
  var min_counts = {};
  var max_counts = {};

  forEach(year_values, function(year_string) {
    var year_value = parseInt(year_string, 10);
    min_counts[year_string] = 0;
    max_counts[year_string] = 0;

    forEach(ranges, function(range) {
      if (range.min >= year_value) {
        min_counts[year_string] += 1;
      }

      if (range.max !== null && range.max <= year_value) {
        max_counts[year_string] += 1;
      }
    });
  });

  return {
    min: min_counts,
    max: max_counts
  };
}

function refresh_year_select_options() {
  var year_values = collect_year_values();
  var counts = build_year_option_counts(year_values);
  var year_min_select = document.getElementById('year-min-search');
  var year_max_select = document.getElementById('year-max-search');
  var selected_min = year_min_select ? year_min_select.value : '';
  var selected_max = year_max_select ? year_max_select.value : '';
  var min_floor = selected_min ? parseInt(selected_min, 10) : null;

  if (year_min_select) {
    year_min_select.innerHTML = '';
    year_min_select.appendChild(new Option('', ''));

    forEach(year_values, function(value) {
      year_min_select.appendChild(new Option(value + ' (' + counts.min[value] + ')', value));
    });

    year_min_select.value = selected_min;
  }

  if (year_max_select) {
    year_max_select.innerHTML = '';
    year_max_select.appendChild(new Option('', ''));

    forEach(year_values, function(value) {
      var numeric_value = parseInt(value, 10);
      if (min_floor !== null && numeric_value < min_floor) {
        return;
      }

      year_max_select.appendChild(new Option(value + ' (' + counts.max[value] + ')', value));
    });

    if (selected_max && min_floor !== null && parseInt(selected_max, 10) < min_floor) {
      selected_max = '';
    }

    year_max_select.value = selected_max;
  }

  format_selected_year_options();

  return selected_max;
}

function clear_tom_select_search_state(tom_select) {
  if (!tom_select) {
    return;
  }

  tom_select.setTextboxValue('');

  if (tom_select.control_input) {
    tom_select.control_input.value = '';
  }

  if (typeof tom_select.lastValue !== 'undefined') {
    tom_select.lastValue = '';
  }

  if (typeof tom_select.lastQuery !== 'undefined') {
    tom_select.lastQuery = null;
  }

  tom_select.inputState();
}

function initialize_enhanced_filter_selects() {
  var rating_select = document.getElementById('rating-search');
  if (rating_select) {
    refresh_rating_select_options();
    if (!rating_select.dataset.filterBound) {
      rating_select.addEventListener('change', function() {
        trigger_page_search();
        format_selected_rating_option();
      });
      rating_select.addEventListener('focus', refresh_rating_select_options);
      rating_select.addEventListener('mousedown', refresh_rating_select_options);
      rating_select.dataset.filterBound = '1';
    }
    format_selected_rating_option();
  }

  var year_values = collect_year_values();
  forEach(['year-min-search', 'year-max-search'], function(field_id) {
    var year_select = document.getElementById(field_id);
    if (year_select) {
      if (!year_select.dataset.filterBound) {
        year_select.addEventListener('change', function() {
          var previous_max = document.getElementById('year-max-search') ? document.getElementById('year-max-search').value : '';
          trigger_page_search();
          var refreshed_max = refresh_year_select_options();
          format_selected_year_options();

          if (field_id === 'year-min-search' && previous_max !== refreshed_max) {
            trigger_page_search();
          }
        });
        year_select.addEventListener('focus', refresh_year_select_options);
        year_select.addEventListener('mousedown', refresh_year_select_options);
        year_select.dataset.filterBound = '1';
      }
    }
  });

  refresh_year_select_options();
  format_selected_year_options();

  if (typeof TomSelect === 'undefined') {
    return;
  }

  [
    { id: 'genre-search', placeholder: 'Any genres' },
    { id: 'language-search', placeholder: 'Any languages' }
  ].forEach(function(config) {
    var select = document.getElementById(config.id);
    if (select && !select.tomselect) {
      populate_select_options(select, collect_table_values(get_filter_option_cell_name(config.id)), false);
      new TomSelect(select, {
        allowEmptyOption: true,
        create: false,
        hideSelected: true,
        maxItems: null,
        placeholder: config.placeholder,
        searchField: ['text'],
        refreshThrottle: 0,
        plugins: {
          remove_button: {
            title: 'Remove'
          },
          no_active_items: {}
        },
        render: {
          option: function(data, escape) {
            var option_label = escape(data.text || '');

            if (typeof data.count === 'number') {
              option_label += ' <span class="filter-option-count">(' + escape(String(data.count)) + ')</span>';
            }

            return '<div>' + option_label + '</div>';
          },
          item: function(data, escape) {
            return '<div>' + escape(data.text || '') + '</div>';
          }
        },
        onDropdownOpen: function() {
          refresh_filter_select_for_visible_rows(config.id);
        },
        onFocus: function() {
          clear_tom_select_search_state(this);
          this.refreshOptions(false);
        },
        onBlur: function() {
          clear_tom_select_search_state(this);
          this.refreshOptions(false);
        },
        onDropdownClose: function() {
          clear_tom_select_search_state(this);
          this.refreshOptions(false);
        },
        onItemAdd: function() {
          clear_tom_select_search_state(this);
        },
        onChange: function() {
          log_filter_debug('tomselect:onChange', {
            field_id: config.id,
            getValue: this.getValue(),
            items: this.items ? this.items.slice() : [],
            selected_texts: (this.items || []).map(function(value) {
              var option = this.options[value];
              return option ? option.text : null;
            }, this)
          });
          trigger_page_search();
        }
      });
    }
  });

}

// Refine Movie Table based on current filters
function search_movie_table(table_id) {
  var movie_table = document.getElementById(table_id);

  // Get queries from each search field
  var rating_query    = get_filter_field_value('rating-search').toLowerCase();
  var vote_query      = get_filter_field_value('vote-search').toLowerCase().replace(/\,/g, '');
  var title_query     = get_filter_field_value('title-search').toLowerCase();
  var year_min_query  = get_filter_field_value('year-min-search').toLowerCase();
  var year_max_query  = get_filter_field_value('year-max-search').toLowerCase();
  var genre_query     = get_filter_field_value('genre-search').toLowerCase();
  var genre_values    = get_filter_field_values('genre-search');
  var cast_query      = get_filter_field_value('cast-search').toLowerCase();
  var director_query  = get_filter_field_value('director-search').toLowerCase();
  var language_query  = get_filter_field_value('language-search').toLowerCase();
  var language_values = get_filter_field_values('language-search');

  log_filter_debug('search_movie_table:queries', {
    title_query: title_query,
    genre_query: genre_query,
    genre_values: genre_values,
    language_query: language_query,
    language_values: language_values
  });

  // Traverse each row and cell. Hide rows whose content fails to match query
  for (var i = 1; i < movie_table.rows.length; i++) {
    var rating_cell   = movie_table.rows[i].cells[1].innerHTML.toLowerCase();
    var vote_cell     = movie_table.rows[i].cells[2].innerHTML.toLowerCase().replace(/\,/g, '');
    var title_cell    = movie_table.rows[i].cells[3].children[0].innerHTML.toLowerCase();
    var year_cell     = movie_table.rows[i].cells[4].innerHTML.toLowerCase();
    var genre_cell    = movie_table.rows[i].cells[6].textContent.toLowerCase();
    var cast_cell     = movie_table.rows[i].cells[7].textContent.toLowerCase();
    var director_cell = movie_table.rows[i].cells[8].textContent.toLowerCase();
    var language_cell = movie_table.rows[i].cells[9].textContent.toLowerCase();

    if (filter_debug_enabled() && i <= 5 && (genre_values.length > 0 || language_values.length > 0)) {
      log_filter_debug('search_movie_table:row_sample', {
        row_index: i,
        title_cell: title_cell,
        raw_genre_cell: movie_table.rows[i].cells[6].textContent,
        parsed_genre_tokens: parse_list_tokens(movie_table.rows[i].cells[6].textContent),
        raw_language_cell: movie_table.rows[i].cells[9].textContent,
        parsed_language_tokens: parse_list_tokens(movie_table.rows[i].cells[9].textContent)
      });
    }

    // Discard row if rating is empty, None, or less than query
    if (rating_query !== '' && (rating_cell === '' || rating_cell === 'none' || rating_cell.trim() === 'none' || parseFloat(rating_cell) < parseFloat(rating_query))) {
      movie_table.rows[i].style.display = 'none';
    }
    else if (vote_query !== '' && (vote_cell === '' || vote_cell === 'none' || vote_cell.trim() === 'none' || parseFloat(vote_cell) < parseFloat(vote_query))) {
      movie_table.rows[i].style.display = 'none';
    }
    else if (!title_match(title_query, title_cell) && !title_match(title_query, remove_diacritics(title_cell)) && title_query !== '') {
      movie_table.rows[i].style.display = 'none';
    }
    else if (year_min_query !== '' && year_cell !== '' && (parseInt(year_cell) < parseInt(year_min_query))) {
      movie_table.rows[i].style.display = 'none';
    }
    else if (year_max_query !== '' && year_cell !== '' && (parseInt(year_cell) > parseInt(year_max_query))) {
      movie_table.rows[i].style.display = 'none';
    }
    else if (genre_values.length > 0 && !selected_values_in_list(genre_values, genre_cell)) {
        movie_table.rows[i].style.display = 'none';
    }
    else if (!substrings_in_list(cast_query, cast_cell) && cast_query !== '') {
      movie_table.rows[i].style.display = 'none';
    }
    else if (!title_match(director_query, director_cell) && !title_match(director_query, remove_diacritics(director_cell)) && director_query !== '') {
      movie_table.rows[i].style.display = 'none';
    }
    else if (language_values.length > 0 && !selected_values_in_list(language_values, language_cell)) {
        movie_table.rows[i].style.display = 'none';
    }
    else {
      movie_table.rows[i].style.display = '';
    }
  }

  // filter each tile
  var tiles = document.querySelectorAll('[name="tile_data"]');

  tiles.forEach(tile => {
    var rating_cell = tile.querySelector('[name="rating_data"]').textContent;
    var vote_cell = tile.querySelector('[name="vote_data"]').textContent;
    var title_cell = tile.querySelector('[name="title_data"]').textContent;
    var year_cell = tile.querySelector('[name="year_data"]').textContent;
    var genre_cell = tile.querySelector('[name="genres_data"]').textContent;
    var cast_cell = tile.querySelector('[name="stars_data"]').textContent;
    var director_cell = tile.querySelector('[name="director_data"]').textContent;
    var language_cell = tile.querySelector('[name="languages_data"]').textContent;

    // Discard row if rating is empty, None, or less than query
    if (rating_query !== '' && (rating_cell === '' || rating_cell === 'none' || rating_cell.trim() === 'none' || parseFloat(rating_cell) < parseFloat(rating_query))) {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (vote_query !== '' && (vote_cell === '' || vote_cell === 'none' || vote_cell.trim() === 'none' || parseFloat(vote_cell) < parseFloat(vote_query))) {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (!title_match(title_query, title_cell) && !title_match(title_query, remove_diacritics(title_cell)) && title_query !== '') {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (year_min_query !== '' && year_cell !== '' && (parseInt(year_cell) < parseInt(year_min_query))) {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (year_max_query !== '' && year_cell !== '' && (parseInt(year_cell) > parseInt(year_max_query))) {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (genre_values.length > 0 && !selected_values_in_list(genre_values, genre_cell)) {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (!substrings_in_list(cast_query, cast_cell) && cast_query !== '') {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (!title_match(director_query, director_cell) && !title_match(director_query, remove_diacritics(director_cell)) && director_query !== '') {
      tile.style.setProperty('display', 'none', 'important');
    }
    else if (language_values.length > 0 && !selected_values_in_list(language_values, language_cell)) {
      tile.style.setProperty('display', 'none', 'important');
    }
    else {
      tile.style.display = '';
    }
  });

  // Update the filtered counter in the page header
  var count = 0;
  for (var j=1; j<movie_table.rows.length; j++) {
    if (movie_table.rows[j].style.display !== 'none') {
      count += 1;
    }
  }

  update_results_count_display(count);
  update_clear_all_filters_button();
  update_results_empty_state(count);
  update_random_selection_button();

  stripe_table();
};


// Refine Series Table based on current filters
function search_series_table(table_id) {
  var series_table = document.getElementById(table_id);

  // Get queries from each search field
  var rating_query    = get_filter_field_value('rating-search').toLowerCase();
  var vote_query      = get_filter_field_value('vote-search').toLowerCase().replace(/\,/g, '');
  var title_query     = get_filter_field_value('title-search').toLowerCase();
  var year_min_query  = get_filter_field_value('year-min-search').toLowerCase();
  var year_max_query  = get_filter_field_value('year-max-search').toLowerCase();
  var genre_query     = get_filter_field_value('genre-search').toLowerCase();
  var genre_values    = get_filter_field_values('genre-search');
  var cast_query      = get_filter_field_value('cast-search').toLowerCase();
  var language_query  = get_filter_field_value('language-search').toLowerCase();
  var language_values = get_filter_field_values('language-search');

  log_filter_debug('search_series_table:queries', {
    title_query: title_query,
    genre_query: genre_query,
    genre_values: genre_values,
    language_query: language_query,
    language_values: language_values
  });

  // Traverse each row and cell. Hide rows whose content fails to match query
  for (var i = 1; i < series_table.rows.length; i++) {
    var rating_cell     = series_table.rows[i].cells[1].innerHTML.toLowerCase();
    var vote_cell       = series_table.rows[i].cells[2].innerHTML.toLowerCase().replace(/\,/g, '');
    var title_cell      = series_table.rows[i].cells[3].children[0].innerHTML.toLowerCase();
    var start_year_cell = series_table.rows[i].cells[4].innerHTML.trim().substring(0,4).toLowerCase().trim();
    var end_year_cell   = series_table.rows[i].cells[4].innerHTML.trim().substring(5,9).toLowerCase().trim();
    var genre_cell      = series_table.rows[i].cells[5].textContent.toLowerCase();
    var cast_cell       = series_table.rows[i].cells[6].textContent.toLowerCase();
    var language_cell   = series_table.rows[i].cells[7].textContent.toLowerCase();

    if (filter_debug_enabled() && i <= 5 && (genre_values.length > 0 || language_values.length > 0)) {
      log_filter_debug('search_series_table:row_sample', {
        row_index: i,
        title_cell: title_cell,
        raw_genre_cell: series_table.rows[i].cells[5].textContent,
        parsed_genre_tokens: parse_list_tokens(series_table.rows[i].cells[5].textContent),
        raw_language_cell: series_table.rows[i].cells[7].textContent,
        parsed_language_tokens: parse_list_tokens(series_table.rows[i].cells[7].textContent)
      });
    }

    // Discard row if rating is empty, None, or less than query
    if (rating_query !== '' && (rating_cell === '' || rating_cell === 'none' || rating_cell.trim() === 'none' || parseFloat(rating_cell) < parseFloat(rating_query))) {
      series_table.rows[i].style.display = 'none';
    }
    else if (vote_query !== '' && (vote_cell === '' || vote_cell === 'none' || vote_cell.trim() === 'none' || parseFloat(vote_cell) < parseFloat(vote_query))) {
      series_table.rows[i].style.display = 'none';
    }
    else if (title_cell.indexOf(title_query) === -1 && remove_diacritics(title_cell).indexOf(title_query) === -1 && title_query !== '') {
      series_table.rows[i].style.display = 'none';
    }
    else if (year_min_query !== '' && start_year_cell !== '' && (parseInt(start_year_cell) < parseInt(year_min_query))) {
      series_table.rows[i].style.display = 'none';
    }
    else if (year_max_query !== '' && ((end_year_cell === '') || (end_year_cell !== '' && (parseInt(end_year_cell) > parseInt(year_max_query))))) {
      series_table.rows[i].style.display = 'none';
    }
    else if (genre_values.length > 0 && !selected_values_in_list(genre_values, genre_cell)) {
        series_table.rows[i].style.display = 'none';
    }
    else if (!substrings_in_list(cast_query, cast_cell) && cast_query !== '') {
      series_table.rows[i].style.display = 'none';
    }
    else if (language_values.length > 0 && !selected_values_in_list(language_values, language_cell)) {
        series_table.rows[i].style.display = 'none';
    }
    else {
      series_table.rows[i].style.display = '';
    }
  }

  // Update the filtered counter in the page header
  var count = 0;
  for (var j = 1; j < series_table.rows.length; j++) {
    if (series_table.rows[j].style.display !== 'none') {
      count += 1
    }
  }

  update_results_count_display(count);
  update_clear_all_filters_button();
  update_results_empty_state(count);
  update_random_selection_button();

  stripe_table();
};


// Return True if any from catagory query list is in item list
function substrings_in_list(query, item, filter_type) {

  var query_list      = query.split(',');
  var item_list       = item.split(',');
  var positive_match  = false;
  var negative_match  = false;

  // allow genres and langugaes to be seperated by spaces (cast must be comma seperated)
  if (filter_type === "genre" || filter_type === "language") {
    if (query_list.length === 1 && query.split(' ').length > 1) {
      query_list = query.split(' ');
    }
  }

  // seperate NOT filters from other filters
  var query_not     = [];
  var query_match   = [];
  var current_query = '';

  // Separate queries into 'match' and 'not' queries
  for(var j=0; j<query_list.length; j++) {
    current_query = query_list[j].trim();
    if (current_query.length > 1 && current_query[0] === "!"){
      query_not.push(current_query.substring(1,current_query.length));
    } else {
      if (current_query !== '!') { query_match.push(current_query); }
    }
  }

  // If any 'match' queries are not present in item list return false
  for(var k=0; k<query_match.length; k++){
    positive_match = false;

    for(l=0; l<item_list.length; l++){
      if (item_list[l].trim().indexOf(query_match[k].trim()) === 0) { positive_match = true; }
    }
    if (!positive_match) { return false; }
  }

  // If any 'not' queries are present in item list return false
  for(var m=0; m<query_not.length; m++){

    negative_match = [];

    // Compare each 'not' query (outer loop) to each item in list (inner loop)
    // If item in item_list begins with text of the current query, negative match is true
    for(var n=0; n<item_list.length; n++){
      if (item_list[n].trim().indexOf(query_not[m].trim()) === 0) {
        negative_match.push(true);
      } else {
        negative_match.push(false);
      }
    }

    if (negative_match.indexOf(true) !== -1) {
      return false;
    }
  }
  return true;
};

// Search for "||" separated query list for any entry to match listing
function title_match(query, listing){
  // Split query string at '||' and remove empty elements from array, or partial search string
  // (trailing '|' or trailing ' ')
  queries = query.split('||').map(function(x){
    return x.trim().replace(/\|/, '').trim();
  }).filter(function(x){
    return x !== '';
  });

  for(var i=0; i<query.length; i++){
    // TODO: Strip more than just the ':' (such as '-', '.', etc)
    if (listing.replace(':', '').indexOf(queries[i] ? queries[i].replace(':','') : queries[i]) !== -1){
      return true;
    }
  }
  return false;
}

// Restripe the table rows after filtering out rows
function stripe_table() {
  var all_rows      = document.querySelectorAll('.table > tbody > tr');
  var visible_rows  = []
  var even_row      = false;

  for(var n=0; n<all_rows.length; n++){
    if (all_rows[n].style.display !== "none") { visible_rows.push(all_rows[n]) }
  }

  for(var k=0; k<visible_rows.length; k++){

    var visible_cells = visible_rows[k].children;

    if (even_row === false) {
      for (var m=0; m<visible_cells.length; m++) {
        // Preserve existing classes and only modify stripe classes
        var existingClasses = visible_cells[m].className.replace(/\s*stripe-off\s*/g, '').replace(/\s*stripe-on\s*/g, '').trim();
        visible_cells[m].className = existingClasses + " stripe-on";
      }
      even_row = true;

    } else {
      for (var m=0; m<visible_cells.length; m++) {
        // Preserve existing classes and only modify stripe classes
        var existingClasses = visible_cells[m].className.replace(/\s*stripe-off\s*/g, '').replace(/\s*stripe-on\s*/g, '').trim();
        visible_cells[m].className = existingClasses + " stripe-off";
      }
      even_row = false;

    }
  }
};


// Return string with diactirics removed
function remove_diacritics(str) {

  var defaultDiacriticsRemovalMap = [
    {'base':'A', 'letters':/[\u0041\u24B6\uFF21\u00C0\u00C1\u00C2\u1EA6\u1EA4\u1EAA\u1EA8\u00C3\u0100\u0102\u1EB0\u1EAE\u1EB4\u1EB2\u0226\u01E0\u00C4\u01DE\u1EA2\u00C5\u01FA\u01CD\u0200\u0202\u1EA0\u1EAC\u1EB6\u1E00\u0104\u023A\u2C6F]/g},
    {'base':'AA','letters':/[\uA732]/g},
    {'base':'AE','letters':/[\u00C6\u01FC\u01E2]/g},
    {'base':'AO','letters':/[\uA734]/g},
    {'base':'AU','letters':/[\uA736]/g},
    {'base':'AV','letters':/[\uA738\uA73A]/g},
    {'base':'AY','letters':/[\uA73C]/g},
    {'base':'B', 'letters':/[\u0042\u24B7\uFF22\u1E02\u1E04\u1E06\u0243\u0182\u0181]/g},
    {'base':'C', 'letters':/[\u0043\u24B8\uFF23\u0106\u0108\u010A\u010C\u00C7\u1E08\u0187\u023B\uA73E]/g},
    {'base':'D', 'letters':/[\u0044\u24B9\uFF24\u1E0A\u010E\u1E0C\u1E10\u1E12\u1E0E\u0110\u018B\u018A\u0189\uA779]/g},
    {'base':'DZ','letters':/[\u01F1\u01C4]/g},
    {'base':'Dz','letters':/[\u01F2\u01C5]/g},
    {'base':'E', 'letters':/[\u0045\u24BA\uFF25\u00C8\u00C9\u00CA\u1EC0\u1EBE\u1EC4\u1EC2\u1EBC\u0112\u1E14\u1E16\u0114\u0116\u00CB\u1EBA\u011A\u0204\u0206\u1EB8\u1EC6\u0228\u1E1C\u0118\u1E18\u1E1A\u0190\u018E]/g},
    {'base':'F', 'letters':/[\u0046\u24BB\uFF26\u1E1E\u0191\uA77B]/g},
    {'base':'G', 'letters':/[\u0047\u24BC\uFF27\u01F4\u011C\u1E20\u011E\u0120\u01E6\u0122\u01E4\u0193\uA7A0\uA77D\uA77E]/g},
    {'base':'H', 'letters':/[\u0048\u24BD\uFF28\u0124\u1E22\u1E26\u021E\u1E24\u1E28\u1E2A\u0126\u2C67\u2C75\uA78D]/g},
    {'base':'I', 'letters':/[\u0049\u24BE\uFF29\u00CC\u00CD\u00CE\u0128\u012A\u012C\u0130\u00CF\u1E2E\u1EC8\u01CF\u0208\u020A\u1ECA\u012E\u1E2C\u0197]/g},
    {'base':'J', 'letters':/[\u004A\u24BF\uFF2A\u0134\u0248]/g},
    {'base':'K', 'letters':/[\u004B\u24C0\uFF2B\u1E30\u01E8\u1E32\u0136\u1E34\u0198\u2C69\uA740\uA742\uA744\uA7A2]/g},
    {'base':'L', 'letters':/[\u004C\u24C1\uFF2C\u013F\u0139\u013D\u1E36\u1E38\u013B\u1E3C\u1E3A\u0141\u023D\u2C62\u2C60\uA748\uA746\uA780]/g},
    {'base':'LJ','letters':/[\u01C7]/g},
    {'base':'Lj','letters':/[\u01C8]/g},
    {'base':'M', 'letters':/[\u004D\u24C2\uFF2D\u1E3E\u1E40\u1E42\u2C6E\u019C]/g},
    {'base':'N', 'letters':/[\u004E\u24C3\uFF2E\u01F8\u0143\u00D1\u1E44\u0147\u1E46\u0145\u1E4A\u1E48\u0220\u019D\uA790\uA7A4]/g},
    {'base':'NJ','letters':/[\u01CA]/g},
    {'base':'Nj','letters':/[\u01CB]/g},
    {'base':'O', 'letters':/[\u004F\u24C4\uFF2F\u00D2\u00D3\u00D4\u1ED2\u1ED0\u1ED6\u1ED4\u00D5\u1E4C\u022C\u1E4E\u014C\u1E50\u1E52\u014E\u022E\u0230\u00D6\u022A\u1ECE\u0150\u01D1\u020C\u020E\u01A0\u1EDC\u1EDA\u1EE0\u1EDE\u1EE2\u1ECC\u1ED8\u01EA\u01EC\u00D8\u01FE\u0186\u019F\uA74A\uA74C]/g},
    {'base':'OI','letters':/[\u01A2]/g},
    {'base':'OO','letters':/[\uA74E]/g},
    {'base':'OU','letters':/[\u0222]/g},
    {'base':'P', 'letters':/[\u0050\u24C5\uFF30\u1E54\u1E56\u01A4\u2C63\uA750\uA752\uA754]/g},
    {'base':'Q', 'letters':/[\u0051\u24C6\uFF31\uA756\uA758\u024A]/g},
    {'base':'R', 'letters':/[\u0052\u24C7\uFF32\u0154\u1E58\u0158\u0210\u0212\u1E5A\u1E5C\u0156\u1E5E\u024C\u2C64\uA75A\uA7A6\uA782]/g},
    {'base':'S', 'letters':/[\u0053\u24C8\uFF33\u1E9E\u015A\u1E64\u015C\u1E60\u0160\u1E66\u1E62\u1E68\u0218\u015E\u2C7E\uA7A8\uA784]/g},
    {'base':'T', 'letters':/[\u0054\u24C9\uFF34\u1E6A\u0164\u1E6C\u021A\u0162\u1E70\u1E6E\u0166\u01AC\u01AE\u023E\uA786]/g},
    {'base':'TZ','letters':/[\uA728]/g},
    {'base':'U', 'letters':/[\u0055\u24CA\uFF35\u00D9\u00DA\u00DB\u0168\u1E78\u016A\u1E7A\u016C\u00DC\u01DB\u01D7\u01D5\u01D9\u1EE6\u016E\u0170\u01D3\u0214\u0216\u01AF\u1EEA\u1EE8\u1EEE\u1EEC\u1EF0\u1EE4\u1E72\u0172\u1E76\u1E74\u0244]/g},
    {'base':'V', 'letters':/[\u0056\u24CB\uFF36\u1E7C\u1E7E\u01B2\uA75E\u0245]/g},
    {'base':'VY','letters':/[\uA760]/g},
    {'base':'W', 'letters':/[\u0057\u24CC\uFF37\u1E80\u1E82\u0174\u1E86\u1E84\u1E88\u2C72]/g},
    {'base':'X', 'letters':/[\u0058\u24CD\uFF38\u1E8A\u1E8C]/g},
    {'base':'Y', 'letters':/[\u0059\u24CE\uFF39\u1EF2\u00DD\u0176\u1EF8\u0232\u1E8E\u0178\u1EF6\u1EF4\u01B3\u024E\u1EFE]/g},
    {'base':'Z', 'letters':/[\u005A\u24CF\uFF3A\u0179\u1E90\u017B\u017D\u1E92\u1E94\u01B5\u0224\u2C7F\u2C6B\uA762]/g},
    {'base':'a', 'letters':/[\u0061\u24D0\uFF41\u1E9A\u00E0\u00E1\u00E2\u1EA7\u1EA5\u1EAB\u1EA9\u00E3\u0101\u0103\u1EB1\u1EAF\u1EB5\u1EB3\u0227\u01E1\u00E4\u01DF\u1EA3\u00E5\u01FB\u01CE\u0201\u0203\u1EA1\u1EAD\u1EB7\u1E01\u0105\u2C65\u0250]/g},
    {'base':'aa','letters':/[\uA733]/g},
    {'base':'ae','letters':/[\u00E6\u01FD\u01E3]/g},
    {'base':'ao','letters':/[\uA735]/g},
    {'base':'au','letters':/[\uA737]/g},
    {'base':'av','letters':/[\uA739\uA73B]/g},
    {'base':'ay','letters':/[\uA73D]/g},
    {'base':'b', 'letters':/[\u0062\u24D1\uFF42\u1E03\u1E05\u1E07\u0180\u0183\u0253]/g},
    {'base':'c', 'letters':/[\u0063\u24D2\uFF43\u0107\u0109\u010B\u010D\u00E7\u1E09\u0188\u023C\uA73F\u2184]/g},
    {'base':'d', 'letters':/[\u0064\u24D3\uFF44\u1E0B\u010F\u1E0D\u1E11\u1E13\u1E0F\u0111\u018C\u0256\u0257\uA77A]/g},
    {'base':'dz','letters':/[\u01F3\u01C6]/g},
    {'base':'e', 'letters':/[\u0065\u24D4\uFF45\u00E8\u00E9\u00EA\u1EC1\u1EBF\u1EC5\u1EC3\u1EBD\u0113\u1E15\u1E17\u0115\u0117\u00EB\u1EBB\u011B\u0205\u0207\u1EB9\u1EC7\u0229\u1E1D\u0119\u1E19\u1E1B\u0247\u025B\u01DD]/g},
    {'base':'f', 'letters':/[\u0066\u24D5\uFF46\u1E1F\u0192\uA77C]/g},
    {'base':'g', 'letters':/[\u0067\u24D6\uFF47\u01F5\u011D\u1E21\u011F\u0121\u01E7\u0123\u01E5\u0260\uA7A1\u1D79\uA77F]/g},
    {'base':'h', 'letters':/[\u0068\u24D7\uFF48\u0125\u1E23\u1E27\u021F\u1E25\u1E29\u1E2B\u1E96\u0127\u2C68\u2C76\u0265]/g},
    {'base':'hv','letters':/[\u0195]/g},
    {'base':'i', 'letters':/[\u0069\u24D8\uFF49\u00EC\u00ED\u00EE\u0129\u012B\u012D\u00EF\u1E2F\u1EC9\u01D0\u0209\u020B\u1ECB\u012F\u1E2D\u0268\u0131]/g},
    {'base':'j', 'letters':/[\u006A\u24D9\uFF4A\u0135\u01F0\u0249]/g},
    {'base':'k', 'letters':/[\u006B\u24DA\uFF4B\u1E31\u01E9\u1E33\u0137\u1E35\u0199\u2C6A\uA741\uA743\uA745\uA7A3]/g},
    {'base':'l', 'letters':/[\u006C\u24DB\uFF4C\u0140\u013A\u013E\u1E37\u1E39\u013C\u1E3D\u1E3B\u017F\u0142\u019A\u026B\u2C61\uA749\uA781\uA747]/g},
    {'base':'lj','letters':/[\u01C9]/g},
    {'base':'m', 'letters':/[\u006D\u24DC\uFF4D\u1E3F\u1E41\u1E43\u0271\u026F]/g},
    {'base':'n', 'letters':/[\u006E\u24DD\uFF4E\u01F9\u0144\u00F1\u1E45\u0148\u1E47\u0146\u1E4B\u1E49\u019E\u0272\u0149\uA791\uA7A5]/g},
    {'base':'nj','letters':/[\u01CC]/g},
    {'base':'o', 'letters':/[\u006F\u24DE\uFF4F\u00F2\u00F3\u00F4\u1ED3\u1ED1\u1ED7\u1ED5\u00F5\u1E4D\u022D\u1E4F\u014D\u1E51\u1E53\u014F\u022F\u0231\u00F6\u022B\u1ECF\u0151\u01D2\u020D\u020F\u01A1\u1EDD\u1EDB\u1EE1\u1EDF\u1EE3\u1ECD\u1ED9\u01EB\u01ED\u00F8\u01FF\u0254\uA74B\uA74D\u0275]/g},
    {'base':'oi','letters':/[\u01A3]/g},
    {'base':'ou','letters':/[\u0223]/g},
    {'base':'oo','letters':/[\uA74F]/g},
    {'base':'p','letters':/[\u0070\u24DF\uFF50\u1E55\u1E57\u01A5\u1D7D\uA751\uA753\uA755]/g},
    {'base':'q','letters':/[\u0071\u24E0\uFF51\u024B\uA757\uA759]/g},
    {'base':'r','letters':/[\u0072\u24E1\uFF52\u0155\u1E59\u0159\u0211\u0213\u1E5B\u1E5D\u0157\u1E5F\u024D\u027D\uA75B\uA7A7\uA783]/g},
    {'base':'s','letters':/[\u0073\u24E2\uFF53\u00DF\u015B\u1E65\u015D\u1E61\u0161\u1E67\u1E63\u1E69\u0219\u015F\u023F\uA7A9\uA785\u1E9B]/g},
    {'base':'t','letters':/[\u0074\u24E3\uFF54\u1E6B\u1E97\u0165\u1E6D\u021B\u0163\u1E71\u1E6F\u0167\u01AD\u0288\u2C66\uA787]/g},
    {'base':'tz','letters':/[\uA729]/g},
    {'base':'u','letters':/[\u0075\u24E4\uFF55\u00F9\u00FA\u00FB\u0169\u1E79\u016B\u1E7B\u016D\u00FC\u01DC\u01D8\u01D6\u01DA\u1EE7\u016F\u0171\u01D4\u0215\u0217\u01B0\u1EEB\u1EE9\u1EEF\u1EED\u1EF1\u1EE5\u1E73\u0173\u1E77\u1E75\u0289]/g},
    {'base':'v','letters':/[\u0076\u24E5\uFF56\u1E7D\u1E7F\u028B\uA75F\u028C]/g},
    {'base':'vy','letters':/[\uA761]/g},
    {'base':'w','letters':/[\u0077\u24E6\uFF57\u1E81\u1E83\u0175\u1E87\u1E85\u1E98\u1E89\u2C73]/g},
    {'base':'x','letters':/[\u0078\u24E7\uFF58\u1E8B\u1E8D]/g},
    {'base':'y','letters':/[\u0079\u24E8\uFF59\u1EF3\u00FD\u0177\u1EF9\u0233\u1E8F\u00FF\u1EF7\u1E99\u1EF5\u01B4\u024F\u1EFF]/g},
    {'base':'z','letters':/[\u007A\u24E9\uFF5A\u017A\u1E91\u017C\u017E\u1E93\u1E95\u01B6\u0225\u0240\u2C6C\uA763]/g},
    {'base':'1/2','letters':/[\xBD]/g},
    {'base':'1/4','letters':/[\xBC]/g},
    {'base':'1/3','letters':/[\xBE]/g},
    {'base':'2','letters':/[\xB2]/g},
    {'base':'3','letters':/[\xB3]/g},
    {'base':'"','letters':/[\xAB\xBB]/g}
  ];

  for(var i=0; i<defaultDiacriticsRemovalMap.length; i++) {
    str = str.replace(defaultDiacriticsRemovalMap[i].letters, defaultDiacriticsRemovalMap[i].base);
  }
  return str;
};

function get_visible_modal_links() {
  var visible_links = [];
  var rows = document.querySelectorAll('.table > tbody > tr');

  for (var i = 0; i < rows.length; i++) {
    if (rows[i].style.display === 'none') {
      continue;
    }

    var row_link = rows[i].querySelector('a[href*=".html"]');
    if (row_link) {
      visible_links.push(row_link);
    }
  }

  return visible_links;
}

function build_modal_details_url(link_element) {
  var movie_details = link_element.href.substring(link_element.href.indexOf('#') + 1);
  var visible_links = get_visible_modal_links();
  var current_index = -1;
  var target_href = link_element.href;

  for (var i = 0; i < visible_links.length; i++) {
    if (visible_links[i].href === target_href) {
      current_index = i;
      break;
    }
  }

  try {
    var details_url = new URL(movie_details, window.location.href);

    if (current_index !== -1) {
      details_url.searchParams.set('position', String(current_index + 1));
      details_url.searchParams.set('total', String(visible_links.length));
    }

    return details_url.pathname + details_url.search + details_url.hash;
  } catch (err) {
    return movie_details;
  }
}


// Load iFrame with specific title
function load_details(movie, preserveCurrentElement) {
  var movie_details = build_modal_details_url(movie);

  // Save current scroll position and current element for navigation
  window.scrollPositionBeforeModal = window.pageYOffset || document.documentElement.scrollTop;
  console.log('load_details called with preserveCurrentElement:', preserveCurrentElement);
  if (!preserveCurrentElement) {
    console.log('Setting currentModalElement to new movie');
    window.currentModalElement = movie;
    window.currentModalUrl = movie.href; // Store URL for navigation
  } else {
    console.log('Preserving currentModalElement');
    // During navigation, we still need to update the URL for next navigation
    window.currentModalUrl = movie.href;
  }

  // Prevent body scroll
  document.body.classList.add('modal-open');
  document.body.style.top = `-${window.scrollPositionBeforeModal}px`;

  console.log('About to show modal - backdrop display:', document.getElementById('backdrop').style.display, 'modal display:', document.getElementById('modal-alert').style.display);
  document.getElementById('backdrop').style.display     = '';
  document.getElementById('modal-alert').style.display  = '';
  console.log('Modal shown - backdrop display:', document.getElementById('backdrop').style.display, 'modal display:', document.getElementById('modal-alert').style.display);

  // Create navigation buttons and close button
  var prevBtn = '<div id="modal-prev-btn" onclick="navigate_modal(\'prev\')" title="Previous (←)">‹</div>';
  var nextBtn = '<div id="modal-next-btn" onclick="navigate_modal(\'next\')" title="Next (→)">›</div>';
  var closeBtn = '<div id="modal-close-btn" onclick="close_details()" title="Close (Esc)">×</div>';
  var navButtons = prevBtn + nextBtn + closeBtn;

  var iframe = "<iframe id='frame' style='z-index: 12; max-width:1000px; height:100%; width:100%; border:none; border-radius:16px; background-color:#fff;' frameborder='0' scrolling='yes' src='" + movie_details + "'></iframe>";
  document.getElementById('modal-alert').innerHTML = navButtons + iframe;

  // Close modal when clicking backdrop (but not during navigation)
  document.getElementById('backdrop').onclick = function() {
    if (!window.isNavigating) {
      close_details();
    }
  };

  // Close modal with Escape key and navigation with arrow keys
  document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.keyCode == 27) {
      close_details();
    } else if (evt.keyCode == 37) {
      navigate_modal('prev');
    } else if (evt.keyCode == 39) {
      navigate_modal('next');
    }
  };

  /* iFrame won't scroll on Desktop Safari unless this state is toggled */
  var ua = navigator.userAgent.toLowerCase();
  if (ua.indexOf('safari') != -1) {
    if (ua.indexOf('chrome') > -1) {
      // Chrome
    } else {
      // Safari
      if (!( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))) {
        // Desktop Safari
        document.getElementById('frame').scrolling = 'no';
        setTimeout(function() { document.getElementById('frame').scrolling = 'yes'; }, 1);
      }
    }
  }

  // Update navigation button visibility after a short delay
  setTimeout(update_navigation_buttons, 100);

  return false;
}

// Navigate to next/previous item in modal
function navigate_modal(direction) {
if (!window.currentModalUrl) {
return;
}

var visibleLinks = get_visible_modal_links();

if (visibleLinks.length === 0) return;

// Find current index by URL
var currentIndex = -1;
for (var j = 0; j < visibleLinks.length; j++) {
var linkUrl = visibleLinks[j].href;
if (window.currentModalUrl.includes(linkUrl.split('#')[1])) {
currentIndex = j;
break;
}
}

if (currentIndex === -1) return;

// Calculate next index (no wrap-around)
var nextIndex;
if (direction === 'next') {
nextIndex = currentIndex + 1;
if (nextIndex >= visibleLinks.length) return; // No next item
} else {
nextIndex = currentIndex - 1;
if (nextIndex < 0) return; // No previous item
}

// Load next item
var nextElement = visibleLinks[nextIndex];
window.currentModalElement = nextElement; // Update for consistency
window.currentModalUrl = nextElement.href; // Store URL for next navigation
window.isNavigating = true; // Set navigation flag to block close calls
load_details(nextElement, false); // Don't preserve current element during navigation

// Reset navigation flag after a short delay
  setTimeout(function() {
    window.isNavigating = false;
  }, 1000);
}

// Update navigation button visibility
function update_navigation_buttons() {
  if (!window.currentModalUrl) return;

  var visibleLinks = get_visible_modal_links();

  if (visibleLinks.length === 0) return;

  // Find current index by URL
  var currentIndex = -1;
  for (var j = 0; j < visibleLinks.length; j++) {
    var linkUrl = visibleLinks[j].href;
    if (window.currentModalUrl.includes(linkUrl.split('#')[1])) {
      currentIndex = j;
      break;
    }
  }

  if (currentIndex === -1) return;

  // Show/hide buttons based on availability
  var prevBtn = document.getElementById('modal-prev-btn');
  var nextBtn = document.getElementById('modal-next-btn');

  if (prevBtn) {
    prevBtn.style.display = currentIndex > 0 ? 'flex' : 'none';
  }
  if (nextBtn) {
    nextBtn.style.display = currentIndex < visibleLinks.length - 1 ? 'flex' : 'none';
  }
}

// Close modal function
function close_details_internal() {
  console.log('CLOSE_DETAILS_INTERNAL CALLED');
  document.getElementById('backdrop').style.display = 'none';
  document.getElementById('modal-alert').style.display = 'none';
  document.getElementById('modal-alert').innerHTML = '';
  document.getElementById('backdrop').onclick = null;
  document.onkeydown = null;
  window.currentModalElement = null;

  // Re-enable body scroll and restore position
  document.body.classList.remove('modal-open');
  document.body.style.top = '';

  // Restore scroll position
  if (window.scrollPositionBeforeModal !== undefined) {
    window.scrollTo(0, window.scrollPositionBeforeModal);
    window.scrollPositionBeforeModal = undefined;
  }
}

// Public close function that can be called by our buttons
function close_details() {
  // Block close calls only during navigation (when iframe is loading)
  if (window.isNavigating) {
    return;
  }

  close_details_internal();
}

// Toggle Display of Search Filters
function filter_toggle() {
  var filters   = document.getElementById('filters');
  var btn       = document.getElementById('filter_toggle_btn');
  var icon      = btn.querySelector('.media-action-btn-icon');
  var label     = btn.querySelector('.media-action-btn-label');

  if (filters.style.maxHeight && filters.style.maxHeight !== '5000px') {
    // Show filters - roll down to full
    filters.style.maxHeight = '5000px';
    icon.textContent = '▲';
    label.textContent = 'Hide Search Filters';
  } else {
    // Partial collapse - show only toolbar + first filter row
    filters.style.maxHeight = '120px';
    icon.textContent = '▼';
    label.textContent = 'Show Search Filters';
    window.scroll(0, 0);
  }
};

function clear_all_filters() {
  var filter_inputs = get_filter_fields();

  forEach(filter_inputs, function(input) {
    clear_filter_field(input.id);
  });

  trigger_page_search();
  update_clear_all_filters_button();
  update_random_selection_button();
};

function toggle_column_visibility(column_name) {
  var column_cells  = document.getElementsByName(column_name);
  var next_state    = "";
  column_cells[0].style.display === "none" ? next_state = "" : next_state = "none";

  forEach(column_cells, function(cell) {
    cell.style.display = next_state;
  });
};

// Choose Random Item from List
function random_selection() {
  // Get all visible rows in one pass
  var all_rows = document.querySelectorAll('.table > tbody > tr');
  var visible_rows = [];

  for(var i = 0; i < all_rows.length; i++){
    if (all_rows[i].style.display !== "none"){
      visible_rows.push(all_rows[i]);
    }
  }

  /* Select a random item only if there are some currently displayed */
  if (visible_rows.length > 0) {
    var random_index = Math.floor(Math.random() * visible_rows.length);
    var table_row = visible_rows[random_index];
    var table_row_name = table_row.querySelectorAll('td')[3];
    var table_row_name_link = table_row_name.querySelectorAll('a')[0];
    table_row_name_link.click();
  }
};

function update_random_selection_button() {
  var random_btn = document.getElementById('random_selection_btn');
  if (!random_btn) {
    return;
  }

  // Get all visible rows
  var all_rows = document.querySelectorAll('.table > tbody > tr');
  var visible_rows = [];

  for(var i = 0; i < all_rows.length; i++){
    if (all_rows[i].style.display !== "none"){
      visible_rows.push(all_rows[i]);
    }
  }

  // Enable/disable based on visible results count
  if (visible_rows.length === 0) {
    random_btn.classList.add('is-disabled');
    random_btn.disabled = true;
  } else {
    random_btn.classList.remove('is-disabled');
    random_btn.disabled = false;
  }
}

/* Clear cell in filters */
function clear_filter(element_id){
  clear_filter_field(element_id);
  trigger_page_search();
  update_clear_all_filters_button();
  update_random_selection_button();
};

function toggleView(view) {
  const table_view = document.getElementById('table-view');
  const tile_view = document.getElementById('tile-view');

  try {
    table_view.style.display = (view === 'table') ? '' : 'none';
    tile_view.style.display = (view === 'tile') ? '' : 'none';
  } catch(err) {
return;
  }

  // Update button styles
  document.getElementById('table-view-btn').classList.toggle('btn-primary', view === 'table');
  document.getElementById('table-view-btn').classList.toggle('btn-secondary', view !== 'table');
  document.getElementById('tile-view-btn').classList.toggle('btn-primary', view === 'tile');
  document.getElementById('tile-view-btn').classList.toggle('btn-secondary', view !== 'tile');

  this.search_movie_table('results');
}

// Dark Mode
function toggleDarkMode() {
  // Toggle on body first to get the new state
  const isDarkMode = document.body.classList.toggle('dark-theme');
  // Apply same state to html element
  document.documentElement.classList.toggle('dark-theme', isDarkMode);
  // Save to localStorage
  localStorage.setItem('darkMode', isDarkMode.toString());
  console.log('[Dark Mode] Toggled to:', isDarkMode, 'Saved to localStorage:', localStorage.getItem('darkMode'));
  // Update checkbox
  updateDarkModeToggle(isDarkMode);
  // Update all navigation links to include dark mode parameter
  updateNavigationLinks(isDarkMode);
}

function updateNavigationLinks(isDarkMode) {
  // Update all internal navigation links to include the dark mode state
  // Match links ending in .html OR containing .html? (with query params)
  const links = document.querySelectorAll('a[href*=".html"]');
  links.forEach(link => {
    try {
      const url = new URL(link.href);
      // Skip movie detail links (they're loaded in iframes and shouldn't have dark mode)
      if (url.pathname.includes('movie_details') || url.pathname.includes('series_details') || url.pathname.includes('standup_details')) {
        return;
      }
      // Only update if it's a local HTML file
      if (url.pathname.endsWith('.html')) {
        if (isDarkMode) {
          url.searchParams.set('dark', '1');
        } else {
          url.searchParams.delete('dark');
        }
        link.href = url.toString();
      }
    } catch (e) {
      // Skip invalid URLs
      console.warn('[Dark Mode] Could not update link:', link.href, e);
    }
  });
  console.log('[Dark Mode] Updated', links.length, 'navigation links. Dark mode:', isDarkMode);
}

function updateDarkModeToggle(isDarkMode) {
  const toggle = document.getElementById('darkModeToggle');
  if (toggle) {
    toggle.checked = isDarkMode;
    console.log('[Dark Mode] Checkbox updated to:', isDarkMode);
  }
}

function applyDarkMode() {
  // Check URL parameter first (for static file:// protocol)
  const urlParams = new URLSearchParams(window.location.search);
  const urlDarkMode = urlParams.get('dark');

  let isDarkMode;
  if (urlDarkMode !== null) {
    // URL parameter takes precedence
    isDarkMode = urlDarkMode === '1';
    // Save to localStorage for this page
    localStorage.setItem('darkMode', isDarkMode.toString());
    console.log('[Dark Mode] URL parameter found:', urlDarkMode, 'Setting dark mode to:', isDarkMode);
  } else {
    // Fall back to localStorage
    const storedValue = localStorage.getItem('darkMode');
    isDarkMode = storedValue === 'true';
    console.log('[Dark Mode] No URL parameter. localStorage value:', storedValue, 'Parsed as:', isDarkMode);
  }

  console.log('[Dark Mode] HTML has dark-theme:', document.documentElement.classList.contains('dark-theme'));
  console.log('[Dark Mode] Body has dark-theme:', document.body.classList.contains('dark-theme'));

  // Early script already applied theme to html and body
  // We just need to sync the checkbox state
  updateDarkModeToggle(isDarkMode);

  // IMPORTANT: Update all navigation links on this page to reflect current state
  // This ensures links are correct even if we navigated from a page with different state
  setTimeout(function() {
    updateNavigationLinks(isDarkMode);
    console.log('[Dark Mode] Navigation links updated to:', isDarkMode ? 'include ?dark=1' : 'remove ?dark=1');
  }, 0);
}

// Call this function when the document is ready to sync checkbox
document.addEventListener('DOMContentLoaded', applyDarkMode);
document.addEventListener('DOMContentLoaded', update_clear_all_filters_button);
document.addEventListener('DOMContentLoaded', initialize_enhanced_filter_selects);
document.addEventListener('DOMContentLoaded', initialize_numeric_filter_inputs);
document.addEventListener('DOMContentLoaded', setup_search_clear_buttons);
document.addEventListener('DOMContentLoaded', update_random_selection_button);
document.addEventListener('DOMContentLoaded', function() {
  var filters = document.getElementById('filters');
  if (!filters) {
    return;
  }

  filters.addEventListener('input', update_clear_all_filters_button);
  filters.addEventListener('change', update_clear_all_filters_button);
  filters.addEventListener('input', update_random_selection_button);
  filters.addEventListener('change', update_random_selection_button);
});


/* Called on Document Load */
// Stylized Tooltips
if (typeof $ !== 'undefined') {
  $(document).ready(function(){
    // Bootstrap doesn't allow html in tooltips without this setting
    $('[data-toggle="tooltip"]').tooltip({
      html: true
    });

    $("a.tooltip-info").tooltip();
  });
}
