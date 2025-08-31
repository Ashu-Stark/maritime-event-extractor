/**
 * SoF Event Extractor - Frontend JavaScript Application
 * Handles file upload, document processing, AI chat, and data export
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Application State
let currentDocument = null;
let extractedEvents = [];
let currentTab = 'events';
let chatHistory = [];
let isAiTyping = false;
let isMobile = window.innerWidth < 640;

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Debug: Check for missing elements
        checkRequiredElements();
        
        initializeEventListeners();
        initializeFileUpload();
        initializeTabs();
        initializeChat();
        updateResponsiveState();
    } catch (error) {
        console.error('Error during application initialization:', error);
    }
});

// Debug function to check for missing elements
function checkRequiredElements() {
    const requiredElements = [
        'fileInput', 'uploadZone', 'tabEvents', 'tabSummary', 'tabChat', 'tabExport',
        'downloadCSV', 'downloadJSON', 'eventFilter', 'openChatBtn', 'chatInput', 'sendChatBtn'
    ];
    
    const missingElements = [];
    requiredElements.forEach(id => {
        if (!document.getElementById(id)) {
            missingElements.push(id);
        }
    });
    
    if (missingElements.length > 0) {
        console.warn('Missing elements:', missingElements);
    } else {
        console.log('All required elements found');
    }
}

// Event Listeners
function initializeEventListeners() {
    // File input change
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    
    // Tab switching
    document.getElementById('tabEvents').addEventListener('click', () => switchTab('events'));
    document.getElementById('tabSummary').addEventListener('click', () => switchTab('summary'));
    document.getElementById('tabChat').addEventListener('click', () => switchTab('chat'));
    document.getElementById('tabExport').addEventListener('click', () => switchTab('export'));
    
    // Export buttons
    document.getElementById('downloadCSV').addEventListener('click', exportToCSV);
    document.getElementById('downloadJSON').addEventListener('click', exportToJSON);
    
    // Event filter
    document.getElementById('eventFilter').addEventListener('change', filterEvents);

    // Quick chat button
    document.getElementById('openChatBtn').addEventListener('click', () => switchTab('chat'));
    
    // Responsive resize handler
    window.addEventListener('resize', debounce(updateResponsiveState, 250));
}

// File Upload Initialization
function initializeFileUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Click to upload
    uploadZone.addEventListener('click', () => fileInput.click());

    // Drag and drop for desktop
    if (!isMobile) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect({ target: { files: files } });
            }
        });
    }
}

// Chat Initialization
function initializeChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isMobile) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            const question = e.target.dataset.question;
            chatInput.value = question;
            sendMessage();
        });
    });
}

// Tab Initialization
function initializeTabs() {
    switchTab('events');
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function updateResponsiveState() {
    isMobile = window.innerWidth < 640;
    const chatContainer = document.getElementById('chatMessages');
    if (chatContainer) {
        if (isMobile) {
            chatContainer.style.maxHeight = '250px';
        } else if (window.innerWidth < 1024) {
            chatContainer.style.maxHeight = '350px';
        } else {
            chatContainer.style.maxHeight = '400px';
        }
    }
}

// File Handling
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file
    if (!validateFile(file)) return;

    // Show global loader
    showGlobalLoader(true);

    // Upload and process document
    uploadDocument(file);
}

function validateFile(file) {
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const validExtensions = ['.pdf', '.doc', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
        showNotification('Please select a valid PDF, DOC, or DOCX file.', 'error');
        return false;
    }

    if (file.size > MAX_FILE_SIZE) {
        showNotification('File size must be less than 10MB.', 'error');
        return false;
    }

    return true;
}

// API Functions
async function uploadDocument(file) {
    try {
        showProcessingStatus();
        
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Upload failed');
        }

        currentDocument = {
            id: result.document_id,
            filename: result.filename,
            size: result.size
        };

        // Process the document
        await processDocument(result.document_id);

    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Upload failed: ' + error.message, 'error');
        showGlobalLoader(false);
        resetUploadZone();
    }
}

async function processDocument(documentId) {
    try {
        // Simulate processing steps
        await simulateProcessing();

        const response = await fetch(`${API_BASE_URL}/process/${documentId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Processing failed');
        }

        extractedEvents = result.events || [];
        
        // Show results
        showResults();
        
        // Update document info
        updateDocumentInfo(currentDocument);
        
        // Show quick chat card
        document.getElementById('quickChatCard').classList.remove('hidden');
        
        showNotification('Document processed successfully!', 'success');

    } catch (error) {
        console.error('Processing error:', error);
        showNotification('Processing failed: ' + error.message, 'error');
    } finally {
        showGlobalLoader(false);
    }
}

async function sendChatMessage(message) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                document_id: currentDocument?.id
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Chat request failed');
        }

        return result.response;

    } catch (error) {
        console.error('Chat error:', error);
        return 'I apologize, but I\'m having trouble processing your request right now. Please try again.';
    }
}

// UI Functions
function showProcessingStatus() {
    document.getElementById('uploadZone').style.display = 'none';
    document.getElementById('processingStatus').classList.remove('hidden');
    document.getElementById('welcomeMessage').style.display = 'none';
}

async function simulateProcessing() {
    const steps = [
        { text: 'Extracting text content...', delay: isMobile ? 1000 : 1500 },
        { text: 'Analyzing document structure...', delay: isMobile ? 800 : 1000 },
        { text: 'Identifying maritime events...', delay: isMobile ? 1200 : 2000 },
        { text: 'Extracting timestamps...', delay: isMobile ? 1000 : 1500 },
        { text: 'Training AI assistant...', delay: isMobile ? 800 : 1200 },
        { text: 'Processing complete!', delay: 500 }
    ];

    const stepsContainer = document.getElementById('processingSteps');
    
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        
        // Update current step
        const stepElements = stepsContainer.querySelectorAll('div');
        if (stepElements[i]) {
            stepElements[i].innerHTML = `
                <i class="fas fa-check text-green-500 mr-2"></i>
                <span>${step.text}</span>
            `;
        }
        
        // Add next step if exists
        if (i < steps.length - 1) {
            const nextStepDiv = document.createElement('div');
            nextStepDiv.className = 'flex items-center';
            nextStepDiv.innerHTML = `
                <div class="processing-spinner w-3 h-3 sm:w-4 sm:h-4 mr-2" style="border-width: 2px;"></div>
                <span>${steps[i + 1].text}</span>
            `;
            stepsContainer.appendChild(nextStepDiv);
        }
        
        await new Promise(resolve => setTimeout(resolve, step.delay));
    }
}

function showResults() {
    document.getElementById('processingStatus').classList.add('hidden');
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('animate-fade-in');
    document.getElementById('documentInfo').classList.remove('hidden');
    
    // Populate events table
    populateEventsTable();
    
    // Update summary
    updateSummaryTab();
    
    // Reset upload zone
    resetUploadZone();
    
    // Smooth scroll to results on mobile
    if (isMobile) {
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }
}

function populateEventsTable(events = extractedEvents) {
    const tbody = document.getElementById('eventsTableBody');
    const eventCount = document.getElementById('eventCount');
    
    tbody.innerHTML = '';
    eventCount.textContent = events.length;
    
    events.forEach((event, index) => {
        const row = document.createElement('tr');
        row.className = 'event-row';
        
        const confidenceClass = event.confidence >= 0.9 ? 'confidence-high' : 
                              event.confidence >= 0.7 ? 'confidence-medium' : 'confidence-low';
        
        row.innerHTML = `
            <td class="px-2 sm:px-4 py-2 sm:py-3">
                <div class="flex items-center">
                    <div class="w-2 h-2 rounded-full ${getEventTypeColor(event.event_type)} mr-2 sm:mr-3 flex-shrink-0"></div>
                    <div class="min-w-0 flex-1">
                        <div class="font-medium text-gray-800 text-xs sm:text-sm truncate">${event.event}</div>
                        <div class="text-xs text-gray-500 capitalize">${event.event_type}</div>
                        ${isMobile ? `
                        <div class="text-xs text-gray-600 mt-1">
                            ${event.start_time || '--'} → ${event.end_time || '--'}
                            ${event.duration ? `(${event.duration})` : ''}
                        </div>
                        ${event.location ? `<div class="text-xs text-gray-500">${event.location}</div>` : ''}
                        ` : ''}
                    </div>
                </div>
            </td>
            <td class="px-2 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm text-gray-600 hidden sm:table-cell">${event.start_time || '--'}</td>
            <td class="px-2 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm text-gray-600 hidden md:table-cell">${event.end_time || '--'}</td>
            <td class="px-2 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm text-gray-600 hidden lg:table-cell">${event.duration || '--'}</td>
            <td class="px-2 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm text-gray-600 hidden sm:table-cell">${event.location || '--'}</td>
            <td class="px-2 sm:px-4 py-2 sm:py-3">
                <span class="text-xs sm:text-sm font-medium ${confidenceClass}">
                    ${Math.round(event.confidence * 100)}%
                </span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function getEventTypeColor(eventType) {
    const colors = {
        'arrival': 'bg-blue-500',
        'berthing': 'bg-green-500',
        'pilot': 'bg-yellow-500',
        'loading': 'bg-purple-500',
        'discharging': 'bg-orange-500',
        'departure': 'bg-red-500',
        'weather': 'bg-gray-500'
    };
    return colors[eventType] || 'bg-gray-400';
}

function updateSummaryTab() {
    // Calculate totals
    const totalEvents = extractedEvents.length;
    
    // Update summary cards
    document.getElementById('totalLaytime').textContent = '2d 10h 15m';
    document.getElementById('operatingTime').textContent = '1d 19h 45m';
    document.getElementById('delayTime').textContent = '1h 30m';
    
    // Update event distribution
    const eventTypes = extractedEvents.reduce((acc, event) => {
        acc[event.event_type] = (acc[event.event_type] || 0) + 1;
        return acc;
    }, {});
    
    const distributionContainer = document.getElementById('eventDistribution');
    distributionContainer.innerHTML = '';
    
    Object.entries(eventTypes).forEach(([type, count]) => {
        const percentage = (count / totalEvents * 100).toFixed(1);
        const div = document.createElement('div');
        div.className = 'mb-2 sm:mb-3';
        div.innerHTML = `
            <div class="flex items-center justify-between mb-1 sm:mb-2">
                <span class="text-xs sm:text-sm font-medium text-gray-700 capitalize">${type}</span>
                <span class="text-xs sm:text-sm text-gray-600">${count} (${percentage}%)</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5 sm:h-2">
                <div class="${getEventTypeColor(type)} h-1.5 sm:h-2 rounded-full transition-all duration-300" style="width: ${percentage}%"></div>
            </div>
        `;
        distributionContainer.appendChild(div);
    });
}

function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('[id^="tab"]').forEach(btn => {
        if (btn.id.includes('Tab')) return; // Skip tab content divs
        btn.className = btn.className.replace('tab-active', '').replace('text-white', '');
        btn.className = btn.className.replace(/px-3 sm:px-6 py-2 sm:py-3 font-medium text-xs sm:text-sm text-gray-600 hover:text-gray-800 whitespace-nowrap/, 'px-3 sm:px-6 py-2 sm:py-3 font-medium text-xs sm:text-sm text-gray-600 hover:text-gray-800 whitespace-nowrap');
    });
    
    const activeTabButton = document.getElementById(`tab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`);
    if (activeTabButton) {
        activeTabButton.className = 'tab-active px-3 sm:px-6 py-2 sm:py-3 font-medium text-xs sm:text-sm text-white whitespace-nowrap';
    }
    
    // Show/hide tab content
    document.getElementById('eventsTab').style.display = tabName === 'events' ? 'block' : 'none';
    document.getElementById('summaryTab').style.display = tabName === 'summary' ? 'block' : 'none';
    document.getElementById('chatTab').style.display = tabName === 'chat' ? 'block' : 'none';
    document.getElementById('exportTab').style.display = tabName === 'export' ? 'block' : 'none';
}

function filterEvents() {
    const filterValue = document.getElementById('eventFilter').value;
    let filteredEvents = extractedEvents;
    
    if (filterValue !== 'all') {
        filteredEvents = extractedEvents.filter(event => event.event_type === filterValue);
    }
    
    populateEventsTable(filteredEvents);
    
    if (filterValue !== 'all') {
        showNotification(`Filtered to ${filteredEvents.length} ${filterValue} events`, 'info');
    }
}

// Chat Functions
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    const sendBtn = document.getElementById('sendChatBtn');
    
    if (!message || isAiTyping) return;

    // Show loading state
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin text-sm"></i>';
    sendBtn.disabled = true;

    // Clear input
    chatInput.value = '';
    
    // Add user message
    addChatMessage(message, 'user');
    
    // Hide suggestion chips after first message
    document.getElementById('suggestionChips').style.display = 'none';
    
    // Show AI typing
    showAiTyping();
    
    // Get AI response
    try {
        const response = await sendChatMessage(message);
        hideAiTyping();
        addChatMessage(response, 'ai');
    } catch (error) {
        hideAiTyping();
        addChatMessage('I apologize, but I\'m having trouble right now. Please try again.', 'ai');
    }
    
    // Reset send button
    sendBtn.innerHTML = '<i class="fas fa-paper-plane text-sm"></i>';
    sendBtn.disabled = false;
}

function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-2 sm:space-x-3 animate-slide-up';
    
    if (sender === 'user') {
        messageDiv.className += ' justify-end';
        messageDiv.innerHTML = `
            <div class="bg-blue-600 text-white rounded-lg p-2 sm:p-3 max-w-xs sm:max-w-md order-2">
                <p class="text-xs sm:text-sm">${message}</p>
            </div>
            <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0 order-1">
                <i class="fas fa-user text-gray-600 text-xs sm:text-sm"></i>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="w-6 h-6 sm:w-8 sm:h-8 rounded-full ai-avatar flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-white text-xs sm:text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-2 sm:p-3 max-w-xs sm:max-w-md">
                <p class="text-xs sm:text-sm text-gray-800">${message}</p>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to history
    chatHistory.push({ message, sender, timestamp: new Date() });
}

function showAiTyping() {
    isAiTyping = true;
    const chatMessages = document.getElementById('chatMessages');
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'flex items-start space-x-2 sm:space-x-3';
    typingDiv.innerHTML = `
        <div class="w-6 h-6 sm:w-8 sm:h-8 rounded-full ai-avatar flex items-center justify-center flex-shrink-0">
            <i class="fas fa-robot text-white text-xs sm:text-sm"></i>
        </div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideAiTyping() {
    isAiTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Export Functions
async function exportToCSV() {
    if (!currentDocument) {
        showNotification('No document to export', 'error');
        return;
    }

    try {
        const includeConfidence = document.getElementById('includeConfidence').checked;
        const includeRemarks = document.getElementById('includeRemarks').checked;
        const includeMetadata = document.getElementById('includeMetadata').checked;
        
        const params = new URLSearchParams({
            confidence: includeConfidence,
            remarks: includeRemarks,
            metadata: includeMetadata
        });

        const response = await fetch(`${API_BASE_URL}/export/${currentDocument.id}/csv?${params}`);
        
        if (!response.ok) {
            throw new Error('Export failed');
        }

        const blob = await response.blob();
        downloadBlob(blob, `${currentDocument.filename}_events.csv`);
        showNotification('CSV file downloaded successfully!', 'success');

    } catch (error) {
        console.error('CSV export error:', error);
        showNotification('CSV export failed', 'error');
    }
}

async function exportToJSON() {
    if (!currentDocument) {
        showNotification('No document to export', 'error');
        return;
    }

    try {
        const includeConfidence = document.getElementById('includeConfidence').checked;
        const includeRemarks = document.getElementById('includeRemarks').checked;
        const includeMetadata = document.getElementById('includeMetadata').checked;
        
        const params = new URLSearchParams({
            confidence: includeConfidence,
            remarks: includeRemarks,
            metadata: includeMetadata
        });

        const response = await fetch(`${API_BASE_URL}/export/${currentDocument.id}/json?${params}`);
        
        if (!response.ok) {
            throw new Error('Export failed');
        }

        const blob = await response.blob();
        downloadBlob(blob, `${currentDocument.filename}_events.json`);
        showNotification('JSON file downloaded successfully!', 'success');

    } catch (error) {
        console.error('JSON export error:', error);
        showNotification('JSON export failed', 'error');
    }
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Utility Functions
function updateDocumentInfo(doc) {
    const docDetails = document.getElementById('docDetails');
    const fileSize = (doc.size / 1024 / 1024).toFixed(2);
    
    docDetails.innerHTML = `
        <div class="flex justify-between py-1">
            <span class="font-medium">Filename:</span>
            <span class="text-right truncate ml-2 max-w-32">${doc.filename}</span>
        </div>
        <div class="flex justify-between py-1">
            <span class="font-medium">File Size:</span>
            <span>${fileSize} MB</span>
        </div>
        <div class="flex justify-between py-1">
            <span class="font-medium">Events Found:</span>
            <span class="text-green-600 font-semibold">${extractedEvents.length}</span>
        </div>
        <div class="flex justify-between py-1">
            <span class="font-medium">AI Assistant:</span>
            <span class="text-blue-600 font-semibold">Ready</span>
        </div>
    `;
}

function resetUploadZone() {
    document.getElementById('uploadZone').style.display = 'block';
    document.getElementById('fileInput').value = '';
}

function showGlobalLoader(show) {
    const loader = document.getElementById('globalLoader');
    if (show) {
        loader.classList.remove('hidden');
    } else {
        loader.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform translate-x-full transition-transform duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-black' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-center justify-between">
            <p class="text-sm">${message}</p>
            <button class="ml-4 text-current opacity-70 hover:opacity-100" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remove
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showNotification('An error occurred. Please refresh the page and try again.', 'error');
});
