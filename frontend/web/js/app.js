/**
 * Quantum Virtual Assistant (QVA) - Frontend Application
 * Main JavaScript file for handling UI interactions and API communication
 */

// Global state management
const QVA = {
    apiBaseUrl: '/api',
    devMode: false,
    darkTheme: false,
    systemStatus: {
        online: true,
        cpu: 45,
        memory: 32,
        quantum: 78
    },
    quantum: {
        qubits: 4,
        gates: 28,
        circuits: 3,
        fidelity: 0.982,
        currentCircuit: null,
        // Quantum circuit state
        circuit: {
            qubits: 3,
            gates: [],
            measurements: []
        },
        // Available quantum gates
        availableGates: [
            { id: 'h', name: 'H', description: 'Hadamard Gate', color: '#3498db' },
            { id: 'x', name: 'X', description: 'Pauli-X Gate', color: '#e74c3c' },
            { id: 'y', name: 'Y', description: 'Pauli-Y Gate', color: '#f39c12' },
            { id: 'z', name: 'Z', description: 'Pauli-Z Gate', color: '#2ecc71' },
            { id: 'cnot', name: 'CNOT', description: 'Controlled NOT Gate', color: '#9b59b6' },
            { id: 'swap', name: 'SWAP', description: 'Swap Gate', color: '#1abc9c' }
        ],
        // Selected quantum gate for placement
        selectedGate: null,
        // Simulation results
        results: {
            states: [],
            probabilities: [],
            counts: []
        }
    },
    blockchain: {
        enabled: false,
        network: 'testnet',
        status: 'disconnected',
        accounts: [],
        balance: 0
    },
    activeView: 'dashboard',
    updateInterval: null
};

// Initialize application when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize Quantum Circuit Designer and Results
 */
function initializeQuantumInterface() {
    // Set up circuit designer controls
    const addQubitBtn = document.querySelector('.add-qubit');
    const addGateBtn = document.querySelector('.add-gate');
    const runCircuitBtn = document.querySelector('.run-circuit');
    const clearCircuitBtn = document.querySelector('.clear-circuit');
    const circuitCanvas = document.getElementById('circuit-canvas');
    const resultsCanvas = document.getElementById('results-canvas');

    // Add Qubit
    if (addQubitBtn) {
        addQubitBtn.addEventListener('click', () => {
            QVA.quantum.circuit.qubits++;
            drawCircuit();
        });
    }

    // Add Gate (shows a selector for available gates)
    if (addGateBtn) {
        addGateBtn.addEventListener('click', () => {
            showGateSelector();
        });
    }

    // Run Circuit
    if (runCircuitBtn) {
        runCircuitBtn.addEventListener('click', () => {
            runQuantumCircuit();
        });
    }

    // Clear Circuit
    if (clearCircuitBtn) {
        clearCircuitBtn.addEventListener('click', () => {
            clearQuantumCircuit();
        });
    }

    // Draw the initial circuit
    drawCircuit();
}

/**
 * Draw the quantum circuit on the canvas
 */
