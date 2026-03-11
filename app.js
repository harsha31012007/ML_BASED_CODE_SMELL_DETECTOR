// Basic configuration for the frontend to communicate with the Flask API
const API_URL = 'http://localhost:5000/api';
const CODE_LABELS = {
    vulnerable: 'Vulnerable Code',
    clean: 'Clean Code',
};

// State tracker for which sample is currently active
let currentCodeType = null;

// UI Element References
const vulnerableBtn = document.getElementById('vulnerableBtn');
const cleanBtn = document.getElementById('cleanBtn');
const randomBtn = document.getElementById('randomBtn');
const executeBtn = document.getElementById('executeBtn');
const clearBtn = document.getElementById('clearBtn');
const codeEditor = document.getElementById('codeEditor');
const outputDisplay = document.getElementById('outputDisplay');
const codeType = document.getElementById('codeType');
const statusBadge = document.getElementById('statusBadge');

/**
 * Initialize the application once the DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    clearAll(); // Reset UI to initial state
});

/**
 * Register click handlers for all interactive buttons.
 */
function setupEventListeners() {
    vulnerableBtn.addEventListener('click', () => switchCode('vulnerable'));
    cleanBtn.addEventListener('click', () => switchCode('clean'));
    randomBtn.addEventListener('click', fetchRandomSample);
    executeBtn.addEventListener('click', executeCode);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeCode);
    clearBtn.addEventListener('click', clearAll);
}

/**
 * Switches between 'vulnerable' and 'clean' code samples.
 * Updates UI styles and loads file content from the backend.
 * @param {string} type - Either 'vulnerable' or 'clean'
 */
function switchCode(type) {
    currentCodeType = type;

    // Toggle active state on buttons
    vulnerableBtn.classList.toggle('active', type === 'vulnerable');
    cleanBtn.classList.toggle('active', type === 'clean');

    // Update the badge display
    if (type === 'vulnerable') {
        codeType.innerHTML = '<i class="fas fa-bug"></i> Vulnerable';
        codeType.className = 'badge badge-danger';
    } else {
        codeType.innerHTML = '<i class="fas fa-shield-alt"></i> Clean';
        codeType.className = 'badge badge-success';
    }

    // Fetch the code from the server
    loadCode(type);

    // Clear any previous execution output
    clearOutput();
}

/**
 * Fetches sample code content from the API server.
 * @param {string} type - The sample type to load
 */
async function loadCode(type) {
    try {
        codeEditor.value = 'Loading code...';

        const response = await fetch(`${API_URL}/get-code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type })
        });

        const data = await response.json();

        if (data.success) {
            codeEditor.value = data.code;
        } else {
            codeEditor.value = `Error: ${data.error}`;
        }
    } catch (error) {
        codeEditor.value = `Error loading code: ${error.message}`;
    }
}

/**
 * Resets the output display area to its placeholder state.
 */
function clearOutput() {
    outputDisplay.innerHTML = '<p class="placeholder">Select a sample and click Execute to see results...</p>';
    statusBadge.innerHTML = '<i class="fas fa-clock"></i> Ready';
    statusBadge.className = 'badge badge-info';
}

/**
 * Sends the current code in the editor to the server for execution.
 * Displays the stdout, stderr, and exit code in the UI.
 */
async function executeCode() {
    try {
        if (!codeEditor.value.trim()) {
            outputDisplay.innerHTML = '<div class="error"><strong><i class="fas fa-info-circle"></i> No code to execute:</strong> please select a sample or type your own code.</div>';
            statusBadge.innerHTML = '<i class="fas fa-exclamation-circle"></i> Editor empty';
            statusBadge.className = 'badge badge-warning';
            return;
        }

        // Update UI to show loading state
        statusBadge.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        statusBadge.className = 'badge badge-warning';
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Executing...';

        outputDisplay.innerHTML = '<p style="color: #888;">Executing code...</p>';

        // POST the code to the execution endpoint
        const response = await fetch(`${API_URL}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: currentCodeType,
                code: codeEditor.value
            })
        });

        const data = await response.json();
        const sampleLabel = CODE_LABELS[currentCodeType] || 'Selected sample';

        if (data.success) {
            let output = '';
            output += `<div class="summary"><strong><i class="fas fa-info-circle"></i> Sample:</strong> ${sampleLabel}</div>`;

            // Display informative messages based on the sample type
            if (currentCodeType === 'vulnerable') {
                output += '<div class="error"><strong><i class="fas fa-bug"></i> Code Smells:</strong> Detected (this sample is intentionally vulnerable)</div>';
            } else if (currentCodeType === 'clean') {
                output += '<div class="success"><strong><i class="fas fa-shield-alt"></i> Code Smells:</strong> None detected (clean sample)</div>';
            }

            // Append program output (stdout)
            if (data.output) {
                output += `<div class="success"><strong><i class="fas fa-check-circle"></i> Output:</strong>\n${escapeHtml(data.output)}</div>`;
            }

            // Append program errors (stderr)
            if (data.error) {
                output += `<div class="error"><strong><i class="fas fa-exclamation-triangle"></i> Errors/Warnings:</strong>\n${escapeHtml(data.error)}</div>`;
            }

            if (!data.output && !data.error) {
                output += '<div class="success"><i class="fas fa-check-circle"></i> Code executed successfully (no output)</div>';
            }

            // Show final execution status
            output += `<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #444;">
                <strong>Exit Code:</strong> ${data.exit_code === 0 ? '<i class="fas fa-check"></i> 0 (Success)' : `<i class="fas fa-times"></i> ${data.exit_code}`}
            </div>`;

            outputDisplay.innerHTML = output;
            statusBadge.innerHTML = data.exit_code === 0 ? '<i class="fas fa-check-circle"></i> Success' : '<i class="fas fa-exclamation-circle"></i> Completed with errors';
            statusBadge.className = data.exit_code === 0 ? 'badge badge-success' : 'badge badge-warning';
        } else {
            outputDisplay.innerHTML = `<div class="summary"><strong><i class="fas fa-info-circle"></i> Sample:</strong> ${sampleLabel}</div>` +
                `<div class="error"><strong><i class="fas fa-times-circle"></i> Execution Error:</strong>\n${escapeHtml(data.error)}</div>`;
            statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Error';
            statusBadge.className = 'badge badge-danger';
        }

    } catch (error) {
        outputDisplay.innerHTML = `<div class="error"><strong><i class="fas fa-times-circle"></i> Error:</strong>\n${escapeHtml(error.message)}\n\nMake sure the API server is running:\npython api.py</div>`;
        statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Error';
        statusBadge.className = 'badge badge-danger';
    } finally {
        executeBtn.disabled = false;
        executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute Code';
    }
}

