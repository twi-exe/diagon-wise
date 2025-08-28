import requests
import os
from dotenv import load_dotenv
import re

load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    "Content-Type": "application/json"
}

def generate_summary(parsed_text):
    # Enhanced prompt for both structured and unstructured medical content
    prompt = (
        "You are a clinical AI assistant analyzing medical content. "
        "Provide a comprehensive analysis regardless of whether the content contains structured test results or general medical information.\n\n"
        
        "ANALYSIS APPROACH:\n"
        "1. If structured lab results are present:\n"
        "   - Compare values to reference ranges\n"
        "   - Classify as Normal/Low/High/Very Low/Very High\n"
        "   - Explain clinical significance\n\n"
        
        "2. If general medical content (reports, notes, etc.):\n"
        "   - Identify key medical findings\n"
        "   - Explain medical terminology in simple terms\n"
        "   - Highlight important health indicators\n"
        "   - Provide relevant health insights\n\n"
        
        "FORMAT: Return clean HTML with this structure:\n"
        "- <h3>Key Findings</h3>\n"
        "- <ul><li>Main medical points identified</li></ul>\n"
        "- <h3>Medical Interpretation</h3>\n"
        "- <ul><li>Explanation of findings in simple terms</li></ul>\n"
        "- <h3>Health Insights</h3>\n"
        "- <ul><li>What these findings mean for health</li></ul>\n"
        "- <h3>Recommendations</h3>\n"
        "- <ul><li>Suggested next steps or considerations</li></ul>\n\n"
        
        "GUIDELINES:\n"
        "- Use first person (speaking to the patient)\n"
        "- Use <b>bold</b> for important terms\n"
        "- Use <span style='color: red;'>red</span> for concerning findings\n"
        "- Use <span style='color: green;'>green</span> for positive findings\n"
        "- Always provide some analysis even if content is unclear\n"
        "- If no clear medical content, explain what was found\n\n"
        
        f"Medical content to analyze:\n{parsed_text}"
    )

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        ai_content = result["choices"][0]["message"]["content"].strip()
        
        # Ensure we always return something useful
        if not ai_content or len(ai_content) < 50:
            raise Exception("AI response too short or empty")
        
        return ai_content
        
    except Exception as e:
        # Fallback analysis when AI service fails
        return f"""
        <h3>Document Analysis Complete</h3>
        <ul>
            <li>Successfully processed your medical document</li>
            <li>Extracted {len(parsed_text)} characters of medical content</li>
            <li>Document appears to contain health-related information</li>
        </ul>
        <h3>Content Overview</h3>
        <ul>
            <li>Text has been extracted and is ready for review</li>
            <li>Document may contain important medical information</li>
            <li>Professional medical interpretation is recommended</li>
        </ul>
        <h3>Next Steps</h3>
        <ul>
            <li>Review the extracted text below for accuracy</li>
            <li>Share this information with your healthcare provider</li>
            <li>Keep this analysis for your medical records</li>
            <li>Consider re-uploading if text quality is poor</li>
        </ul>
        <h3>Technical Note</h3>
        <ul>
            <li>AI analysis service temporarily unavailable</li>
            <li>Basic document processing completed successfully</li>
            <li>Error details: {str(e)}</li>
        </ul>
        """

