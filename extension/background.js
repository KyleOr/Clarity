chrome.runtime.onInstalled.addListener(() => {
    console.log('SafeSearch extension installed');
    
    // Set default settings
    chrome.storage.local.set({
        'autoScan': false,
        'highlightSuspicious': true,
        'showNotifications': true
    });
});

chrome.action.onClicked.addListener(async (tab) => {
    try {
        // Send message to content script to toggle sidebar
        await chrome.tabs.sendMessage(tab.id, { action: 'toggleSidebar' });
    } catch (error) {
        console.error('Failed to toggle sidebar:', error);
    }
});

// Handle content extraction and backend communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'analyzeContent') {
        handleContentAnalysis(request.contentData)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ error: error.message }));
        return true; // Will respond asynchronously
    }
});

async function handleContentAnalysis(contentData) {
    try {
        // Send to integration server
        const response = await fetch('http://localhost:8888/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: contentData.url,
                title: contentData.title,
                content: contentData.content,
                timestamp: contentData.timestamp,
                extraction_method: 'browser_extension',
                // Include security indicators from content extraction
                advertisements: contentData.advertisements || [],
                popups: contentData.popups || [],
                externalLinks: contentData.externalLinks || [],
                suspiciousElements: contentData.suspiciousElements || []
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.request_id) {
            // Poll for results
            const analysisResult = await pollForResults(result.request_id);
            return analysisResult;
        } else {
            throw new Error('No request ID received from server');
        }
        
    } catch (error) {
        console.error('Analysis failed:', error);
        // Return mock data if server is unavailable
        return {
            success: false,
            error: error.message,
            mockData: true
        };
    }
}

async function pollForResults(requestId, maxAttempts = 60) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const response = await fetch(`http://localhost:8888/results?id=${requestId}`);
            const result = await response.json();
            
            if (result.status === 'completed') {
                return {
                    success: true,
                    data: result.results,
                    requestId: requestId
                };
            } else if (result.status === 'failed') {
                throw new Error(result.error || 'Analysis failed');
            }
            
            // Wait before next attempt - shorter initial waits, longer later
            const waitTime = attempt <= 10 ? 1000 : 2000;
            await new Promise(resolve => setTimeout(resolve, waitTime));
            
        } catch (error) {
            console.error(`Polling attempt ${attempt} failed:`, error);
            if (attempt === maxAttempts) {
                throw error;
            }
        }
    }
    
    throw new Error('Analysis timed out');
}
