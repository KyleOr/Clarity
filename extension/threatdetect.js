/**
 * SafeSearch Threat Detection Module (ThreatBox System)
 * Handles cyberthreat analysis and display in the sidebar
 * Similar to ClaimBox but for cyberthreats
 */

class SafeSearchThreatDetect {
    constructor(highlighter) {
        this.highlighter = highlighter;
        this.threatResults = null;
    }

    /**
     * Display threat detection results (main entry point)
     * @param {Object} results - Threat analysis results from backend
     */
    displayThreats(results) {
        const threatContainer = document.getElementById('threatResults');
        if (!threatContainer) {
            console.warn('Threat results container not found');
            return;
        }

        console.log('Displaying threat results:', results);

        // Handle the actual threat detection JSON structure
        const threats = results.detailed_analysis || results.threats_detected || [];
        const summary = results.summary || {};
        const recommendations = results.recommendations || [];
        const securityIndicators = results.security_indicators_summary || null;

        // Clear container and remove loading
        threatContainer.innerHTML = '';
        this.hideLoading();

        // Show summary first if available (includes security indicators count)
        if (summary && (summary.total_threats > 0 || summary.overall_risk_level)) {
            this.displayThreatSummary(summary, threatContainer, securityIndicators);
        }

        // Show recommendations if available
        if (recommendations && recommendations.length > 0) {
            this.displayRecommendations(recommendations, threatContainer);
        }

        // Combine text-based threats and security threats for display
        let allThreatsToDisplay = [...threats];
        
        // Add top security threats if available
        if (securityIndicators && securityIndicators.top_security_threats) {
            allThreatsToDisplay = allThreatsToDisplay.concat(securityIndicators.top_security_threats);
        }

        // Display individual threats or no threats message
        if (!allThreatsToDisplay || allThreatsToDisplay.length === 0) {
            this.displayNoThreats(threatContainer, summary);
            return;
        }

        this.threatResults = results;

        // Display individual threats as clickable boxes (limited to top threats)
        this.displayThreatBoxes(allThreatsToDisplay, threatContainer);
    }

    /**
     * Display threat summary statistics (similar to claim summary)
     * @param {Object} summary - Threat summary data
     * @param {Element} container - Container element
     * @param {Object} securityIndicators - Security indicators summary (optional)
     */
    displayThreatSummary(summary, container, securityIndicators = null) {
        const totalThreats = summary.total_threats || 0;
        const highRisk = summary.high_risk_threats || 0;
        const mediumRisk = summary.medium_risk_threats || 0;
        const lowRisk = summary.low_risk_threats || 0;
        const riskLevel = summary.overall_risk_level || 'safe';

        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'threat-summary-box';
        
        // Build security indicators section if available
        let securityIndicatorsHTML = '';
        if (securityIndicators) {
            const totalAds = securityIndicators.total_advertisements || 0;
            const totalPopups = securityIndicators.total_popups || 0;
            const totalLinks = securityIndicators.total_external_links || 0;
            const totalSuspicious = securityIndicators.total_suspicious_elements || 0;
            const securityRiskLevel = securityIndicators.security_risk_level || 'safe';
            
            securityIndicatorsHTML = `
                <div class="security-indicators-section">
                    <h5>🔍 Security Indicators Detected</h5>
                    <div class="security-stats-grid">
                        <div class="security-stat ${totalAds > 0 ? 'has-count' : ''}">
                            <span class="stat-number">${totalAds}</span>
                            <span class="stat-label">Advertisements</span>
                        </div>
                        <div class="security-stat ${totalPopups > 0 ? 'has-count' : ''}">
                            <span class="stat-number">${totalPopups}</span>
                            <span class="stat-label">Popups</span>
                        </div>
                        <div class="security-stat ${totalLinks > 0 ? 'has-count' : ''}">
                            <span class="stat-number">${totalLinks}</span>
                            <span class="stat-label">External Links</span>
                        </div>
                        <div class="security-stat ${totalSuspicious > 0 ? 'has-count' : ''}">
                            <span class="stat-number">${totalSuspicious}</span>
                            <span class="stat-label">Suspicious Elements</span>
                        </div>
                    </div>
                    <div class="security-note">Showing top 5 highest-risk security threats below</div>
                </div>
            `;
        }
        
        summaryDiv.innerHTML = `
            <div class="summary-header">
                <h4>🛡️ Cyberthreat Analysis</h4>
                <div class="risk-badge ${riskLevel}">${riskLevel.toUpperCase()}</div>
            </div>
            <div class="threat-stats-grid">
                <div class="threat-stat-item">
                    <div class="stat-number">${totalThreats}</div>
                    <div class="stat-label">Content Threats</div>
                </div>
                <div class="threat-stat-item high-risk">
                    <div class="stat-number">${highRisk}</div>
                    <div class="stat-label">High Risk</div>
                </div>
                <div class="threat-stat-item medium-risk">
                    <div class="stat-number">${mediumRisk}</div>
                    <div class="stat-label">Medium Risk</div>
                </div>
                <div class="threat-stat-item low-risk">
                    <div class="stat-number">${lowRisk}</div>
                    <div class="stat-label">Low Risk</div>
                </div>
            </div>
            ${securityIndicatorsHTML}
        `;

        container.appendChild(summaryDiv);
    }

