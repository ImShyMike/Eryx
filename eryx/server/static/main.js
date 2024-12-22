const codeEditor = CodeMirror.fromTextArea(document.getElementById("code-area"), {
    lineNumbers: true,
    mode: "text/x-go",
    theme: "material-palenight",
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    foldGutter: true,
    extraKeys: {
        "Ctrl-Q": function(cm) {
            cm.foldCode(cm.getCursor());
        }
    }
});

const modeSelectDropdown = document.getElementById("mode-select");
const output = document.getElementById("repl-output");
const keepMemory = document.getElementById("memory-enabled");
const editorHeader = document.getElementById("editor-header");

let envId = null;

async function getEnvId() {
    return fetch('/repl', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then((response) => {
        if (!response.ok) {
            throw new Error('An unknown error has occurred :(');
        }
        return response.json();
    }).catch(error => {
        alert('Error fetching environment ID: ' + error.message);
    });
}

async function runCode(code, mode, envId) {
    const body = { source_code: code };
    if (envId !== null) {
        body.env_uuid = envId;
    }

    try {
        const response = await fetch(`/${mode}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            throw new Error('An unknown error has occurred :(');
        }

        return await response.json();
    } catch (error) {
        alert('Error running code: ' + error.message);
    }
}

function deleteEnvId() {
    fetch('/repl?envId=' + envId , {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
    }).catch(error => {
        alert('Error deleting environment ID: ' + error.message);
    });
}

function showRunning() {
    output.textContent = "Running...";
};

function showExecutionResult(result) {
    output.innerHTML = result;
};

document.getElementById("run-button").addEventListener("click", async () => {
    showRunning();
    const code = codeEditor.getValue();
    if (code.trim() === "") {
        showExecutionResult("");
        return;
    }
    if (!keepMemory.checked) {
        if (envId !== null) {
            deleteEnvId();
            envId = null;
        }
    } else if (envId === null) {
        response = await getEnvId();
        envId = response["env_uuid"];
    }
    await runCode(code, modeSelectDropdown.value, envId).then((response) => {
        if (response.error) {
            showExecutionResult(response.error);
            return;
        }
        showExecutionResult(response.result);
    });
});

document.getElementById("clear-console").addEventListener("click", () => {
    document.getElementById("repl-output").textContent = "";
});

document.getElementById("clear-memory").addEventListener("click", () => {
    if (envId !== null) {
        deleteEnvId();
        envId = null;
        alert("REPL reloaded!");
    }
});

document.getElementById("import-button").addEventListener("click", () => {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".eryx";
    fileInput.onchange = (event) => {
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
            codeEditor.setValue(e.target.result);
        };
        reader.readAsText(file);
    };
    fileInput.click();
});

document.getElementById("export-button").addEventListener("click", () => {
    const code = codeEditor.getValue();
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = editorHeader.textContent || "code.eryx";
    link.click();
    URL.revokeObjectURL(url);
});

document.getElementById("documentation-button").addEventListener("click", () => {
    window.open("https://ImShyMike.github.io/Eryx", "_blank");
});

document.getElementById("settings-button").addEventListener("click", () => {
    document.getElementById("settings-menu").classList.toggle("show");
});

editorHeader.addEventListener("click", () => {
    if (!editorHeader.isContentEditable) {
        editorHeader.setAttribute("contenteditable", "true");
        editorHeader.setAttribute("spellcheck", "false");
        editorHeader.focus();
    }
});

editorHeader.addEventListener("blur", () => {
    editorHeader.removeAttribute("contenteditable");
});

editorHeader.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        editorHeader.blur();
    }
});
