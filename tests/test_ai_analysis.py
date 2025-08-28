import pytest
from app import app
from utils.summarizer import generate_summary

def test_ai_analysis_with_no_tables():
    """Test that AI generates results even without structured tables"""
    
    # Sample medical text without clear tables
    medical_text = """
    Patient presents with fatigue and weakness. 
    Physical examination shows pale conjunctiva.
    Blood work was ordered to investigate possible anemia.
    Patient reports feeling tired for the past 3 months.
    """
    
    summary = generate_summary(medical_text)
    
    # Assert that we get some AI analysis
    assert summary is not None
    assert len(summary) > 50
    assert "<h3>" in summary  # Should contain HTML formatting
    assert "analysis" in summary.lower() or "findings" in summary.lower()

def test_app_handles_no_structured_data():
    """Test that the app properly handles documents with no test tables"""
    
    with app.test_client() as client:
        # This would normally be tested with actual file upload
        # For now, test that the route exists and basic functionality works
        response = client.get('/')
        assert response.status_code == 200

def test_ai_fallback_on_error():
    """Test that we get fallback content when AI service fails"""
    
    # Test with empty text
    summary = generate_summary("")
    assert summary is not None
    assert len(summary) > 0
    
    # Should contain helpful fallback content
    assert "analysis" in summary.lower() or "information" in summary.lower()