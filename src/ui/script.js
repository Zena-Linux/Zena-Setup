const welcomeScreen = document.getElementById('welcome-screen');
const step1 = document.getElementById('setup-screen-step1');
const step2 = document.getElementById('setup-screen-step2');

const setupBtn = document.getElementById('setup-btn');
const backFromStep1 = document.getElementById('back-from-step1');
const nextToStep2 = document.getElementById('next-to-step2');
const backFromStep2 = document.getElementById('back-from-step2');

function callPython(message) {
  if (window.webkit && window.webkit.messageHandlers.pythonHandler) {
    window.webkit.messageHandlers.pythonHandler.postMessage(message);
  } else {
    console.error("Bridge not available");
  }
}

window.receiveFromPython = function(text) {
  console.log(text)
};

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

setupBtn.addEventListener('click', function() { pageTransition(welcomeScreen, step1) });
backFromStep1.addEventListener('click', function() { pageTransition(step1, welcomeScreen) });
nextToStep2.addEventListener('click', function() { pageTransition(step1, step2) });
backFromStep2.addEventListener('click', function() { pageTransition(step2, step1) });

welcomeScreen.style.opacity = '1';
step1.style.opacity = '0';
step2.style.opacity = '0';
