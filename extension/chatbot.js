/**
 * SafeSearch Analysis Summary Module
 * Handles the display and management of analysis summaries
 */

class SafeSearchSummary {
    constructor() {
        this.summaryContainer = null;
        this.currentSummary = null;
    }

    /**
     * Initialize the summary module
     */
    init() {
        this.summaryContainer = document.getElementById('summary');
        if (!this.summaryContainer) {
            console.warn('Summary container not found');
        }
    }

    /**
     * Display chatbot introduction interface
     * @param {Object} summaryData - Summary data from analysis results (for context)
     */
    displaySummary(summaryData) {
        if (!this.summaryContainer) {
            this.init();
            if (!this.summaryContainer) return;
        }

        this.currentSummary = summaryData;
        this.createChatbotIntroduction();
    }

    /**
     * Create the chatbot introduction interface
     */
    createChatbotIntroduction() {
        // Array of introduction messages that will cycle through
        const introMessages = [
            "Hello! I'm Clarity, your digital fact-checking assistant. Would you like to analyze the information on this page?",
            "Hi there! I'm here to help you understand the credibility of claims. Ready to dive into the analysis?",
            "Greetings! I'm your AI companion for sorting fact from fiction. Shall we examine this content together?",
            "Hello! I specialize in analyzing information using official data sources. Want to get started?",
            "Hey! I'm your trusty fact-checking buddy. Ready to explore what's true and what's not?"
        ];

        // Pick a random message from the array
        const randomMessage = introMessages[Math.floor(Math.random() * introMessages.length)];

        this.summaryContainer.innerHTML = `
            <div class="analysis-assistant-container collapsed">
                <div class="assistant-header">
                    <h3>Clarity Insights</h3>
                </div>
                <div class="chatbot-intro">
                    <div class="intro-avatar">
                        🤖
                    </div>
                    <div class="intro-message">
                        ${randomMessage}
                    </div>
                    <button id="startChattingButton" class="start-chat-button">
                        Start Chatting
                    </button>
                </div>
                <div class="chat-interface">
                    <div class="chat-header">
                        <div class="chat-title">
                            <span class="chat-title-icon">🤖</span>
                            Clarity Assistant
                        </div>
                        <button id="minimizeChatButton" class="minimize-chat-button">
                            Minimize
                        </button>
                    </div>
                    <div class="chat-messages" id="chatMessages">
                        <div class="chat-status">
                            💡 Ask me anything about digital safety or this page!
                        </div>
                    </div>
                    <div class="chat-input-area">
                        <textarea 
                            id="chatInput" 
                            class="chat-input" 
                            placeholder="Ask me anything..."
                            rows="1"
                        ></textarea>
                        <button id="sendMessageButton" class="send-button">
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add click event listeners
        this.setupChatEventListeners();
    }

    /**
     * Setup event listeners for the chat interface
     */
    setupChatEventListeners() {
        const startButton = document.getElementById('startChattingButton');
        const minimizeButton = document.getElementById('minimizeChatButton');
        const sendButton = document.getElementById('sendMessageButton');
        const chatInput = document.getElementById('chatInput');
        
        if (startButton) {
            startButton.addEventListener('click', () => {
                this.expandChatInterface();
            });
        }

        if (minimizeButton) {
            minimizeButton.addEventListener('click', () => {
                this.collapseChatInterface();
            });
        }

        if (sendButton && chatInput) {
            sendButton.addEventListener('click', () => {
                this.handleSendMessage();
            });

            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });

            // Auto-resize textarea
            chatInput.addEventListener('input', () => {
                this.autoResizeTextarea(chatInput);
            });
        }
    }

    /**
     * Expand the chat interface
     */
    expandChatInterface() {
        const container = this.summaryContainer.querySelector('.analysis-assistant-container');
        const intro = this.summaryContainer.querySelector('.chatbot-intro');
        const chatInterface = this.summaryContainer.querySelector('.chat-interface');

        if (container && intro && chatInterface) {
            // Add expanding animation
            container.classList.remove('collapsed');
            container.classList.add('expanded');

            // Hide intro with animation
            setTimeout(() => {
                intro.classList.add('hidden');
            }, 200);

            // Show chat interface with delay
            setTimeout(() => {
                chatInterface.classList.add('active');
                // Focus on input
                const chatInput = document.getElementById('chatInput');
                if (chatInput) {
                    chatInput.focus();
                }
            }, 400);

            console.log('Chat interface expanded');
        }
    }

    /**
     * Collapse the chat interface back to introduction
     */
    collapseChatInterface() {
        const container = this.summaryContainer.querySelector('.analysis-assistant-container');
        const intro = this.summaryContainer.querySelector('.chatbot-intro');
        const chatInterface = this.summaryContainer.querySelector('.chat-interface');

        if (container && intro && chatInterface) {
            // Hide chat interface
            chatInterface.classList.remove('active');

            // Show intro after delay
            setTimeout(() => {
                intro.classList.remove('hidden');
            }, 200);

            // Collapse container
            setTimeout(() => {
                container.classList.remove('expanded');
                container.classList.add('collapsed');
            }, 400);

            console.log('Chat interface collapsed');
        }
    }

    /**
     * Handle sending a message to the AI chatbot
     */
    async handleSendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput?.value.trim();
        
        if (message) {
            console.log('User message:', message);
            
            // Add user message to chat
            this.addMessageToChat(message, 'user');
            
            // Clear input
            chatInput.value = '';
            chatInput.style.height = 'auto';
            
            // Show typing indicator
            this.showTypingIndicator();
            
            try {
                // Call the AI chatbot API
                const response = await this.callChatbotAPI(message);
                this.hideTypingIndicator();
                this.addMessageToChat(response, 'bot');
            } catch (error) {
                console.error('Error calling chatbot API:', error);
                this.hideTypingIndicator();
                this.addMessageToChat('Sorry, I encountered an error while processing your message. Please try again.', 'bot');
            }
        }
    }

    /**
     * Call the SafeSearch chatbot API
     */
    async callChatbotAPI(message) {
        const API_BASE = 'http://localhost:5000';
        
        // Gather context from the current page
        const context = {
            url: window.location.href,
            title: document.title,
            content: this.getPageContent(),
            analysisResults: this.getAnalysisResults()
        };

        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: context
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data.response || 'I received your message but had trouble generating a response.';
    }

    /**
     * Get current page content for context
     */
    getPageContent() {
        // Extract meaningful text content from the page
        const textContent = document.body.innerText || document.body.textContent || '';
        // Limit content to prevent API overload (first 2000 characters)
        return textContent.substring(0, 2000);
    }

    /**
     * Get any analysis results that might be available
     */
    getAnalysisResults() {
        // Try to get analysis results from the SafeSearch summary
        try {
            const summaryElement = document.querySelector('.safesearch-summary');
            if (summaryElement) {
                return summaryElement.innerText || null;
            }
        } catch (error) {
            console.log('No analysis results available');
        }
        return null;
    }

    /**
     * Add a message to the chat
     */
    addMessageToChat(message, sender) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message message-${sender}`;
        
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${message}
            </div>
            <div class="message-timestamp">
                ${timestamp}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-status status-typing';
        typingDiv.id = 'typingIndicator';
        typingDiv.textContent = 'Clarity is thinking...';

        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * Auto-resize textarea based on content
     */
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }

