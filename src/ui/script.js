
function callPython(message) {
  if (window.webkit && window.webkit.messageHandlers.pythonHandler) {
    window.webkit.messageHandlers.pythonHandler.postMessage(message);
  } else {
    console.error("Bridge not available");
  }
}

window.receiveFromPython = function(text) {
  document.getElementById("output").innerText = text;
};

const welcomeScreen = document.getElementById('welcome-screen');
const step1 = document.getElementById('setup-screen-step1');
const step2 = document.getElementById('setup-screen-step2');

const setupBtn = document.getElementById('setup-btn');
const backFromStep1 = document.getElementById('back-from-step1');
const nextToStep2 = document.getElementById('next-to-step2');
const backFromStep2 = document.getElementById('back-from-step2');

setupBtn.addEventListener('click', function() {
  welcomeScreen.style.opacity = '0';
  setTimeout(function() {
    welcomeScreen.classList.add('hidden');
    step1.classList.remove('hidden');
    setTimeout(function() {
      step1.style.opacity = '1';
    }, 20);
  }, 300);
});

backFromStep1.addEventListener('click', function() {
  step1.style.opacity = '0';
  setTimeout(function() {
    step1.classList.add('hidden');
    welcomeScreen.classList.remove('hidden');
    setTimeout(function() {
      welcomeScreen.style.opacity = '1';
    }, 20);
  }, 300);
});

nextToStep2.addEventListener('click', function() {
  step1.style.opacity = '0';
  setTimeout(function() {
    step1.classList.add('hidden');
    step2.classList.remove('hidden');
    setTimeout(function() {
      step2.style.opacity = '1';
    }, 20);
  }, 300);
});

// Step 2 → Step 1 (Back)
backFromStep2.addEventListener('click', function() {
  step2.style.opacity = '0';
  setTimeout(function() {
    step2.classList.add('hidden');
    step1.classList.remove('hidden');
    setTimeout(function() {
      step1.style.opacity = '1';
    }, 20);
  }, 300);
});

welcomeScreen.style.opacity = '1';
step1.style.opacity = '0';
step2.style.opacity = '0';

document.getElementById("btnGet").addEventListener("click", () => {
  callPython("get_data");
});
document.getElementById("btnAdd").addEventListener("click", () => {
  callPython("add:5:3");
});
