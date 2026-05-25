document.addEventListener("DOMContentLoaded", () => {
    const wsStatus = document.getElementById("ws-status");
    const logBox = document.getElementById("log-box");
    
    // Connect to FastAPI WebSocket
    const ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onopen = () => {
        wsStatus.innerText = "Connected";
        wsStatus.style.color = "#4ade80";
        appendLog("System: Connected to TARS stream.");
    };
    
    ws.onmessage = (event) => {
        appendLog(event.data);
    };
    
    ws.onclose = () => {
        wsStatus.innerText = "Disconnected";
        wsStatus.style.color = "#ef4444";
        appendLog("System: Connection lost.");
    };
    
    function appendLog(msg) {
        const div = document.createElement("div");
        div.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
        logBox.appendChild(div);
        logBox.scrollTop = logBox.scrollHeight;
    }
});
