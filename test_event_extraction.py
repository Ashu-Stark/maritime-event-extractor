#!/usr/bin/env python3
"""
Comprehensive Event Extraction Test
Tests the trained NLP model on actual maritime documents
"""

import os
import json
import logging
from pathlib import Path
from backend.enhanced_maritime_extractor import EnhancedMaritimeExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_document(extractor, pdf_path):
    """Test event extraction on a single document"""
    print(f"\n📄 Testing: {os.path.basename(pdf_path)}")
    print("-" * 60)
    
    try:
        # Extract text from PDF
        import PyPDF2
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        if not text.strip():
            print("❌ No text extracted from PDF")
            return None
        
        print(f"📝 Text length: {len(text)} characters")
        print(f"📝 First 200 chars: {text[:200]}...")
        
        # Extract events using the enhanced extractor
        events = extractor.extract_events(text)
        
        print(f"🎯 Events found: {len(events)}")
        
        if events:
            for i, event in enumerate(events, 1):
                print(f"  {i}. {event.get('event_name', 'N/A')}")
                print(f"     Type: {event.get('event_type', 'N/A')}")
                print(f"     Start: {event.get('start_time', 'N/A')}")
                print(f"     End: {event.get('end_time', 'N/A')}")
                print(f"     Location: {event.get('location', 'N/A')}")
                print(f"     Confidence: {event.get('confidence', 'N/A')}")
                print()
        else:
            print("❌ No events extracted")
        
        return events
        
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
        return None

def test_multiple_documents():
    """Test event extraction on multiple documents"""
    print("🚀 Starting Comprehensive Event Extraction Test")
    print("=" * 70)
    
    # Initialize the enhanced extractor
    extractor = EnhancedMaritimeExtractor()
    
    # Get list of PDF files in uploads folder
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return
    
    pdf_files = list(uploads_dir.glob("*.pdf"))
    print(f"📁 Found {len(pdf_files)} PDF files for testing")
    
    # Test on a subset of files first (to avoid overwhelming output)
    test_files = pdf_files[:10]  # Test first 10 files
    
    total_events = 0
    successful_extractions = 0
    
    for pdf_file in test_files:
        events = test_single_document(extractor, str(pdf_file))
        
        if events is not None:
            successful_extractions += 1
            total_events += len(events)
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"📁 Files tested: {len(test_files)}")
    print(f"✅ Successful extractions: {successful_extractions}")
    print(f"❌ Failed extractions: {len(test_files) - successful_extractions}")
    print(f"🎯 Total events extracted: {total_events}")
    print(f"📈 Average events per document: {total_events/successful_extractions:.1f}" if successful_extractions > 0 else "📈 Average events per document: 0")
    
    # Test specific patterns
    print("\n🔍 Testing Specific Maritime Patterns:")
    test_patterns = [
        "Vessel arrived at port at 06:45 on 15/03/2024",
        "Pilot boarded the vessel at 07:00",
        "Loading commenced at 08:00",
        "Vessel berthed alongside at 09:30",
        "Weather delay from 14:00 to 16:00"
    ]
    
    for pattern in test_patterns:
        events = extractor.extract_events(pattern)
        print(f"  Pattern: {pattern}")
        print(f"    Events: {len(events)}")
        if events:
            for event in events:
                print(f"      - {event.get('event_name', 'N/A')} ({event.get('event_type', 'N/A')})")

def test_specific_document(filename):
    """Test a specific document by filename"""
    print(f"🎯 Testing specific document: {filename}")
    print("=" * 70)
    
    extractor = EnhancedMaritimeExtractor()
    pdf_path = Path("uploads") / filename
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    events = test_single_document(extractor, str(pdf_path))
    
    if events:
        print(f"\n✅ Successfully extracted {len(events)} events from {filename}")
    else:
        print(f"\n❌ No events extracted from {filename}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific document
        test_specific_document(sys.argv[1])
    else:
        # Test multiple documents
        test_multiple_documents()
