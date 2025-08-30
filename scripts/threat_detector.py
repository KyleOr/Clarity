#!/usr/bin/env python3
"""
Cyberthreat Detection Script for SafeSearch Extension
Analyzes web content for phishing, scams, malware, and other cyberthreats
Uses comprehensive threat_detect.json configuration
"""

import json
import os
import re
import hashlib
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any
import argparse

class ThreatDetector:
    def __init__(self, config_path: str = None):
        """Initialize the threat detector with threat patterns from JSON config."""
        if config_path is None:
            # Default path to threat_detect.json
            config_path = os.path.join(os.path.dirname(__file__), '..', 'threatdetect', 'threat_detect.json')
        
        self.config = self._load_config(config_path)
        self.threat_categories = {cat['id']: cat for cat in self.config['threat_categories']}
        self.global_signals = self.config['global_signals']
        self.risk_thresholds = self.config['scoring']['risk_thresholds']
        self.default_signal_weight = self.config['scoring']['default_signal_weight']
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load threat detection configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using minimal fallback.")
            return self._get_fallback_config()
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {config_path}: {e}. Using minimal fallback.")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Provide minimal fallback configuration if JSON loading fails."""
        return {
            "scoring": {"risk_thresholds": {"low": 20, "medium": 40, "high": 70, "critical": 90}, "default_signal_weight": 5},
            "global_signals": {"urgency_phrases": ["urgent", "immediate", "verify now"]},
            "threat_categories": [
                {
                    "id": "phishing",
                    "name": "Phishing",
                    "severity_default": "high",
                    "weights": {"keyword": 6, "regex": 8},
                    "signals": {
                        "keywords": ["verify your account", "suspended account", "urgent action required"],
                        "regex_patterns": ["(?i)\\bverify (?:your|the) (?:account|identity)\\b"]
                    }
                }
            ]
        }

    def analyze_content(self, content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyze content for cyberthreats using JSON configuration.
        
        Args:
            content: Text content to analyze
            url: URL of the content (optional)
            
        Returns:
            Dictionary containing threat analysis results
        """
        threats_detected = []
        total_risk_score = 0
        
        # Convert content to lowercase for pattern matching
        content_lower = content.lower()
        
        # Check each threat category from JSON config
        for category_id, category in self.threat_categories.items():
            category_threats = self._analyze_category(content, content_lower, url, category)
            if category_threats:
                threats_detected.extend(category_threats)
                total_risk_score += sum(threat['risk_score'] for threat in category_threats)
        
        # Analyze global signals (urgency phrases, brand impersonation, etc.)
        global_threats = self._analyze_global_signals(content, content_lower, url)
        if global_threats:
            threats_detected.extend(global_threats)
            total_risk_score += sum(threat['risk_score'] for threat in global_threats)
        
        # Analyze URL for suspicious indicators
        url_threats = self._analyze_url_advanced(url) if url else []
        if url_threats:
            threats_detected.extend(url_threats)
            total_risk_score += sum(threat['risk_score'] for threat in url_threats)
        
        # Determine overall risk level using JSON thresholds
        risk_level = self._calculate_risk_level_advanced(total_risk_score)
        
        # Generate recommendations based on findings
        recommendations = self._generate_recommendations_advanced(threats_detected, risk_level)
        
        # Limit to top 5 threats for performance and manageable output
        # Sort by risk score (highest first) and take top 5
        if len(threats_detected) > 5:
            threats_detected_sorted = sorted(threats_detected, key=lambda x: x.get('risk_score', 0), reverse=True)
            threats_detected = threats_detected_sorted[:5]
            total_risk_score = sum(threat['risk_score'] for threat in threats_detected)
            # Recalculate risk level with limited threats
            risk_level = self._calculate_risk_level_advanced(total_risk_score)
        
        return {
            'metadata': {
                'url': url,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content_length': len(content),
                'threats_analyzed': len(self.threat_categories),
                'config_version': self.config.get('version', '1.0')
            },
            'summary': {
                'total_threats': len(threats_detected),
                'high_risk_threats': len([t for t in threats_detected if self._get_threat_severity_advanced(t) == 'high']),
                'medium_risk_threats': len([t for t in threats_detected if self._get_threat_severity_advanced(t) == 'medium']),
                'low_risk_threats': len([t for t in threats_detected if self._get_threat_severity_advanced(t) == 'low']),
                'overall_risk_level': risk_level,
                'total_risk_score': total_risk_score
            },
            'detailed_analysis': threats_detected,
            'recommendations': recommendations,
            # Legacy format for backward compatibility
            'threats_detected': threats_detected,
            'risk_level': risk_level,
            'analysis_timestamp': datetime.now().isoformat(),
            'threat_count': len(threats_detected)
        }

    def _analyze_category(self, content: str, content_lower: str, url: str, category: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze content for a specific threat category."""
        threats = []
        category_id = category['id']
        category_name = category['name']
        signals = category.get('signals', {})
        weights = category.get('weights', {})
        
        # Analyze keywords
        if 'keywords' in signals:
            keyword_matches = self._find_keyword_matches(content_lower, signals['keywords'])
            if keyword_matches:
                risk_score = len(keyword_matches) * weights.get('keyword', self.default_signal_weight)
                threats.append({
                    'type': category_id,
                    'subtype': 'keywords',
                    'matches': keyword_matches,
                    'count': len(keyword_matches),
                    'risk_score': risk_score,
                    'description': f"{category_name} - Keyword indicators detected",
                    'severity': category.get('severity_default', 'medium')
                })
        
        # Analyze regex patterns
        if 'regex_patterns' in signals:
            regex_matches = self._find_regex_matches(content, signals['regex_patterns'])
            if regex_matches:
                risk_score = len(regex_matches) * weights.get('regex', self.default_signal_weight)
                threats.append({
                    'type': category_id,
                    'subtype': 'regex_patterns',
                    'matches': regex_matches,
                    'count': len(regex_matches),
                    'risk_score': risk_score,
                    'description': f"{category_name} - Pattern matches detected",
                    'severity': category.get('severity_default', 'medium')
                })
        
        # Analyze URL indicators
        if 'url_indicators' in signals and url:
            url_matches = self._find_url_matches(url, signals['url_indicators'])
            if url_matches:
                risk_score = len(url_matches) * weights.get('url', signals['url_indicators'].get('weight', self.default_signal_weight))
                threats.append({
                    'type': category_id,
                    'subtype': 'url_indicators',
                    'matches': url_matches,
                    'count': len(url_matches),
                    'risk_score': risk_score,
                    'description': f"{category_name} - Suspicious URL patterns detected",
                    'severity': category.get('severity_default', 'medium')
                })
        
        return threats
    
    def _analyze_global_signals(self, content: str, content_lower: str, url: str) -> List[Dict[str, Any]]:
        """Analyze content for global threat signals."""
        threats = []
        
        # Check urgency phrases
        if 'urgency_phrases' in self.global_signals:
            urgency_matches = self._find_keyword_matches(content_lower, self.global_signals['urgency_phrases'])
            if urgency_matches:
                threats.append({
                    'type': 'global_urgency',
                    'subtype': 'urgency_phrases',
                    'matches': urgency_matches,
                    'count': len(urgency_matches),
                    'risk_score': len(urgency_matches) * 4,  # High weight for urgency
                    'description': 'Urgency manipulation tactics detected',
                    'severity': 'medium'
                })
        
        # Check brand impersonation
        if 'brand_impersonation' in self.global_signals:
            brand_matches = self._find_keyword_matches(content_lower, self.global_signals['brand_impersonation'])
            if brand_matches:
                threats.append({
                    'type': 'global_brand_impersonation',
                    'subtype': 'brand_references',
                    'matches': brand_matches,
                    'count': len(brand_matches),
                    'risk_score': len(brand_matches) * 3,
                    'description': 'Potential brand impersonation detected',
                    'severity': 'medium'
                })
        
        # Check cryptocurrency terms
        if 'cryptocurrency_terms' in self.global_signals:
            crypto_matches = self._find_keyword_matches(content_lower, self.global_signals['cryptocurrency_terms'])
            if crypto_matches:
                threats.append({
                    'type': 'global_crypto',
                    'subtype': 'crypto_references',
                    'matches': crypto_matches,
                    'count': len(crypto_matches),
                    'risk_score': len(crypto_matches) * 2,
                    'description': 'Cryptocurrency-related content detected',
                    'severity': 'low'
                })
        
        # Check homoglyph hints
        if 'homoglyph_hints' in self.global_signals:
            homoglyph_data = self.global_signals['homoglyph_hints']
            homoglyph_matches = self._find_regex_matches(content, homoglyph_data['patterns'])
            if homoglyph_matches:
                threats.append({
                    'type': 'global_homoglyph',
                    'subtype': 'character_spoofing',
                    'matches': homoglyph_matches,
                    'count': len(homoglyph_matches),
                    'risk_score': len(homoglyph_matches) * homoglyph_data.get('weight', 8),
                    'description': 'Potential character spoofing (homoglyph attack) detected',
                    'severity': 'high'
                })
        
        return threats
    
    def _find_keyword_matches(self, content_lower: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find keyword matches in content."""
        matches = []
        for keyword in keywords:
            if keyword.lower() in content_lower:
                # Find all occurrences of this keyword
                start = 0
                while True:
                    pos = content_lower.find(keyword.lower(), start)
                    if pos == -1:
                        break
                    
                    snippet = self._extract_snippet_at_position(content_lower, pos, len(keyword))
                    matches.append({
                        'text': snippet,
                        'matched_text': keyword,
                        'position': (pos, pos + len(keyword)),
                        'pattern': keyword
                    })
                    start = pos + 1
        
        return matches
    
    def _find_regex_matches(self, content: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Find regex pattern matches in content."""
        matches = []
        for pattern in patterns:
            try:
                found_matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in found_matches:
                    snippet = self._extract_threat_snippet(content, match)
                    matches.append({
                        'text': snippet,
                        'matched_text': match.group(0),
                        'position': match.span(),
                        'pattern': pattern
                    })
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}")
                continue
        
        return matches
    
    def _find_url_matches(self, url: str, url_indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find URL-based threat indicators."""
        matches = []
        
        if 'regex' in url_indicators:
            for pattern in url_indicators['regex']:
                try:
                    if re.search(pattern, url, re.IGNORECASE):
                        matches.append({
                            'text': url,
                            'matched_text': url,
                            'position': (0, len(url)),
                            'pattern': pattern
                        })
                except re.error as e:
                    print(f"Warning: Invalid URL regex pattern '{pattern}': {e}")
                    continue
        
        return matches
    
    def _extract_snippet_at_position(self, content: str, pos: int, length: int) -> str:
        """Extract a snippet around a specific position."""
        start = max(0, pos - 50)
        end = min(len(content), pos + length + 50)
        
        snippet = content[start:end]
        
        # Clean up and limit length
        snippet = snippet.strip()
        if len(snippet) > 150:
            snippet = snippet[:147] + "..."
        
        return snippet
    def _analyze_url_advanced(self, url: str) -> List[Dict[str, Any]]:
        """Analyze URL using advanced patterns from JSON config."""
        threats = []
        
        if not url:
            return threats
        
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Check for suspicious TLDs
            if 'common_suspicious_tlds' in self.global_signals:
                for tld in self.global_signals['common_suspicious_tlds']:
                    if domain.endswith(f'.{tld}'):
                        threats.append({
                            'type': 'suspicious_tld',
                            'matches': [{'text': domain, 'matched_text': f'.{tld}', 'position': (0, len(domain))}],
                            'count': 1,
                            'risk_score': 3,
                            'description': f'Domain uses suspicious TLD: .{tld}',
                            'severity': 'medium'
                        })
            
            # Check for URL shorteners
            if 'url_shorteners' in self.global_signals:
                for shortener in self.global_signals['url_shorteners']:
                    if shortener in domain:
                        threats.append({
                            'type': 'url_shortener',
                            'matches': [{'text': domain, 'matched_text': shortener, 'position': (0, len(domain))}],
                            'count': 1,
                            'risk_score': 4,
                            'description': f'Uses URL shortening service: {shortener}',
                            'severity': 'medium'
                        })
            
            # Check for high-risk file extensions in URL path
            if 'file_extensions_high_risk' in self.global_signals and parsed_url.path:
                for ext in self.global_signals['file_extensions_high_risk']:
                    if parsed_url.path.lower().endswith(ext):
                        threats.append({
                            'type': 'high_risk_file',
                            'matches': [{'text': parsed_url.path, 'matched_text': ext, 'position': (0, len(parsed_url.path))}],
                            'count': 1,
                            'risk_score': 6,
                            'description': f'URL points to high-risk file type: {ext}',
                            'severity': 'high'
                        })
            
        except Exception as e:
            print(f"Error analyzing URL {url}: {str(e)}")
        
        return threats
    
    def _calculate_risk_level_advanced(self, total_score: int) -> str:
        """Calculate overall risk level using JSON thresholds."""
        thresholds = self.risk_thresholds
        
        if total_score >= thresholds.get('critical', 90):
            return 'critical'
        elif total_score >= thresholds.get('high', 70):
            return 'high'
        elif total_score >= thresholds.get('medium', 40):
            return 'medium'
        elif total_score >= thresholds.get('low', 20):
            return 'low'
        else:
            return 'safe'
    
    def _generate_recommendations_advanced(self, threats_detected: List[Dict[str, Any]], risk_level: str) -> List[str]:
        """Generate recommendations using UI guidance from JSON config."""
        recommendations = []
        
        # Get base recommendations from config if available
        ui_guidance = self.config.get('ui_guidance', {})
        action_advice = ui_guidance.get('action_advice', [])
        
        if risk_level == 'safe':
            recommendations.append("✅ No significant cyberthreats detected")
            recommendations.append("✅ Content appears safe for general consumption")
            recommendations.append("ℹ️ Continue practicing safe browsing habits")
        elif risk_level == 'low':
            recommendations.append("⚠️ Minor suspicious indicators found")
            recommendations.append("💡 Exercise normal caution when interacting with this content")
            recommendations.append("🔍 Verify any claims before taking action")
        elif risk_level == 'medium':
            recommendations.append("⚠️ Moderate threat indicators detected")
            recommendations.append("🛡️ Be cautious with personal information on this site")
            recommendations.append("🔍 Verify legitimacy before making any payments or downloads")
            recommendations.append("💡 Consider using additional security measures")
        else:  # high or critical
            recommendations.append("🚨 High risk threats detected")
            recommendations.append("❌ Avoid providing personal or financial information")
            recommendations.append("❌ Do not download or install any software from this site")
            recommendations.append("🛡️ Consider leaving this website immediately")
            recommendations.append("📞 Report suspicious content to relevant authorities")
        
        # Add specific recommendations based on threat types
        threat_types = [threat['type'] for threat in threats_detected]
        unique_types = set(threat_types)
        
        for threat_type in unique_types:
            if threat_type in ['phishing', 'global_urgency']:
                recommendations.append("🎣 Potential phishing detected - verify sender legitimacy")
            elif threat_type in ['malicious_download', 'high_risk_file']:
                recommendations.append("🦠 Potential malware distribution - avoid downloads")
            elif 'scam' in threat_type or 'investment' in threat_type:
                recommendations.append("💰 Potential scam indicators - verify financial claims")
            elif 'crypto' in threat_type:
                recommendations.append("₿ Cryptocurrency content - be extra cautious with wallet/key requests")
            elif 'homoglyph' in threat_type:
                recommendations.append("🔤 Character spoofing detected - verify domain spelling carefully")
            elif 'brand' in threat_type:
                recommendations.append("🏢 Potential brand impersonation - verify through official channels")
        
        # Add general action advice from config
        if action_advice and risk_level in ['medium', 'high', 'critical']:
            recommendations.extend([f"💡 {advice}" for advice in action_advice[:3]])  # Limit to top 3
        
        return recommendations
    
    def analyze_security_indicators(self, security_indicators: Dict[str, List]) -> Dict[str, Any]:
        """
        Analyze security indicators from browser extension and limit to top 5 highest risk.
        
        Args:
            security_indicators: Dict containing advertisements, popups, external_links, suspicious_elements
            
        Returns:
            Dictionary with processed security indicators (limited to top 5)
        """
        processed_indicators = {
            'total_advertisements': len(security_indicators.get('advertisements', [])),
            'total_popups': len(security_indicators.get('popups', [])),
            'total_external_links': len(security_indicators.get('externalLinks', [])),
            'total_suspicious_elements': len(security_indicators.get('suspiciousElements', [])),
            'top_security_threats': [],
            'security_risk_level': 'safe'
        }
        
        # Collect and prioritize all security indicators
        all_indicators = []
        
        # Process advertisements with risk scoring
        for ad in security_indicators.get('advertisements', []):
            risk_score = self._calculate_ad_risk_score(ad)
            all_indicators.append({
                'type': 'advertisement',
                'description': "⚠️ Avoid clicking on advertisements - they may lead to malicious sites or downloads",
                'risk_score': risk_score,
                'details': {
                    'text': ad.get('text', '')[:100] + '...' if len(ad.get('text', '')) > 100 else ad.get('text', ''),
                    'className': ad.get('className', ''),
                    'position': ad.get('position', {}),
                    'visible': ad.get('visible', True)
                },
                'severity': self._get_security_severity_from_score(risk_score)
            })
        
        # Process popups with risk scoring  
        for popup in security_indicators.get('popups', []):
            risk_score = self._calculate_popup_risk_score(popup)
            all_indicators.append({
                'type': 'popup',
                'description': "🚨 Do not interact with popup windows - close them immediately using the X button",
                'risk_score': risk_score,
                'details': {
                    'text': popup.get('text', '')[:100] + '...' if len(popup.get('text', '')) > 100 else popup.get('text', ''),
                    'zIndex': popup.get('zIndex', 0),
                    'position': popup.get('position', ''),
                    'dimensions': popup.get('dimensions', {})
                },
                'severity': self._get_security_severity_from_score(risk_score)
            })
        
        # Process external links with risk scoring
        for link in security_indicators.get('externalLinks', []):
            risk_score = self._calculate_link_risk_score(link)
            
            # Create user-friendly warning based on risk level
            if link.get('suspicious', False):
                description = "🚫 Suspicious external link detected - verify destination before clicking"
            else:
                description = "🔗 External link detected - verify it's legitimate before clicking"
            
            all_indicators.append({
                'type': 'external_link',
                'description': description,
                'risk_score': risk_score,
                'details': {
                    'href': link.get('href', ''),
                    'text': link.get('text', '')[:100] + '...' if len(link.get('text', '')) > 100 else link.get('text', ''),
                    'suspicious': link.get('suspicious', False),
                    'suspiciousReasons': link.get('suspiciousReasons', [])
                },
                'severity': self._get_security_severity_from_score(risk_score)
            })
        
        # Process suspicious elements with risk scoring
        for element in security_indicators.get('suspiciousElements', []):
            risk_score = self._calculate_suspicious_element_risk_score(element)
            
            # Create user-friendly warning based on element type
            element_type = element.get('type', '')
            if element_type == 'download_element':
                description = "💾 Download link detected - only download from trusted sources"
            elif element_type == 'sensitive_form':
                description = "📝 Form requesting sensitive information - verify site security before submitting"
            elif element_type == 'suspicious_text':
                description = "⚠️ Suspicious text detected - be cautious of urgent or threatening language"
            else:
                description = "🔍 Suspicious page element detected - exercise caution when interacting"
            
            all_indicators.append({
                'type': 'suspicious_element',
                'description': description,
                'risk_score': risk_score,
                'details': element,
                'severity': self._get_security_severity_from_score(risk_score)
            })
        
        # Sort by risk score (highest first) and take top 5
        all_indicators_sorted = sorted(all_indicators, key=lambda x: x['risk_score'], reverse=True)
        processed_indicators['top_security_threats'] = all_indicators_sorted[:5]
        
        # Calculate overall security risk level
        if all_indicators_sorted:
            highest_risk = all_indicators_sorted[0]['risk_score']
            if highest_risk >= 8:
                processed_indicators['security_risk_level'] = 'high'
            elif highest_risk >= 5:
                processed_indicators['security_risk_level'] = 'medium'  
            elif highest_risk >= 2:
                processed_indicators['security_risk_level'] = 'low'
        
        return processed_indicators
    
    def _calculate_ad_risk_score(self, ad: Dict) -> int:
        """Calculate risk score for advertisement based on properties."""
        risk_score = 1  # Base score for any ad
        
        # Higher risk for visible ads
        if ad.get('visible', True):
            risk_score += 1
            
        # Higher risk for iframe ads (often malicious)
        if 'iframe' in ad.get('selector', '').lower():
            risk_score += 3
            
        # Higher risk for Google ads (could be malicious ads served through legit networks)
        if 'google' in ad.get('src', '').lower() or 'doubleclick' in ad.get('src', '').lower():
            risk_score += 2
            
        # Higher risk for ads with suspicious text
        text = ad.get('text', '').lower()
        if any(word in text for word in ['download', 'click here', 'urgent', 'free']):
            risk_score += 2
            
        return min(risk_score, 10)  # Cap at 10
    
    def _calculate_popup_risk_score(self, popup: Dict) -> int:
        """Calculate risk score for popup based on properties."""
        risk_score = 3  # Base score for popups (inherently more suspicious)
        
        # Higher risk for high z-index (overlay popups)
        z_index = popup.get('zIndex', 0)
        if z_index > 1000:
            risk_score += 3
        elif z_index > 100:
            risk_score += 2
            
        # Higher risk for fixed position popups
        if popup.get('position') == 'fixed':
            risk_score += 2
            
        return min(risk_score, 10)
    
    def _calculate_link_risk_score(self, link: Dict) -> int:
        """Calculate risk score for external link based on properties."""
        risk_score = 1  # Base score for external links
        
        # Much higher risk if marked as suspicious
        if link.get('suspicious', False):
            risk_score += 6
            
        # Add risk based on suspicious reasons
        reasons = link.get('suspiciousReasons', [])
        risk_score += len(reasons) * 2
        
        # Higher risk for certain domains
        href = link.get('href', '').lower()
        if any(pattern in href for pattern in ['bit.ly', 'tinyurl', 'exe', 'download']):
            risk_score += 3
            
        return min(risk_score, 10)
    
    def _calculate_suspicious_element_risk_score(self, element: Dict) -> int:
        """Calculate risk score for suspicious element based on type."""
        element_type = element.get('type', '')
        
        if element_type == 'download_element':
            return 8  # High risk for download elements
        elif element_type == 'sensitive_form':
            return 7  # High risk for forms requesting sensitive data
        elif element_type == 'suspicious_text':
            return 4  # Medium risk for suspicious text
        else:
            return 2  # Low risk for unknown suspicious elements
    
    def _get_security_severity_from_score(self, risk_score: int) -> str:
        """Convert risk score to severity level for security indicators."""
        if risk_score >= 8:
            return 'high'
        elif risk_score >= 5:
            return 'medium'
        elif risk_score >= 2:
            return 'low'
        else:
            return 'info'
    
    def _get_threat_severity_advanced(self, threat: Dict[str, Any]) -> str:
        """Determine severity level using JSON config and threat data."""
        # Use explicit severity from threat if available
        if 'severity' in threat:
            return threat['severity']
        
        # Fall back to category default
        threat_type = threat.get('type', '')
        if threat_type in self.threat_categories:
            return self.threat_categories[threat_type].get('severity_default', 'medium')
        
        # Final fallback based on risk score
        risk_score = threat.get('risk_score', 0)
        if risk_score >= 8:
            return 'high'
        elif risk_score >= 4:
            return 'medium'
        else:
            return 'low'

    def _extract_threat_snippet(self, content: str, match) -> str:
        """
        Extract a reasonable snippet around the threat match.
        
        Args:
            content: Original content
            match: Regex match object
            
        Returns:
            A snippet of text around the threat (max ~100 chars)
        """
        start_pos = match.start()
        end_pos = match.end()
        
        # Find word boundaries around the match to get context
        snippet_start = max(0, start_pos - 50)
        snippet_end = min(len(content), end_pos + 50)
        
        # Try to break at word boundaries
        snippet = content[snippet_start:snippet_end]
        
        # Find the first space after our start (to avoid cutting words)
        if snippet_start > 0:
            first_space = snippet.find(' ')
            if first_space != -1 and first_space < 30:  # Only if it's reasonable
                snippet = snippet[first_space + 1:]
        
        # Find the last space before our end (to avoid cutting words)
        if snippet_end < len(content):
            last_space = snippet.rfind(' ')
            if last_space != -1 and last_space > len(snippet) - 30:  # Only if it's reasonable
                snippet = snippet[:last_space]
        
        # Clean up and limit length
        snippet = snippet.strip()
        if len(snippet) > 150:
            snippet = snippet[:147] + "..."
        
        return snippet

    def save_results(self, results: Dict[str, Any], file_id: str) -> str:
        """Save threat detection results to JSON file."""
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'threat_detect_results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename
        filename = f'threat_detect_{file_id}.json'
        filepath = os.path.join(results_dir, filename)
        
        # Save results
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Threat detection results saved to: {filepath}")
        return filepath

def process_web_content_file(file_path: str, detector: ThreatDetector) -> str:
    """Process a single web content JSON file for threat detection."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract content and URL
        content = data.get('content', '')
        url = data.get('url', '')
        title = data.get('title', '')
        
        # Extract security indicators for additional analysis
        security_indicators = data.get('security_indicators', {})
        
        # Combine title and content for analysis
        full_content = f"{title} {content}"
        
        # Run threat detection on text content
        results = detector.analyze_content(full_content, url)
        
        # Process security indicators and add to results
        if security_indicators:
            security_summary = detector.analyze_security_indicators(security_indicators)
            results['security_indicators_summary'] = security_summary
        
        # Add metadata
        results['source_file'] = os.path.basename(file_path)
        results['original_data'] = {
            'title': title,
            'url': url,
            'content_length': len(content)
        }
        
        # Generate file ID from original filename
        file_id = os.path.splitext(os.path.basename(file_path))[0]
        if file_id.startswith('web_content_'):
            file_id = file_id[12:]  # Remove 'web_content_' prefix
        
        # Save results
        results_file = detector.save_results(results, file_id)
        
        return results_file
        
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Detect cyberthreats in web content using JSON configuration')
    parser.add_argument('input_path', help='Path to input file or directory')
    parser.add_argument('--single', action='store_true', help='Process single file instead of directory')
    parser.add_argument('--config', help='Path to threat_detect.json config file', 
                       default=None)
    
    args = parser.parse_args()
    
    detector = ThreatDetector(config_path=args.config)
    
    print(f"🔍 SafeSearch Threat Detector v{detector.config.get('version', '1.0')}")
    print(f"📋 Loaded {len(detector.threat_categories)} threat categories")
    
    if args.single:
        # Process single file
        if os.path.isfile(args.input_path):
            results_file = process_web_content_file(args.input_path, detector)
            if results_file:
                print(f"✅ Processed: {args.input_path}")
                print(f"📄 Results: {results_file}")
            else:
                print(f"❌ Failed to process: {args.input_path}")
        else:
            print(f"❌ File not found: {args.input_path}")
    else:
        # Process directory
        input_dir = args.input_path
        if not os.path.isdir(input_dir):
            print(f"❌ Directory not found: {input_dir}")
            return
        
        processed_count = 0
        failed_count = 0
        
        # Process all JSON files in directory
        for filename in os.listdir(input_dir):
            if filename.endswith('.json') and 'web_content' in filename:
                file_path = os.path.join(input_dir, filename)
                results_file = process_web_content_file(file_path, detector)
                
                if results_file:
                    print(f"✅ Processed: {filename}")
                    processed_count += 1
                else:
                    print(f"❌ Failed: {filename}")
                    failed_count += 1
        
        print(f"\n📊 Summary:")
        print(f"✅ Processed: {processed_count}")
        print(f"❌ Failed: {failed_count}")

if __name__ == "__main__":
    main()
