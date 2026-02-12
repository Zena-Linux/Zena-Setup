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

document.getElementById("btnGet").addEventListener("click", () => {
    callPython("get_data");
});
document.getElementById("btnAdd").addEventListener("click", () => {
    callPython("add:5:3");
});
