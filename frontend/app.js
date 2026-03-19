const API_URL = "http://localhost:8080";

const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');

const queryBtn = document.getElementById('queryBtn');
const queryInput = document.getElementById('queryInput');
const loading = document.getElementById('loading');
const responseContainer = document.getElementById('responseContainer');

const routeDisplay = document.getElementById('routeDisplay');
const answerText = document.getElementById('answerText');
const sourcesList = document.getElementById('sourcesList');
const sourcesBox = document.getElementById('sourcesBox');

uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    uploadStatus.textContent = "Uploading and ingesting...";
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        uploadStatus.textContent = data.status || "Error uploading.";
    } catch (error) {
        console.error("Upload error:", error);
        uploadStatus.textContent = "Error connecting to backend.";
    }
});

queryBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();
    if (!query) return;

    loading.classList.remove('hidden');
    responseContainer.classList.add('hidden');

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        loading.classList.add('hidden');
        responseContainer.classList.remove('hidden');

        answerText.textContent = data.answer;
        routeDisplay.textContent = `Decision: ${data.route.replace('_', ' ')}`;
        routeDisplay.className = `route-tag ${data.route}`;

        sourcesList.innerHTML = '';
        if (data.sources && data.sources.length > 0) {
            sourcesBox.classList.remove('hidden');
            [...new Set(data.sources)].forEach(source => {
                const li = document.createElement('li');
                li.textContent = source;
                sourcesList.appendChild(li);
            });
        } else {
            sourcesBox.classList.add('hidden');
        }
    } catch (error) {
        console.error("Query error:", error);
        loading.classList.add('hidden');
        alert("Error connecting to backend.");
    }
});
