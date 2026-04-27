// === THEME ===
const root = document.documentElement;
const themeToggle = document.querySelector('[data-theme-toggle]');

themeToggle?.addEventListener('click', () => {
  const newTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  root.dataset.theme = newTheme;

  setThemeCookie(newTheme);
});

function setThemeCookie(theme) {
  document.cookie = `theme=${theme}; path=/; max-age=31536000`; // 1 год
}


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


// === DROPDOWN MENU ===
const avatarTrigger = document.getElementById('avatarTrigger');
const dropdownMenu = document.getElementById('dropdownMenu');
const avatarDropdown = document.getElementById('avatarDropdown');

avatarTrigger.addEventListener('click', (e) => {
e.stopPropagation();
dropdownMenu.classList.toggle('active');
});

document.addEventListener('click', (e) => {
if (!avatarDropdown.contains(e.target)) {
  dropdownMenu.classList.remove('active');
}
});

document.addEventListener('keydown', (e) => {
if (e.key === 'Escape') {
  dropdownMenu.classList.remove('active');
}
});


// === MODAL ===
const deleteProjectModal = document.getElementById('deleteProjectModal');
const openDeleteModal = document.getElementById('openDeleteModal');
const closeModalBtn = document.getElementById('closeModal');
const cancelDelete = document.getElementById('cancelDelete');
const modalOverlay = document.getElementById('modalOverlay');
const confirmDelete = document.getElementById('confirmDelete');

let timer = null;
let seconds = 5;

function openModal() {
  deleteProjectModal.classList.add('is-open');
  deleteProjectModal.setAttribute('aria-hidden', 'false');
  document.body.classList.add('modal-open');

  confirmDelete.disabled = true;
  seconds = 5;
  confirmDelete.textContent = `Удалить (${seconds})`;

  timer = setInterval(() => {
    seconds--;
    if (seconds > 0) {
      confirmDelete.textContent = `Удалить (${seconds})`;
    } else {
      clearInterval(timer);
      confirmDelete.disabled = false;
      confirmDelete.textContent = 'Удалить';
    }
  }, 1000);
}

function closeModal() {
  deleteProjectModal.classList.remove('is-open');
  deleteProjectModal.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('modal-open');

  clearInterval(timer);
}

openDeleteModal.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);
cancelDelete.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', closeModal);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeModal();
  }
});