    /**
     * Display error summary
     * @param {string} errorMessage - Error message to display
     */
    displayError(errorMessage) {
        if (!this.summaryContainer) {
            this.init();
            if (!this.summaryContainer) return;
        }

        this.summaryContainer.innerHTML = `
            <h3 style="color: #ff4444;">Analysis Error</h3>
            <p>${errorMessage}</p>
        `;
    }

    /**
     * Display timeout/processing message
     */
    displayTimeoutMessage() {
        if (!this.summaryContainer) {
            this.init();
            if (!this.summaryContainer) return;
        }

        this.summaryContainer.innerHTML = `
            <h3 style="color: #ffa500;">Analysis In Progress</h3>
            <p>The analysis may have completed successfully! Check the <code>fact_check_results</code> folder for your analysis file.</p>
            <p style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 10px;">
                The backend processed your content but took longer than expected to return results.
            </p>
        `;
    }

    /**
     * Display loading state
     */
    displayLoading() {
        if (!this.summaryContainer) {
            this.init();
            if (!this.summaryContainer) return;
        }

        this.summaryContainer.innerHTML = `
            <h3>Analyzing Content...</h3>
            <div class="loading-indicator">
                <div class="loading-spinner"></div>
                <p>Processing claims and cross-referencing with ABS data...</p>
            </div>
        `;
    }

    /**
     * Clear the summary display
     */
    clear() {
        if (this.summaryContainer) {
            this.summaryContainer.innerHTML = '';
        }
        this.currentSummary = null;
    }

