"""
SafeSearch Misinformation Detector
Fact-checks web content against official ABS housing and spending data
"""

import json
import re
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class MisinformationDetector:
    def __init__(self):
        self.abs_data = self.load_abs_data()
        self.housing_keywords = [
            'housing cost', 'rent', 'mortgage', 'property price', 'housing affordability',
            'housing crisis', 'rental market', 'home ownership', 'housing expense',
            'accommodation cost', 'dwelling cost', 'real estate', 'property market'
        ]
        self.spending_keywords = [
            'household spending', 'consumer spending', 'discretionary spending',
            'non-discretionary', 'household budget', 'living costs', 'cost of living',
            'household expenditure', 'consumer expenditure', 'spending patterns'
        ]
        
    def load_abs_data(self) -> Dict:
        """Load all processed ABS data for fact-checking"""
        data = {}
        
        # Load trimmed data (most reliable)
        try:
            with open('trimmed_data/spending_essentials.json', 'r', encoding='utf-8') as f:
                data['spending_essentials'] = json.load(f)
            
            with open('trimmed_data/covid_impact_focus.json', 'r', encoding='utf-8') as f:
                data['covid_impact'] = json.load(f)
            
            # Load processed data for detailed reference
            with open('processed/household_spending.json', 'r', encoding='utf-8') as f:
                data['household_spending'] = json.load(f)
                
            with open('processed/housing_costs.json', 'r', encoding='utf-8') as f:
                data['housing_costs'] = json.load(f)
                
            with open('processed/cross_dataset_analysis.json', 'r', encoding='utf-8') as f:
                data['cross_analysis'] = json.load(f)
                
        except Exception as e:
            print(f"Warning: Could not load some ABS data files: {e}")
            
        return data
    
    def extract_claims_from_content(self, content: str) -> List[Dict]:
        """Extract potential claims about housing/spending from web content"""
        claims = []
        
        # Common claim patterns
        claim_patterns = [
            # Percentage claims
            r'(?:housing|rent|mortgage|spending).*?(\d+(?:\.\d+)?)(?:%|percent)',
            
            # Increase/decrease claims  
            r'(?:housing|rent|spending).*?(?:increased|decreased|risen|fallen).*?(?:by )?(\d+(?:\.\d+)?)(?:%|percent)',
            
            # Comparison claims
            r'(?:housing|spending).*?(?:higher|lower|more|less).*?than.*?(\d{4}|\w+)',
            
            # COVID impact claims
            r'(?:covid|pandemic).*?(?:housing|spending).*?(?:increased|decreased|affected)',
            
            # Trend claims
            r'(?:housing|spending).*?(?:trend|pattern|trajectory).*?(?:up|down|stable)',
            
            # Affordability claims
            r'housing.*?affordability.*?(?:crisis|problem|improved|worsened)',
            
            # Market claims
            r'(?:rental|housing) market.*?(?:tight|loose|competitive|stable)',
        ]
        
        for pattern in claim_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                claim_text = self._extract_sentence_containing_match(content, match)
                if claim_text:
                    claims.append({
                        'claim': claim_text,
                        'pattern_matched': pattern,
                        'confidence': 'medium',
                        'category': self._categorize_claim(claim_text)
                    })
        
        return claims
    
    def _extract_sentence_containing_match(self, content: str, match) -> str:
        """Extract the full sentence containing a regex match"""
        start = match.start()
        
        # Find sentence boundaries
        sentence_start = content.rfind('.', 0, start) + 1
        sentence_end = content.find('.', match.end())
        
        if sentence_end == -1:
            sentence_end = len(content)
            
        sentence = content[sentence_start:sentence_end].strip()
        return sentence if len(sentence) > 20 else None
    
    def _categorize_claim(self, claim: str) -> str:
        """Categorize the type of claim"""
        claim_lower = claim.lower()
        
        if any(keyword in claim_lower for keyword in ['housing', 'rent', 'mortgage', 'property']):
            if any(word in claim_lower for word in ['cost', 'price', 'afford']):
                return 'housing_affordability'
            return 'housing_general'
        elif any(keyword in claim_lower for keyword in ['spending', 'expenditure', 'budget']):
            if 'discretionary' in claim_lower:
                return 'discretionary_spending'
            elif 'covid' in claim_lower or 'pandemic' in claim_lower:
                return 'covid_spending_impact'
            return 'household_spending'
        
        return 'general_economic'
    
    def fact_check_claim(self, claim: Dict) -> Dict:
        """Fact-check a single claim against ABS data"""
        claim_text = claim['claim']
        category = claim['category']
        
        fact_check_result = {
            'claim': claim_text,
            'category': category,
            'verdict': 'unknown',
            'confidence': 'low',
            'contradictions': [],
            'supporting_evidence': [],
            'abs_data_references': []
        }
        
        # Route to specific fact-checking logic
        if category == 'housing_affordability':
            return self._fact_check_housing_affordability(claim, fact_check_result)
        elif category == 'household_spending':
            return self._fact_check_household_spending(claim, fact_check_result)
        elif category == 'covid_spending_impact':
            return self._fact_check_covid_impact(claim, fact_check_result)
        else:
            return self._fact_check_general_economic(claim, fact_check_result)
    
    def _fact_check_housing_affordability(self, claim: Dict, result: Dict) -> Dict:
        """Fact-check housing affordability claims"""
        claim_text = claim['claim'].lower()
        
        # Extract key ABS housing data
        housing_data = self.abs_data.get('housing_costs', {})
        cross_analysis = self.abs_data.get('cross_analysis', {})
        
        # Check for common housing misinformation patterns
        contradictions = []
        
        # Pattern 1: Extreme percentage claims
        percentages = re.findall(r'(\d+(?:\.\d+)?)(?:%|percent)', claim_text)
        for pct in percentages:
            pct_val = float(pct)
            if pct_val > 80:  # Extremely high percentage claims
                contradictions.append({
                    'type': 'extreme_percentage',
                    'claim_value': f"{pct}%",
                    'issue': f"Claim of {pct}% appears unusually high for typical housing metrics",
                    'context': "ABS housing cost data typically shows proportions of income, not extreme percentages"
                })
        
        # Pattern 2: Timeline inconsistencies
        if 'recent' in claim_text and ('2019' in claim_text or '2020' in claim_text):
            contradictions.append({
                'type': 'timeline_inconsistency',
                'issue': "Claim references 2019-2020 as 'recent' but current date is 2025",
                'context': "ABS housing cost data is from 2019-20 period, pre-COVID impact"
            })
        
        # Pattern 3: COVID impact claims without context
        if 'covid' in claim_text and 'housing' in claim_text:
            if housing_data.get('metadata', {}).get('data_period') == '2019-20':
                contradictions.append({
                    'type': 'data_period_mismatch',
                    'issue': "COVID impact claims cannot be verified with pre-COVID housing data",
                    'context': "Available ABS housing data predates COVID-19 pandemic impact"
                })
        
        result['contradictions'] = contradictions
        result['verdict'] = 'suspicious' if contradictions else 'plausible'
        result['confidence'] = 'medium' if contradictions else 'low'
        
        return result
    
    def _fact_check_household_spending(self, claim: Dict, result: Dict) -> Dict:
        """Fact-check household spending claims using ABS data"""
        claim_text = claim['claim'].lower()
        spending_data = self.abs_data.get('spending_essentials', {})
        
        contradictions = []
        supporting_evidence = []
        
        # Get spending categories overview
        categories = spending_data.get('category_overview', {})
        
        # Pattern 1: Verify spending trend claims
        if any(word in claim_text for word in ['increased', 'decreased', 'risen', 'fallen']):
            # We have 2019-2025 data, so we can check trend directions
            if 'spending' in claim_text and 'decreased' in claim_text and 'covid' not in claim_text:
                # General claim about spending decrease without COVID context might be misleading
                contradictions.append({
                    'type': 'trend_oversimplification',
                    'issue': "Spending trends varied significantly during 2019-2025 period",
                    'context': f"ABS data shows {len(categories)} different spending categories with varying patterns",
                    'abs_reference': "Monthly Household Spending Indicator 2019-2025"
                })
        
        # Pattern 2: Check data availability claims
        if any(word in claim_text for word in ['no data', 'lack of data', 'insufficient data']):
            supporting_evidence.append({
                'type': 'data_availability',
                'evidence': f"ABS provides comprehensive spending data with {spending_data.get('metadata', {}).get('total_series_analyzed', 0)} time series",
                'context': "Monthly Household Spending Indicator provides detailed breakdown"
            })
        
        # Pattern 3: Extreme spending claims
        percentages = re.findall(r'(\d+(?:\.\d+)?)(?:%|percent)', claim_text)
        for pct in percentages:
            pct_val = float(pct)
            if pct_val > 50 and 'spending' in claim_text and 'increase' in claim_text:
                contradictions.append({
                    'type': 'extreme_spending_claim',
                    'claim_value': f"{pct}% increase",
                    'issue': "Household spending rarely increases by such extreme percentages year-over-year",
                    'context': "Typical spending variations are more moderate according to ABS patterns"
                })
        
        result['contradictions'] = contradictions
        result['supporting_evidence'] = supporting_evidence
        result['verdict'] = self._determine_verdict(contradictions, supporting_evidence)
        result['confidence'] = 'high' if (contradictions or supporting_evidence) else 'low'
        
        return result
    
    def _fact_check_covid_impact(self, claim: Dict, result: Dict) -> Dict:
        """Fact-check COVID-19 impact claims"""
        claim_text = claim['claim'].lower()
        covid_data = self.abs_data.get('covid_impact', {})
        
        contradictions = []
        supporting_evidence = []
        
        # Extract expected COVID impacts from our analysis
        expected_impacts = covid_data.get('key_metrics_to_track', {})
        
        # Pattern 1: Discretionary spending claims
        if 'discretionary' in claim_text:
            expected = expected_impacts.get('discretionary_spending', {})
            if 'increased' in claim_text and 'covid' in claim_text:
                contradictions.append({
                    'type': 'covid_impact_contradiction',
                    'issue': "Discretionary spending typically declined during COVID-19",
                    'expected_pattern': expected.get('expected_impact', ''),
                    'abs_reference': "ABS analysis suggests sharp decline in discretionary spending during 2020"
                })
        
        # Pattern 2: Services vs goods claims
        if any(word in claim_text for word in ['services', 'goods']) and 'covid' in claim_text:
            expected = expected_impacts.get('goods_vs_services', {})
            if 'services increased' in claim_text:
                contradictions.append({
                    'type': 'services_pattern_contradiction',
                    'issue': "Services consumption typically decreased during COVID lockdowns",
                    'expected_pattern': expected.get('expected_impact', ''),
                    'context': "Lockdowns shifted consumption from services to goods"
                })
        
        result['contradictions'] = contradictions
        result['supporting_evidence'] = supporting_evidence
        result['verdict'] = self._determine_verdict(contradictions, supporting_evidence)
        result['confidence'] = 'high' if contradictions else 'medium'
        
        return result
    
    def _fact_check_general_economic(self, claim: Dict, result: Dict) -> Dict:
        """General economic fact-checking"""
        claim_text = claim['claim'].lower()
        
        # Basic sanity checks
        contradictions = []
        
        # Check for unrealistic economic claims
        percentages = re.findall(r'(\d+(?:\.\d+)?)(?:%|percent)', claim_text)
        for pct in percentages:
            pct_val = float(pct)
            if pct_val > 100 and any(word in claim_text for word in ['increase', 'decrease', 'change']):
                contradictions.append({
                    'type': 'unrealistic_percentage',
                    'claim_value': f"{pct}%",
                    'issue': "Economic indicators rarely change by more than 100% in normal circumstances"
                })
        
        result['contradictions'] = contradictions
        result['verdict'] = 'suspicious' if contradictions else 'plausible'
        result['confidence'] = 'medium' if contradictions else 'low'
        
        return result
    
    def _determine_verdict(self, contradictions: List, supporting_evidence: List) -> str:
        """Determine overall verdict based on contradictions and evidence"""
        if contradictions and not supporting_evidence:
            return 'suspicious'
        elif supporting_evidence and not contradictions:
            return 'supported'
        elif contradictions and supporting_evidence:
            return 'mixed'
        else:
            return 'plausible'
    
    def analyze_webpage_content(self, content: str, url: str = "") -> Dict:
        """Main function to analyze webpage content for misinformation"""
        print(f"Analyzing content from: {url}")
        
        # Extract claims
        claims = self.extract_claims_from_content(content)
        print(f"Found {len(claims)} potential claims")
        
        # Fact-check each claim
        fact_checked_claims = []
        for claim in claims:
            fact_check_result = self.fact_check_claim(claim)
            fact_checked_claims.append(fact_check_result)
        
        # Generate summary
        suspicious_claims = [c for c in fact_checked_claims if c['verdict'] == 'suspicious']
        supported_claims = [c for c in fact_checked_claims if c['verdict'] == 'supported']
        
        analysis_result = {
            'metadata': {
                'url': url,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content_length': len(content),
                'claims_analyzed': len(claims)
            },
            'summary': {
                'total_claims': len(fact_checked_claims),
                'suspicious_claims': len(suspicious_claims),
                'supported_claims': len(supported_claims),
                'overall_credibility': 'high' if len(suspicious_claims) == 0 else 'medium' if len(suspicious_claims) < 2 else 'low'
            },
            'detailed_analysis': fact_checked_claims,
            'recommendations': self._generate_recommendations(fact_checked_claims)
        }
        
        return analysis_result
    
    def _generate_recommendations(self, fact_checked_claims: List) -> List[str]:
        """Generate recommendations based on fact-check results"""
        recommendations = []
        
        suspicious_count = len([c for c in fact_checked_claims if c['verdict'] == 'suspicious'])
        
        if suspicious_count > 2:
            recommendations.append("⚠️ High number of suspicious claims detected - exercise caution with this content")
        elif suspicious_count > 0:
            recommendations.append("⚠️ Some claims appear suspicious - verify with official sources")
        
        covid_claims = [c for c in fact_checked_claims if c['category'] == 'covid_spending_impact']
        if covid_claims:
            recommendations.append("📊 COVID-19 economic claims detected - check against latest ABS data")
        
        housing_claims = [c for c in fact_checked_claims if 'housing' in c['category']]
        if housing_claims:
            recommendations.append("🏠 Housing claims detected - verify with current ABS housing cost data")
        
        if not recommendations:
            recommendations.append("✅ No major red flags detected in economic claims")
        
        return recommendations
    
    def process_input_file(self, input_filename: str) -> str:
        """Process a single input file and save results"""
        input_path = os.path.join('input_pages', input_filename)
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
            
            content = content_data.get('content', '')
            url = content_data.get('url', '')
            
            # Analyze content
            analysis = self.analyze_webpage_content(content, url)
            
            # Save results
            output_filename = f"fact_check_{input_filename}"
            output_path = os.path.join('fact_check_results', output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"Analysis complete: {output_filename}")
            return output_filename
            
        except Exception as e:
            print(f"Error processing {input_filename}: {e}")
            return None

def main():
    """Main function for batch processing"""
    detector = MisinformationDetector()
    
    # Process all files in input_pages folder
    input_folder = 'input_pages'
    if not os.path.exists(input_folder):
        print(f"Creating {input_folder} folder...")
        os.makedirs(input_folder)
        print(" Place webpage content JSON files in the input_pages folder")
        return
    
    input_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    
    if not input_files:
        print("No input files found. Add JSON files with webpage content to input_pages folder")
        print("Expected format: {'url': 'https://example.com', 'content': 'webpage text...'}")
        return
    
    print(f"🔍 Processing {len(input_files)} input files...")
    
    processed_files = []
    for filename in input_files:
        result = detector.process_input_file(filename)
        if result:
            processed_files.append(result)
    
    print(f"\n Completed processing {len(processed_files)} files")
    print(" Results saved to fact_check_results folder")

if __name__ == "__main__":
    main()
