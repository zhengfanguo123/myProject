document.getElementById('generate-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = document.getElementById('prompt').value;
    const result = document.getElementById('result');
    result.textContent = 'Generating...';
    try {
        const resp = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        const data = await resp.json();
        if (data.url) {
            result.innerHTML = `<img src="${data.url}" alt="generated">`;
        } else {
            result.textContent = data.error || 'Error';
        }
    } catch (err) {
        result.textContent = 'Error generating image';
    }
});
