/**
 * SafeSearch Claim Box Module
 * Handles display and interaction of analysis results in the sidebar
 */

class SafeSearchClaimBox {
    constructor(highlighter, summaryModule) {
        this.highlighter = highlighter;
        this.summaryModule = summaryModule;
    }

    /**
     * Display analysis results in the sidebar
     * @param {Object} results - Analysis results from backend
     */
    displayResults(results) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsDiv = document.getElementById('results');

        // Handle JSON format
        const claims = results.claims || results.detailed_analysis;
        const summary = results.summary;

        if (!results || !claims) {
            this.displayError('No analysis results available');
            return;
        }

        // Display summary using the summary module
        if (this.summaryModule && summary) {
            this.summaryModule.displaySummary(summary);
        }

        // Display individual results
        this.displayClaims(claims, resultsDiv);

        resultsContainer.style.display = 'block';
    }

    /**
     * Display individual claims in the results area
     * @param {Array} claims - Array of claim objects
     * @param {Element} resultsDiv - Container element for results
     */
    displayClaims(claims, resultsDiv) {
        resultsDiv.innerHTML = '';
        
        claims.forEach((claim, index) => {
            const claimElement = this.createClaimElement(claim, index);
            resultsDiv.appendChild(claimElement);
        });
    }

    /**
     * Create a single claim element with all interactions
     * @param {Object} claim - Claim data
     * @param {number} index - Claim index
     * @returns {Element} - Claim DOM element
     */
    createClaimElement(claim, index) {
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${claim.verdict}`;
        
        // Handle different field names for claim text
        const claimText = claim.text || claim.claim || 'Analysis claim';
        const confidence = claim.confidence || 'medium';
        const reason = claim.reason || (claim.contradictions && claim.contradictions.length > 0 
            ? claim.contradictions[0].issue 
            : 'Based on ABS data analysis');
        
        // Store the full claim text for highlighting
        const fullClaimText = claimText;
        
        // Build the HTML content
        resultItem.innerHTML = this.buildClaimHTML(claimText, claim.verdict, confidence, reason);
        
        // Add interactions
        this.attachClaimInteractions(resultItem, fullClaimText, claim.verdict);
        
        return resultItem;
    }

    /**
     * Build HTML content for a claim
     * @param {string} claimText - The claim text
     * @param {string} verdict - Verdict type
     * @param {string|number} confidence - Confidence level
     * @param {string} reason - Reason for the verdict
     * @returns {string} - HTML string
     */
    buildClaimHTML(claimText, verdict, confidence, reason) {
        const truncatedText = claimText.length > 200 
            ? claimText.substring(0, 200) + '...'
            : claimText;
            
        const confidenceText = typeof confidence === 'number' 
            ? `${Math.round(confidence * 100)}% confidence`
            : `${confidence} confidence`;

        return `
            <div class="claim-text">"${truncatedText}"</div>
            <div class="verdict ${verdict}">
                ${verdict.toUpperCase()} (${confidenceText})
            </div>
            <div class="reason" style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 8px;">
                ${reason}
            </div>
            <div class="click-hint" style="font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 5px;">
                Click to highlight on page
            </div>
        `;
    }

    /**
     * Attach event listeners to a claim element
     * @param {Element} claimElement - The claim DOM element
     * @param {string} claimText - Full claim text for highlighting
     * @param {string} verdict - Verdict type
     */
    attachClaimInteractions(claimElement, claimText, verdict) {
        // Make clickable
        claimElement.style.cursor = 'pointer';
        
        // Click handler for highlighting
        claimElement.addEventListener('click', () => {
            this.handleClaimClick(claimText, verdict, claimElement);
        });
        
        // Hover effects
        claimElement.addEventListener('mouseenter', () => {
            claimElement.style.background = 'rgba(255, 255, 255, 0.15)';
        });
        
        claimElement.addEventListener('mouseleave', () => {
            claimElement.style.background = 'rgba(255, 255, 255, 0.08)';
        });
    }

    /**
     * Handle claim click - highlight and show clear button
     * @param {string} claimText - Text to highlight
     * @param {string} verdict - Verdict type
     * @param {Element} claimElement - The clicked element
     */
    handleClaimClick(claimText, verdict, claimElement) {
        if (this.highlighter) {
            console.log('Highlighting claim:', claimText);
            this.highlighter.highlightAndNavigateToText(claimText, verdict);
            
            // Show clear highlights button
            const clearButton = document.getElementById('clearHighlights');
            if (clearButton) {
                clearButton.style.display = 'block';
            }
        }
        
        // Visual feedback
        this.animateClickFeedback(claimElement);
    }

    /**
     * Animate click feedback on claim element
     * @param {Element} element - Element to animate
     */
    animateClickFeedback(element) {
        element.style.transform = 'scale(0.98)';
        setTimeout(() => {
            element.style.transform = 'translateX(5px)';
        }, 150);
    }

    /**
     * Display error message
     * @param {string} message - Error message to display
     */
    displayError(message) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsDiv = document.getElementById('results');

        // Use summary module for error display
        if (this.summaryModule) {
            this.summaryModule.displayError(message);
        }
        
        resultsDiv.innerHTML = '';
        resultsContainer.style.display = 'block';
    }

    /**
     * Display timeout message
     */
    displayTimeoutMessage() {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsDiv = document.getElementById('results');

        // Use summary module for timeout message
        if (this.summaryModule) {
            this.summaryModule.displayTimeoutMessage();
        }
        
        resultsDiv.innerHTML = `
            <div class="result-item plausible">
                <div class="claim-text">Analysis may be available in the results folder</div>
                <div class="verdict plausible">CHECK FOLDER</div>
                <div class="reason" style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 8px;">
                    Look for JSON files in /fact_check_results/ directory
                </div>
            </div>
        `;
        
        resultsContainer.style.display = 'block';
    }

    /**
     * Add a new feature/button to a specific claim
     * @param {Element} claimElement - The claim element to enhance
     * @param {Object} feature - Feature configuration
     */
    addFeatureToClaim(claimElement, feature) {
        const featureButton = document.createElement('button');
        featureButton.className = 'claim-feature-button';
        featureButton.textContent = feature.text || 'Feature';
        featureButton.style.cssText = `
            margin-top: 8px;
            padding: 4px 8px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            color: white;
            font-size: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        `;
        
        featureButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Don't trigger claim click
            if (feature.handler) {
                feature.handler(claimElement, feature);
            }
        });
        
        featureButton.addEventListener('mouseenter', () => {
            featureButton.style.background = 'rgba(255, 255, 255, 0.2)';
        });
        
        featureButton.addEventListener('mouseleave', () => {
            featureButton.style.background = 'rgba(255, 255, 255, 0.1)';
        });
        
        claimElement.appendChild(featureButton);
    }
}

// Make available globally
window.SafeSearchClaimBox = SafeSearchClaimBox;