    /**
     * Display recommendations from threat analysis
     * @param {Array} recommendations - Array of recommendation strings
     * @param {Element} container - Container element
     */
    displayRecommendations(recommendations, container) {
        const recDiv = document.createElement('div');
        recDiv.className = 'threat-recommendations';
        
        const recHTML = recommendations.map(rec => 
            `<div class="recommendation-item">${rec}</div>`
        ).join('');

        recDiv.innerHTML = `
            <div class="recommendations-header">
                <h5>🔍 Security Recommendations</h5>
            </div>
            <div class="recommendations-list">
                ${recHTML}
            </div>
        `;

        container.appendChild(recDiv);
    }

    /**
     * Display individual threats as clickable boxes (like claim boxes)
     * @param {Array} threats - Array of threat objects
     * @param {Element} container - Container element
     */
    displayThreatBoxes(threats, container) {
        const threatsDiv = document.createElement('div');
        threatsDiv.className = 'threat-boxes-container';
        
        threats.forEach((threat, index) => {
            const threatBox = this.createThreatBox(threat, index);
            threatsDiv.appendChild(threatBox);
        });

        container.appendChild(threatsDiv);
    }

    /**
     * Create a single threat box (similar to claim box)
     * @param {Object} threat - Threat data
     * @param {number} index - Threat index
     * @returns {Element} - Threat box DOM element
     */
    createThreatBox(threat, index) {
        const threatBox = document.createElement('div');
        threatBox.className = `threat-box ${this.getThreatSeverity(threat)}`;
        
        // Handle both text-based threats and security indicator threats
        if (threat.details) {
            // This is a security indicator threat
            return this.createSecurityIndicatorBox(threat, index);
        } else {
            // This is a text-based threat
            return this.createTextThreatBox(threat, index);
        }
    }
    
    /**
     * Create a text-based threat box
     * @param {Object} threat - Text threat data
     * @param {number} index - Threat index
     * @returns {Element} - Threat box DOM element
     */
    createTextThreatBox(threat, index) {
        const threatBox = document.createElement('div');
        threatBox.className = `threat-box ${this.getThreatSeverity(threat)}`;
        
        // Extract threat data
        const threatType = threat.type || 'unknown';
        const description = threat.description || 'Threat detected';
        const riskScore = threat.risk_score || 1;
        const matches = threat.matches || [];
        const matchCount = threat.count || matches.length || 1;

        // Get the first match text for highlighting - use matched_text for precision
        const highlightText = matches.length > 0 ? (matches[0].matched_text || matches[0].text) : '';
        const truncatedHighlight = highlightText.length > 150 
            ? highlightText.substring(0, 150) + '...'
            : highlightText;

        // Build the threat box HTML
        threatBox.innerHTML = this.buildThreatBoxHTML(
            threatType, description, riskScore, matchCount, truncatedHighlight
        );
        
        // Store the full highlight text for clicking
        threatBox.dataset.highlightText = highlightText;
        threatBox.dataset.threatType = threatType;
        
        // Add interactions
        this.attachThreatBoxInteractions(threatBox, highlightText, threatType);
        
        return threatBox;
    }
    
