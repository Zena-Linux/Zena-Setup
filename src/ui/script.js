const welcomeScreen = document.getElementById('welcome-screen');
const step1 = document.getElementById('setup-screen-step1');
const step2 = document.getElementById('setup-screen-step2');
const step3 = document.getElementById('setup-screen-step3');

const setupBtn = document.getElementById('setup-btn');
const backFromStep1 = document.getElementById('back-from-step1');
const nextToStep2 = document.getElementById('next-to-step2');
const backFromStep2 = document.getElementById('back-from-step2');
const nextToStep3 = document.getElementById('next-to-step3');
const backFromStep3 = document.getElementById('back-from-step3');

const keymapContainer = document.getElementById('keymap-container');
const localeContainer = document.getElementById('locale-container');
const timezoneContainer = document.getElementById('timezone-container');

const keymapSearch = document.getElementById('keymap-search');
const localeSearch = document.getElementById('locale-search');
const timezoneSearch = document.getElementById('timezone-search');

const homeSizeSlider = document.getElementById('home-size-slider');
const homeSizeValue = document.getElementById('home-size-value');
const homeSizeMax = document.getElementById('home-size-max');

function callPython(message) {
  if (window.webkit && window.webkit.messageHandlers.pythonHandler) {
    window.webkit.messageHandlers.pythonHandler.postMessage(message);
  } else {
    console.error("Bridge not available");
  }
}

window.receiveFromPython = function(text) {
  console.log("Received from Python:", text);

  if (text.startsWith("keymaps:")) {
    const data = text.substring(8);
    const keymaps = data.split(',');
    populateContainer(keymapContainer, keymaps, "keymap")
  }
  else if (text.startsWith("locales:")) {
    const data = text.substring(8);
    const locales = data.split(',');
    populateContainer(localeContainer, locales, "locale")
  }
  else if (text.startsWith("timezones:")) {
    const data = text.substring(10);
    const timezones = data.split(',');
    populateContainer(timezoneContainer, timezones, "timezone")
  }
  else if (text.startsWith("free_space:")) {
    const freeSpace = parseInt(text.substring(11));
    homeSizeSlider.max = freeSpace;
    homeSizeMax.textContent = `${freeSpace} GB`;

    if (parseInt(homeSizeSlider.value) > freeSpace) {
      homeSizeSlider.value = freeSpace;
      homeSizeValue.textContent = freeSpace;
    }
  }
};

function populateContainer(container, list, name) {
  container.innerHTML = '';

  list.forEach((item, index) => {
    const label = document.createElement('label');
    label.className = 'label cursor-pointer justify-start gap-3 py-2 hover:bg-base-200/50 rounded-lg transition-colors';
    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = name;
    radio.className = 'radio radio-primary radio-sm';
    if (index === 0) radio.checked = true;

    const span = document.createElement('span');
    span.className = 'label-text font-mono text-xs';
    span.textContent = item;

    label.appendChild(radio);
    label.appendChild(span);
    container.appendChild(label);
  });
}

function setupSearch(searchInput, container) {
  searchInput.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase().trim();
    const labels = container.querySelectorAll('label');

    labels.forEach(label => {
      const text = label.querySelector('span').textContent.toLowerCase();
      label.style.display = text.includes(searchTerm) ? 'flex' : 'none';
    });
  });
}

function pageTransition(page_a, page_b) {
  page_a.style.opacity = '0';
  setTimeout(function() {
    page_a.classList.add('hidden');
    page_b.classList.remove('hidden');
    setTimeout(function() {
      page_b.style.opacity = '1';
    }, 20);
  }, 300);
}

setupBtn.addEventListener('click', function() {
  pageTransition(welcomeScreen, step1);
});

backFromStep1.addEventListener('click', function() {
  pageTransition(step1, welcomeScreen)
});

nextToStep2.addEventListener('click', function() {
  pageTransition(step1, step2)
});

backFromStep2.addEventListener('click', function() {
  pageTransition(step2, step1)
});

nextToStep3.addEventListener('click', function() {
  pageTransition(step2, step3)
});

backFromStep3.addEventListener('click', function() {
  pageTransition(step3, step2)
});

homeSizeSlider.addEventListener('input', function() {
  homeSizeValue.textContent = this.value;
});

welcomeScreen.style.opacity = '1';
step1.style.opacity = '0';
step2.style.opacity = '0';
step3.style.opacity = '0';

callPython('get_keymap_list');
callPython('get_locale_list');
callPython('get_timezone_list');
callPython('get_free_space');

setupSearch(keymapSearch, keymapContainer);
setupSearch(localeSearch, localeContainer);
setupSearch(timezoneSearch, timezoneContainer);

setTimeout(function() {
  welcomeScreen.classList.remove('hidden');
}, 1100);