function drawCircuit() {
    const canvas = document.getElementById('circuit-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const { qubits, gates } = QVA.quantum.circuit;
    // Draw qubit lines
    for (let q = 0; q < qubits; q++) {
        ctx.strokeStyle = '#888';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(40, 40 + q * 40);
        ctx.lineTo(canvas.width - 40, 40 + q * 40);
        ctx.stroke();
        ctx.fillStyle = '#333';
        ctx.font = '16px Arial';
        ctx.fillText('q' + q, 10, 45 + q * 40);
    }
    // Draw gates
    gates.forEach(gate => {
        ctx.fillStyle = gate.color || '#3498db';
        ctx.fillRect(gate.x, gate.y, 32, 32);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(gate.name, gate.x + 16, gate.y + 22);
    });
}

/**
 * Show the quantum gate selector for adding a gate
 */
function showGateSelector() {
    // Simple prompt for now; can be replaced by a modal or palette
    const gateNames = QVA.quantum.availableGates.map(g => g.name).join(', ');
    const chosen = prompt('Select a gate to add (' + gateNames + '):');
    if (!chosen) return;
    const gate = QVA.quantum.availableGates.find(g => g.name.toUpperCase() === chosen.trim().toUpperCase());
    if (gate) {
        // For demo, add to first qubit at next available x
        const qubit = 0;
        const x = 80 + QVA.quantum.circuit.gates.length * 40;
        const y = 40 + qubit * 40 - 16;
        QVA.quantum.circuit.gates.push({ ...gate, x, y });
        drawCircuit();
    } else {
        alert('Invalid gate selection.');
    }
}

/**
 * Run the quantum circuit simulation (mocked)
 */
function runQuantumCircuit() {
    // For demo, generate random results for 2^n states
    const n = QVA.quantum.circuit.qubits;
    const numStates = Math.pow(2, n);
    const results = [];
    let sum = 0;
    for (let i = 0; i < numStates; i++) {
        const prob = Math.random();
        results.push({ state: '|' + i.toString(2).padStart(n, '0') + '⟩', prob });
        sum += prob;
    }
    // Normalize
    results.forEach(r => r.prob /= sum);
    // Save and display
    QVA.quantum.results.states = results.map(r => r.state);
    QVA.quantum.results.probabilities = results.map(r => r.prob.toFixed(3));
    QVA.quantum.results.counts = results.map(r => Math.floor(r.prob * 1000));
    visualizeResults();
}

/**
 * Visualize quantum simulation results
 */
function visualizeResults() {
    const resultsBody = document.getElementById('results-body');
    if (!resultsBody) return;
    resultsBody.innerHTML = '';
    for (let i = 0; i < QVA.quantum.results.states.length; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${QVA.quantum.results.states[i]}</td><td>${QVA.quantum.results.probabilities[i]}</td><td>${QVA.quantum.results.counts[i]}</td>`;
        resultsBody.appendChild(row);
    }
    // Optionally, draw histogram on results-canvas
    const canvas = document.getElementById('results-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const n = QVA.quantum.results.states.length;
        const maxCount = Math.max(...QVA.quantum.results.counts, 1);
        for (let i = 0; i < n; i++) {
            const x = 40 + i * ((canvas.width - 80) / n);
            const y = canvas.height - 30;
            const barHeight = (QVA.quantum.results.counts[i] / maxCount) * (canvas.height - 60);
            ctx.fillStyle = '#3498db';
            ctx.fillRect(x, y - barHeight, 20, barHeight);
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(QVA.quantum.results.states[i], x + 10, canvas.height - 10);
        }
    }
}

/**
 * Clear the quantum circuit
 */
function clearQuantumCircuit() {
    QVA.quantum.circuit.gates = [];
    drawCircuit();
    QVA.quantum.results = { states: [], probabilities: [], counts: [] };
    visualizeResults();
}


/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing QVA frontend application...');
    
    // Check if we're in development mode
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        QVA.devMode = true;
        console.log('Running in development mode with mock data');
    }
    
    // Initialize UI components
    initializeNavigation();
    initializeThemeToggle();
    
    // Initialize views
    initializeDashboard();
    initializeAssistant();
    initializeQuantumInterface();
    initializeBlockchainInterface();
    
    // Start periodic updates
    startPeriodicUpdates();
    
    // Connect to the API if in production mode
    if (!QVA.devMode) {
        connectToAPI();
    }
    
    console.log('QVA frontend application initialized successfully');
}

/**
 * Start periodic updates for real-time data
 */
function startPeriodicUpdates() {
    // Clear any existing interval
    if (QVA.updateInterval) {
        clearInterval(QVA.updateInterval);
    }
    
    // Update system status immediately
    updateSystemStatus();
    
    // Set up periodic updates every 5 seconds
    QVA.updateInterval = setInterval(() => {
        // Only update active view components to save resources
        if (QVA.activeView === 'dashboard') {
            updateSystemStatus();
            updateQuantumVisualization();
        } else if (QVA.activeView === 'quantum') {
            // Update quantum-specific data
            if (!QVA.devMode) {
                fetchQuantumStatus();
            }
        } else if (QVA.activeView === 'blockchain') {
            // Update blockchain-specific data
            if (!QVA.devMode && QVA.blockchain.enabled) {
                fetchBlockchainStatus();
            }
        }
    }, 5000);
}

/**
 * Initialize blockchain interface
 */
function initializeBlockchainInterface() {
    // Get blockchain status elements
    const enableBlockchainBtn = document.querySelector('.enable-blockchain');
    const statusMessage = document.querySelector('.blockchain-card .status-message');
    const statusIndicator = document.querySelector('.blockchain-card .status-indicator');
    
    // Set up event listeners
    if (enableBlockchainBtn) {
        enableBlockchainBtn.addEventListener('click', toggleBlockchain);
    }
    
    // Update blockchain status display
    updateBlockchainStatus();
}

/**
 * Toggle blockchain integration
 */
function toggleBlockchain() {
    const enableBtn = document.querySelector('.enable-blockchain');
    const statusMessage = document.querySelector('.blockchain-card .status-message');
    const statusIndicator = document.querySelector('.blockchain-card .status-indicator');
    
    if (!QVA.blockchain.enabled) {
        // Enable blockchain
        QVA.blockchain.enabled = true;
        
        // Update UI
        if (statusIndicator) {
            statusIndicator.classList.remove('offline');
            statusIndicator.classList.add('online');
        }
        
        if (statusMessage) {
            statusMessage.textContent = 'Connecting to blockchain network...';
        }
        
        if (enableBtn) {
            enableBtn.textContent = 'Disable Blockchain';
        }
        
        // In a real implementation, we would connect to the blockchain here
        // For this demo, we'll simulate a connection process
        setTimeout(() => {
            if (statusMessage) {
                statusMessage.textContent = 'Connected to ' + QVA.blockchain.network + ' network';
            }
            
            // Fetch blockchain status
            fetchBlockchainStatus();
        }, 1500);
    } else {
        // Disable blockchain
        QVA.blockchain.enabled = false;
        
        // Update UI
        if (statusIndicator) {
            statusIndicator.classList.remove('online');
            statusIndicator.classList.add('offline');
        }
        
        if (statusMessage) {
            statusMessage.textContent = 'Blockchain integration is currently disabled.';
        }
        
        if (enableBtn) {
            enableBtn.textContent = 'Enable Blockchain';
        }
    }
}

/**
 * Update blockchain status display
 */
function updateBlockchainStatus() {
    const statusIndicator = document.querySelector('.blockchain-card .status-indicator');
    const statusMessage = document.querySelector('.blockchain-card .status-message');
    const enableBtn = document.querySelector('.enable-blockchain');
    
    if (statusIndicator && statusMessage && enableBtn) {
        if (QVA.blockchain.enabled) {
            statusIndicator.classList.remove('offline');
            statusIndicator.classList.add('online');
            statusMessage.textContent = 'Connected to ' + QVA.blockchain.network + ' network';
            enableBtn.textContent = 'Disable Blockchain';
        } else {
            statusIndicator.classList.remove('online');
            statusIndicator.classList.add('offline');
            statusMessage.textContent = 'Blockchain integration is currently disabled.';
            enableBtn.textContent = 'Enable Blockchain';
        }
    }
}

/**
 * Fetch blockchain status from API
 */
function fetchBlockchainStatus() {
    if (QVA.devMode) {
        // Generate mock blockchain data in development mode
        QVA.blockchain.accounts = [
            { address: '0x7a1C9f59F3489...', balance: 2.54 },
            { address: '0x40A2D9f83c5D3...', balance: 0.12 }
        ];
        QVA.blockchain.status = 'connected';
        updateBlockchainStatus();
        return;
    }
    
    // In production, fetch from API
    fetch(`${QVA.apiBaseUrl}/blockchain/status`)
        .then(response => response.json())
        .then(data => {
            QVA.blockchain = {
                ...QVA.blockchain,
                accounts: data.accounts,
                status: data.status
            };
            updateBlockchainStatus();
        })
        .catch(error => {
            console.error('Error fetching blockchain status:', error);
            QVA.blockchain.status = 'error';
            updateBlockchainStatus();
        });
}

/**
 * Update quantum visualization on dashboard
 */
function updateQuantumVisualization() {
    const canvas = document.getElementById('quantum-visualization');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw background
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, '#2c3e50');
    gradient.addColorStop(1, '#1a202c');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    // Draw qubit states
    const numQubits = QVA.quantum.qubits;
    const stateHeight = height / numQubits;
    
    for (let i = 0; i < numQubits; i++) {
        // Generate a random state for visualization (in a real app, this would use actual quantum state data)
        const amplitude = Math.random();
        const phase = Math.random() * Math.PI * 2;
        
        // Draw qubit label
        ctx.fillStyle = '#e2e8f0';
        ctx.font = '12px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`q${i}`, 10, i * stateHeight + stateHeight/2 + 4);
        
        // Draw amplitude
        const barWidth = (width - 50) * amplitude;
        const hue = (i * 30 + 210) % 360;
        ctx.fillStyle = `hsl(${hue}, 80%, 60%)`;
        ctx.fillRect(40, i * stateHeight + 10, barWidth, stateHeight - 20);
        
        // Draw phase indicator
        const centerX = 40 + barWidth - 10;
        const centerY = i * stateHeight + stateHeight/2;
        if (barWidth > 20) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, 8, 0, Math.PI * 2);
            ctx.fillStyle = '#fff';
            ctx.fill();
            
            // Draw phase line
            const lineLength = 6;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(
                centerX + Math.cos(phase) * lineLength,
                centerY + Math.sin(phase) * lineLength
            );
            ctx.strokeStyle = '#2c3e50';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    }
}

/**
 * Show a notification message
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 * @param {string} type - Notification type ('info', 'success', 'warning', 'error')
 */
function showNotification(title, message, type = 'info') {
    // In a real implementation, this would show a toast notification
    // For this demo, we'll just log to console
    console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-title">${title}</div>
        <div class="notification-message">${message}</div>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to DOM
    const notificationsContainer = document.querySelector('.notifications-container');
    if (!notificationsContainer) {
        // Create notifications container if it doesn't exist
        const container = document.createElement('div');
        container.className = 'notifications-container';
        document.body.appendChild(container);
        container.appendChild(notification);
    } else {
        notificationsContainer.appendChild(notification);
    }
    
    // Add close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 5000);
}

/**
 * Connect to the backend API
 */
function connectToAPI() {
    fetch(`${QVA.apiBaseUrl}/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Connected to QVA API:', data);
        // Update system status with real data
        updateSystemStatus(data);
    })
    .catch(error => {
        console.error('Failed to connect to QVA API:', error);
        // Show an error notification
        showNotification('API Connection Error', 'Could not connect to the QVA backend.', 'error');
    });
}

