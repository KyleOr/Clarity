#!/usr/bin/env python3
"""
Clarity Service Launcher
Starts all required services for the Clarity extension:
- Integration Server (for misinformation detection and threat analysis)
- Chatbot Web Server (for AI assistant functionality)
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid

# Import the existing threat detector
try:
    from threat_detector import ThreatDetector
except ImportError:
    print("Error: Could not import threat_detector.py")
    print("Make sure threat_detector.py is in the same directory as this script")
    sys.exit(1)

class UnifiedClarityHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle content analysis requests from browser extension"""
        try:
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/analyze':
                result = self.handle_misinformation_analysis(request_data)
                self.send_json_response(result)
            elif self.path == '/threat-analyze':
                result = self.handle_threat_analysis(request_data)
                self.send_json_response(result)
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self.send_error_response(500, str(e))
    
    def do_GET(self):
        """Handle status and result requests"""
        try:
            parsed_url = urlparse(self.path)
            
            if parsed_url.path == '/status':
                self.send_json_response({
                    "status": "online", 
                    "services": {
                        "misinformation_detection": "active",
                        "threat_detection": "active",
                        "chatbot_server": "active"
                    },
                    "server": "Clarity Unified API"
                })
            elif parsed_url.path == '/results':
                # Get misinformation analysis result by ID
                query_params = parse_qs(parsed_url.query)
                result_id = query_params.get('id', [None])[0]
                
                if result_id:
                    result = self.get_misinformation_result(result_id)
                    self.send_json_response(result)
                else:
                    self.send_error_response(400, "Missing result ID")
            elif parsed_url.path == '/threat-results':
                # Get threat analysis result by ID
                query_params = parse_qs(parsed_url.query)
                result_id = query_params.get('id', [None])[0]
                
                if result_id:
                    result = self.get_threat_result(result_id)
                    try:
                        self.send_json_response(result)
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                        print(f"Connection closed by client during threat result response for ID: {result_id}")
                else:
                    self.send_error_response(400, "Missing result ID")
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error handling GET request: {e}")
            try:
                self.send_error_response(500, str(e))
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as conn_err:
                print(f"Connection closed by client during error response: {conn_err}")
                # Don't try to send another response if connection is broken
    
    def handle_misinformation_analysis(self, request_data):
        """Process misinformation analysis request"""
        print(f"📊 Analyzing content for misinformation from: {request_data.get('url', 'Unknown URL')}")
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]
        
        # Create input file
        input_filename = f"web_content_{request_id}.json"
        input_path = os.path.join('input_pages', input_filename)
        
        # Add metadata and security indicators
        content_data = {
            'url': request_data.get('url', ''),
            'title': request_data.get('title', ''),
            'content': request_data.get('content', ''),
            'timestamp': datetime.now().isoformat(),
            'extraction_method': 'browser_extension',
            'request_id': request_id,
            # Security threat indicators from page analysis
            'security_indicators': {
                'advertisements': request_data.get('advertisements', []),
                'popups': request_data.get('popups', []),
                'external_links': request_data.get('externalLinks', []),
                'suspicious_elements': request_data.get('suspiciousElements', [])
            }
        }
        
        # Save input file
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        # Process with misinformation detector (in a separate thread)
        def run_misinformation_analysis():
            try:
                script_path = os.path.join(os.path.dirname(__file__), 'process_single_file.py')
                
                # Set encoding explicitly to handle Unicode characters
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run([
                    sys.executable,
                    script_path,
                    input_filename
                ], capture_output=True, text=True, encoding='utf-8', 
                   errors='replace', cwd=os.getcwd(), env=env)
                
                if result.returncode == 0:
                    print(f"✅ Misinformation analysis complete for request {request_id}")
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                else:
                    print(f"❌ Error in misinformation analysis for request {request_id}")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                    
            except Exception as e:
                print(f"❌ Error in misinformation analysis for request {request_id}: {e}")
        
        # Run analysis in background
        threading.Thread(target=run_misinformation_analysis, daemon=True).start()
        
        return {
            'success': True,
            'request_id': request_id,
            'message': 'Misinformation analysis started',
            'status_url': f'/results?id={request_id}',
            'estimated_time': '5-10 seconds'
        }
    
    def handle_threat_analysis(self, request_data):
        """Process threat analysis request"""
        print(f"🛡️ Analyzing content for cyberthreats from: {request_data.get('url', 'Unknown URL')}")
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]
        
        # Process with threat detector immediately (faster than misinformation analysis)
        def run_threat_analysis():
            try:
                # Initialize threat detector with default JSON config path
                config_path = os.path.join(os.path.dirname(__file__), '..', 'threatdetect', 'threat_detect.json')
                detector = ThreatDetector(config_path=config_path)
                
                content = request_data.get('content', '')
                url = request_data.get('url', '')
                title = request_data.get('title', '')
                
                # Combine title and content for analysis
                full_content = f"{title} {content}".strip()
                
                if not full_content:
                    result = {
                        'status': 'error',
                        'message': 'No content provided for analysis',
                        'threats_detected': [],
                        'risk_level': 'safe',
                        'threat_count': 0
                    }
                else:
                    # Run threat detection
                    result = detector.analyze_content(full_content, url)
                    result['status'] = 'success'
                
                # Add metadata
                result['content_id'] = request_id
                result['original_data'] = {
                    'title': title,
                    'url': url,
                    'content_length': len(content),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Save results
                try:
                    detector.save_results(result, request_id)
                    print(f"✅ Threat analysis complete for request {request_id} - Risk: {result.get('risk_level', 'unknown')}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not save threat results file: {str(e)}")
                
                # Store result in memory for quick retrieval
                if not hasattr(self.server, 'threat_results'):
                    self.server.threat_results = {}
                self.server.threat_results[request_id] = result
                    
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'message': str(e),
                    'threats_detected': [],
                    'risk_level': 'safe',
                    'threat_count': 0,
                    'content_id': request_id
                }
                if not hasattr(self.server, 'threat_results'):
                    self.server.threat_results = {}
                self.server.threat_results[request_id] = error_result
                print(f"❌ Error in threat analysis for request {request_id}: {e}")
        
        # Run analysis in background
        threading.Thread(target=run_threat_analysis, daemon=True).start()
        
        return {
            'success': True,
            'request_id': request_id,
            'message': 'Threat analysis started',
            'status_url': f'/threat-results?id={request_id}',
            'estimated_time': '1-3 seconds'
        }
    
    def get_misinformation_result(self, request_id):
        """Get misinformation analysis result by request ID"""
        # Look for result file
        result_filename = f"fact_check_web_content_{request_id}.json"
        result_path = os.path.join('fact_check_results', result_filename)
        
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            return {
                'success': True,
                'request_id': request_id,
                'status': 'completed',
                'results': result_data
            }
        else:
            return {
                'success': True,
                'request_id': request_id,
                'status': 'processing',
                'message': 'Misinformation analysis still in progress...'
            }
    
    def get_threat_result(self, request_id):
        """Get threat analysis result by request ID"""
        # First check in-memory results (faster)
        if hasattr(self.server, 'threat_results') and request_id in self.server.threat_results:
            result_data = self.server.threat_results[request_id]
            return {
                'success': True,
                'request_id': request_id,
                'status': 'completed',
                'results': result_data
            }
        
        # Fallback to file system
        result_filename = f"threat_detect_{request_id}.json"
        result_path = os.path.join('threat_detect_results', result_filename)
        
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            return {
                'success': True,
                'request_id': request_id,
                'status': 'completed',
                'results': result_data
            }
        else:
            return {
                'success': True,
                'request_id': request_id,
                'status': 'processing',
                'message': 'Threat analysis still in progress...'
            }
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        response = json.dumps(data, ensure_ascii=False, default=str)
        
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(response.encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
            print(f"Connection closed by client during response: {e}")
            # Client disconnected, don't try to send response
        except Exception as e:
            print(f"Unexpected error sending response: {e}")
    
    def send_error_response(self, code, message):
        """Send error response with CORS headers"""
        error_data = {'error': message, 'code': code}
        response = json.dumps(error_data)
        
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(response.encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
            print(f"Connection closed by client during error response: {e}")
            # Client disconnected, don't try to send error response
        except Exception as e:
            print(f"Unexpected error sending error response: {e}")
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

class ClarityServer(HTTPServer):
    """Extended HTTPServer to store threat results in memory"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threat_results = {}

def start_analysis_server(port=8888):
    """Start the unified analysis server"""
    print("🚀 Starting Clarity Analysis Server")
    print("="*60)
    
    # Ensure required directories exist
    os.makedirs('input_pages', exist_ok=True)
    os.makedirs('fact_check_results', exist_ok=True)
    os.makedirs('threat_detect_results', exist_ok=True)
    
    server_address = ('localhost', port)
    httpd = ClarityServer(server_address, UnifiedClarityHandler)
    
    print(f"🌐 Analysis Server running at http://localhost:{port}")
    print("\n📋 Available endpoints:")
    print("   POST /analyze - Submit content for misinformation analysis")
    print("   POST /threat-analyze - Submit content for threat analysis")
    print("   GET /results?id=<request_id> - Get misinformation analysis results")
    print("   GET /threat-results?id=<request_id> - Get threat analysis results")
    print("   GET /status - Check server status")
    print("\n🔧 Active services:")
    print("   📊 Misinformation Detection - Advanced fact-checking analysis")
    print("   🛡️ Cyberthreat Detection - Real-time security threat analysis")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Analysis server shutdown requested")
        httpd.server_close()
        print("✅ Analysis server stopped successfully")

def start_chatbot_server():
    """Start the chatbot web server"""
    print("🚀 Starting Clarity Chatbot Server")
    print("="*40)
    
    # Change to chatbot directory and run the web server
    chatbot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chatbot')
    web_server_path = os.path.join(chatbot_dir, 'web_server.py')
    
    if not os.path.exists(web_server_path):
        print(f"❌ Chatbot web server not found at: {web_server_path}")
        return
    
    try:
        # Start the Flask web server
        env = os.environ.copy()
        env['PYTHONPATH'] = chatbot_dir
        
        subprocess.run([
            sys.executable,
            web_server_path
        ], cwd=chatbot_dir, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Chatbot server shutdown requested")
    except Exception as e:
        print(f"❌ Error starting chatbot server: {e}")

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_files = [
        'threat_detector.py',
        'process_single_file.py'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    # Check chatbot files
    chatbot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chatbot')
    chatbot_files = ['web_server.py', 'chatbot.py', 'model_processor.py']
    
    for file in chatbot_files:
        file_path = os.path.join(chatbot_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(f"chatbot/{file}")
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all required files are available.")
        return False
    
    print("✅ All dependencies found")
    return True

def main():
    """Main function - start both servers"""
    print("🌟 Clarity Unified Service Launcher")
    print("Integrating misinformation detection, cyberthreat analysis, and AI chatbot")
    print("="*70)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Change to the correct working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Start chatbot server in a separate thread
    chatbot_thread = threading.Thread(target=start_chatbot_server, daemon=True)
    chatbot_thread.start()
    
    # Small delay to let chatbot server start
    time.sleep(2)
    
    print("✅ Ready to accept requests from Clarity browser extension")
    print("Press Ctrl+C to stop all servers")
    print("="*70)
    
    # Start the analysis server (blocks until interrupted)
    try:
        start_analysis_server()
    except Exception as e:
        print(f"❌ Failed to start analysis server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
