#!/usr/bin/env python3
"""
Context Compiler for Clarity Chatbot
Processes fact-check results, threat detection, and input pages to create
comprehensive context summaries for the AI chatbot.
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

class ContextCompiler:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = base_dir
        
        # Define directories
        self.input_pages_dir = os.path.join(self.base_dir, "input_pages")
        self.fact_check_dir = os.path.join(self.base_dir, "fact_check_results")
        self.threat_detect_dir = os.path.join(self.base_dir, "threat_detect_results")
        self.context_output_dir = os.path.join(self.base_dir, "chatbot", "context_input")
        
        # Create context output directory if it doesn't exist
        os.makedirs(self.context_output_dir, exist_ok=True)

    def load_json_file(self, file_path: str) -> Optional[Dict]:
        """Load and parse a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Error loading {file_path}: {e}")
            return None

    def extract_page_id(self, filename: str) -> str:
        """Extract page ID from filename (e.g., 'web_content_abc123.json' -> 'abc123')"""
        if filename.startswith("web_content_"):
            return filename.replace("web_content_", "").replace(".json", "")
        elif filename.startswith("fact_check_web_content_"):
            return filename.replace("fact_check_web_content_", "").replace(".json", "")
        elif filename.startswith("threat_detect_"):
            return filename.replace("threat_detect_", "").replace(".json", "")
        return filename.replace(".json", "")

    def compile_talking_points(self, page_data: Dict, fact_check: Dict, threat_analysis: Dict) -> Dict:
        """Compile comprehensive talking points from all analysis data"""
        
        page_id = page_data.get('url', 'unknown').split('/')[-1] or 'unknown'
        
        talking_points = {
            "page_info": {
                "url": page_data.get('url', 'Unknown URL'),
                "title": page_data.get('title', 'Unknown Title'),
                "analysis_date": datetime.now().isoformat(),
                "content_length": page_data.get('content_length', len(page_data.get('content', ''))),
                "page_id": page_id
            },
            "credibility_assessment": self._assess_credibility(fact_check),
            "security_assessment": self._assess_security(threat_analysis),
            "key_talking_points": self._generate_talking_points(page_data, fact_check, threat_analysis),
            "educational_opportunities": self._identify_educational_points(fact_check, threat_analysis),
            "actionable_advice": self._generate_actionable_advice(fact_check, threat_analysis),
            "context_summary": self._create_context_summary(page_data, fact_check, threat_analysis)
        }
        
        return talking_points

    def _assess_credibility(self, fact_check: Dict) -> Dict:
        """Assess page credibility from fact-check results"""
        if not fact_check or 'summary' not in fact_check:
            return {"status": "unknown", "details": "No fact-check data available"}
        
        summary = fact_check.get('summary', {})
        total_claims = summary.get('total_claims', 0)
        suspicious_claims = summary.get('suspicious_claims', 0)
        supported_claims = summary.get('supported_claims', 0)
        overall_credibility = summary.get('overall_credibility', 'unknown')
        
        assessment = {
            "overall_rating": overall_credibility,
            "total_claims_analyzed": total_claims,
            "suspicious_claims": suspicious_claims,
            "supported_claims": supported_claims,
            "credibility_percentage": round(((total_claims - suspicious_claims) / max(total_claims, 1)) * 100, 1),
            "key_concerns": []
        }
        
        # Extract key concerns from detailed analysis
        detailed = fact_check.get('detailed_analysis', [])
        for analysis in detailed:
            if analysis.get('verdict') == 'suspicious' or analysis.get('verdict') == 'false':
                concern = {
                    "claim": analysis.get('claim', '')[:200] + "..." if len(analysis.get('claim', '')) > 200 else analysis.get('claim', ''),
                    "category": analysis.get('category', 'general'),
                    "confidence": analysis.get('confidence', 'unknown')
                }
                assessment['key_concerns'].append(concern)
        
        return assessment

    def _assess_security(self, threat_analysis: Dict) -> Dict:
        """Assess security threats from threat detection results"""
        if not threat_analysis or 'summary' not in threat_analysis:
            return {"status": "unknown", "details": "No threat analysis data available"}
        
        summary = threat_analysis.get('summary', {})
        
        assessment = {
            "overall_risk_level": summary.get('overall_risk_level', 'unknown'),
            "total_threats": summary.get('total_threats', 0),
            "high_risk_threats": summary.get('high_risk_threats', 0),
            "medium_risk_threats": summary.get('medium_risk_threats', 0),
            "low_risk_threats": summary.get('low_risk_threats', 0),
            "total_risk_score": summary.get('total_risk_score', 0),
            "threat_types": []
        }
        
        # Extract threat types
        detailed = threat_analysis.get('detailed_analysis', [])
        for threat in detailed:
            threat_info = {
                "type": threat.get('type', 'unknown'),
                "description": threat.get('description', ''),
                "severity": threat.get('severity', 'unknown'),
                "risk_score": threat.get('risk_score', 0),
                "count": threat.get('count', 0)
            }
            assessment['threat_types'].append(threat_info)
        
        return assessment

    def _generate_talking_points(self, page_data: Dict, fact_check: Dict, threat_analysis: Dict) -> List[str]:
        """Generate key talking points for the chatbot"""
        points = []
        
        # Page overview
        if page_data.get('title'):
            points.append(f"📄 This page is titled '{page_data['title']}' from {page_data.get('url', 'unknown source')}")
        
        # Credibility points
        if fact_check and fact_check.get('summary'):
            credibility = fact_check['summary'].get('overall_credibility', 'unknown')
            total_claims = fact_check['summary'].get('total_claims', 0)
            suspicious = fact_check['summary'].get('suspicious_claims', 0)
            
            if credibility == 'high':
                points.append(f"✅ Content credibility is HIGH - {total_claims} claims analyzed with {suspicious} flagged as suspicious")
            elif credibility == 'medium':
                points.append(f"⚠️ Content credibility is MEDIUM - {total_claims} claims analyzed with {suspicious} potentially suspicious")
            elif credibility == 'low':
                points.append(f"❌ Content credibility is LOW - {suspicious} out of {total_claims} claims appear suspicious")
        
        # Security points
        if threat_analysis and threat_analysis.get('summary'):
            risk_level = threat_analysis['summary'].get('overall_risk_level', 'unknown')
            total_threats = threat_analysis['summary'].get('total_threats', 0)
            
            if risk_level == 'high':
                points.append(f"🚨 HIGH SECURITY RISK detected - {total_threats} threats identified")
            elif risk_level == 'medium':
                points.append(f"⚠️ MEDIUM security risk - {total_threats} potential threats found")
            elif risk_level == 'low':
                points.append(f"✅ LOW security risk - {total_threats} minor threats detected")
            else:
                points.append("🔍 Security analysis complete - proceed with normal caution")
        
        return points

    def _identify_educational_points(self, fact_check: Dict, threat_analysis: Dict) -> List[str]:
        """Identify educational opportunities from the analysis"""
        educational_points = []
        
        # Fact-checking education
        if fact_check and fact_check.get('detailed_analysis'):
            categories = set()
            for analysis in fact_check['detailed_analysis']:
                if analysis.get('category'):
                    categories.add(analysis['category'])
            
            if 'housing_affordability' in categories:
                educational_points.append("🏠 Housing market claims detected - I can help explain how to verify property market data using official ABS statistics")
            
            if 'health' in categories:
                educational_points.append("🏥 Health-related claims found - I can guide you to trusted health information sources")
            
            if 'financial' in categories:
                educational_points.append("💰 Financial claims present - I can help you identify reliable financial information sources")
        
        # Security education
        if threat_analysis and threat_analysis.get('detailed_analysis'):
            threat_types = [t.get('type', '') for t in threat_analysis['detailed_analysis']]
            
            if any('phish' in t for t in threat_types):
                educational_points.append("🎣 Phishing indicators detected - I can teach you how to recognize and avoid phishing attempts")
            
            if any('brand_impersonation' in t for t in threat_types):
                educational_points.append("🏢 Brand impersonation detected - I can help you verify legitimate business communications")
            
            if any('crypto' in t for t in threat_types):
                educational_points.append("₿ Cryptocurrency content found - I can explain common crypto scams and safety measures")
        
        return educational_points

    def _generate_actionable_advice(self, fact_check: Dict, threat_analysis: Dict) -> List[str]:
        """Generate specific actionable advice"""
        advice = []
        
        # Credibility-based advice
        if fact_check and fact_check.get('summary'):
            credibility = fact_check['summary'].get('overall_credibility', 'unknown')
            
            if credibility == 'low':
                advice.append("🔍 Cross-reference claims with official sources like ABS, government websites, or established news outlets")
                advice.append("📊 Look for recent, verifiable data when evaluating statistical claims")
            
            suspicious_claims = fact_check['summary'].get('suspicious_claims', 0)
            if suspicious_claims > 0:
                advice.append(f"⚠️ {suspicious_claims} claims flagged as suspicious - verify these through independent sources")
        
        # Security-based advice
        if threat_analysis and threat_analysis.get('summary'):
            risk_level = threat_analysis['summary'].get('overall_risk_level', 'unknown')
            
            if risk_level == 'high':
                advice.append("🛡️ HIGH RISK: Avoid entering personal information or clicking suspicious links")
                advice.append("📱 Consider using this site only for reading, not for transactions or account access")
            
            # Specific threat advice
            recommendations = threat_analysis.get('recommendations', [])
            advice.extend(recommendations[:3])  # Add top 3 recommendations
        
        return advice

    def _create_context_summary(self, page_data: Dict, fact_check: Dict, threat_analysis: Dict) -> str:
        """Create a comprehensive context summary for the AI"""
        summary_parts = []
        
        # Page overview
        url = page_data.get('url', 'Unknown URL')
        title = page_data.get('title', 'Unknown Title')
        summary_parts.append(f"PAGE ANALYSIS: {title} ({url})")
        
        # Credibility summary
        if fact_check and fact_check.get('summary'):
            credibility = fact_check['summary']
            summary_parts.append(f"FACT-CHECK: {credibility.get('overall_credibility', 'unknown').upper()} credibility - {credibility.get('total_claims', 0)} claims analyzed, {credibility.get('suspicious_claims', 0)} suspicious")
        
        # Security summary
        if threat_analysis and threat_analysis.get('summary'):
            security = threat_analysis['summary']
            summary_parts.append(f"SECURITY: {security.get('overall_risk_level', 'unknown').upper()} risk - {security.get('total_threats', 0)} threats detected")
        
        return " | ".join(summary_parts)

    def process_all_pages(self):
        """Process all pages and generate context files"""
        print("🔄 Starting context compilation for all pages...")
        
        # Find all input pages
        input_files = glob.glob(os.path.join(self.input_pages_dir, "web_content_*.json"))
        
        processed_count = 0
        for input_file in input_files:
            page_id = self.extract_page_id(os.path.basename(input_file))
            
            # Load corresponding files
            page_data = self.load_json_file(input_file)
            if not page_data:
                continue
            
            fact_check_file = os.path.join(self.fact_check_dir, f"fact_check_web_content_{page_id}.json")
            threat_detect_file = os.path.join(self.threat_detect_dir, f"threat_detect_{page_id}.json")
            
            fact_check = self.load_json_file(fact_check_file)
            threat_analysis = self.load_json_file(threat_detect_file)
            
            # Generate talking points
            talking_points = self.compile_talking_points(page_data, fact_check or {}, threat_analysis or {})
            
            # Save to context input folder
            output_file = os.path.join(self.context_output_dir, f"context_{page_id}.json")
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(talking_points, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Generated context for {page_id}: {talking_points['page_info']['title']}")
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Error saving context for {page_id}: {e}")
        
        print(f"\n🎉 Context compilation complete! Processed {processed_count} pages.")
        print(f"📁 Context files saved to: {self.context_output_dir}")
        
        # Generate master index
        self.generate_master_index()

    def generate_master_index(self):
        """Generate a master index of all context files"""
        context_files = glob.glob(os.path.join(self.context_output_dir, "context_*.json"))
        
        index = {
            "generated_at": datetime.now().isoformat(),
            "total_contexts": len(context_files),
            "contexts": []
        }
        
        for context_file in context_files:
            context_data = self.load_json_file(context_file)
            if context_data:
                index_entry = {
                    "page_id": context_data['page_info']['page_id'],
                    "url": context_data['page_info']['url'],
                    "title": context_data['page_info']['title'],
                    "credibility": context_data['credibility_assessment']['overall_rating'],
                    "security_risk": context_data['security_assessment']['overall_risk_level'],
                    "context_file": os.path.basename(context_file)
                }
                index['contexts'].append(index_entry)
        
        # Save master index
        index_file = os.path.join(self.context_output_dir, "master_index.json")
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
            print(f"✅ Master index generated: {index_file}")
        except Exception as e:
            print(f"❌ Error generating master index: {e}")

def main():
    print("🤖 Clarity Context Compiler")
    print("=" * 50)
    
    compiler = ContextCompiler()
    compiler.process_all_pages()

if __name__ == "__main__":
    main()
