const button = document.getElementById("research-btn");
const topicInput = document.getElementById("topic-input");
const statusDiv = document.getElementById("status");

button.addEventListener("click", function() {
    const topic = topicInput.value;
    if (!topic) {
        statusDiv.innerText = "Please enter a research topic!";
        return;
    }
    statusDiv.innerText = "Ready to start research...";
    // Agle video mein yahan fetch() call aayega
});