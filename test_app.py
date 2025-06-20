#!/usr/bin/env python3
"""
Simple test script for Legal Contract Analyzer
"""

import os
import sys
import tempfile
import shutil

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_text_extractor():
    """Test the text extraction functionality"""
    print("Testing text extraction...")
    
    try:
        from utils.text_extractor import TextExtractor
        
        # Create a temporary text file
        test_content = """
        This is a test contract.
        
        Section 1: Services
        The provider shall deliver services as specified.
        
        Section 2: Payment
        Payment is due within 30 days.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        # Test extraction
        extractor = TextExtractor()
        extracted_text = extractor.extract_text(temp_file)
        
        # Clean up
        os.unlink(temp_file)
        
        if extracted_text and len(extracted_text) > 0:
            print("✓ Text extraction working")
            return True
        else:
            print("✗ Text extraction failed")
            return False
            
    except Exception as e:
        print(f"✗ Text extraction error: {e}")
        return False

def test_clause_extractor():
    """Test the clause extraction functionality"""
    print("Testing clause extraction...")
    
    try:
        from utils.clause_extractor import ClauseExtractor
        
        test_text = """
        Section 1: Services
        The provider shall deliver services as specified.
        
        Section 2: Payment
        Payment is due within 30 days.
        
        Section 3: Termination
        This agreement may be terminated with 30 days notice.
        """
        
        extractor = ClauseExtractor()
        clauses = extractor.extract_clauses(test_text)
        
        if clauses and len(clauses) > 0:
            print(f"✓ Clause extraction working - found {len(clauses)} clauses")
            return True
        else:
            print("✗ Clause extraction failed")
            return False
            
    except Exception as e:
        print(f"✗ Clause extraction error: {e}")
        return False

def test_summarizer():
    """Test the summarization functionality"""
    print("Testing summarization...")
    
    try:
        from utils.summarizer import Summarizer
        
        test_text = """
        This agreement establishes the terms and conditions for the provision of software development services. 
        The provider will deliver high-quality code and documentation according to the project specifications. 
        Payment will be made monthly based on hours worked and deliverables completed.
        """
        
        summarizer = Summarizer()
        summary = summarizer.summarize(test_text)
        
        if summary and len(summary) > 0:
            print("✓ Summarization working")
            return True
        else:
            print("✗ Summarization failed")
            return False
            
    except Exception as e:
        print(f"✗ Summarization error: {e}")
        return False

def test_risk_detector():
    """Test the risk detection functionality"""
    print("Testing risk detection...")
    
    try:
        from utils.risk_detector import RiskDetector
        
        test_text = """
        This agreement automatically renews for successive terms unless terminated. 
        Late payments will incur a penalty fee of 2% per month. 
        The provider has unlimited liability for any damages.
        """
        
        detector = RiskDetector()
        risks = detector.detect_risks(test_text)
        
        if risks is not None:
            print(f"✓ Risk detection working - found {len(risks)} risks")
            return True
        else:
            print("✗ Risk detection failed")
            return False
            
    except Exception as e:
        print(f"✗ Risk detection error: {e}")
        return False

def test_sample_contract():
    """Test with the sample contract"""
    print("Testing with sample contract...")
    
    try:
        sample_file = "data/sample_contract.txt"
        if not os.path.exists(sample_file):
            print("✗ Sample contract file not found")
            return False
        
        from utils.text_extractor import TextExtractor
        from utils.clause_extractor import ClauseExtractor
        from utils.summarizer import Summarizer
        from utils.risk_detector import RiskDetector
        
        # Extract text
        extractor = TextExtractor()
        text = extractor.extract_text(sample_file)
        
        if not text:
            print("✗ Failed to extract text from sample contract")
            return False
        
        # Extract clauses
        clause_extractor = ClauseExtractor()
        clauses = clause_extractor.extract_clauses(text)
        
        # Summarize
        summarizer = Summarizer()
        summary = summarizer.summarize(text[:1000])
        
        # Detect risks
        risk_detector = RiskDetector()
        risks = risk_detector.detect_risks(text, clauses)
        
        print(f"✓ Sample contract analysis complete:")
        print(f"  - Text length: {len(text)} characters")
        print(f"  - Clauses found: {len(clauses)}")
        print(f"  - Risks detected: {len(risks)}")
        print(f"  - Summary generated: {len(summary)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Sample contract test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Legal Contract Analyzer - Test Suite")
    print("=" * 40)
    
    tests = [
        test_text_extractor,
        test_clause_extractor,
        test_summarizer,
        test_risk_detector,
        test_sample_contract
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Legal Contract Analyzer is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 