import os
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Optional imports for LLM integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    provider: str = "openai"  # "openai", "anthropic", "local"
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.3
    enable_llm: bool = True
    fallback_to_local: bool = True

class LLMAnalyzer:
    """Advanced legal analysis using Large Language Models"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.client = None
        
        # Initialize LLM client based on provider
        if self.config.enable_llm:
            self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client"""
        try:
            if self.config.provider == "openai" and OPENAI_AVAILABLE:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.client = openai.OpenAI(api_key=api_key)  # type: ignore
                    logger.info("OpenAI client initialized successfully")
                else:
                    logger.warning("OpenAI API key not found")
                    
            elif self.config.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)  # type: ignore
                    logger.info("Anthropic client initialized successfully")
                else:
                    logger.warning("Anthropic API key not found")
                    
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None
    
    def analyze_contract_comprehensive(self, text: str, clauses: List[Dict], risks: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive contract analysis using LLM
        
        Args:
            text (str): Contract text
            clauses (List[Dict]): Extracted clauses
            risks (List[Dict]): Detected risks
            
        Returns:
            Dict: Comprehensive analysis results
        """
        if not self.client:
            return self._fallback_analysis(clauses, risks)
        
        try:
            analysis = {
                'legal_insights': self._generate_legal_insights(text, clauses, risks),
                'risk_explanations': self._explain_risks(risks),
                'clause_interpretations': self._interpret_clauses(clauses),
                'recommendations': self._generate_recommendations(clauses, risks),
                'compliance_check': self._check_compliance(text),
                'negotiation_points': self._identify_negotiation_points(clauses, risks)
            }
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_analysis(clauses, risks)
    
    def _generate_legal_insights(self, text: str, clauses: List[Dict], risks: List[Dict]) -> str:
        """Generate legal insights about the contract"""
        prompt = f"""
        As a legal expert, analyze this contract and provide key legal insights:

        CONTRACT TEXT (first 1000 characters):
        {text[:1000]}...

        EXTRACTED CLAUSES:
        {json.dumps([{'type': c['type'], 'text': c['text'][:200]} for c in clauses], indent=2)}

        DETECTED RISKS:
        {json.dumps([{'category': r['category'], 'severity': r['severity']} for r in risks], indent=2)}

        Please provide:
        1. Key legal implications
        2. Potential issues to watch for
        3. Standard vs. unusual terms
        4. Overall contract fairness assessment

        Keep the response concise and practical for business users.
        """
        
        return self._call_llm(prompt, "Generate legal insights")
    
    def _explain_risks(self, risks: List[Dict]) -> List[Dict]:
        """Explain detected risks in plain language"""
        explanations = []
        
        for risk in risks:
            prompt = f"""
            Explain this contract risk in simple terms for a business person:

            RISK CATEGORY: {risk['category']}
            SEVERITY: {risk['severity']}
            CONTEXT: {risk['text'][:300]}...

            Please explain:
            1. What this risk means in business terms
            2. Why it's concerning
            3. What could happen if not addressed
            4. How to mitigate or negotiate this risk

            Keep it simple and actionable.
            """
            
            explanation = self._call_llm(prompt, f"Explain {risk['category']} risk")
            
            explanations.append({
                'risk_id': risk.get('category', 'unknown'),
                'explanation': explanation,
                'severity': risk.get('severity', 'medium'),
                'mitigation_suggestions': self._generate_mitigation_suggestions(risk)
            })
        
        return explanations
    
    def _interpret_clauses(self, clauses: List[Dict]) -> List[Dict]:
        """Provide plain-language interpretations of legal clauses"""
        interpretations = []
        
        for clause in clauses:
            prompt = f"""
            Translate this legal clause into plain English for a business person:

            CLAUSE TYPE: {clause['type']}
            LEGAL TEXT: {clause['text'][:500]}...

            Please provide:
            1. What this clause means in simple terms
            2. Key obligations or rights it creates
            3. Important deadlines or conditions
            4. What to watch out for

            Make it easy for non-lawyers to understand.
            """
            
            interpretation = self._call_llm(prompt, f"Interpret {clause['type']} clause")
            
            interpretations.append({
                'clause_type': clause['type'],
                'interpretation': interpretation,
                'key_points': self._extract_key_points(clause['text']),
                'business_impact': self._assess_business_impact(clause)
            })
        
        return interpretations
    
    def _generate_recommendations(self, clauses: List[Dict], risks: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        prompt = f"""
        Based on this contract analysis, provide 5-7 actionable recommendations:

        CLAUSES FOUND: {len(clauses)}
        RISKS DETECTED: {len(risks)}
        HIGH RISKS: {len([r for r in risks if r.get('severity') == 'high'])}
        MEDIUM RISKS: {len([r for r in risks if r.get('severity') == 'medium'])}

        RISK CATEGORIES: {[r.get('category') for r in risks]}

        Please provide specific, actionable recommendations for:
        1. Negotiation priorities
        2. Risk mitigation strategies
        3. Legal review needs
        4. Business considerations

        Format as a numbered list of clear, actionable items.
        """
        
        recommendations_text = self._call_llm(prompt, "Generate recommendations")
        return [rec.strip() for rec in recommendations_text.split('\n') if rec.strip()]
    
    def _check_compliance(self, text: str) -> Dict[str, Any]:
        """Check for compliance issues"""
        prompt = f"""
        Analyze this contract for potential compliance issues:

        CONTRACT TEXT: {text[:1500]}...

        Check for:
        1. Data protection/privacy compliance (GDPR, CCPA, etc.)
        2. Industry-specific regulations
        3. Standard contract requirements
        4. Missing essential clauses
        5. Unusual or problematic terms

        Provide a compliance assessment with specific concerns and recommendations.
        """
        
        compliance_analysis = self._call_llm(prompt, "Compliance check")
        
        return {
            'assessment': compliance_analysis,
            'compliance_score': self._calculate_compliance_score(text),
            'missing_clauses': self._identify_missing_clauses(text),
            'regulatory_concerns': self._identify_regulatory_concerns(text)
        }
    
    def _identify_negotiation_points(self, clauses: List[Dict], risks: List[Dict]) -> List[Dict]:
        """Identify key negotiation points"""
        prompt = f"""
        Based on this contract analysis, identify the most important negotiation points:

        CLAUSES: {[c['type'] for c in clauses]}
        RISKS: {[r['category'] for r in risks if r.get('severity') in ['high', 'medium']]}

        For each key area, provide:
        1. What to negotiate
        2. Why it's important
        3. Suggested approach
        4. Potential compromises

        Focus on high-impact, negotiable items.
        """
        
        negotiation_text = self._call_llm(prompt, "Identify negotiation points")
        
        # Parse negotiation points (this is a simplified approach)
        points = []
        lines = negotiation_text.split('\n')
        current_point = {}
        
        for line in lines:
            if line.strip() and not line.startswith(' '):
                if current_point:
                    points.append(current_point)
                current_point = {'topic': line.strip(), 'details': ''}
            elif current_point:
                current_point['details'] += line.strip() + ' '
        
        if current_point:
            points.append(current_point)
        
        return points
    
    def _call_llm(self, prompt: str, task_name: str) -> str:
        """Make LLM API call with error handling"""
        try:
            if isinstance(self.client, openai.OpenAI):  # type: ignore
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": "You are a legal expert specializing in contract analysis. Provide clear, practical advice for business users."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                return response.choices[0].message.content.strip()  # type: ignore
                
            elif (hasattr(self.client, 'messages') and 
                  ANTHROPIC_AVAILABLE and 
                  anthropic is not None and 
                  isinstance(self.client, anthropic.Anthropic)):  # type: ignore
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()  # type: ignore
                
        except Exception as e:
            logger.error(f"LLM call failed for {task_name}: {e}")
        
        return f"Analysis unavailable for {task_name}. Please consult with a legal professional."
    
    def _fallback_analysis(self, clauses: List[Dict], risks: List[Dict]) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        return {
            'legal_insights': "LLM analysis not available. Please consult with a legal professional for detailed insights.",
            'risk_explanations': [
                {
                    'risk_id': risk.get('category', 'unknown'),
                    'explanation': f"This is a {risk.get('severity', 'medium')} risk related to {risk.get('category', 'unknown')}. Please review with legal counsel.",
                    'severity': risk.get('severity', 'medium'),
                    'mitigation_suggestions': ["Consult with legal counsel", "Review industry standards", "Consider negotiation"]
                }
                for risk in risks
            ],
            'clause_interpretations': [
                {
                    'clause_type': clause['type'],
                    'interpretation': f"This is a {clause['type']} clause. Please have it reviewed by legal counsel.",
                    'key_points': ["Legal review recommended"],
                    'business_impact': "Requires legal assessment"
                }
                for clause in clauses
            ],
            'recommendations': [
                "Have the contract reviewed by legal counsel",
                "Identify and prioritize key risks",
                "Consider industry best practices",
                "Negotiate unfavorable terms",
                "Ensure compliance with applicable laws"
            ],
            'compliance_check': {
                'assessment': "Compliance review requires legal expertise",
                'compliance_score': 0.5,
                'missing_clauses': [],
                'regulatory_concerns': []
            },
            'negotiation_points': [
                {
                    'topic': 'Legal Review',
                    'details': 'Have the entire contract reviewed by qualified legal counsel.'
                }
            ]
        }
    
    def _generate_mitigation_suggestions(self, risk: Dict) -> List[str]:
        """Generate risk mitigation suggestions"""
        risk_type = risk.get('category', 'general')
        
        mitigation_strategies = {
            'auto_renewal': [
                "Add explicit termination notice requirements",
                "Include opt-out mechanisms",
                "Set clear renewal terms"
            ],
            'penalty_fees': [
                "Negotiate reasonable penalty caps",
                "Add grace periods",
                "Include dispute resolution procedures"
            ],
            'unlimited_liability': [
                "Add liability caps",
                "Include insurance requirements",
                "Negotiate mutual limitation of liability"
            ],
            'data_ownership': [
                "Clarify data ownership terms",
                "Add data protection clauses",
                "Include data return provisions"
            ]
        }
        
        return mitigation_strategies.get(risk_type, [
            "Consult with legal counsel",
            "Review industry standards",
            "Consider alternative terms"
        ])
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from clause text"""
        # Simple keyword extraction - could be enhanced with NLP
        keywords = ['shall', 'must', 'will', 'agree', 'obligation', 'liability', 'terminate']
        key_points = []
        
        for keyword in keywords:
            if keyword in text.lower():
                key_points.append(f"Contains '{keyword}' obligations")
        
        return key_points[:3]  # Limit to top 3
    
    def _assess_business_impact(self, clause: Dict) -> str:
        """Assess business impact of a clause"""
        clause_type = clause.get('type', '').lower()
        
        impact_map = {
            'payment': 'Financial impact',
            'termination': 'Operational risk',
            'liability': 'Legal exposure',
            'confidentiality': 'Information security',
            'indemnification': 'Financial protection'
        }
        
        return impact_map.get(clause_type, 'Requires legal review')
    
    def _calculate_compliance_score(self, text: str) -> float:
        """Calculate a basic compliance score"""
        # Simple scoring based on presence of key terms
        compliance_terms = ['governing law', 'jurisdiction', 'dispute resolution', 'confidentiality', 'termination']
        score = 0.0
        
        for term in compliance_terms:
            if term in text.lower():
                score += 0.2
        
        return min(score, 1.0)
    
    def _identify_missing_clauses(self, text: str) -> List[str]:
        """Identify potentially missing clauses"""
        common_clauses = [
            'governing law', 'dispute resolution', 'confidentiality', 
            'termination', 'force majeure', 'entire agreement'
        ]
        
        missing = []
        for clause in common_clauses:
            if clause not in text.lower():
                missing.append(clause.replace(' ', ' ').title())
        
        return missing
    
    def _identify_regulatory_concerns(self, text: str) -> List[str]:
        """Identify potential regulatory concerns"""
        concerns = []
        
        if 'data' in text.lower() and 'privacy' not in text.lower():
            concerns.append("Data handling without privacy provisions")
        
        if 'personal information' in text.lower() and 'gdpr' not in text.lower():
            concerns.append("Personal data without GDPR compliance")
        
        return concerns 