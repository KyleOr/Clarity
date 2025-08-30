#!/usr/bin/env python3
"""
Clarity Chatbot Web Server
Provides a REST API for the browser extension to communicate with the AI chatbot
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import generate_chat_response, load_page_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension communication

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Clarity Chatbot API'
    })

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Main chat endpoint for the browser extension"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message in request body',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        analysis_context = data.get('context', None)
        
        logger.info(f"Processing chat request: {user_message[:100]}...")
        
        # Generate response using the AI chatbot
        response = generate_chat_response(user_message, analysis_context)
        
        logger.info(f"Generated response: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """Endpoint for analyzing web content with context"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'error': 'Missing content in request body',
                'status': 'error'
            }), 400
        
        content = data['content']
        question = data.get('question', 'Can you analyze this content for safety and accuracy?')
        
        logger.info(f"Processing analysis request for content length: {len(content)}")
        
        # Create analysis context
        analysis_context = {
            'content': content,
            'url': data.get('url', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate analysis using the AI chatbot
        response = generate_chat_response(question, analysis_context)
        
        return jsonify({
            'analysis': response,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'content_length': len(content)
        })
        
    except Exception as e:
        logger.error(f"Error processing analysis request: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/context/<path:url>', methods=['GET'])
def get_context_endpoint(url):
    """Get context information for a specific URL"""
    try:
        # Decode URL
        from urllib.parse import unquote
        decoded_url = unquote(url)
        
        logger.info(f"Loading context for URL: {decoded_url}")
        
        # Load context data
        context_data = load_page_context(decoded_url)
        
        if context_data:
            return jsonify({
                'context': context_data,
                'status': 'success',
                'url': decoded_url,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'context': None,
                'status': 'not_found',
                'message': 'No context data available for this URL',
                'url': decoded_url,
                'timestamp': datetime.now().isoformat()
            }), 404
        
    except Exception as e:
        logger.error(f"Error loading context: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def status_endpoint():
    """Get chatbot status and model information"""
    try:
        # Import model info function
        from model_processor import get_model_info
        
        model_info = get_model_info()
        
        return jsonify({
            'status': 'active',
            'model_info': model_info,
            'timestamp': datetime.now().isoformat(),
            'api_version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error',
        'available_endpoints': ['/health', '/chat', '/analyze', '/context/<url>', '/status']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Clarity Chatbot Web Server...")
    print("📡 API Endpoints:")
    print("   GET  /health       - Health check")
    print("   POST /chat         - Chat with AI")
    print("   POST /analyze      - Analyze content")
    print("   GET  /context/<url>- Get context for URL")
    print("   GET  /status       - Get chatbot status")
    print()
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔧 CORS enabled for browser extension communication")
    print("⚡ CUDA acceleration enabled")
    print("🧠 Rich context system enabled")
    print()
    
    # Run the Flask development server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,  # Set to True for development
        threaded=True
    )