/**
 * Initialize navigation system
 */
function initializeNavigation() {
    const navItems = document.querySelectorAll('.sidebar-nav li');
    const views = document.querySelectorAll('.view');
    
    // Add click event to all navigation items
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get view ID from the href attribute
            const viewId = this.querySelector('a').getAttribute('href').substring(1);
            
            // Update active navigation item
            navItems.forEach(navItem => navItem.classList.remove('active'));
            this.classList.add('active');
            
            // Update active view
            views.forEach(view => {
                if (view.id === `${viewId}-view`) {
                    view.classList.add('active');
                } else {
                    view.classList.remove('active');
                }
            });
            
            // Update active view in state
            QVA.activeView = viewId;
            
            // Update URL hash
            window.history.pushState(null, null, `#${viewId}`);
        });
    });
    
    // Handle navigation on page load and history changes
    window.addEventListener('popstate', handleUrlNavigation);
    handleUrlNavigation();
}

/**
 * Handle navigation based on URL hash
 */
function handleUrlNavigation() {
    // Get current hash or default to dashboard
    const currentHash = window.location.hash.substring(1) || 'dashboard';
    
    // Find the corresponding nav item and click it
    const navItem = document.querySelector(`.sidebar-nav li a[href="#${currentHash}"]`);
    if (navItem) {
        navItem.parentElement.click();
    } else {
        // Default to dashboard if hash doesn't match any view
        document.querySelector('.sidebar-nav li a[href="#dashboard"]').parentElement.click();
    }
}

