"""
Process Single File for Misinformation Detection
Called by integration server to process individual files
"""

import sys
import json
import os

# Ensure UTF-8 encoding for Windows compatibility
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def process_single_file(input_filename):
    """Process a single input file with both misinformation and threat detection"""
    try:
        from misinformation_detector import MisinformationDetector
        from threat_detector import ThreatDetector, process_web_content_file
        
        # Run misinformation detection
        print(f"📊 Running misinformation analysis for {input_filename}...")
        misinformation_detector = MisinformationDetector()
        misinformation_result = misinformation_detector.process_input_file(input_filename)
        
        # Run threat detection on the same file
        print(f"🛡️ Running threat analysis for {input_filename}...")
        threat_detector = ThreatDetector()
        input_file_path = os.path.join('input_pages', input_filename)
        threat_result = process_web_content_file(input_file_path, threat_detector)
        
        # Report results
        success_count = 0
        if misinformation_result:
            print(f"✅ Misinformation analysis: {misinformation_result}")
            success_count += 1
        else:
            print("❌ Misinformation analysis failed")
            
        if threat_result:
            print(f"✅ Threat analysis: {threat_result}")
            success_count += 1
        else:
            print("❌ Threat analysis failed")
        
        # Return success if at least one analysis succeeded
        if success_count > 0:
            print(f"🎯 Analysis complete: {success_count}/2 successful")
            return True
        else:
            print("❌ Both analyses failed")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_single_file.py <input_filename>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    success = process_single_file(input_filename)
    sys.exit(0 if success else 1)
