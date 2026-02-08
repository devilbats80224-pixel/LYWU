(function initMobileDatalistDropdown() {
  const MOBILE_QUERY = '(max-width: 900px)';
  const WRAP_CLASS = 'mobile-datalist-wrap';
  const INPUT_CLASS = 'mobile-datalist-input';
  const BUTTON_CLASS = 'mobile-datalist-arrow';
  const MENU_CLASS = 'mobile-datalist-menu';
  const ITEM_CLASS = 'mobile-datalist-item';
  const EMPTY_CLASS = 'mobile-datalist-empty';

  const states = new WeakMap();
  let openedState = null;
  let queued = false;

  function isMobile() {
    return window.matchMedia(MOBILE_QUERY).matches;
  }

  function collectDatalistValues(input) {
    const listId = input.getAttribute('list');
    if (!listId) return [];
    const datalist = document.getElementById(listId);
    if (!datalist) return [];

    const seen = new Set();
    const values = [];
    datalist.querySelectorAll('option').forEach((option) => {
      const value = (option.value || option.textContent || '').trim();
      if (!value) return;
      const key = value.toLocaleLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      values.push(value);
    });

    return values;
  }

  function filteredValues(input) {
    const query = (input.value || '').trim().toLocaleLowerCase();
    const values = collectDatalistValues(input);
    if (!query) return values;
    return values.filter((value) => value.toLocaleLowerCase().includes(query));
  }

  function dispatchInputEvents(input) {
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function closeMenu(state) {
    if (!state || state.menu.hidden) return;
    state.menu.hidden = true;
    state.wrap.classList.remove('is-open');
    state.button.setAttribute('aria-expanded', 'false');
    if (openedState === state) openedState = null;
  }

  function closeOpenedMenu() {
    if (openedState) closeMenu(openedState);
  }

  function renderMenu(state) {
    const values = filteredValues(state.input);
    state.menu.innerHTML = '';

    if (!values.length) {
      const empty = document.createElement('div');
      empty.className = EMPTY_CLASS;
      empty.textContent = '沒有可選項目';
      state.menu.appendChild(empty);
      return;
    }

    const fragment = document.createDocumentFragment();
    values.forEach((value) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = ITEM_CLASS;
      btn.textContent = value;
      btn.dataset.value = value;
      fragment.appendChild(btn);
    });
    state.menu.appendChild(fragment);
  }

  function openMenu(state) {
    if (!isMobile()) return;
    if (openedState && openedState !== state) closeMenu(openedState);

    renderMenu(state);
    state.menu.hidden = false;
    state.wrap.classList.add('is-open');
    state.button.setAttribute('aria-expanded', 'true');
    openedState = state;
  }

  function toggleMenu(state) {
    if (state.menu.hidden) {
      openMenu(state);
      state.input.focus();
      return;
    }
    closeMenu(state);
  }

  function onMenuClick(state, event) {
    const item = event.target instanceof HTMLElement
      ? event.target.closest('.' + ITEM_CLASS)
      : null;
    if (!item) return;

    const value = item.dataset.value || item.textContent || '';
    state.input.value = value;
    dispatchInputEvents(state.input);
    closeMenu(state);
    state.input.focus();
  }

  function createState(input) {
    if (states.has(input)) return states.get(input);
    if (input.closest('.' + WRAP_CLASS)) return null;

    const parent = input.parentElement;
    if (!parent) return null;

    const wrap = document.createElement('div');
    wrap.className = WRAP_CLASS;
    parent.insertBefore(wrap, input);
    wrap.appendChild(input);

    input.classList.add(INPUT_CLASS);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = BUTTON_CLASS;
    button.setAttribute('aria-label', '展開選單');
    button.setAttribute('aria-expanded', 'false');
    button.textContent = '▾';
    wrap.appendChild(button);

    const menu = document.createElement('div');
    menu.className = MENU_CLASS;
    menu.hidden = true;
    wrap.appendChild(menu);

    const state = { input, wrap, button, menu };
    states.set(input, state);

    button.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      toggleMenu(state);
    });

    input.addEventListener('input', () => {
      if (!menu.hidden) renderMenu(state);
    });

    input.addEventListener('keydown', (event) => {
      if (!isMobile()) return;
      if (event.key === 'Escape') {
        closeMenu(state);
      } else if (event.key === 'ArrowDown' && menu.hidden) {
        event.preventDefault();
        openMenu(state);
      }
    });

    input.addEventListener('focus', () => {
      if (!menu.hidden) renderMenu(state);
    });

    menu.addEventListener('mousedown', (event) => {
      event.preventDefault();
    });

    menu.addEventListener('click', (event) => {
      onMenuClick(state, event);
    });

    return state;
  }

  function enhanceAll(root) {
    if (!isMobile()) return;
    const scope = root && root.querySelectorAll ? root : document;
    scope.querySelectorAll('input[list]').forEach((input) => {
      createState(input);
    });
  }

  function queueEnhance(root) {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      enhanceAll(root || document);
    });
  }

  function initObserver() {
    if (!document.body) return;

    const observer = new MutationObserver((mutations) => {
      let hasAddedNodes = false;
      for (const mutation of mutations) {
        if (mutation.type !== 'childList') continue;
        if (mutation.addedNodes.length > 0) hasAddedNodes = true;
        if (openedState && !document.body.contains(openedState.input)) {
          openedState = null;
        }
      }
      if (hasAddedNodes) queueEnhance(document);
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  function init() {
    enhanceAll(document);
    initObserver();
  }

  document.addEventListener('click', (event) => {
    if (!openedState) return;
    if (openedState.wrap.contains(event.target)) return;
    closeMenu(openedState);
  });

  window.addEventListener('resize', () => {
    if (!isMobile()) {
      closeOpenedMenu();
      return;
    }
    queueEnhance(document);
  });

  window.addEventListener('orientationchange', () => {
    if (!isMobile()) {
      closeOpenedMenu();
      return;
    }
    queueEnhance(document);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