/**
 * Initialize theme toggle
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('qva-theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        QVA.darkTheme = true;
    }
    
    // Add click event to theme toggle button
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-theme');
        QVA.darkTheme = body.classList.contains('dark-theme');
        
        // Update button icon
        themeToggle.innerHTML = QVA.darkTheme 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
        
        // Save preference
        localStorage.setItem('qva-theme', QVA.darkTheme ? 'dark' : 'light');
    });
}

/**
 * Initialize dashboard view
 */
function initializeDashboard() {
    // Initialize system status card
    updateSystemStatusDisplay();
    
    // Add event listeners to dashboard buttons
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            updateSystemStatus();
        });
    }
}

/**
 * Update system status data
 */
function updateSystemStatus(data = null) {
    if (data) {
        // Update with provided data
        QVA.systemStatus = data;
    } else if (!QVA.devMode) {
        // Fetch from API in production mode
        fetch(`${QVA.apiBaseUrl}/system/status`)
            .then(response => response.json())
            .then(data => {
                QVA.systemStatus = data;
                updateSystemStatusDisplay();
            })
            .catch(error => {
                console.error('Error fetching system status:', error);
            });
    } else {
        // Generate mock data in dev mode
        QVA.systemStatus = {
            online: true,
            cpu: Math.floor(Math.random() * 60) + 20, // 20-80%
            memory: Math.floor(Math.random() * 50) + 10, // 10-60%
            quantum: Math.floor(Math.random() * 40) + 50  // 50-90%
        };
    }
    
    // Update the UI
    updateSystemStatusDisplay();
}