def extract_tests(text):
    """Extract medical test results with improved flexibility"""
    
    results = []
    processed_tests = set()
    
    print("="*50)
    print("MEDICAL TEST EXTRACTION DEBUG")
    print("="*50)
    print(f"Input text length: {len(text)}")
    print(f"First 500 chars: {repr(text[:500])}")
    
    # Clean the text first
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Split into lines for processing
    lines = text.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # More flexible patterns that catch common medical test formats
    patterns = [
        # Pattern 1: Test Name: Value Unit (Low-High) or Test Name: Value Unit Low-High
        r'([A-Za-z][A-Za-z\s]{1,40}?)[\s:]+([0-9]+\.?[0-9]*)\s*([a-zA-Z/%µ/]+).*?([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)',
        
        # Pattern 2: Test Name Value Unit Range (space separated)
        r'([A-Za-z][A-Za-z\s]{1,40}?)\s+([0-9]+\.?[0-9]*)\s+([a-zA-Z/%µ/]+)\s+([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)',
        
        # Pattern 3: More flexible - any text followed by numbers and range
        r'([A-Za-z][^\d]*?)\s+([0-9]+\.?[0-9]*)\s*([a-zA-Z/%µ/]*)\s*[^\d]*([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)'
    ]
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if len(line) < 5:  # Skip very short lines
            continue
            
        print(f"Line {line_num}: '{line}'")
        
        # Check if line contains numbers and a dash (potential test result)
        if re.search(r'\d', line) and re.search(r'[-–—]', line):
            print(f"  -> Line contains numbers and dash, analyzing...")
            
            for pattern_num, pattern in enumerate(patterns):
                matches = re.findall(pattern, line, re.IGNORECASE)
                
                if matches:
                    print(f"  -> Pattern {pattern_num + 1} found {len(matches)} matches")
                    
                    for match in matches:
                        try:
                            if len(match) == 5:
                                test_name, value_str, unit, low_str, high_str = match
                            else:
                                continue
                            
                            # Clean up test name
                            test_name = clean_test_name(test_name)
                            print(f"    -> Cleaned test name: '{test_name}'")
                            
                            # Skip if test name is too short or invalid
                            if len(test_name) < 2:
                                print(f"    -> Skipped: test name too short")
                                continue
                            
                            # Skip if already processed (case insensitive)
                            test_key = test_name.lower().strip()
                            if test_key in processed_tests:
                                print(f"    -> Skipped: already processed")
                                continue
                            
                            # Parse values
                            try:
                                value = float(value_str)
                                low = float(low_str)
                                high = float(high_str)
                            except ValueError as e:
                                print(f"    -> Skipped: value parsing error - {e}")
                                continue
                            
                            # Basic sanity checks
                            if value <= 0 or low <= 0 or high <= 0:
                                print(f"    -> Skipped: negative or zero values")
                                continue
                                
                            if low >= high:
                                print(f"    -> Skipped: invalid range (low >= high)")
                                continue
                            
                            # Skip extreme values that are likely OCR errors
                            if value > 1000000 or low > 1000000 or high > 1000000:
                                print(f"    -> Skipped: extreme values")
                                continue
                            
                            # Determine status
                            status = determine_status(value, low, high)
                            ref_range = f"{low} - {high}"
                            
                            # Generate explanation
                            explanation = generate_explanation(test_name, status, value, unit)
                            
                            result = {
                                "test": test_name,
                                "value": value,
                                "unit": unit.strip() if unit else "",
                                "ref_range": ref_range,
                                "status": status,
                                "explanation": explanation,
                                "ref_low": low,
                                "ref_high": high
                            }
                            
                            results.append(result)
                            processed_tests.add(test_key)
                            print(f"    -> ✓ Added: {test_name} = {value} {unit} ({status})")
                            break  # Stop trying other patterns for this line
                            
                        except Exception as e:
                            print(f"    -> Error processing match {match}: {e}")
                            continue
                else:
                    print(f"  -> Pattern {pattern_num + 1}: No matches")
        else:
            print(f"  -> Skipped: no numbers or dash")
    
    print(f"\nTotal results found: {len(results)}")
    print("="*50)
    return results

def clean_test_name(name):
    """Clean and normalize test names"""
    if not name:
        return ""
    
    name = name.strip()
    
    # Remove common OCR artifacts
    name = re.sub(r'\b[A-Z]{1}\b(?![a-z])', '', name)  # Remove isolated capital letters
    name = re.sub(r'[^\w\s]', ' ', name)  # Remove special chars except word chars and spaces
    name = re.sub(r'\s+', ' ', name).strip()  # Normalize spaces
    
    # Remove trailing/leading numbers
    name = re.sub(r'^\d+\s*', '', name)  # Remove leading numbers
    name = re.sub(r'\s*\d+$', '', name)  # Remove trailing numbers
    
    return name.title().strip()

def determine_status(value, low, high):
    """Determine if a test result is normal, low, or high"""
    if value < low:
        return "Low" if value >= low * 0.8 else "Very Low"
    elif value > high:
        return "High" if value <= high * 1.2 else "Very High"
    else:
        return "Normal"

def generate_explanation(test_name, status, value, unit):
    """Generate explanations for test results"""
    
    # Basic explanations based on status
    if status == "Normal":
        return f"{test_name} level is within normal range."
    elif status == "Low":
        return f"{test_name} is below normal range, which may require medical attention."
    elif status == "Very Low":
        return f"{test_name} is significantly below normal range, which requires immediate medical attention."
    elif status == "High":
        return f"{test_name} is above normal range, which may require medical attention."
    elif status == "Very High":
        return f"{test_name} is significantly above normal range, which requires immediate medical attention."
    else:
        return f"{test_name} result needs to be evaluated by a healthcare provider."
