let currentEnvId = null;

function getEnvId() {
    return fetch('/repl', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'token' })
    }).then((response) => {
        if (!response.ok) {
            throw new Error('An unknown error has occurred :(');
        }
        return response.json();
    }).catch(error => {
        alert('Error fetching environment ID: ' + error.message);
    });
}

function runCode(code, mode, envId) {
    if (envId === null) {
        return fetch('/' + mode, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ source_code: code })
        }).then((response) => {
            if (!response.ok) {
                throw new Error('An unknown error has occurred :(');
            }
            return response.json();
        }).catch(error => {
            alert('Error running code: ' + error.message);
        });
    } else {
        return fetch('/' + mode, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ source_code: code, env_uuid: envId })
        }).then((response) => {
            if (!response.ok) {
                throw new Error('An unknown error has occurred :(');
            }
            return response.json();
        }).catch(error => {
            alert('Error running code: ' + error.message);
        });
    }
}

function deleteEnv() {
    fetch('/repl', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'delete', env_uuid: currentEnvId })
    }).then((response) => response.json()).then((data) => {
        currentEnvId = null;
    });
}

document.getElementById('execute-button').addEventListener('click', () => {
    const mode = document.getElementById('mode-select').value;
    const code = document.getElementById('code-area').value;

    if (currentEnvId === null) {
        getEnvId().then(data => {
            currentEnvId = data.env_uuid;
            return runCode(code, mode, currentEnvId);
        }).then(output => {
            if (output.error !== undefined) {
                document.getElementById('repl-output').innerHTML = "Error: " + output.error;
            } else {
                document.getElementById('repl-output').innerHTML = output.result;
            }
        });
    } else {
        memoryEnabled = document.getElementById('memory-enabled').checked;
        runCode(code, mode, memoryEnabled ? currentEnvId : null).then(output => {
            if (output.error !== undefined) {
                document.getElementById('repl-output').innerHTML = "Error: " + output.error;
            } else {
                document.getElementById('repl-output').innerHTML = output.result;
            }
        });
    }
});

document.getElementById('clear-console').addEventListener('click', () => {
    document.getElementById('repl-output').innerText = "";
});

document.getElementById('clear-memory').addEventListener('click', () => {
    if (currentEnvId !== null) {
        deleteEnv();
    }
});

document.getElementById('help-button').addEventListener('click', (event) => {
    const helpModal = document.getElementById('help-modal');
    helpModal.style.display = (helpModal.style.display === 'block') ? 'none' : 'block';
    event.stopPropagation();
});

document.addEventListener('click', (event) => {
    const helpModal = document.getElementById('help-modal');
    if (helpModal.style.display === 'block' && !helpModal.contains(event.target)) {
        helpModal.style.display = 'none';
    }
});