/**
 * Update system status UI elements
 */
function updateSystemStatusDisplay() {
    const statusIndicator = document.querySelector('.status-card .status-indicator');
    
    // CPU usage
    const cpuBar = document.querySelector('.status-metric:nth-child(1) .progress');
    const cpuValue = document.querySelector('.status-metric:nth-child(1) .metric-value');
    
    // Memory usage
    const memoryBar = document.querySelector('.status-metric:nth-child(2) .progress');
    const memoryValue = document.querySelector('.status-metric:nth-child(2) .metric-value');
    
    // Quantum usage
    const quantumBar = document.querySelector('.status-metric:nth-child(3) .progress');
    const quantumValue = document.querySelector('.status-metric:nth-child(3) .metric-value');
    
    if (statusIndicator && cpuBar && memoryBar && quantumBar) {
        // Update status indicator
        if (QVA.systemStatus.online) {
            statusIndicator.classList.add('online');
            statusIndicator.classList.remove('offline');
        } else {
            statusIndicator.classList.add('offline');
            statusIndicator.classList.remove('online');
        }
        
        // Update progress bars
        cpuBar.style.width = `${QVA.systemStatus.cpu}%`;
        cpuValue.textContent = `${QVA.systemStatus.cpu}%`;
        
        memoryBar.style.width = `${QVA.systemStatus.memory}%`;
        memoryValue.textContent = `${QVA.systemStatus.memory}%`;
        
        quantumBar.style.width = `${QVA.systemStatus.quantum}%`;
        quantumValue.textContent = `${QVA.systemStatus.quantum}%`;
    }
}

/**
 * Initialize Assistant view
 */
function initializeAssistant() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    
    if (messageInput && sendButton) {
        // Handle send button click
        sendButton.addEventListener('click', () => {
            sendMessage(messageInput.value);
        });
        
        // Handle Enter key press
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage(messageInput.value);
            }
        });
    }
}

/**
 * Send a message to the assistant
 */
function sendMessage(text) {
    if (!text.trim()) return;
    
    const messageInput = document.getElementById('message-input');
    const messagesContainer = document.getElementById('chat-messages');
    
    // Clear input
    messageInput.value = '';
    
    // Add user message to chat
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userMessageHtml = `
        <div class="message user">
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <p>${text}</p>
            </div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;
    
    messagesContainer.innerHTML += userMessageHtml;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // In development mode, simulate response
    if (QVA.devMode) {
        setTimeout(() => {
            const responses = [
                "I'm processing your quantum request...",
                "Let me analyze that with the quantum processor.",
                "Interesting question! Let me check the quantum database.",
                "I've calculated a response using quantum algorithms."
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addAssistantMessage(randomResponse);
        }, 1000);
    } else {
        // In production, send to API
        fetch(`${QVA.apiBaseUrl}/assistant/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(response => response.json())
        .then(data => {
            addAssistantMessage(data.response);
        })
        .catch(error => {
            console.error('Error sending message:', error);
            addAssistantMessage("I'm sorry, I'm having trouble connecting to the quantum processor. Please try again later.");
        });
    }
}

/**
 * Add an assistant message to the chat
 */
function addAssistantMessage(text) {
    const messagesContainer = document.getElementById('chat-messages');
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const assistantMessageHtml = `
        <div class="message system">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>${text}</p>
            </div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;
    
    messagesContainer.innerHTML += assistantMessageHtml;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
