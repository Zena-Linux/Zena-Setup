// Send a message to the Python bridge
function callPython(message) {
    if (window.webkit && window.webkit.messageHandlers.pythonHandler) {
        window.webkit.messageHandlers.pythonHandler.postMessage(message);
    } else {
        console.error("Bridge not available");
    }
}

// Called by Python via evaluate_javascript()
window.receiveFromPython = function(text) {
    document.getElementById("output").innerText = text;
};

// Example bindings
document.getElementById("btnGet").addEventListener("click", () => {
    callPython("get_data");
});
document.getElementById("btnAdd").addEventListener("click", () => {
    callPython("add:5:3");
});
