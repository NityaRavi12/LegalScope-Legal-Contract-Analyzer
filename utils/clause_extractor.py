import re
import logging
from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

class ClauseExtractor:
    """Extract and classify contract clauses using NLP"""
    
    def __init__(self):
        self.clause_types = [
            'Termination',
            'Confidentiality',
            'Liability',
            'Indemnification',
            'Payment',
            'Governing Law',
            'Dispute Resolution',
            'Force Majeure',
            'Assignment',
            'Amendments',
            'Notices',
            'Severability',
            'Entire Agreement',
            'Waiver',
            'Survival'
        ]
        
        # Initialize zero-shot classifier for clause classification
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            logger.warning(f"Could not initialize classifier: {e}")
            self.classifier = None
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract clauses from contract text
        
        Args:
            text (str): Contract text
            
        Returns:
            List[Dict]: List of extracted clauses with type and text
        """
        try:
            # Check if text is valid
            if not text or not isinstance(text, str):
                logger.warning("Invalid or empty text provided for clause extraction")
                return []
            
            # Split text into potential clauses
            clauses = self._segment_text(text)
            
            # Classify each clause
            classified_clauses = []
            for clause in clauses:
                # Add null check to prevent NoneType error
                if clause is not None and isinstance(clause, str) and len(clause.strip()) > 50:
                    clause_type = self._classify_clause(clause)
                    classified_clauses.append({
                        'type': clause_type,
                        'text': clause.strip(),
                        'confidence': 0.8  # Placeholder confidence
                    })
            
            return classified_clauses
            
        except Exception as e:
            logger.error(f"Error extracting clauses: {str(e)}")
            return []
    
    def _segment_text(self, text: str) -> List[str]:
        """
        Segment text into potential clauses
        
        Args:
            text (str): Contract text
            
        Returns:
            List[str]: List of text segments
        """
        if not text or len(text.strip()) < 50:
            return []
        
        # Split by common clause headers
        clause_patterns = [
            r'\b\d+\.\s*[A-Z][^.]*\.',  # Numbered clauses
            r'\b[A-Z][A-Z\s]+:?\s*\n',  # ALL CAPS headers
            r'\b(Article|Section|Clause)\s+\d+',  # Article/Section headers
            r'\b(Termination|Confidentiality|Liability|Indemnification|Payment|Governing Law|Dispute Resolution|Force Majeure|Assignment|Amendments|Notices|Severability|Entire Agreement|Waiver|Survival)\b'
        ]
        
        # Combine patterns
        pattern = '|'.join(clause_patterns)
        
        # Split text at clause boundaries
        segments = re.split(pattern, text, flags=re.IGNORECASE)
        
        # Clean and filter segments
        cleaned_segments = []
        for segment in segments:
            if segment and len(segment.strip()) > 20:  # Minimum length
                cleaned_segments.append(segment.strip())
        
        # If no segments found with patterns, try sentence-based segmentation
        if not cleaned_segments:
            logger.info("No clauses found with patterns, using sentence-based segmentation")
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                if sentence and len(sentence.strip()) > 50:  # Longer sentences as potential clauses
                    cleaned_segments.append(sentence.strip())
        
        # If still no segments, use paragraph-based segmentation
        if not cleaned_segments:
            logger.info("No sentences found, using paragraph-based segmentation")
            paragraphs = text.split('\n\n')
            for paragraph in paragraphs:
                if paragraph and len(paragraph.strip()) > 30:
                    cleaned_segments.append(paragraph.strip())
        
        logger.info(f"Segmented text into {len(cleaned_segments)} potential clauses")
        return cleaned_segments
    
    def _classify_clause(self, clause_text: str) -> str:
        """
        Classify a clause into one of the predefined types
        
        Args:
            clause_text (str): Text of the clause
            
        Returns:
            str: Classified clause type
        """
        if not self.classifier:
            return self._rule_based_classification(clause_text)
        
        try:
            # Use zero-shot classification
            result = self.classifier(
                clause_text[:500],  # Limit text length
                candidate_labels=self.clause_types,
                hypothesis_template="This text is about {}."
            )
            
            # Handle the result properly
            if isinstance(result, dict) and 'labels' in result and result['labels']:
                return str(result['labels'][0])
            else:
                return self._rule_based_classification(clause_text)
            
        except Exception as e:
            logger.warning(f"Classification failed, using rule-based: {e}")
            return self._rule_based_classification(clause_text)
    
    def _rule_based_classification(self, clause_text: str) -> str:
        """
        Rule-based classification using keyword matching
        
        Args:
            clause_text (str): Text of the clause
            
        Returns:
            str: Classified clause type
        """
        clause_text_lower = clause_text.lower()
        
        # Define keyword patterns for each clause type
        patterns = {
            'Termination': [
                r'\bterminat(e|ion|ing)\b',
                r'\bend\s+of\s+term\b',
                r'\bcancel(lation)?\b',
                r'\bexpir(e|ation)\b'
            ],
            'Confidentiality': [
                r'\bconfidential(ity)?\b',
                r'\bnon-disclosure\b',
                r'\bsecret(s)?\b',
                r'\bproprietary\b',
                r'\bprivacy\b'
            ],
            'Liability': [
                r'\bliability\b',
                r'\blimit(ed)?\s+liability\b',
                r'\bdamages\b',
                r'\bresponsibility\b',
                r'\baccountable\b'
            ],
            'Indemnification': [
                r'\bindemnif(y|ication)\b',
                r'\bhold\s+harmless\b',
                r'\bdefend\b',
                r'\bcompensate\b'
            ],
            'Payment': [
                r'\bpayment\b',
                r'\binvoice\b',
                r'\bbilling\b',
                r'\bprice\b',
                r'\bfee(s)?\b',
                r'\bamount\b'
            ],
            'Governing Law': [
                r'\bgoverning\s+law\b',
                r'\bjurisdiction\b',
                r'\blaw\s+of\s+[a-z\s]+\b',
                r'\bvenue\b'
            ],
            'Dispute Resolution': [
                r'\bdispute\b',
                r'\barbitration\b',
                r'\bmediation\b',
                r'\blitigation\b',
                r'\bconflict\b'
            ],
            'Force Majeure': [
                r'\bforce\s+majeure\b',
                r'\bact\s+of\s+god\b',
                r'\bunforeseen\b',
                r'\bcircumstances\b'
            ],
            'Assignment': [
                r'\bassign(ment)?\b',
                r'\btransfer\b',
                r'\bsubcontract\b'
            ],
            'Amendments': [
                r'\bamend(ment)?\b',
                r'\bmodif(y|ication)\b',
                r'\bchange\b'
            ],
            'Notices': [
                r'\bnotice\b',
                r'\bnotification\b',
                r'\bcommunicat(e|ion)\b'
            ],
            'Severability': [
                r'\bseverability\b',
                r'\bseverable\b',
                r'\bseparate\b'
            ],
            'Entire Agreement': [
                r'\bentire\s+agreement\b',
                r'\bcomplete\s+agreement\b',
                r'\bwhole\s+agreement\b'
            ],
            'Waiver': [
                r'\bwaiv(e|er)\b',
                r'\bforfeit\b',
                r'\babandon\b'
            ],
            'Survival': [
                r'\bsurviv(e|al)\b',
                r'\bcontinue\b',
                r'\bremain\b'
            ]
        }
        
        # Score each clause type
        scores = {}
        for clause_type, pattern_list in patterns.items():
            score = 0
            for pattern in pattern_list:
                matches = re.findall(pattern, clause_text_lower)
                score += len(matches)
            scores[clause_type] = score
        
        # Return the clause type with highest score
        if scores:
            return max(scores.keys(), key=lambda k: scores[k])
        else:
            return 'Other'
    
    def get_clause_statistics(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about extracted clauses
        
        Args:
            clauses (List[Dict]): List of extracted clauses
            
        Returns:
            Dict: Statistics about clauses
        """
        if not clauses:
            return {}
        
        type_counts = {}
        total_length = 0
        
        for clause in clauses:
            clause_type = clause['type']
            type_counts[clause_type] = type_counts.get(clause_type, 0) + 1
            total_length += len(clause['text'])
        
        return {
            'total_clauses': len(clauses),
            'type_distribution': type_counts,
            'average_clause_length': total_length / len(clauses),
            'most_common_type': max(type_counts.keys(), key=lambda k: type_counts[k]) if type_counts else None
        } 