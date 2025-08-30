/**
 * SafeSearch Text Highlighter Module
 * Handles highlighting and navigation to claims on web pages
 */

class SafeSearchHighlighter {
    constructor() {
        this.highlightedElements = [];
        this.highlightCounter = 0;
    }

    /**
     * Highlight and navigate to claim text on page
     * @param {string} claimText - The text shown in the sidebar
     * @param {string} verdict - The verdict type for color coding
     */
    highlightAndNavigateToText(claimText, verdict) {
        // Clear previous highlights
        this.clearHighlights();

        // Extract meaningful sentences or phrases
        const searchTargets = this.extractSearchTargets(claimText);
        console.log('Searching for targets:', searchTargets);

        let found = false;
        // Try each search target until we find a match
        for (const target of searchTargets) {
            if (this.findAndHighlightText(target, verdict)) {
                found = true;
                break; // Stop after first successful match
            }
        }
        
        if (found) {
            console.log(`Found matches, scrolling to first one`);
            this.scrollToFirstHighlight();
        } else {
            console.log('No matches found');
            this.showNoMatchesMessage();
        }
    }

    /**
     * Extract search targets from claim text - focus on sentences and key phrases
     * @param {string} claimText - Full text from sidebar
     * @returns {Array} - Array of search targets, ordered by priority
     */
    extractSearchTargets(claimText) {
        const targets = [];
        
        // Clean the text first
        let cleanText = claimText.trim();
        
        // Remove quotes if present
        if (cleanText.startsWith('"') && cleanText.includes('"', 1)) {
            const endQuoteIndex = cleanText.indexOf('"', 1);
            cleanText = cleanText.substring(1, endQuoteIndex);
        }
        
        // Remove trailing ellipsis and quotes
        cleanText = cleanText.replace(/['"…\.]+$/, '').trim();
        
        // Split into sentences (look for . ! ?)
        const sentences = cleanText.split(/[.!?]+/).filter(s => s.trim().length > 10);
        
        // Add individual sentences as targets (highest priority)
        sentences.forEach(sentence => {
            const trimmed = sentence.trim();
            if (trimmed.length > 10) {
                targets.push(trimmed);
            }
        });
        
        // Add meaningful phrases (chunks of 5-8 words)
        const words = cleanText.split(/\s+/).filter(word => word.length > 2);
        if (words.length >= 5) {
            for (let i = 0; i <= words.length - 5; i++) {
                const phrase = words.slice(i, i + 5).join(' ');
                if (phrase.length > 20) {
                    targets.push(phrase);
                }
            }
        }
        
        // Add significant word combinations as last resort
        const significantWords = words.filter(word => word.length > 4);
        if (significantWords.length >= 3) {
            targets.push(significantWords.slice(0, 3).join(' '));
        }
        
        return targets;
    }

    /**
     * Find and highlight text matches
     * @param {string} searchText - Text to search for
     * @param {string} verdict - Verdict type for styling
     * @returns {boolean} - Whether any matches were found
     */
    findAndHighlightText(searchText, verdict) {
        if (!searchText || searchText.length < 10) return false;

        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: (node) => {
                    // Skip sidebar, scripts, styles
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    
                    const tagName = parent.tagName.toLowerCase();
                    if (['script', 'style', 'noscript'].includes(tagName)) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Skip our sidebar
                    if (parent.closest('#safesearch-sidebar-root')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        const textNodes = [];
        let node;
        
        // Collect all text nodes
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        let foundMatches = false;
        
        // Look for matches (case insensitive)
        for (const textNode of textNodes) {
            const text = textNode.textContent;
            const lowerText = text.toLowerCase();
            const lowerSearch = searchText.toLowerCase();
            
            if (lowerText.includes(lowerSearch)) {
                this.highlightTextInNode(textNode, searchText, verdict);
                foundMatches = true;
                break; // Only highlight first match to avoid too many highlights
            }
        }

        return foundMatches;
    }

    /**
     * Highlight text within a text node
     * @param {Node} textNode - The text node to search in
     * @param {string} searchText - Text to highlight
     * @param {string} verdict - Verdict type for styling
     */
    highlightTextInNode(textNode, searchText, verdict) {
        const text = textNode.textContent;
        const parent = textNode.parentElement;
        
        if (!parent) return;
        
        // Create case-insensitive regex for match
        const escapedSearch = this.escapeRegExp(searchText);
        const regex = new RegExp(`(${escapedSearch})`, 'gi');
        
        const matches = text.match(regex);
        if (matches) {
            // Create highlighted version
            const highlightedHTML = text.replace(regex, (match) => {
                this.highlightCounter++;
                const highlightClass = `safesearch-highlight-${verdict}`;
                return `<mark class="${highlightClass}" data-verdict="${verdict}" data-id="${this.highlightCounter}">${match}</mark>`;
            });
            
            // Replace the text node with highlighted content
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = highlightedHTML;
            
            // Move all child nodes to replace the text node
            const fragment = document.createDocumentFragment();
            while (tempDiv.firstChild) {
                if (tempDiv.firstChild.nodeType === Node.ELEMENT_NODE && 
                    tempDiv.firstChild.classList.contains(`safesearch-highlight-${verdict}`)) {
                    this.highlightedElements.push(tempDiv.firstChild);
                }
                fragment.appendChild(tempDiv.firstChild);
            }
            
            parent.replaceChild(fragment, textNode);
        }
    }

    /**
     * Scroll to the first highlighted element
     */
    scrollToFirstHighlight() {
        if (this.highlightedElements.length > 0) {
            const firstHighlight = this.highlightedElements[0];
            
            // Use a slight delay to ensure the highlight is fully rendered
            setTimeout(() => {
                firstHighlight.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center',
                    inline: 'center'
                });
                
                // Add pulse effect to draw attention
                firstHighlight.style.animation = 'safesearch-pulse 3s ease-in-out';
                
                // Remove animation after it completes
                setTimeout(() => {
                    if (firstHighlight.style) {
                        firstHighlight.style.animation = '';
                    }
                }, 3000);
                
            }, 100);
        }
    }

    /**
     * Clear all highlights from the page
     */
    clearHighlights() {
        // Remove all existing highlights
        const existingHighlights = document.querySelectorAll('[class*="safesearch-highlight-"]');
        existingHighlights.forEach(highlight => {
            const parent = highlight.parentNode;
            if (parent) {
                parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
                parent.normalize(); // Merge adjacent text nodes
            }
        });
        
        this.highlightedElements = [];
        this.highlightCounter = 0;
        
        // Hide clear highlights button
        const clearButton = document.getElementById('clearHighlights');
        if (clearButton) {
            clearButton.style.display = 'none';
        }
    }

    /**
     * Escape special regex characters
     * @param {string} string - String to escape
     * @returns {string} - Escaped string
     */
    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Show a brief message when no matches are found
     */
    showNoMatchesMessage() {
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 420px;
            background: rgba(255, 165, 0, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 10001;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = 'No matching text found on this page';
        
        // Add slide-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
            if (style.parentNode) {
                style.remove();
            }
        }, 3000);
    }

    /**
     * Get highlight color configuration
     * @param {string} verdict - Verdict type
     * @returns {object} - Color configuration
     */
    getHighlightColor(verdict) {
        const colors = {
            'suspicious': { bg: 'rgba(255, 68, 68, 0.3)', border: '#ff4444' },
            'supported': { bg: 'rgba(68, 255, 68, 0.3)', border: '#44ff44' },
            'plausible': { bg: 'rgba(255, 255, 255, 0.3)', border: 'rgba(255, 255, 255, 0.6)' },
            'contradicted': { bg: 'rgba(255, 68, 68, 0.4)', border: '#ff4444' },
            'verified': { bg: 'rgba(68, 255, 68, 0.4)', border: '#44ff44' }
        };
        
        return colors[verdict] || colors['plausible'];
    }
}

// Make available globally
window.SafeSearchHighlighter = SafeSearchHighlighter;