    /**
     * Get current summary data
     * @returns {Object|null} - Current summary data
     */
    getCurrentSummary() {
        return this.currentSummary;
    }

    /**
     * Update a specific summary statistic
     * @param {string} statType - Type of stat ('totalClaims', 'suspiciousClaims', 'supportedClaims')
     * @param {number} value - New value
     */
    updateStat(statType, value) {
        if (!this.currentSummary) return;

        this.currentSummary[statType] = value;
        
        // Find and update the specific stat element
        const statElement = this.summaryContainer.querySelector(`.summary-stat.${statType} .stat-number`);
        if (statElement) {
            statElement.textContent = value;
            
            // Add update animation
            statElement.style.transform = 'scale(1.1)';
            statElement.style.transition = 'transform 0.2s ease';
            setTimeout(() => {
                statElement.style.transform = 'scale(1)';
            }, 200);
        }
    }

    /**
     * Animate summary stats on first display
     */
    animateStatsIn() {
        const statNumbers = this.summaryContainer.querySelectorAll('.stat-number');
        statNumbers.forEach((stat, index) => {
            stat.style.opacity = '0';
            stat.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                stat.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                stat.style.opacity = '1';
                stat.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * Add interactive hover effects to summary stats
     */
    addInteractivity() {
        const statElements = this.summaryContainer.querySelectorAll('.summary-stat');
        
        statElements.forEach(stat => {
            stat.addEventListener('mouseenter', () => {
                stat.style.transform = 'translateY(-2px)';
                stat.style.boxShadow = '0 4px 15px rgba(255, 255, 255, 0.2)';
            });
            
            stat.addEventListener('mouseleave', () => {
                stat.style.transform = 'translateY(0)';
                stat.style.boxShadow = 'none';
            });
        });
    }

    /**
     * Create expandable details section
     * @param {Object} detailsData - Additional analysis details
     */
    addExpandableDetails(detailsData) {
        if (!this.summaryContainer || !detailsData) return;

        const detailsSection = document.createElement('div');
        detailsSection.className = 'summary-details';
        detailsSection.innerHTML = `
            <button class="details-toggle" type="button">
                <span>Show Details</span>
                <span class="toggle-icon">▼</span>
            </button>
            <div class="details-content" style="display: none;">
                <div class="detail-item">
                    <span class="detail-label">Processing Time:</span>
                    <span class="detail-value">${detailsData.processingTime || 'Unknown'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Sources Checked:</span>
                    <span class="detail-value">${detailsData.sourcesChecked || 0}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Confidence Level:</span>
                    <span class="detail-value">${detailsData.confidenceLevel || 'Medium'}</span>
                </div>
            </div>
        `;

        // Add toggle functionality
        const toggleButton = detailsSection.querySelector('.details-toggle');
        const detailsContent = detailsSection.querySelector('.details-content');
        const toggleIcon = detailsSection.querySelector('.toggle-icon');

        toggleButton.addEventListener('click', () => {
            const isHidden = detailsContent.style.display === 'none';
            detailsContent.style.display = isHidden ? 'block' : 'none';
            toggleIcon.textContent = isHidden ? '▲' : '▼';
            toggleButton.querySelector('span').textContent = isHidden ? 'Hide Details' : 'Show Details';
        });

        this.summaryContainer.appendChild(detailsSection);
    }

    /**
     * Export summary data as JSON
     * @returns {string} - JSON string of current summary
     */
    exportSummary() {
        if (!this.currentSummary) return null;
        
        return JSON.stringify({
            ...this.currentSummary,
            exportTime: new Date().toISOString(),
            pageUrl: window.location.href
        }, null, 2);
    }

    /**
     * Display custom message in summary area
     * @param {string} title - Message title
     * @param {string} message - Message content
     * @param {string} type - Message type ('info', 'warning', 'error', 'success')
     */
    displayCustomMessage(title, message, type = 'info') {
        if (!this.summaryContainer) {
            this.init();
            if (!this.summaryContainer) return;
        }

        const typeColors = {
            info: '#4a9eff',
            warning: '#ffa500',
            error: '#ff4444',
            success: '#44ff44'
        };

        this.summaryContainer.innerHTML = `
            <h3 style="color: ${typeColors[type] || typeColors.info};">${title}</h3>
            <p>${message}</p>
        `;
    }
}

// Make available globally
window.SafeSearchSummary = SafeSearchSummary;
