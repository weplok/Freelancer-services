// === THEME ===
const root = document.documentElement;
const themeToggle = document.querySelector('[data-theme-toggle]');

themeToggle?.addEventListener('click', () => {
  root.dataset.theme =
    root.dataset.theme === 'dark' ? 'light' : 'dark';
});


// === MOBILE MENU ===
const mobileMenu = document.getElementById('mobileMenu');
const menuToggle = document.querySelector('[data-menu-toggle]');

menuToggle?.addEventListener('click', () => {
  const open = mobileMenu.classList.toggle('mobile-menu--open');
  menuToggle.setAttribute('aria-expanded', String(open));
});


// === SWITCHES ===
document.querySelectorAll('[data-switch]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const checked = btn.dataset.state === 'checked';

    btn.dataset.state = checked ? 'unchecked' : 'checked';
    btn.setAttribute('aria-pressed', String(!checked));
  });
});


// === TABS ===
document.querySelectorAll('[data-tabs]').forEach((tabs) => {
  const triggers = tabs.querySelectorAll('[data-tab]');
  const panels = tabs.querySelectorAll('[data-tab-panel]');

  triggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const target = trigger.dataset.tab;

      triggers.forEach((t) => {
        t.dataset.state = t === trigger ? 'active' : '';
      });

      panels.forEach((panel) => {
        panel.hidden = panel.dataset.tabPanel !== target;
      });
    });
  });
});


// === ACCORDION ===
const accordionTrigger = document.querySelector('[data-accordion-trigger]');

accordionTrigger?.addEventListener('click', (e) => {
  const btn = e.currentTarget;
  const content = document.querySelector('[data-accordion-content]');
  const isOpen = btn.getAttribute('aria-expanded') === 'true';

  btn.setAttribute('aria-expanded', String(!isOpen));

  if (content) {
    content.hidden = isOpen;
  }
});


// === COLLAPSIBLE ===
const collapsibleTrigger = document.querySelector('[data-collapsible-trigger]');

collapsibleTrigger?.addEventListener('click', (e) => {
  const btn = e.currentTarget;
  const content = document.querySelector('[data-collapsible-content]');
  const isOpen = btn.getAttribute('aria-expanded') === 'true';

  btn.setAttribute('aria-expanded', String(!isOpen));

  if (content) {
    content.hidden = isOpen;
  }
});


const avatarTrigger = document.getElementById('avatarTrigger');
const dropdownMenu = document.getElementById('dropdownMenu');
const avatarDropdown = document.getElementById('avatarDropdown');

// toggle по клику
avatarTrigger.addEventListener('click', (e) => {
e.stopPropagation();
dropdownMenu.classList.toggle('active');
});

// клик вне — закрыть
document.addEventListener('click', (e) => {
if (!avatarDropdown.contains(e.target)) {
  dropdownMenu.classList.remove('active');
}
});

// опционально: закрытие по ESC
document.addEventListener('keydown', (e) => {
if (e.key === 'Escape') {
  dropdownMenu.classList.remove('active');
}
});
