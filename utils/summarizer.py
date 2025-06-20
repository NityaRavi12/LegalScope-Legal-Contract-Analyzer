import logging
from typing import Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logger = logging.getLogger(__name__)

class Summarizer:
    """Generate summaries of contract clauses using NLP models"""
    
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.max_length = 150
        self.min_length = 30
        
        try:
            # Initialize summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load summarization model: {e}")
            self.summarizer = None
    
    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Summarize contract text
        
        Args:
            text (str): Text to summarize
            max_length (int, optional): Maximum length of summary
            
        Returns:
            str: Generated summary
        """
        if not text or len(text.strip()) < 50:
            return text
        
        if not self.summarizer:
            return self._extractive_summarization(text)
        
        try:
            # Clean and prepare text
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text) < 100:
                return cleaned_text
            
            # Generate summary
            summary_length = max_length or self.max_length
            
            result = self.summarizer(
                cleaned_text,
                max_length=summary_length,
                min_length=self.min_length,
                do_sample=False,
                truncation=True
            )
            
            # Handle the result properly
            if (isinstance(result, list) and len(result) > 0 and 
                isinstance(result[0], dict) and 'summary_text' in result[0]):
                summary = str(result[0]['summary_text'])
            else:
                return self._extractive_summarization(text)
            
            # Post-process summary
            summary = self._postprocess_summary(summary)
            
            return summary
            
        except Exception as e:
            logger.warning(f"Summarization failed, using extractive method: {e}")
            return self._extractive_summarization(text)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for summarization
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Preprocessed text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might confuse the model
        text = text.replace('§', 'Section ')
        text = text.replace('¶', 'Paragraph ')
        
        # Limit text length for model input
        if len(text) > 1024:
            text = text[:1024]
        
        return text
    
    def _postprocess_summary(self, summary: str) -> str:
        """
        Post-process generated summary
        
        Args:
            summary (str): Raw summary
            
        Returns:
            str: Processed summary
        """
        # Clean up summary
        summary = summary.strip()
        
        # Ensure proper sentence ending
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        # Capitalize first letter
        if summary:
            summary = summary[0].upper() + summary[1:]
        
        return summary
    
    def _extractive_summarization(self, text: str) -> str:
        """
        Simple extractive summarization using sentence scoring
        
        Args:
            text (str): Text to summarize
            
        Returns:
            str: Extractive summary
        """
        import re
        from collections import Counter
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text
        
        # Score sentences based on word frequency
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        for word in stop_words:
            word_freq[word] = 0
        
        # Score sentences
        sentence_scores = {}
        for sentence in sentences:
            score = 0
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            for word in sentence_words:
                score += word_freq[word]
            sentence_scores[sentence] = score / len(sentence_words) if sentence_words else 0
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 2-3 sentences or first 200 characters
        summary_sentences = []
        char_count = 0
        
        for sentence, score in top_sentences[:3]:
            if char_count + len(sentence) < 200:
                summary_sentences.append(sentence)
                char_count += len(sentence)
            else:
                break
        
        if not summary_sentences:
            # Fallback to first sentence
            summary_sentences = [sentences[0]] if sentences else [text[:200]]
        
        summary = '. '.join(summary_sentences)
        
        # Ensure proper ending
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def summarize_clauses(self, clauses: list) -> list:
        """
        Summarize a list of clauses
        
        Args:
            clauses (list): List of clause dictionaries
            
        Returns:
            list: List of clauses with summaries
        """
        summarized_clauses = []
        
        for clause in clauses:
            if isinstance(clause, dict) and 'text' in clause:
                summary = self.summarize(clause['text'])
                clause_copy = clause.copy()
                clause_copy['summary'] = summary
                summarized_clauses.append(clause_copy)
            elif isinstance(clause, str):
                # Handle case where clause is just text
                summary = self.summarize(clause)
                summarized_clauses.append({
                    'text': clause,
                    'summary': summary
                })
            else:
                # Skip invalid clause types
                logger.warning(f"Skipping invalid clause type: {type(clause)}")
                continue
        
        return summarized_clauses
    
    def get_summary_statistics(self, original_text: str, summary: str) -> dict:
        """
        Get statistics about the summarization
        
        Args:
            original_text (str): Original text
            summary (str): Generated summary
            
        Returns:
            dict: Summary statistics
        """
        original_words = len(original_text.split())
        summary_words = len(summary.split())
        
        compression_ratio = summary_words / original_words if original_words > 0 else 0
        
        return {
            'original_length': len(original_text),
            'summary_length': len(summary),
            'original_words': original_words,
            'summary_words': summary_words,
            'compression_ratio': compression_ratio,
            'reduction_percentage': (1 - compression_ratio) * 100
        } 