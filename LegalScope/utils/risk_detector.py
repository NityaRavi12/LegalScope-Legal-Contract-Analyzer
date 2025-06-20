import re
import logging
from typing import List, Dict, Any
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class RiskDetector:
    """Detect potential risks and unusual terms in contracts"""
    
    def __init__(self):
        self.risk_categories = {
            'auto_renewal': {
                'name': 'Automatic Renewal',
                'severity': 'high',
                'description': 'Contract automatically renews without explicit consent'
            },
            'penalty_fees': {
                'name': 'Penalty Fees',
                'severity': 'medium',
                'description': 'High fees or penalties for contract violations'
            },
            'unlimited_liability': {
                'name': 'Unlimited Liability',
                'severity': 'high',
                'description': 'No cap on liability or damages'
            },
            'data_ownership': {
                'name': 'Data Ownership Issues',
                'severity': 'medium',
                'description': 'Unclear or unfavorable data ownership terms'
            },
            'termination_penalties': {
                'name': 'Termination Penalties',
                'severity': 'medium',
                'description': 'High costs or penalties for early termination'
            },
            'exclusive_terms': {
                'name': 'Exclusive Terms',
                'severity': 'medium',
                'description': 'Exclusive arrangements that limit business options'
            },
            'unilateral_changes': {
                'name': 'Unilateral Changes',
                'severity': 'high',
                'description': 'One party can change terms without notice'
            },
            'confidentiality_breach': {
                'name': 'Confidentiality Breach Penalties',
                'severity': 'medium',
                'description': 'Severe penalties for confidentiality violations'
            },
            'jurisdiction_issues': {
                'name': 'Jurisdiction Issues',
                'severity': 'medium',
                'description': 'Unfavorable jurisdiction or governing law'
            },
            'arbitration_requirements': {
                'name': 'Mandatory Arbitration',
                'severity': 'low',
                'description': 'Forced arbitration instead of court proceedings'
            }
        }
        
        # Initialize sentiment analysis for risk assessment
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            logger.warning(f"Could not initialize sentiment analyzer: {e}")
            self.sentiment_analyzer = None
    
    def detect_risks(self, text: str, clauses: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
        """
        Detect potential risks in contract text
        
        Args:
            text (str): Contract text
            clauses (List[Dict]): Extracted clauses (optional)
            
        Returns:
            List[Dict]: List of detected risks
        """
        risks = []
        
        try:
            # Rule-based risk detection
            rule_based_risks = self._rule_based_detection(text)
            risks.extend(rule_based_risks)
            
            # Clause-specific risk detection
            if clauses:
                clause_risks = self._analyze_clause_risks(clauses)
                risks.extend(clause_risks)
            
            # Sentiment-based risk detection
            sentiment_risks = self._sentiment_based_detection(text)
            risks.extend(sentiment_risks)
            
            # Remove duplicates and sort by severity
            unique_risks = self._deduplicate_risks(risks)
            sorted_risks = self._sort_risks_by_severity(unique_risks)
            
            return sorted_risks
            
        except Exception as e:
            logger.error(f"Error detecting risks: {str(e)}")
            return []
    
    def _rule_based_detection(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect risks using rule-based patterns
        
        Args:
            text (str): Contract text
            
        Returns:
            List[Dict]: List of detected risks
        """
        risks = []
        text_lower = text.lower()
        
        # Auto-renewal patterns
        auto_renewal_patterns = [
            r'\bauto(mat)?ic\s+renew(al)?\b',
            r'\bcontinue\s+unless\s+terminated\b',
            r'\broll(ing)?\s+over\b',
            r'\bperpetual\b',
            r'\bongoing\b'
        ]
        
        if any(re.search(pattern, text_lower) for pattern in auto_renewal_patterns):
            risks.append({
                'category': 'auto_renewal',
                'text': self._extract_context(text, 'auto renewal'),
                'severity': 'high',
                'confidence': 0.8
            })
        
        # Penalty fees patterns
        penalty_patterns = [
            r'\bpenalty\b',
            r'\blate\s+fee\b',
            r'\bdefault\s+fee\b',
            r'\bbreach\s+fee\b',
            r'\bdamages?\b',
            r'\bliquidated\s+damages\b'
        ]
        
        if any(re.search(pattern, text_lower) for pattern in penalty_patterns):
            risks.append({
                'category': 'penalty_fees',
                'text': self._extract_context(text, 'penalty'),
                'severity': 'medium',
                'confidence': 0.7
            })
        
        # Unlimited liability patterns
        liability_patterns = [
            r'\bunlimited\s+liability\b',
            r'\bno\s+limit\s+on\s+liability\b',
            r'\bunlimited\s+damages\b',
            r'\bconsequential\s+damages\b'
        ]
        
        if any(re.search(pattern, text_lower) for pattern in liability_patterns):
            risks.append({
                'category': 'unlimited_liability',
                'text': self._extract_context(text, 'liability'),
                'severity': 'high',
                'confidence': 0.9
            })
        
        # Data ownership patterns
        data_patterns = [
            r'\bdata\s+ownership\b',
            r'\bintellectual\s+property\b',
            r'\bwork\s+product\b',
            r'\bderivative\s+works\b'
        ]
        
        if any(re.search(pattern, text_lower) for pattern in data_patterns):
            risks.append({
                'category': 'data_ownership',
                'text': self._extract_context(text, 'data'),
                'severity': 'medium',
                'confidence': 0.6
            })
        
        # Termination penalties
        termination_patterns = [
            r'\bearly\s+termination\s+fee\b',
            r'\bcancellation\s+fee\b',
            r'\bexit\s+fee\b',
            r'\btermination\s+penalty\b'
        ]
        
        if any(re.search(pattern, text_lower) for pattern in termination_patterns):
            risks.append({
                'category': 'termination_penalties',
                'text': self._extract_context(text, 'termination'),
                'severity': 'medium',
                'confidence': 0.7
            })
        
        return risks
    
    def _analyze_clause_risks(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze risks in specific clauses
        
        Args:
            clauses (List[Dict]): List of extracted clauses
            
        Returns:
            List[Dict]: List of clause-specific risks
        """
        risks = []
        
        for clause in clauses:
            clause_text = clause.get('text', '')
            clause_type = clause.get('type', '')
            
            # Analyze based on clause type
            if clause_type == 'Liability':
                if 'unlimited' in clause_text.lower() or 'no limit' in clause_text.lower():
                    risks.append({
                        'category': 'unlimited_liability',
                        'text': clause_text[:200] + '...' if len(clause_text) > 200 else clause_text,
                        'severity': 'high',
                        'confidence': 0.8,
                        'clause_type': clause_type
                    })
            
            elif clause_type == 'Payment':
                if any(word in clause_text.lower() for word in ['penalty', 'late fee', 'default']):
                    risks.append({
                        'category': 'penalty_fees',
                        'text': clause_text[:200] + '...' if len(clause_text) > 200 else clause_text,
                        'severity': 'medium',
                        'confidence': 0.7,
                        'clause_type': clause_type
                    })
            
            elif clause_type == 'Termination':
                if 'automatic' in clause_text.lower() or 'renew' in clause_text.lower():
                    risks.append({
                        'category': 'auto_renewal',
                        'text': clause_text[:200] + '...' if len(clause_text) > 200 else clause_text,
                        'severity': 'high',
                        'confidence': 0.8,
                        'clause_type': clause_type
                    })
        
        return risks
    
    def _sentiment_based_detection(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect risks using sentiment analysis
        
        Args:
            text (str): Contract text
            
        Returns:
            List[Dict]: List of sentiment-based risks
        """
        risks = []
        
        if not self.sentiment_analyzer:
            return risks
        
        try:
            # Split text into sentences for analysis
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            for sentence in sentences[:10]:  # Limit to first 10 sentences
                result = self.sentiment_analyzer(sentence)
                
                # Check for negative sentiment in legal context
                if (isinstance(result, list) and len(result) > 0 and 
                    isinstance(result[0], dict) and 
                    result[0].get('label') == 'NEGATIVE' and 
                    result[0].get('score', 0) > 0.7):
                    
                    # Look for risk indicators in negative sentences
                    risk_indicators = ['must', 'shall', 'required', 'obligation', 'penalty', 'damages']
                    if any(indicator in sentence.lower() for indicator in risk_indicators):
                        risks.append({
                            'category': 'general_risk',
                            'text': sentence,
                            'severity': 'medium',
                            'confidence': result[0].get('score', 0.5),
                            'sentiment_score': result[0].get('score', 0.5)
                        })
        
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
        
        return risks
    
    def _extract_context(self, text: str, keyword: str, context_length: int = 100) -> str:
        """
        Extract context around a keyword
        
        Args:
            text (str): Full text
            keyword (str): Keyword to search for
            context_length (int): Length of context to extract
            
        Returns:
            str: Context around keyword
        """
        try:
            index = text.lower().find(keyword.lower())
            if index != -1:
                start = max(0, index - context_length)
                end = min(len(text), index + len(keyword) + context_length)
                context = text[start:end]
                
                # Clean up context
                if start > 0:
                    context = '...' + context
                if end < len(text):
                    context = context + '...'
                
                return context
        except Exception:
            pass
        
        return f"Contains '{keyword}'"
    
    def _deduplicate_risks(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate risks
        
        Args:
            risks (List[Dict]): List of risks
            
        Returns:
            List[Dict]: Deduplicated risks
        """
        seen = set()
        unique_risks = []
        
        for risk in risks:
            # Create a key for deduplication
            key = (risk['category'], risk['text'][:100])  # Use first 100 chars of text
            
            if key not in seen:
                seen.add(key)
                unique_risks.append(risk)
        
        return unique_risks
    
    def _sort_risks_by_severity(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort risks by severity level
        
        Args:
            risks (List[Dict]): List of risks
            
        Returns:
            List[Dict]: Sorted risks
        """
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        
        return sorted(risks, key=lambda x: severity_order.get(x.get('severity', 'low'), 0), reverse=True)
    
    def get_risk_summary(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of detected risks
        
        Args:
            risks (List[Dict]): List of detected risks
            
        Returns:
            Dict: Risk summary
        """
        if not risks:
            return {
                'total_risks': 0,
                'high_risks': 0,
                'medium_risks': 0,
                'low_risks': 0,
                'risk_categories': {},
                'overall_risk_level': 'low'
            }
        
        # Count risks by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        category_counts = {}
        
        for risk in risks:
            severity = risk.get('severity', 'low')
            category = risk.get('category', 'unknown')
            
            severity_counts[severity] += 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Determine overall risk level
        if severity_counts['high'] > 0:
            overall_risk = 'high'
        elif severity_counts['medium'] > 2:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'total_risks': len(risks),
            'high_risks': severity_counts['high'],
            'medium_risks': severity_counts['medium'],
            'low_risks': severity_counts['low'],
            'risk_categories': category_counts,
            'overall_risk_level': overall_risk
        } 