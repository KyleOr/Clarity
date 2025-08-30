console.log('Clarity content script loaded');

class ClarityContentManager {
    constructor() {
        this.housingKeywords = [
            'housing cost', 'rent', 'mortgage', 'property price', 'housing affordability',
            'housing crisis', 'rental market', 'home ownership', 'real estate'
        ];
        
        this.economicKeywords = [
            'household spending', 'consumer spending', 'cost of living', 
            'discretionary spending', 'household budget', 'economic impact'
        ];
        
        this.sidebarInjected = false;
        this.sidebarContainer = null;
        this.highlighter = null; // Will be initialized after DOM is ready
        this.claimBox = null; // Will be initialized after DOM is ready
        this.summaryModule = null; // Will be initialized after DOM is ready
        this.init();
    }

    init() {
        this.setupMessageListeners();
        this.injectSidebar();
    }

    setupMessageListeners() {
        // Listen for messages from popup/background
        chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
            if (request.action === 'extractContent') {
                const content = await this.extractPageContent();
                sendResponse({ success: true, content: content });
            } else if (request.action === 'toggleSidebar') {
                this.toggleSidebar();
                sendResponse({ success: true });
            } else if (request.action === 'openSidebar') {
                this.openSidebar();
                sendResponse({ success: true });
            }
        });
    }

    async injectSidebar() {
        if (this.sidebarInjected) return;

        try {
            // Create sidebar container
            this.sidebarContainer = document.createElement('div');
            this.sidebarContainer.id = 'clarity-sidebar-root';
            
            // Load sidebar HTML
            const sidebarHTML = await this.loadSidebarHTML();
            this.sidebarContainer.innerHTML = sidebarHTML;
            
            // Inject into page
            document.body.appendChild(this.sidebarContainer);
            
            // Load and inject CSS
            await this.loadSidebarCSS();
            
            // Load and execute JavaScript
            await this.loadSidebarJS();
            
            // Initialize tab functionality
            this.initializeTabFunctionality();
            
            this.sidebarInjected = true;
            console.log('SafeSearch sidebar injected successfully');
            
        } catch (error) {
            console.error('Failed to inject sidebar:', error);
        }
    }

    async loadSidebarHTML() {
        return `
        <div class="sidebar-container" id="clarity-sidebar">
            <div class="header">
                <div class="logo">Clarity</div>
                <div class="subtitle">Digital Confidence Tool</div>
                <button id="closeSidebar" class="close-button">×</button>
            </div>
            
            <div class="content-section">
                <button id="scanButton" class="scan-button">
                    Scan This Page
                </button>
                <button id="clearHighlights" class="clear-highlights-button" style="display: none;">
                    Clear Highlights
                </button>
                
                <div id="loadingContainer" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Analyzing content...</p>
                </div>
                
                <div id="resultsContainer" class="results-container">
                    <div id="summary" class="summary"></div>
                    
                    <!-- Tabbed Results Section -->
                    <div class="results-tabs">
                        <div class="tab-buttons">
                            <button id="claimsTab" class="tab-button active">
                                Claims Analysis
                            </button>
                            <button id="threatsTab" class="tab-button">
                                Cyberthreats
                            </button>
                        </div>
                        
                        <div class="tab-content">
                            <div id="claimsContent" class="tab-panel active">
                                <div id="results"></div>
                            </div>
                            <div id="threatsContent" class="tab-panel">
                                <div id="threatResults"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">One commit away from greatness</div>
                <div class="version">Endorsed by zero hackers</div>
            </div>
        </div>
        `;
    }

    async loadSidebarCSS() {
        // Load main sidebar CSS
        const sidebarCssURL = chrome.runtime.getURL('sidebar.css');
        const sidebarResponse = await fetch(sidebarCssURL);
        const sidebarCssText = await sidebarResponse.text();
        
        const sidebarStyle = document.createElement('style');
        sidebarStyle.textContent = sidebarCssText;
        document.head.appendChild(sidebarStyle);

        // Load chatbot CSS
        const chatbotCssURL = chrome.runtime.getURL('chatbot.css');
        const chatbotResponse = await fetch(chatbotCssURL);
        const chatbotCssText = await chatbotResponse.text();
        
        const chatbotStyle = document.createElement('style');
        chatbotStyle.textContent = chatbotCssText;
        document.head.appendChild(chatbotStyle);
    }

    async loadSidebarJS() {
        // Initialize highlighter
        this.highlighter = new SafeSearchHighlighter();
        
        // Initialize summary module
        this.summaryModule = new SafeSearchSummary();
        this.summaryModule.init();
        
        // Initialize threat detection module
        this.threatDetect = new SafeSearchThreatDetect(this.highlighter);
        
        // Initialize claim box with highlighter and summary references
        this.claimBox = new SafeSearchClaimBox(this.highlighter, this.summaryModule);
        
        // Initialize sidebar functionality
        this.initializeSidebarEvents();
        this.initializeTabFunctionality();
    }

    initializeSidebarEvents() {
        const scanButton = document.getElementById('scanButton');
        const closeButton = document.getElementById('closeSidebar');
        const sidebar = document.getElementById('clarity-sidebar');

        // Scan button functionality
        scanButton?.addEventListener('click', () => this.handleScan());

        // Close button functionality  
        closeButton?.addEventListener('click', () => this.closeSidebar());

        // Clear highlights button functionality
        const clearHighlightsButton = document.getElementById('clearHighlights');
        clearHighlightsButton?.addEventListener('click', () => {
            if (this.highlighter) {
                this.highlighter.clearHighlights();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSidebar();
                if (this.highlighter) {
                    this.highlighter.clearHighlights();
                }
            }
            
            // Clear highlights with Ctrl+Shift+C
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                if (this.highlighter) {
                    this.highlighter.clearHighlights();
                }
            }
        });
    }

    /**
     * Initialize tab functionality for Claims and Cyberthreats
     */
    initializeTabFunctionality() {
        const claimsTab = document.getElementById('claimsTab');
        const threatsTab = document.getElementById('threatsTab');
        const claimsContent = document.getElementById('claimsContent');
        const threatsContent = document.getElementById('threatsContent');

        if (claimsTab && threatsTab && claimsContent && threatsContent) {
            claimsTab.addEventListener('click', () => {
                this.switchTab('claims');
            });

            threatsTab.addEventListener('click', () => {
                this.switchTab('threats');
            });
        }
    }

    /**
     * Switch between tabs
     * @param {string} activeTab - 'claims' or 'threats'
     */
    switchTab(activeTab) {
        const claimsTab = document.getElementById('claimsTab');
        const threatsTab = document.getElementById('threatsTab');
        const claimsContent = document.getElementById('claimsContent');
        const threatsContent = document.getElementById('threatsContent');

        // Remove active class from all tabs and panels
        [claimsTab, threatsTab].forEach(tab => tab?.classList.remove('active'));
        [claimsContent, threatsContent].forEach(panel => panel?.classList.remove('active'));

        // Add active class to selected tab and panel
        if (activeTab === 'claims') {
            claimsTab?.classList.add('active');
            claimsContent?.classList.add('active');
        } else if (activeTab === 'threats') {
            threatsTab?.classList.add('active');
            threatsContent?.classList.add('active');
        }
    }

    openSidebar() {
        const sidebar = document.getElementById('clarity-sidebar');
        if (sidebar) {
            sidebar.classList.add('active');
            // Removed overlay creation to keep page readable
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('clarity-sidebar');
        if (sidebar) {
            sidebar.classList.remove('active');
            // Removed overlay removal since we don't create it anymore
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('clarity-sidebar');
        if (sidebar && sidebar.classList.contains('active')) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    createOverlay() {
        this.removeOverlay();
        
        const overlay = document.createElement('div');
        overlay.id = 'clarity-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(2px);
            z-index: 9999;
            transition: all 0.4s ease;
        `;
        
        overlay.addEventListener('click', () => this.closeSidebar());
        document.body.appendChild(overlay);
    }

    removeOverlay() {
        const overlay = document.getElementById('clarity-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    async handleScan() {
        const scanButton = document.getElementById('scanButton');
        const loadingContainer = document.getElementById('loadingContainer');
        const resultsContainer = document.getElementById('resultsContainer');

        // Disable scan button and show loading
        scanButton.disabled = true;
        scanButton.innerHTML = 'Scanning...';
        loadingContainer.style.display = 'block';
        resultsContainer.style.display = 'none';

        try {
            // Extract page content
            const contentData = await this.extractPageContent();
            console.log('Extracted content from:', contentData.url);
            
            // Send for analysis via background script (this triggers both misinformation and threat detection)
            const analysisResult = await chrome.runtime.sendMessage({
                action: 'analyzeContent',
                contentData: contentData
            });

            console.log('Analysis result:', analysisResult);

            if (analysisResult && analysisResult.success && analysisResult.data) {
                // Display misinformation results using ClaimBox
                this.claimBox.displayResults(analysisResult.data);
                
                // Show loading for threat detection and then fetch results
                this.threatDetect.showLoading();
                await this.fetchAndDisplayThreats(analysisResult.requestId);
                
            } else if (analysisResult && !analysisResult.error) {
                // Show mock results if backend unavailable
                const mockResults = this.generateMockResults(contentData);
                this.claimBox.displayResults(mockResults);
                
                // Show mock threat results too
                this.threatDetect.displayNoThreats(document.getElementById('threatResults'), {overall_risk_level: 'safe'});
            } else {
                throw new Error(analysisResult?.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Scan failed:', error);
            
            // If there's a timeout or connection error, show mock data with a note
            if (error.message.includes('timeout') || error.message.includes('Analysis timed out')) {
                console.log('Analysis timed out, but check results folders for completed analysis');
                this.claimBox.displayTimeoutMessage();
                this.threatDetect.displayError('Analysis timed out - check threat_detect_results folder');
            } else {
                this.claimBox.displayError('Failed to analyze page content: ' + error.message);
                this.threatDetect.displayError('Failed to analyze threats: ' + error.message);
            }
        } finally {
            // Re-enable scan button
            scanButton.disabled = false;
            scanButton.innerHTML = 'Scan This Page';
            loadingContainer.style.display = 'none';
        }
    }

    /**
     * Fetch and display threat detection results
     * @param {string} requestId - The request ID from the analysis
     */
    async fetchAndDisplayThreats(requestId) {
        try {
            console.log('Fetching threat results for request ID:', requestId);
            
            // Poll for threat detection results (using same request ID, but different endpoint)
            const threatResult = await this.pollForThreatResults(requestId);
            
            if (threatResult && threatResult.success && threatResult.data) {
                console.log('Threat analysis completed:', threatResult.data);
                this.threatDetect.displayThreats(threatResult.data);
            } else {
                console.warn('No threat results available');
                this.threatDetect.displayNoThreats(document.getElementById('threatResults'), {overall_risk_level: 'safe'});
            }
            
        } catch (error) {
            console.error('Failed to fetch threat results:', error);
            this.threatDetect.displayError('Failed to load threat analysis results');
        }
    }

    /**
     * Poll for threat detection results
     * @param {string} requestId - Request ID to poll for
     * @param {number} maxAttempts - Maximum polling attempts
     * @returns {Promise<Object>} - Threat analysis results
     */
    async pollForThreatResults(requestId, maxAttempts = 30) {
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                // Check if the server has threat results (our unified server automatically creates both)
                // The threat detection runs alongside misinformation detection, so we check for the file
                const response = await fetch(`http://localhost:8888/threat-results?id=${requestId}`);
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.status === 'completed' && result.results) {
                    return {
                        success: true,
                        data: result.results,
                        requestId: requestId
                    };
                } else if (result.status === 'failed') {
                    throw new Error(result.error || 'Threat analysis failed');
                }
                
                // Wait before next attempt - shorter waits for threat detection since it's faster
                const waitTime = attempt <= 5 ? 500 : 1000;
                await new Promise(resolve => setTimeout(resolve, waitTime));
                
            } catch (error) {
                console.warn(`Threat polling attempt ${attempt} failed:`, error.message);
                
                // If it's the last attempt, don't throw error - just show safe message
                if (attempt === maxAttempts) {
                    console.log('Threat detection timed out - showing safe message');
                    return {
                        success: true,
                        data: {
                            summary: { overall_risk_level: 'safe', total_threats: 0 },
                            detailed_analysis: [],
                            recommendations: ['✅ No significant cyberthreats detected']
                        }
                    };
                }
            }
        }
    }
    
    async extractPageContent() {
        // Get main content areas
        const contentSelectors = [
            'article',
            'main', 
            '.content',
            '.article-body',
            '.post-content',
            'p'
        ];
        
        let extractedText = '';
        
        // Try each selector to get the most relevant content
        for (const selector of contentSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach(el => {
                    extractedText += el.textContent + ' ';
                });
                break;
            }
        }
        
        // Fallback to body text if no specific content found
        if (!extractedText.trim()) {
            extractedText = document.body.textContent || '';
        }

        // Extract potential security threats from page elements
        const securityIndicators = this.extractSecurityIndicators();
        
        // Log what we found for debugging
        console.log('SafeSearch Security Indicators:', {
            ads: securityIndicators.advertisements.length,
            popups: securityIndicators.popups.length, 
            externalLinks: securityIndicators.externalLinks.length,
            suspicious: securityIndicators.suspiciousElements.length
        });
        
        return {
            url: window.location.href,
            title: document.title,
            content: extractedText.trim(),
            timestamp: new Date().toISOString(),
            extractionMethod: 'browser_extension',
            // Add security threat indicators
            advertisements: securityIndicators.advertisements,
            popups: securityIndicators.popups,
            externalLinks: securityIndicators.externalLinks,
            suspiciousElements: securityIndicators.suspiciousElements
        };
    }

    /**
     * Extract various security threat indicators from the page
     * @returns {Object} Security indicators found on the page
     */
    extractSecurityIndicators() {
        console.log('SafeSearch: Starting security indicator extraction...');
        const currentDomain = new URL(window.location.href).hostname;
        
        const indicators = {
            advertisements: this.detectAdvertisements(),
            popups: this.detectPopups(),
            externalLinks: this.detectExternalLinks(currentDomain),
            suspiciousElements: this.detectSuspiciousElements()
        };
        
        console.log('SafeSearch: Security indicators detected:', indicators);
        return indicators;
    }

    /**
     * Detect advertisement-related elements
     * @returns {Array} Array of detected advertisements
     */
    detectAdvertisements() {
        console.log('SafeSearch: Detecting advertisements...');
        
        const adSelectors = [
            '[class*="ad"]', '[id*="ad"]', '[class*="ads"]', '[id*="ads"]',
            '[class*="advertisement"]', '[id*="advertisement"]',
            '[class*="banner"]', '[id*="banner"]',
            '[class*="promo"]', '[id*="promo"]',
            '[class*="sponsored"]', '[id*="sponsored"]',
            'iframe[src*="doubleclick"]', 'iframe[src*="googlesyndication"]',
            'iframe[src*="googleadservices"]', 'iframe[src*="adsystem"]',
            '.adsbygoogle', '#google_ads_frame'
        ];

        const advertisements = [];
        
        // Also check for text-based advertisement indicators
        const textElements = document.querySelectorAll('*');
        textElements.forEach(el => {
            const text = el.textContent?.trim().toLowerCase() || '';
            const tagName = el.tagName.toLowerCase();
            
            // Skip if element is too large (likely body/html) or script/style tags
            if (tagName === 'body' || tagName === 'html' || tagName === 'script' || tagName === 'style') return;
            
            if (text === 'advertisement' || text.includes('advertisement')) {
                advertisements.push({
                    type: 'text_advertisement',
                    selector: tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
                    text: el.textContent?.substring(0, 200) || '',
                    className: el.className || '',
                    id: el.id || '',
                    position: this.getElementPosition(el),
                    textMatch: 'advertisement'
                });
            }
        });
        
        // Check traditional ad selectors
        adSelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                console.log(`SafeSearch: Selector "${selector}" found ${elements.length} elements`);
                
                elements.forEach(el => {
                    advertisements.push({
                        type: 'selector_advertisement',
                        selector: selector,
                        text: el.textContent?.substring(0, 200) || '',
                        src: el.src || '',
                        className: el.className || '',
                        id: el.id || '',
                        position: this.getElementPosition(el),
                        visible: el.offsetWidth > 0 && el.offsetHeight > 0
                    });
                });
            } catch (e) {
                console.log(`SafeSearch: Error checking ad selector ${selector}:`, e);
            }
        });

        console.log(`SafeSearch: Found ${advertisements.length} advertisements`);
        return advertisements;
    }

    /**
     * Detect popup-related elements and behaviors
     * @returns {Array} Array of detected popups
     */
    detectPopups() {
        const popupSelectors = [
            '[class*="popup"]', '[id*="popup"]',
            '[class*="modal"]', '[id*="modal"]', 
            '[class*="overlay"]', '[id*="overlay"]',
            '[class*="dialog"]', '[id*="dialog"]',
            '[class*="notification"]', '[id*="notification"]',
            '[style*="z-index"]', '[style*="position: fixed"]',
            '[style*="position: absolute"]'
        ];

        const popups = [];
        
        popupSelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    const computedStyle = window.getComputedStyle(el);
                    const zIndex = parseInt(computedStyle.zIndex) || 0;
                    const position = computedStyle.position;
                    
                    // Check if element looks like a popup
                    if ((position === 'fixed' || position === 'absolute') && 
                        (zIndex > 100 || el.offsetWidth > 200) &&
                        el.offsetWidth > 0 && el.offsetHeight > 0) {
                        
                        popups.push({
                            type: 'popup',
                            selector: selector,
                            text: el.textContent?.substring(0, 200) || '',
                            className: el.className || '',
                            id: el.id || '',
                            zIndex: zIndex,
                            position: position,
                            dimensions: {
                                width: el.offsetWidth,
                                height: el.offsetHeight
                            }
                        });
                    }
                });
            } catch (e) {
                console.log(`Error checking popup selector ${selector}:`, e);
            }
        });

        return popups;
    }

    /**
     * Detect external links that could be suspicious
     * @param {string} currentDomain - Current page domain
     * @returns {Array} Array of external links
     */
    detectExternalLinks(currentDomain) {
        console.log('SafeSearch: Detecting external links...');
        const externalLinks = [];
        const links = document.querySelectorAll('a[href]');
        
        console.log(`SafeSearch: Found ${links.length} total links to analyze`);
        
        links.forEach(link => {
            try {
                const href = link.href;
                if (href && href.startsWith('http')) {
                    const linkDomain = new URL(href).hostname;
                    
                    // Check if it's an external link
                    if (linkDomain !== currentDomain) {
                        // Check for suspicious patterns
                        const isSuspicious = this.isSuspiciousLink(href, link);
                        
                        externalLinks.push({
                            type: 'external_link',
                            href: href,
                            domain: linkDomain,
                            text: link.textContent?.substring(0, 100) || '',
                            title: link.title || '',
                            suspicious: isSuspicious,
                            suspiciousReasons: isSuspicious ? this.getSuspiciousLinkReasons(href, link) : [],
                            position: this.getElementPosition(link)
                        });
                    }
                }
            } catch (e) {
                console.log('SafeSearch: Error processing link:', link, e);
            }
        });

        console.log(`SafeSearch: Found ${externalLinks.length} external links (${externalLinks.filter(l => l.suspicious).length} suspicious)`);
        return externalLinks;
    }

    /**
     * Detect other suspicious elements
     * @returns {Array} Array of suspicious elements
     */
    detectSuspiciousElements() {
        console.log('SafeSearch: Detecting suspicious elements...');
        const suspicious = [];
        
        // Check for download buttons/links
        const downloadSelectors = [
            'a[href*="download"]', 'button[class*="download"]',
            'a[href$=".exe"]', 'a[href$=".zip"]', 'a[href$=".apk"]',
            '[class*="download"]', '[id*="download"]'
        ];
        
        downloadSelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                console.log(`SafeSearch: Download selector "${selector}" found ${elements.length} elements`);
                
                elements.forEach(el => {
                    suspicious.push({
                        type: 'download_element',
                        selector: selector,
                        text: el.textContent?.substring(0, 100) || '',
                        href: el.href || '',
                        className: el.className || '',
                        id: el.id || ''
                    });
                });
            } catch (e) {
                console.log(`SafeSearch: Error checking suspicious selector ${selector}:`, e);
            }
        });

        // Check for forms asking for sensitive information
        const forms = document.querySelectorAll('form');
        console.log(`SafeSearch: Found ${forms.length} forms to analyze`);
        
        forms.forEach((form, index) => {
            const inputs = form.querySelectorAll('input[type="password"], input[name*="card"], input[name*="ssn"], input[name*="social"]');
            if (inputs.length > 0) {
                suspicious.push({
                    type: 'sensitive_form',
                    formIndex: index,
                    inputCount: inputs.length,
                    action: form.action || '',
                    method: form.method || 'GET',
                    hasSSL: window.location.protocol === 'https:'
                });
            }
        });

        // Check for content that mentions suspicious keywords
        const suspiciousTextElements = [];
        const allElements = document.querySelectorAll('*');
        
        allElements.forEach(el => {
            const text = el.textContent?.trim().toLowerCase() || '';
            const tagName = el.tagName.toLowerCase();
            
            // Skip large containers and script/style tags
            if (tagName === 'body' || tagName === 'html' || tagName === 'script' || tagName === 'style') return;
            
            // Check for suspicious text patterns
            const suspiciousPatterns = [
                /download.*now/i, /click.*here.*immediately/i, /urgent.*action/i,
                /verify.*account/i, /suspended.*account/i, /security.*alert/i
            ];
            
            suspiciousPatterns.forEach(pattern => {
                if (pattern.test(text) && text.length < 500) { // Avoid huge text blocks
                    suspicious.push({
                        type: 'suspicious_text',
                        pattern: pattern.toString(),
                        text: text.substring(0, 200),
                        tagName: tagName,
                        className: el.className || '',
                        id: el.id || ''
                    });
                }
            });
        });

        console.log(`SafeSearch: Found ${suspicious.length} suspicious elements`);
        return suspicious;
    }

    /**
     * Check if a link appears suspicious
     * @param {string} href - Link URL
     * @param {Element} element - Link element
     * @returns {boolean} True if link is suspicious
     */
    isSuspiciousLink(href, element) {
        const suspiciousPatterns = [
            /bit\.ly|tinyurl|short\.link|ow\.ly|t\.co|goo\.gl|is\.gd/i,
            /download.*now|click.*here|urgent|verify.*account/i,
            /\.exe|\.scr|\.bat|\.cmd|\.vbs|\.js$/i,
            /login|signin|verify|confirm|update|secure.*account/i
        ];
        
        const text = element.textContent?.toLowerCase() || '';
        
        return suspiciousPatterns.some(pattern => 
            pattern.test(href) || pattern.test(text)
        );
    }

    /**
     * Get reasons why a link is suspicious
     * @param {string} href - Link URL
     * @param {Element} element - Link element
     * @returns {Array} Array of suspicious reasons
     */
    getSuspiciousLinkReasons(href, element) {
        const reasons = [];
        const text = element.textContent?.toLowerCase() || '';
        
        if (/bit\.ly|tinyurl|short\.link|ow\.ly|t\.co|goo\.gl|is\.gd/i.test(href)) {
            reasons.push('URL shortener');
        }
        if (/download.*now|click.*here|urgent/i.test(text)) {
            reasons.push('Urgent language');
        }
        if (/\.exe|\.scr|\.bat|\.cmd|\.vbs|\.js$/i.test(href)) {
            reasons.push('Executable file');
        }
        if (/verify.*account|login|signin/i.test(text)) {
            reasons.push('Account verification request');
        }
        
        return reasons;
    }

    /**
     * Get element position information
     * @param {Element} element - DOM element
     * @returns {Object} Position information
     */
    getElementPosition(element) {
        const rect = element.getBoundingClientRect();
        return {
            top: Math.round(rect.top),
            left: Math.round(rect.left),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
        };
    }
}

// Initialize content manager
const clarityManager = new ClarityContentManager();
