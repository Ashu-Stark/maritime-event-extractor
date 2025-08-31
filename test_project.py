#!/usr/bin/env python3
"""
Comprehensive Project Test Script
Tests all major functionality before deployment
"""

import requests
import os
import time

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_PDF = "uploads/(2) IOLCOS unity SOF.pdf"


def test_frontend():
    """Test frontend accessibility"""
    print("🧪 Testing Frontend...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False


def test_api_health():
    """Test API health and basic endpoints"""
    print("🧪 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        if response.status_code == 200:
            data = response.json()
            doc_count = len(data.get('documents', []))
            print(f"✅ API healthy - Found {doc_count} documents")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_file_upload():
    """Test file upload functionality"""
    print("🧪 Testing File Upload...")
    try:
        if not os.path.exists(TEST_PDF):
            print(f"❌ Test file not found: {TEST_PDF}")
            return False
        
        with open(TEST_PDF, 'rb') as f:
            files = {
                'file': (os.path.basename(TEST_PDF), f, 'application/pdf')
            }
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get('document_id', 'N/A')
            print(f"✅ File upload successful - ID: {doc_id}")
            return doc_id
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False


def test_document_processing(document_id):
    """Test document processing"""
    print("🧪 Testing Document Processing...")
    try:
        url = f"{BASE_URL}/api/process/{document_id}"
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'N/A')
            print(f"✅ Document processing successful - Status: {status}")
            return True
        else:
            print(f"❌ Document processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        return False


def test_event_extraction(document_id):
    """Test event extraction"""
    print("🧪 Testing Event Extraction...")
    try:
        time.sleep(2)
        url = f"{BASE_URL}/api/documents/{document_id}/events"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"✅ Event extraction successful - Found {len(events)} events")
            if events:
                event_name = events[0].get('event_name', 'N/A')
                print(f"   Sample event: {event_name}")
            return True
        else:
            print(f"❌ Event extraction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Event extraction test failed: {e}")
        return False


def test_ai_chat(document_id):
    """Test AI chat functionality"""
    print("🧪 Testing AI Chat...")
    try:
        message = "What events were extracted from this document?"
        chat_data = {
            "message": message,
            "document_id": document_id
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', 'N/A')[:100]
            print(f"✅ AI chat successful - Response: {response_text}...")
            return True
        else:
            print(f"❌ AI chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI chat test failed: {e}")
        return False


def test_export_functionality(document_id):
    """Test export functionality"""
    print("🧪 Testing Export Functionality...")
    try:
        csv_url = f"{BASE_URL}/api/export/{document_id}/csv"
        response = requests.get(csv_url)
        if response.status_code == 200:
            print("✅ CSV export successful")
        else:
            print(f"❌ CSV export failed: {response.status_code}")
        
        json_url = f"{BASE_URL}/api/export/{document_id}/json"
        response = requests.get(json_url)
        if response.status_code == 200:
            print("✅ JSON export successful")
        else:
            print(f"❌ JSON export failed: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False


def test_document_summary(document_id):
    """Test document summary functionality"""
    print("🧪 Testing Document Summary...")
    try:
        url = f"{BASE_URL}/api/documents/{document_id}/summary"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            total_events = stats.get('total_events', 'N/A')
            print(f"✅ Document summary successful - Total events: {total_events}")
            return True
        else:
            print(f"❌ Document summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document summary test failed: {e}")
        return False


def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Project Test...")
    print("=" * 50)
    
    tests = [
        ("Frontend", test_frontend),
        ("API Health", test_api_health),
    ]
    
    for test_name, test_func in tests:
        if not test_func():
            print(f"❌ {test_name} test failed. Stopping tests.")
            return False
    
    document_id = test_file_upload()
    if not document_id:
        print("❌ File upload test failed. Cannot continue with processing tests.")
        return False
    
    processing_tests = [
        ("Document Processing",
         lambda: test_document_processing(document_id)),
        ("Event Extraction",
         lambda: test_event_extraction(document_id)),
        ("AI Chat", 
         lambda: test_ai_chat(document_id)),
        ("Export Functionality", 
         lambda: test_export_functionality(document_id)),
        ("Document Summary", 
         lambda: test_document_summary(document_id)),
    ]
    
    for test_name, test_func in processing_tests:
        test_func()
        print()
    
    print("=" * 50)
    print("🎉 Comprehensive test completed!")
    return True


if __name__ == "__main__":
    run_comprehensive_test()