    /**
     * Create a security indicator threat box
     * @param {Object} threat - Security indicator threat data
     * @param {number} index - Threat index
     * @returns {Element} - Threat box DOM element
     */
    createSecurityIndicatorBox(threat, index) {
        const threatBox = document.createElement('div');
        threatBox.className = `threat-box security-indicator ${this.getThreatSeverity(threat)}`;
        
        // Extract threat data
        const threatType = threat.type || 'unknown';
        const description = threat.description || 'Security indicator detected';
        const riskScore = threat.risk_score || 1;
        const details = threat.details || {};
        
        // Get highlight text based on threat type
        let highlightText = '';
        if (details.text) {
            highlightText = details.text;
        } else if (details.href) {
            highlightText = details.href;
        }
        
        const truncatedHighlight = highlightText.length > 150 
            ? highlightText.substring(0, 150) + '...'
            : highlightText;

        // Build security-specific threat box HTML
        threatBox.innerHTML = this.buildSecurityThreatBoxHTML(
            threatType, description, riskScore, details, truncatedHighlight
        );
        
        // Store data for clicking
        threatBox.dataset.highlightText = highlightText;
        threatBox.dataset.threatType = threatType;
        
        // Add interactions
        this.attachThreatBoxInteractions(threatBox, highlightText, threatType);
        
        return threatBox;
    }
    
    /**
     * Build HTML content for a security indicator threat box
     * @param {string} threatType - Type of threat
     * @param {string} description - Threat description
     * @param {number} riskScore - Risk score
     * @param {Object} details - Threat details
     * @param {string} highlightText - Text to show/highlight
     * @returns {string} - HTML string
     */
    buildSecurityThreatBoxHTML(threatType, description, riskScore, details, highlightText) {
        const severity = this.getThreatSeverityFromScore(riskScore);
        const threatIcon = this.getSecurityThreatIcon(threatType);
        
        let detailsHTML = '';
        
        // Build details based on threat type
        if (threatType === 'advertisement') {
            detailsHTML = `
                <div class="security-details">
                    <div class="detail-item">Type: ${details.className || 'Generic ad'}</div>
                    ${details.visible !== undefined ? `<div class="detail-item">Visible: ${details.visible ? 'Yes' : 'No'}</div>` : ''}
                </div>
            `;
        } else if (threatType === 'external_link') {
            detailsHTML = `
                <div class="security-details">
                    <div class="detail-item">Domain: ${details.href ? new URL(details.href).hostname : 'Unknown'}</div>
                    ${details.suspicious ? `<div class="detail-item suspicious">Suspicious: ${details.suspiciousReasons?.join(', ') || 'Yes'}</div>` : ''}
                </div>
            `;
        } else if (threatType === 'popup') {
            detailsHTML = `
                <div class="security-details">
                    <div class="detail-item">Position: ${details.position || 'Unknown'}</div>
                    ${details.zIndex ? `<div class="detail-item">Z-Index: ${details.zIndex}</div>` : ''}
                </div>
            `;
        }
        
        return `
            <div class="threat-header">
                <div class="threat-icon">${threatIcon}</div>
                <div class="threat-info">
                    <div class="threat-type">${threatType.replace('_', ' ').toUpperCase()}</div>
                    <div class="threat-severity ${severity}">
                        ${severity.toUpperCase()} RISK (Score: ${riskScore})
                    </div>
                </div>
            </div>
            <div class="threat-description">
                ${description}
            </div>
            ${detailsHTML}
            ${highlightText ? `
                <div class="threat-sample">
                    <div class="sample-label">Detected content:</div>
                    <div class="sample-text">"${highlightText}"</div>
                </div>
            ` : ''}
            <div class="threat-actions">
                <div class="click-hint">Click to highlight on page</div>
            </div>
        `;
    }
    
    /**
     * Get icon for security threat type
     * @param {string} threatType - Type of security threat
     * @returns {string} - Emoji icon
     */
    getSecurityThreatIcon(threatType) {
        const icons = {
            'advertisement': '📢',
            'popup': '📱',
            'external_link': '🔗',
            'suspicious_element': '⚠️'
        };
        return icons[threatType] || '🔍';
    }

