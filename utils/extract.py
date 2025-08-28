# utils/extract.py

import re
import requests
import os
import json

def extract_tests(text):
    """Extract medical test results with strict medical test validation"""
    
    # Define actual medical test names that we want to extract
    medical_tests = {
        'hemoglobin': ['hemoglobin', 'hb', 'hgb'],
        'hematocrit': ['hematocrit', 'hct', 'packed cell volume', 'pcv'],
        'rbc': ['rbc', 'red blood cell count', 'erythrocyte count'],
        'wbc': ['wbc', 'white blood cell count', 'total leucocyte count', 'tlc', 'leukocyte count'],
        'platelet': ['platelet count', 'platelets', 'plt'],
        'mcv': ['mcv', 'mean corpuscular volume'],
        'mch': ['mch', 'mean corpuscular hemoglobin'],
        'mchc': ['mchc', 'mean corpuscular hemoglobin concentration'],
        'rdw': ['rdw', 'red cell distribution width'],
        'neutrophils': ['neutrophils', 'neutrophil', 'pmn'],
        'lymphocytes': ['lymphocytes', 'lymphocyte'],
        'monocytes': ['monocytes', 'monocyte'],
        'eosinophils': ['eosinophils', 'eosinophil'],
        'basophils': ['basophils', 'basophil'],
        'esr': ['esr', 'erythrocyte sedimentation rate'],
        'glucose': ['glucose', 'blood glucose', 'fasting glucose'],
        'urea': ['urea', 'blood urea'],
        'creatinine': ['creatinine', 'serum creatinine'],
        'bilirubin': ['bilirubin', 'total bilirubin'],
        'sgpt': ['sgpt', 'alt', 'alanine transaminase'],
        'sgot': ['sgot', 'ast', 'aspartate transaminase'],
        'cholesterol': ['cholesterol', 'total cholesterol'],
        'triglycerides': ['triglycerides', 'tg'],
        'hdl': ['hdl', 'hdl cholesterol'],
        'ldl': ['ldl', 'ldl cholesterol'],
        'iron': ['iron', 'serum iron'],
        'ferritin': ['ferritin'],
        'transferrin': ['transferrin'],
        'tibc': ['tibc', 'total iron binding capacity'],
        'vitamin_b12': ['vitamin b12', 'b12', 'cobalamin'],
        'vitamin_d': ['vitamin d', '25-oh vitamin d', '25(oh)d'],
        'folate': ['folate', 'folic acid'],
        'tsh': ['tsh', 'thyroid stimulating hormone'],
        't3': ['t3', 'triiodothyronine'],
        't4': ['t4', 'thyroxine']
    }
    
    results = []
    processed_tests = set()
    
    print("="*50)
    print("MEDICAL TEST EXTRACTION")
    print("="*50)
    
    # Clean the text first
    text = re.sub(r'\s+', ' ', text)
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if len(line) < 10:
            continue
            
        if re.search(r'\d', line) and re.search(r'[-–—]', line):
            patterns = [
                r'([A-Za-z][A-Za-z\s]{2,30}?)[\s:]+([0-9]+\.?[0-9]*)\s*([a-zA-Z/%µ/]+)\s+([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)',
                r'([A-Za-z][A-Za-z\s]{2,30}?)\s+([0-9]+\.?[0-9]*)\s+([a-zA-Z/%µ/]+)\s*\(?([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)\)?',
                r'([A-Za-z][A-Za-z\s]{2,30}?)\s+([0-9]+\.?[0-9]*)\s+([a-zA-Z/%µ/]+)\s+([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)',
                r'([A-Za-z][^\d]*?)\s+([0-9]+\.?[0-9]*)\s*([a-zA-Z/%µ/]*)\s*[^\d]*([0-9]+\.?[0-9]*)\s*[-–—]\s*([0-9]+\.?[0-9]*)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                
                if matches:
                    for match in matches:
                        try:
                            if len(match) != 5:
                                continue
                                
                            test_name, value_str, unit, low_str, high_str = match
                            
                            # Clean test name
                            original_test_name = test_name.strip()
                            test_name = test_name.strip().lower()
                            test_name = re.sub(r'[^\w\s]', ' ', test_name)
                            test_name = re.sub(r'\s+', ' ', test_name).strip()
                            
                            # Check if this is actually a medical test
                            is_medical_test = False
                            clean_test_name = ""
                            
                            for standard_name, variations in medical_tests.items():
                                for variation in variations:
                                    if variation in test_name or test_name in variation:
                                        is_medical_test = True
                                        clean_test_name = standard_name.replace('_', ' ').title()
                                        break
                                if is_medical_test:
                                    break
                            
                            # If not found in predefined tests, check for medical keywords
                            if not is_medical_test and len(test_name) > 3:
                                medical_keywords = ['vitamin', 'hemoglobin', 'glucose', 'cholesterol', 'protein', 'iron', 'calcium', 'sodium', 'potassium', 'urea', 'creatinine']
                                for keyword in medical_keywords:
                                    if keyword in test_name:
                                        is_medical_test = True
                                        clean_test_name = original_test_name.title().strip()
                                        break
                            
                            if not is_medical_test:
                                continue
                            
                            test_key = clean_test_name.lower().strip()
                            if test_key in processed_tests:
                                continue
                            
                            # Parse values
                            try:
                                value = float(value_str)
                                low = float(low_str)
                                high = float(high_str)
                            except ValueError:
                                continue
                            
                            # Sanity checks
                            if value <= 0 or low <= 0 or high <= 0 or low >= high or value > 100000:
                                continue
                            
                            # Determine status
                            if value < low:
                                status = "Low" if value >= low * 0.8 else "Very Low"
                            elif value > high:
                                status = "High" if value <= high * 1.2 else "Very High"
                            else:
                                status = "Normal"
                            
                            # Create result - we'll get AI explanation later
                            result = {
                                "test": clean_test_name,
                                "value": value,
                                "unit": unit.strip() if unit else "",
                                "ref_range": f"{low} - {high}",
                                "status": status,
                                "explanation": "",  # Will be filled by AI
                                "ref_low": low,
                                "ref_high": high
                            }
                            
                            results.append(result)
                            processed_tests.add(test_key)
                            break
                            
                        except Exception as e:
                            continue
    
    # Now get AI-powered explanations for all results
    if results:
        results = get_ai_explanations(results)
    
    print(f"\nTotal medical tests found: {len(results)}")
    return results

def get_ai_explanations(test_results):
    """Get AI-powered explanations for test results"""
    
    try:
        # Prepare the test data for AI analysis
        test_summary = []
        abnormal_tests = []
        
        for test in test_results:
            test_info = f"{test['test']}: {test['value']} {test['unit']} (Reference: {test['ref_range']}) - Status: {test['status']}"
            test_summary.append(test_info)
            
            if test['status'] != 'Normal':
                abnormal_tests.append(test_info)
        
        # Create prompt for AI analysis
        prompt = f"""
As a medical expert, please provide detailed explanations for these lab test results. For each test, provide:
1. A brief explanation of what the test measures
2. Clinical significance of the abnormal values (if any)
3. Possible causes or implications
4. Recommendations for follow-up (if needed)

Test Results:
{chr(10).join(test_summary)}

Please respond in JSON format with this structure:
{{
    "explanations": {{
        "Test Name": "Detailed explanation here",
        "Another Test": "Another explanation here"
    }}
}}

Focus especially on abnormal results: {chr(10).join(abnormal_tests) if abnormal_tests else "All results are normal"}
"""

        # Make API call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3-sonnet",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_response = response.json()
            content = ai_response['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                # Extract JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_content = content[json_start:json_end]
                    explanations = json.loads(json_content)
                    
                    # Update test results with AI explanations
                    for test in test_results:
                        test_name = test['test']
                        
                        # Try to find matching explanation
                        explanation = None
                        for key, value in explanations.get('explanations', {}).items():
                            if test_name.lower() in key.lower() or key.lower() in test_name.lower():
                                explanation = value
                                break
                        
                        if explanation:
                            test['explanation'] = explanation
                        else:
                            # Fallback to basic explanation
                            test['explanation'] = generate_basic_explanation(test['test'], test['status'])
                
                else:
                    # Fallback if JSON parsing fails
                    for test in test_results:
                        test['explanation'] = generate_basic_explanation(test['test'], test['status'])
                        
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                for test in test_results:
                    test['explanation'] = generate_basic_explanation(test['test'], test['status'])
        
        else:
            print(f"AI API call failed: {response.status_code}")
            # Fallback to basic explanations
            for test in test_results:
                test['explanation'] = generate_basic_explanation(test['test'], test['status'])
    
    except Exception as e:
        print(f"Error getting AI explanations: {str(e)}")
        # Fallback to basic explanations
        for test in test_results:
            test['explanation'] = generate_basic_explanation(test['test'], test['status'])
    
    return test_results

def generate_basic_explanation(test_name, status):
    """Generate basic explanations as fallback"""
    
    basic_explanations = {
        "Normal": f"{test_name} is within normal range.",
        "Low": f"{test_name} is below normal range, which may require medical evaluation.",
        "High": f"{test_name} is above normal range, which may require medical evaluation.",
        "Very Low": f"{test_name} is significantly below normal range, which requires immediate medical attention.",
        "Very High": f"{test_name} is significantly above normal range, which requires immediate medical attention."
    }
    
    return basic_explanations.get(status, f"{test_name} result needs to be evaluated by a healthcare provider.")