/**
 * Sends the current code in the editor to the analysis endpoint.
 * Displays a list of detected smells and their severity.
 */
async function analyzeCode() {
    try {
        if (!codeEditor.value.trim()) {
            outputDisplay.innerHTML = '<div class="error"><strong><i class="fas fa-info-circle"></i> No code to analyze.</strong></div>';
            return;
        }

        statusBadge.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        statusBadge.className = 'badge badge-warning';

        outputDisplay.innerHTML = '<p style="color: #888;">Analyzing code smells...</p>';

        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: currentCodeType,
                code: codeEditor.value
            })
        });

        const data = await response.json();

        if (data.success) {
            let output = '<div class="summary"><strong><i class="fas fa-microscope"></i> Analysis Results:</strong></div>';

            if (data.smells.length === 0) {
                output += '<div class="success"><i class="fas fa-check-circle"></i> No code smells detected. Excellent!</div>';
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Clean';
                statusBadge.className = 'badge badge-success';
            } else {
                statusBadge.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Smells Detected';
                statusBadge.className = 'badge badge-danger';

                output += '<ul class="smell-list" style="list-style: none; padding: 0;">';
                data.smells.forEach(smell => {
                    // Use different colors for different severity levels
                    const severityClass = (smell.severity === 'Critical' || smell.severity === 'High') ? 'text-danger' : 'text-warning';
                    output += `<li style="margin-bottom: 10px; padding: 10px; border-left: 3px solid #ff4444; background: rgba(255,0,0,0.1);">
                        <strong class="${severityClass}">[${smell.severity}] ${smell.type}</strong> (Line ${smell.line})<br>
                        ${escapeHtml(smell.description)}
                    </li>`;
                });
                output += '</ul>';
            }

            outputDisplay.innerHTML = output;
        } else {
            outputDisplay.innerHTML = `<div class="error">Error: ${data.error}</div>`;
        }

    } catch (error) {
        outputDisplay.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

/**
 * Helper to prevent XSS when rendering user-provided or program output.
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Fetches a random sample from the ML dataset.
 */
async function fetchRandomSample() {
    try {
        currentCodeType = 'random';
        codeEditor.value = 'Loading random sample...';
        
        vulnerableBtn.classList.remove('active');
        cleanBtn.classList.remove('active');
        randomBtn.classList.add('active');

        const response = await fetch(`${API_URL}/random-sample`);
        const data = await response.json();

        if (data.success) {
            codeEditor.value = data.code;
            codeType.innerHTML = `<i class="fas fa-random"></i> ML Sample: ${data.label}`;
            codeType.className = 'badge badge-info';
            clearOutput();
        } else {
            codeEditor.value = `Error: ${data.error}`;
        }
    } catch (error) {
        codeEditor.value = `Error fetching random sample: ${error.message}`;
    }
}

/**
 * Resets the entire application state and UI.
 */
function clearAll() {
    currentCodeType = null;
    vulnerableBtn.classList.remove('active');
    cleanBtn.classList.remove('active');
    codeEditor.value = '';
    codeType.innerHTML = '<i class="fas fa-hand-pointer"></i> Select a sample or type code';
    codeType.className = 'badge badge-info';
    clearOutput();
}