    /**
     * Build HTML content for a threat box
     * @param {string} threatType - Type of threat
     * @param {string} description - Threat description
     * @param {number} riskScore - Risk score
     * @param {number} matchCount - Number of matches
     * @param {string} highlightText - Text to show/highlight
     * @returns {string} - HTML string
     */
    buildThreatBoxHTML(threatType, description, riskScore, matchCount, highlightText) {
        const severity = this.getThreatSeverityFromScore(riskScore);
        const threatIcon = this.getThreatIcon(threatType);
        
        return `
            <div class="threat-header">
                <div class="threat-icon">${threatIcon}</div>
                <div class="threat-info">
                    <div class="threat-type">${threatType.toUpperCase()}</div>
                    <div class="threat-severity ${severity}">
                        ${severity.toUpperCase()} RISK (Score: ${riskScore})
                    </div>
                </div>
                <div class="threat-count">
                    ${matchCount} match${matchCount !== 1 ? 'es' : ''}
                </div>
            </div>
            <div class="threat-description">
                ${description}
            </div>
            ${highlightText ? `
                <div class="threat-sample">
                    <div class="sample-label">Sample detected:</div>
                    <div class="sample-text">"${highlightText}"</div>
                </div>
            ` : ''}
            <div class="threat-actions">
                <div class="click-hint">Click to highlight suspicious content</div>
            </div>
        `;
    }

    /**
     * Attach event listeners to threat box (similar to claim box interactions)
     * @param {Element} threatBox - The threat box DOM element
     * @param {string} highlightText - Text to highlight when clicked
     * @param {string} threatType - Type of threat
     */
    attachThreatBoxInteractions(threatBox, highlightText, threatType) {
        // Make clickable
        threatBox.style.cursor = 'pointer';
        
        // Click handler for highlighting
        threatBox.addEventListener('click', () => {
            this.handleThreatBoxClick(highlightText, threatType, threatBox);
        });
        
        // Hover effects (similar to claim box)
        threatBox.addEventListener('mouseenter', () => {
            threatBox.style.background = 'rgba(255, 68, 68, 0.15)';
            threatBox.style.transform = 'translateX(3px)';
        });
        
        threatBox.addEventListener('mouseleave', () => {
            threatBox.style.background = 'rgba(255, 255, 255, 0.08)';
            threatBox.style.transform = 'translateX(0)';
        });
    }

    /**
     * Handle threat box click - highlight and show clear button
     * @param {string} highlightText - Text to highlight
     * @param {string} threatType - Type of threat
     * @param {Element} threatBox - The clicked element
     */
    handleThreatBoxClick(highlightText, threatType, threatBox) {
        if (this.highlighter && highlightText) {
            console.log('Highlighting threat content:', highlightText.substring(0, 100) + '...');
            this.highlighter.highlightAndNavigateToText(highlightText, threatType);
            
            // Show clear highlights button
            const clearButton = document.getElementById('clearHighlights');
            if (clearButton) {
                clearButton.style.display = 'block';
            }
        }
        
        // Visual feedback (similar to claim box)
        this.animateClickFeedback(threatBox);
    }

    /**
     * Animate click feedback on threat box
     * @param {Element} element - Element to animate
     */
    animateClickFeedback(element) {
        element.style.transform = 'scale(0.98)';
        setTimeout(() => {
            element.style.transform = 'translateX(5px)';
        }, 150);
    }

    /**
     * Display message when no threats are found
     */
    displayNoThreats(container, summary = {}) {
        const riskLevel = summary.overall_risk_level || 'safe';
        const noThreatsDiv = document.createElement('div');
        noThreatsDiv.className = `no-threats-message ${riskLevel}`;
        
        let message, icon, statusText;
        if (riskLevel === 'safe') {
            icon = '✅';
            statusText = 'ALL CLEAR';
            message = 'No cyberthreats detected on this page.';
        } else {
            icon = '⚠️';
            statusText = 'LOW RISK';
            message = 'Minor security indicators found, but no major threats detected.';
        }

        noThreatsDiv.innerHTML = `
            <div class="no-threats-icon">${icon}</div>
            <div class="no-threats-status">${statusText}</div>
            <div class="no-threats-description">${message}</div>
            <div class="security-tips">
                <div class="tips-header">🔐 Security Tips:</div>
                <div class="tips-list">
                    • Always verify download sources
                    • Be cautious with personal information
                    • Keep your browser updated
                    • Use strong, unique passwords
                </div>
            </div>
        `;

        container.appendChild(noThreatsDiv);
    }

