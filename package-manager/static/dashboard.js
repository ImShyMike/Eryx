const copyKeyButton = document.getElementById('copy-key');
const refreshKeyButton = document.getElementById('refresh-key');
const apiKey = document.getElementById('api-key-value');

copyKeyButton.addEventListener('click', () => {
    navigator.clipboard.writeText(apiKey.textContent).then(() => {
        copyKeyButton.textContent = 'Copied!';
        setTimeout(() => {
            copyKeyButton.textContent = 'Copy';
        }, 2000);
    });
});

refreshKeyButton.addEventListener('click', () => {
    const currentApiKey = apiKey.textContent;

    if (!currentApiKey) {
        alert('No API key to refresh, this should not happen. Please refresh the page.');
        return;
    }

    if (refreshKeyButton.textContent === 'Refreshing...' || refreshKeyButton.textContent === 'Refreshed!') {
        return;
    }

    refreshKeyButton.textContent = 'Refreshing...';

    fetch('/api/refresh-key', {
        method: 'POST',
        headers: {
            'X-API-Key': currentApiKey
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        apiKey.textContent = data.key;
        refreshKeyButton.textContent = 'Refreshed!';
        setTimeout(() => {
            refreshKeyButton.textContent = 'Refresh';
        }, 2000);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to refresh API key. Please try again.');
        refreshKeyButton.textContent = 'Refresh';
    });
});

