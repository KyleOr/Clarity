"""
SafeSearch Integration Server
Simple local server to bridge browser extension with Python misinformation detector
"""

import json
import os
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class SafeSearchHandler(BaseHTTPRequestHandler):
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
                result = self.handle_analysis_request(request_data)
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
                self.send_json_response({"status": "online", "service": "SafeSearch API"})
            elif parsed_url.path == '/results':
                # Get specific result by ID
                query_params = parse_qs(parsed_url.query)
                result_id = query_params.get('id', [None])[0]
                
                if result_id:
                    result = self.get_analysis_result(result_id)
                    self.send_json_response(result)
                else:
                    self.send_error_response(400, "Missing result ID")
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error handling GET request: {e}")
            self.send_error_response(500, str(e))
    
    def handle_analysis_request(self, request_data):
        """Process content analysis request"""
        print(f" Analyzing content from: {request_data.get('url', 'Unknown URL')}")
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]
        
        # Create input file
        input_filename = f"web_content_{request_id}.json"
        input_path = os.path.join('input_pages', input_filename)
        
        # Add metadata
        content_data = {
            'url': request_data.get('url', ''),
            'title': request_data.get('title', ''),
            'content': request_data.get('content', ''),
            'timestamp': datetime.now().isoformat(),
            'extraction_method': 'browser_extension',
            'request_id': request_id
        }
        
        # Save input file
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        # Process with misinformation detector (in a separate thread)
        def run_analysis():
            try:
                import subprocess
                import sys
                
                # Use the virtual environment Python executable
                venv_python = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')
                if not os.path.exists(venv_python):
                    # Fallback to current Python if venv not found
                    venv_python = sys.executable
                
                script_path = os.path.join(os.path.dirname(__file__), 'process_single_file.py')
                
                # Set encoding explicitly to handle Unicode characters
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run([
                    venv_python,  # Use virtual environment Python
                    script_path,
                    input_filename
                ], capture_output=True, text=True, encoding='utf-8', 
                   errors='replace', cwd=os.getcwd(), env=env)
                
                if result.returncode == 0:
                    print(f" Analysis complete for request {request_id}")
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                else:
                    print(f" Error in analysis for request {request_id}")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                    
            except Exception as e:
                print(f" Error in analysis for request {request_id}: {e}")
        
        # Run analysis in background
        threading.Thread(target=run_analysis, daemon=True).start()
        
        return {
            'success': True,
            'request_id': request_id,
            'message': 'Analysis started',
            'status_url': f'/results?id={request_id}',
            'estimated_time': '5-10 seconds'
        }
    
    def get_analysis_result(self, request_id):
        """Get analysis result by request ID"""
        # Look for result file
        result_filename = f"fact_check_web_content_{request_id}.json"
        result_path = os.path.join('fact_check_results', result_filename)
        
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            return {
                'success': True,
                'request_id': request_id,
                'status': 'completed',  # Fixed: was 'complete', now matches browser expectation
                'results': result_data  # Fixed: was 'analysis', now matches browser expectation
            }
        else:
            return {
                'success': True,
                'request_id': request_id,
                'status': 'processing',
                'message': 'Analysis still in progress...'
            }
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        response = json.dumps(data, ensure_ascii=False, default=str)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, code, message):
        """Send error response with CORS headers"""
        error_data = {'error': message, 'code': code}
        response = json.dumps(error_data)
        
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def start_server(port=8888):
    """Start the SafeSearch integration server"""
    print(" Starting SafeSearch Integration Server")
    print("="*50)
    
    # Ensure required directories exist
    os.makedirs('input_pages', exist_ok=True)
    os.makedirs('fact_check_results', exist_ok=True)
    
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, SafeSearchHandler)
    
    print(f" Server running at http://localhost:{port}")
    print(" Available endpoints:")
    print("   POST /analyze - Submit content for analysis")
    print("   GET /results?id=<request_id> - Get analysis results")
    print("   GET /status - Check server status")
    print()
    print(" Ready to accept requests from browser extension")
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n Server shutdown requested")
        httpd.server_close()
        print(" Server stopped successfully")

if __name__ == "__main__":
    start_server()