    /**
     * Display error message for threat detection
     * @param {string} errorMessage - Error message to display
     */
    displayError(errorMessage) {
        const threatContainer = document.getElementById('threatResults');
        if (threatContainer) {
            // Hide loading and show error
            this.hideLoading();
            threatContainer.innerHTML = `
                <div class="threat-error">
                    <div class="error-icon">❌</div>
                    <div class="error-message">
                        <strong>Threat Analysis Error</strong>
                        <p>${errorMessage}</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Get threat severity from threat object
     * @param {Object} threat - Threat object
     * @returns {string} - Severity level
     */
    getThreatSeverity(threat) {
        const riskScore = threat.risk_score || 1;
        return this.getThreatSeverityFromScore(riskScore);
    }

    /**
     * Get threat severity from risk score
     * @param {number} riskScore - Risk score
     * @returns {string} - Severity level
     */
    getThreatSeverityFromScore(riskScore) {
        if (riskScore >= 6) return 'high';
        if (riskScore >= 3) return 'medium';
        return 'low';
    }

    /**
     * Get icon for threat type
     * @param {string} threatType - Type of threat
     * @returns {string} - Emoji icon
     */
    getThreatIcon(threatType) {
        const icons = {
            'phishing': '🎣',
            'malware': '🦠',
            'scam': '💰',
            'social_engineering': '🧠',
            'fake_urgency': '⏰',
            'suspicious_links': '🔗',
            'suspicious_domain': '🌐',
            'url_shortener': '📎',
            'suspicious_path': '📂'
        };
        return icons[threatType] || '🛡️';
    }

    /**
     * Get color for risk level
     * @param {string} riskLevel - Risk level (high, medium, low)
     * @returns {string} - Color value
     */
    getRiskColor(riskLevel) {
        const colors = {
            'high': '#ff4444',
            'critical': '#cc0000',
            'medium': '#ffa500',
            'low': '#44ff44',
            'safe': '#44ff44'
        };
        return colors[riskLevel] || colors['medium'];
    }

    /**
     * Get current threat results
     * @returns {Object|null} - Current threat results
     */
    getCurrentThreats() {
        return this.threatResults;
    }

    /**
     * Clear threat results
     */
    clear() {
        const threatContainer = document.getElementById('threatResults');
        if (threatContainer) {
            threatContainer.innerHTML = '';
        }
        this.threatResults = null;
    }

    /**
     * Show loading indicator in cyberthreats tab
     */
    showLoading() {
        const threatContainer = document.getElementById('threatResults');
        if (!threatContainer) return;

        threatContainer.innerHTML = `
            <div class="threat-loading">
                <div class="threat-loading-spinner">
                    <div class="spinner-circle"></div>
                    <div class="spinner-circle"></div>
                    <div class="spinner-circle"></div>
                </div>
                <div class="threat-loading-text">
                    <h4>🛡️ Analyzing Cyberthreats</h4>
                    <p>Scanning for security indicators...</p>
                    <div class="loading-progress">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <div class="loading-steps">
                            <div class="step active">📄 Processing content</div>
                            <div class="step">🔍 Detecting threats</div>
                            <div class="step">📊 Analyzing security</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Animate the loading steps
        this.animateLoadingSteps();
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        // Loading is removed when displayThreats clears the container
        // This method exists for consistency and future use
    }

    /**
     * Animate the loading steps to show progress
     */
    animateLoadingSteps() {
        const steps = document.querySelectorAll('.loading-steps .step');
        const progressFill = document.querySelector('.progress-fill');
        
        if (!steps.length || !progressFill) return;

        let currentStep = 0;
        
        const animateStep = () => {
            // Remove active class from all steps
            steps.forEach(step => step.classList.remove('active'));
            
            // Add active class to current step
            if (currentStep < steps.length) {
                steps[currentStep].classList.add('active');
                
                // Update progress bar
                const progress = ((currentStep + 1) / steps.length) * 100;
                progressFill.style.width = `${progress}%`;
                
                currentStep++;
                
                // Continue to next step
                if (currentStep < steps.length) {
                    setTimeout(animateStep, 1500); // 1.5 seconds per step
                }
            }
        };

        // Start animation
        setTimeout(animateStep, 500);
    }
}

// Make available globally
window.SafeSearchThreatDetect = SafeSearchThreatDetect;
