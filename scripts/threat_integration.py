#!/usr/bin/env python3
"""
Integration server for SafeSearch Extension - Threat Detection
Handles threat detection requests from the browser extension
"""

import json
import os
import sys
import tempfile
import hashlib
from datetime import datetime
from threat_detector import ThreatDetector

def generate_content_id(content: str, url: str = "") -> str:
    """Generate a unique ID for content based on URL and content hash."""
    combined = f"{url}_{content}"
    return hashlib.md5(combined.encode()).hexdigest()[:8]

def process_threat_request(data: dict) -> dict:
    """
    Process a threat detection request from the browser extension.
    
    Args:
        data: Dictionary containing 'content' and optionally 'url', 'title'
    
    Returns:
        Dictionary with threat detection results
    """
    try:
        detector = ThreatDetector()
        
        content = data.get('content', '')
        url = data.get('url', '')
        title = data.get('title', '')
        
        # Combine title and content for analysis
        full_content = f"{title} {content}".strip()
        
        if not full_content:
            return {
                'status': 'error',
                'message': 'No content provided for analysis',
                'threats_detected': [],
                'risk_level': 'safe',
                'threat_count': 0
            }
        
        # Run threat detection
        results = detector.analyze_content(full_content, url)
        
        # Generate content ID
        content_id = generate_content_id(content, url)
        
        # Add metadata
        results['status'] = 'success'
        results['content_id'] = content_id
        results['original_data'] = {
            'title': title,
            'url': url,
            'content_length': len(content)
        }
        
        # Save results for debugging/logging
        try:
            results_file = detector.save_results(results, content_id)
        except Exception as e:
            # Don't fail the entire request if saving fails
            print(f"Warning: Could not save results file: {str(e)}", file=sys.stderr)
        
        return results
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'threats_detected': [],
            'risk_level': 'safe',
            'threat_count': 0
        }

def main():
    """Main function for handling stdin/stdout communication with browser extension."""
    try:
        # Read input from stdin (sent by browser extension)
        input_data = sys.stdin.read()
        
        if not input_data.strip():
            result = {
                'status': 'error',
                'message': 'No input data received'
            }
        else:
            # Parse JSON input
            try:
                data = json.loads(input_data)
                result = process_threat_request(data)
            except json.JSONDecodeError as e:
                result = {
                    'status': 'error',
                    'message': f'Invalid JSON input: {str(e)}'
                }
        
        # Output result as JSON to stdout
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()
