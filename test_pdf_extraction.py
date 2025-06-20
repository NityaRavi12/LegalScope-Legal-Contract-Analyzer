#!/usr/bin/env python3
"""
Test script to debug PDF text extraction
"""

import os
import sys
from utils.text_extractor import TextExtractor

def test_pdf_extraction():
    """Test PDF text extraction with detailed logging"""
    
    print("🔍 Testing PDF Text Extraction")
    print("=" * 50)
    
    # Initialize text extractor
    te = TextExtractor()
    print(f"✅ TextExtractor initialized")
    print(f"📁 Supported formats: {te.supported_formats}")
    
    # Check if we have any PDF files in uploads
    uploads_dir = "./uploads"
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
        print(f"📄 Found {len(pdf_files)} PDF files in uploads directory")
        
        for pdf_file in pdf_files:
            filepath = os.path.join(uploads_dir, pdf_file)
            print(f"\n🔍 Testing: {pdf_file}")
            print(f"📂 File path: {filepath}")
            print(f"📏 File size: {os.path.getsize(filepath)} bytes")
            
            try:
                # Test text extraction
                print("🔄 Extracting text...")
                text = te.extract_text(filepath)
                
                if text:
                    print(f"✅ SUCCESS: Extracted {len(text)} characters")
                    print(f"📝 First 200 chars: {text[:200]}...")
                    print(f"📝 Last 200 chars: ...{text[-200:]}")
                    
                    # Test clause extraction
                    print("\n🔄 Testing clause extraction...")
                    from utils.clause_extractor import ClauseExtractor
                    ce = ClauseExtractor()
                    clauses = ce.extract_clauses(text)
                    print(f"✅ Found {len(clauses)} clauses")
                    
                    if clauses:
                        for i, clause in enumerate(clauses[:3]):  # Show first 3
                            print(f"  📋 Clause {i+1}: {clause['type']} ({len(clause['text'])} chars)")
                    
                else:
                    print("❌ FAILED: No text extracted")
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
    
    else:
        print("❌ Uploads directory not found")
    
    # Test with sample text file as comparison
    print(f"\n🔍 Testing with sample text file for comparison")
    sample_file = "./data/sample_contract.txt"
    if os.path.exists(sample_file):
        try:
            text = te.extract_text(sample_file)
            print(f"✅ Sample file: Extracted {len(text)} characters")
        except Exception as e:
            print(f"❌ Sample file error: {str(e)}")
    else:
        print("❌ Sample file not found")

if __name__ == "__main__":
    test_pdf_extraction() 