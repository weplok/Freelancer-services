const form = document.getElementById('upload-form');
const dropZone = document.getElementById('drop-zone');
const dropZoneIcon = document.getElementById('drop-zone-icon');
const dropZoneTitle = document.getElementById('drop-zone-title');
const dropZoneHint = document.getElementById('drop-zone-hint');
const fileInput = document.getElementById('file-input');

const filePreview = document.getElementById('file-preview');
const fileNameEl = document.getElementById('file-name');
const fileExtEl = document.getElementById('file-ext');
const fileSizeEl = document.getElementById('file-size');

const uploadBlock = document.getElementById('upload-block');
const uploadPercent = document.getElementById('upload-percent');
const uploadIndicator = document.getElementById('upload-indicator');

const messageEl = document.getElementById('form-message');
const resetBtn = document.getElementById('reset-btn');

let selectedFile = null;

const icons = {
  default: `
    <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z"></path>
      <path d="M14 2v5h5"></path>
    </svg>
  `,
  active: `
    <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z"></path>
      <path d="M14 2v5h5"></path>
      <path d="M12 12v6"></path>
      <path d="m9 15 3 3 3-3"></path>
    </svg>
  `,
  selected: `
    <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z"></path>
      <path d="M14 2v5h5"></path>
      <path d="m9 13 2 2 4-4"></path>
    </svg>
  `
};

function setIcon(type) {
  dropZoneIcon.innerHTML = icons[type] || icons.default;
}

function humanFileSize(bytes) {
  if (!bytes && bytes !== 0) return '—';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(size < 10 && unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
}

function getExtension(filename) {
  const parts = filename.split('.');
  if (parts.length < 2) return 'без расширения';
  return parts.pop().toLowerCase();
}

function showMessage(text, isError = false) {
  messageEl.textContent = text;
  messageEl.style.color = isError ? 'crimson' : 'inherit';
}

function setSelectedFile(file) {
  selectedFile = file;

  if (!file) {
    filePreview.hidden = true;
    dropZone.classList.remove('drop-zone--filled');
    dropZoneTitle.textContent = 'Перетащи файл сюда или кликни';
    dropZoneHint.textContent = 'После drop появятся название, размер и расширение.';
    setIcon('default');
    return;
  }

  filePreview.hidden = false;
  dropZone.classList.add('drop-zone--filled');

  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = humanFileSize(file.size);
  fileExtEl.textContent = getExtension(file.name);

  dropZoneTitle.textContent = 'Файл выбран';
  dropZoneHint.textContent = 'Теперь можно отправлять форму.';
  setIcon('selected');
}

function activateDropZone() {
  dropZone.classList.add('drop-zone--active');
  setIcon('active');
}

function deactivateDropZone() {
  dropZone.classList.remove('drop-zone--active');
  if (selectedFile) {
    setIcon('selected');
  } else {
    setIcon('default');
  }
}

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileInput.click();
  }
});

dropZone.addEventListener('dragenter', (e) => {
  e.preventDefault();
  activateDropZone();
});

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  activateDropZone();
});

dropZone.addEventListener('dragleave', (e) => {
  e.preventDefault();
  const rect = dropZone.getBoundingClientRect();
  const inside =
    e.clientX >= rect.left &&
    e.clientX <= rect.right &&
    e.clientY >= rect.top &&
    e.clientY <= rect.bottom;

  if (!inside) deactivateDropZone();
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  deactivateDropZone();

  const files = e.dataTransfer.files;
  if (!files || files.length === 0) return;

  fileInput.files = files;
  setSelectedFile(files[0]);
  showMessage('Файл готов к отправке.', false);
});

fileInput.addEventListener('change', () => {
  const file = fileInput.files && fileInput.files[0];
  if (!file) {
    setSelectedFile(null);
    return;
  }

  setSelectedFile(file);
  showMessage('Файл готов к отправке.', false);
});

resetBtn.addEventListener('click', () => {
  form.reset();
  selectedFile = null;
  uploadBlock.hidden = true;
  uploadPercent.textContent = '0%';
  uploadIndicator.style.transform = 'translateX(-100%)';
  setSelectedFile(null);
  showMessage('Форма очищена.', false);
});

function getCSRFToken() {
  const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
  if (cookieMatch) return cookieMatch[1];

  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  return input ? input.value : '';
}

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const file = fileInput.files && fileInput.files[0];
  if (!file) {
    showMessage('Сначала выбери файл.', true);
    return;
  }

  const formData = new FormData(form);

  uploadBlock.hidden = false;
  uploadPercent.textContent = '0%';
  uploadIndicator.style.transform = 'translateX(-100%)';
  showMessage('Начинаю загрузку...', false);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', form.action || window.location.href, true);
  xhr.setRequestHeader('X-CSRFToken', getCSRFToken());

  xhr.upload.onprogress = (event) => {
    if (!event.lengthComputable) return;

    const percent = Math.round((event.loaded / event.total) * 50);
    uploadPercent.textContent = `${percent}%`;
    uploadIndicator.style.transform = `translateX(-${100 - percent}%)`;
  };

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      showMessage('Файл успешно загружен.', false);
      uploadPercent.textContent = '100%';
      uploadIndicator.style.transform = 'translateX(0%)';

      let response = {};
      try {
        response = JSON.parse(xhr.responseText);
      } catch (err) {}

      console.log('Server response:', response);
    } else {
      showMessage('Ошибка загрузки файла.', true);
    }
  };

  xhr.onerror = () => {
    showMessage('Сетевая ошибка при загрузке.', true);
  };

  xhr.send(formData);
});