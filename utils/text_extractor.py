import os
import logging
import re

# Optional imports with fallbacks
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = None

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

logger = logging.getLogger(__name__)

class TextExtractor:
    """Extract text from various document formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
    
    def extract_text(self, filepath):
        """
        Extract text from a document file
        
        Args:
            filepath (str): Path to the document file
            
        Returns:
            str: Extracted text content
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(filepath)
        elif file_ext == '.docx':
            return self._extract_from_docx(filepath)
        elif file_ext == '.doc':
            return self._extract_from_doc(filepath)
        elif file_ext == '.txt':
            return self._extract_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, filepath):
        """Extract text from PDF file using pdfplumber"""
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber is not installed. Please install it with: pip install pdfplumber")
        
        try:
            text = ""
            with pdfplumber.open(filepath) as pdf:  # type: ignore
                logger.info(f"PDF opened successfully. Number of pages: {len(pdf.pages)}")
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    logger.info(f"Page {i+1}: Extracted {len(page_text) if page_text else 0} characters")
                    if page_text:
                        text += page_text + "\n"
                    else:
                        logger.warning(f"Page {i+1}: No text extracted")
            
            cleaned_text = self._clean_text(text)
            logger.info(f"PDF extraction completed. Raw text: {len(text)} chars, Cleaned text: {len(cleaned_text)} chars")
            
            if not cleaned_text:
                logger.error("PDF extraction resulted in empty text")
                raise ValueError("No text could be extracted from PDF")
            
            return cleaned_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filepath}: {str(e)}")
            raise
    
    def _extract_from_docx(self, filepath):
        """Extract text from DOCX file using python-docx"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is not installed. Please install it with: pip install python-docx")
        
        try:
            doc = Document(filepath)  # type: ignore
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {filepath}: {str(e)}")
            raise
    
    def _extract_from_doc(self, filepath):
        """Extract text from DOC file (basic implementation)"""
        # Note: python-docx doesn't support .doc files
        # This would require additional libraries like antiword or textract
        raise NotImplementedError("DOC file extraction not yet implemented. Please convert to DOCX or PDF.")
    
    def _extract_from_txt(self, filepath):
        """Extract text from plain text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
            return self._clean_text(text)
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as file:
                    text = file.read()
                return self._clean_text(text)
            except Exception as e:
                logger.error(f"Error reading text file {filepath}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error reading text file {filepath}: {str(e)}")
            raise
    
    def _clean_text(self, text):
        """
        Clean and normalize extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (basic patterns)
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'\d+/\d+', '', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_document_info(self, filepath):
        """
        Get basic information about the document
        
        Args:
            filepath (str): Path to the document file
            
        Returns:
            dict: Document information
        """
        try:
            text = self.extract_text(filepath)
            return {
                'filename': os.path.basename(filepath),
                'file_size': os.path.getsize(filepath),
                'text_length': len(text),
                'word_count': len(text.split()),
                'line_count': len(text.split('\n'))
            }
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            raise 