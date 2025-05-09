// Code Assistant UI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    const socket = io();

    // DOM Elements
    const repoForm = document.getElementById('repo-form');
    const repoTypeSelect = document.getElementById('repo-type');
    const localPathContainer = document.getElementById('local-path-container');
    const githubOwnerContainer = document.getElementById('github-owner-container');
    const githubRepoContainer = document.getElementById('github-repo-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const analyzeRepoBtn = document.getElementById('analyze-repo-btn');
    const analysisResults = document.getElementById('analysis-results');
    const findingsCount = document.getElementById('findings-count');
    const findingsList = document.getElementById('findings-list');
    const selectAllBtn = document.getElementById('select-all-btn');
    const createSelectedIssuesBtn = document.getElementById('create-selected-issues-btn');

    // State
    let currentRepository = null;
    let sessionId = null;
    let recentRepositories = JSON.parse(localStorage.getItem('recentRepositories') || '[]');
    let currentFindings = [];

    // Socket.IO event listeners
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        addSystemMessage('Disconnected from server. Please refresh the page.');
    });

    socket.on('repo-connected', (data) => {
        if (data.success) {
            sessionId = data.sessionId;

            // Enable chat and issue forms
            enableForms();

            // Display repository summary
            displayRepositorySummary(data.summary);
        } else {
            addSystemMessage(`Error: ${data.error}`);
        }
    });

    socket.on('chat-thinking', () => {
        // Add thinking message
        addSystemMessage('Thinking...', 'loading-message');
    });

    socket.on('chat-response', (data) => {
        // Remove loading indicator
        document.querySelector('.loading-message')?.remove();

        if (data.success) {
            // Add bot response to chat
            addBotMessage(data.message);
        } else {
            addSystemMessage(`Error: ${data.error}`);
        }
    });

    // Event Listeners
    repoTypeSelect.addEventListener('change', toggleRepoInputs);
    repoForm.addEventListener('submit', handleRepoFormSubmit);
    chatForm.addEventListener('submit', handleChatSubmit);
    analyzeRepoBtn.addEventListener('click', handleAnalyzeRepo);
    selectAllBtn.addEventListener('click', handleSelectAllFindings);
    createSelectedIssuesBtn.addEventListener('click', handleCreateSelectedIssues);

    // Initialize UI
    toggleRepoInputs();
    loadRecentRepositories();

    // Functions
    function toggleRepoInputs() {
        const repoType = repoTypeSelect.value;

        if (repoType === 'local') {
            localPathContainer.classList.remove('hidden');
            githubOwnerContainer.classList.add('hidden');
            githubRepoContainer.classList.add('hidden');
        } else {
            localPathContainer.classList.add('hidden');
            githubOwnerContainer.classList.remove('hidden');
            githubRepoContainer.classList.remove('hidden');
        }
    }

    function loadRecentRepositories() {
        // This would display recent repositories for quick selection
        // Implementation depends on how we store this data
    }

    async function handleRepoFormSubmit(event) {
        event.preventDefault();

        // Clear previous messages
        chatMessages.innerHTML = '';
        addSystemMessage('Connecting to repository...');

        // Get form data
        const repoType = repoTypeSelect.value;
        let repoData = {};

        if (repoType === 'local') {
            const localPath = document.getElementById('local-path').value.trim();
            if (!localPath) {
                addSystemMessage('Error: Please enter a valid repository path');
                return;
            }
            repoData = { type: 'local', path: localPath };
        } else {
            const owner = document.getElementById('github-owner').value.trim();
            const repo = document.getElementById('github-repo').value.trim();
            if (!owner || !repo) {
                addSystemMessage('Error: Please enter both owner and repository name');
                return;
            }
            repoData = { type: 'github', owner, repo };
        }

        try {
            // Store current repository data
            currentRepository = repoData;

            // Add repository to recent list
            addToRecentRepositories(repoData);

            // Connect to repository using Socket.IO
            socket.emit('connect-repo', repoData);
        } catch (error) {
            addSystemMessage(`Error: ${error.message}`);
        }
    }

    async function handleChatSubmit(event) {
        event.preventDefault();

        const message = chatInput.value.trim();
        if (!message || !sessionId) return;

        // Add user message to chat
        addUserMessage(message);

        // Clear input
        chatInput.value = '';

        // Send message using Socket.IO
        socket.emit('chat-message', { sessionId, message });
    }

    // Removed manual issue creation function

    function enableForms() {
        // Enable chat form
        chatInput.disabled = false;
        chatForm.querySelector('button').disabled = false;

        // Enable analyze button
        analyzeRepoBtn.disabled = false;
    }

    function addToRecentRepositories(repoData) {
        // Add to recent repositories list and save to localStorage
        const exists = recentRepositories.findIndex(repo =>
            repo.type === repoData.type &&
            (repo.type === 'local' ? repo.path === repoData.path :
                repo.owner === repoData.owner && repo.repo === repoData.repo)
        );

        if (exists !== -1) {
            recentRepositories.splice(exists, 1);
        }

        recentRepositories.unshift(repoData);

        // Keep only the 5 most recent
        if (recentRepositories.length > 5) {
            recentRepositories = recentRepositories.slice(0, 5);
        }

        localStorage.setItem('recentRepositories', JSON.stringify(recentRepositories));
    }

    function displayRepositorySummary(summary) {
        const summaryElement = document.createElement('div');
        summaryElement.className = 'repo-summary';
        summaryElement.innerHTML = `
            <h3>Repository Summary</h3>
            <p>${summary}</p>
        `;
        chatMessages.appendChild(summaryElement);
    }

    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        messageElement.innerHTML = formatMessage(message);
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addSystemMessage(message, className = '') {
        const messageElement = document.createElement('div');
        messageElement.className = `message system-message ${className}`;

        if (className === 'loading-message') {
            messageElement.innerHTML = `
                ${message}
                <span class="loading ml-2"></span>
            `;
        } else {
            messageElement.textContent = message;
        }

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMessage(message) {
        // Convert markdown-like syntax to HTML
        // This is a simple implementation and could be enhanced
        return message
            .replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    // Repository Analysis Functions
    async function handleAnalyzeRepo() {
        if (!currentRepository || currentRepository.type !== 'github') {
            addSystemMessage('Error: Only GitHub repositories can be analyzed at this time');
            return;
        }

        // Show loading message
        addSystemMessage('Analyzing repository... This may take a few minutes.', 'analysis-loading');

        try {
            // Call the analyze API
            const response = await fetch('/api/repository/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: currentRepository.type,
                    owner: currentRepository.owner,
                    repo: currentRepository.repo
                })
            });

            // Remove loading message
            document.querySelector('.analysis-loading')?.remove();

            const result = await response.json();

            if (result.success) {
                // Store findings
                currentFindings = result.findings || [];

                // Display findings
                displayFindings(currentFindings);
            } else {
                addSystemMessage(`Error analyzing repository: ${result.error}`);
            }
        } catch (error) {
            document.querySelector('.analysis-loading')?.remove();
            addSystemMessage(`Error: ${error.message}`);
        }
    }

    function displayFindings(findings) {
        // Clear previous findings
        findingsList.innerHTML = '';

        // Update count
        findingsCount.textContent = findings.length;

        // Show results section
        analysisResults.classList.remove('hidden');

        // No findings
        if (findings.length === 0) {
            findingsList.innerHTML = '<div class="p-4 text-center text-gray-500">No issues found</div>';
            return;
        }

        // Add each finding
        findings.forEach((finding, index) => {
            const findingElement = document.createElement('div');
            findingElement.className = 'finding-item';

            const priorityClass = `priority-${finding.priority.toLowerCase()}`;

            findingElement.innerHTML = `
                <div class="finding-header">
                    <input type="checkbox" id="finding-${index}" class="finding-checkbox">
                    <div class="finding-title">${finding.title}</div>
                    <span class="finding-priority ${priorityClass}">${finding.priority}</span>
                </div>
                <div class="finding-details">
                    <div>${finding.description}</div>
                    <div class="finding-area">Area: ${finding.area || finding.location || 'Repository-wide'}</div>
                    <div class="finding-suggestion">Suggestion: ${finding.suggestion}</div>
                </div>
            `;

            findingsList.appendChild(findingElement);
        });
    }

    function handleSelectAllFindings() {
        const checkboxes = document.querySelectorAll('.finding-checkbox');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);

        // Toggle all checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.checked = !allChecked;
        });

        // Update button text
        selectAllBtn.textContent = allChecked ? 'Select All' : 'Deselect All';
    }

    async function handleCreateSelectedIssues() {
        const checkboxes = document.querySelectorAll('.finding-checkbox:checked');

        if (checkboxes.length === 0) {
            addSystemMessage('Please select at least one issue to create');
            return;
        }

        // Get selected findings
        const selectedFindings = Array.from(checkboxes).map(checkbox => {
            const index = parseInt(checkbox.id.replace('finding-', ''));
            return currentFindings[index];
        });

        // Show loading message
        addSystemMessage(`Creating ${selectedFindings.length} issues...`, 'issues-loading');

        try {
            // Create issues
            const response = await createIssuesBatch(currentRepository, selectedFindings);

            // Remove loading message
            document.querySelector('.issues-loading')?.remove();

            if (response.success) {
                // Show success message
                const successCount = response.results.filter(r => r.success).length;
                const failCount = response.results.length - successCount;

                let message = `Created ${successCount} issues successfully.`;
                if (failCount > 0) {
                    message += ` ${failCount} issues failed to create.`;
                }

                addSystemMessage(message);

                // Clear checkboxes for created issues
                response.results.forEach((result, index) => {
                    if (result.success) {
                        const findingIndex = currentFindings.findIndex(f => f.title === result.title);
                        if (findingIndex !== -1) {
                            const checkbox = document.getElementById(`finding-${findingIndex}`);
                            if (checkbox) checkbox.checked = false;
                        }
                    }
                });
            } else {
                addSystemMessage(`Error creating issues: ${response.error}`);
            }
        } catch (error) {
            document.querySelector('.issues-loading')?.remove();
            addSystemMessage(`Error: ${error.message}`);
        }
    }

    // API Functions - For issue creation (still using REST API)
    // Socket.IO is used for repository connection and chat

    async function createIssue(repoData, issueData) {
        try {
            const response = await fetch('/api/issues/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repositoryType: repoData.type,
                    owner: repoData.owner,
                    repo: repoData.repo,
                    title: issueData.title,
                    body: issueData.body,
                    labels: issueData.labels
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Error creating issue:', error);
            return {
                success: false,
                error: error.message || 'Failed to create issue'
            };
        }
    }

    async function createIssuesBatch(repoData, issues) {
        try {
            const response = await fetch('/api/issues/create-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repositoryType: repoData.type,
                    owner: repoData.owner,
                    repo: repoData.repo,
                    issues: issues
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Error creating issues:', error);
            return {
                success: false,
                error: error.message || 'Failed to create issues'
            };
        }
    }
});
