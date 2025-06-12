import json
import re
from collections import defaultdict

# Unicode script ranges
UNICODE_SCRIPTS = [
    (re.compile(r'[\u4E00-\u9FFF]'), 'CJK Unified Ideographs'),
    (re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF]'), 'Japanese (Hiragana/Katakana/Kanji)'),
    (re.compile(r'[\uAC00-\uD7AF]'), 'Hangul (Korean)'),
    (re.compile(r'[\u0600-\u06FF]'), 'Arabic'),
    (re.compile(r'[\u0590-\u05FF]'), 'Hebrew'),
    (re.compile(r'[\u0900-\u097F]'), 'Devanagari (Hindi, etc.)'),
    (re.compile(r'[\u0B80-\u0BFF]'), 'Tamil'),
    (re.compile(r'[\u0E00-\u0E7F]'), 'Thai'),
    (re.compile(r'[\u0400-\u04FF]'), 'Cyrillic'),
    (re.compile(r'[\u0370-\u03FF]'), 'Greek and Coptic'),
    (re.compile(r'[\u0980-\u09FF]'), 'Bengali'),
    (re.compile(r'[\u0A80-\u0AFF]'), 'Gujarati'),
]

# Helper to classify a string
def classify_string(s):
    total = len(s)
    if total == 0:
        return {'script': 'English/ASCII', 'confidence': 1.0}
    script_counts = defaultdict(int)
    for c in s:
        found = False
        for regex, script in UNICODE_SCRIPTS:
            if regex.match(c):
                script_counts[script] += 1
                found = True
                break
        if not found and ord(c) > 127:
            script_counts['Other Non-English'] += 1
    if not script_counts:
        return {'script': 'English/ASCII', 'confidence': 1.0}
    # Find the dominant script
    dominant_script = max(script_counts, key=script_counts.get)
    confidence = script_counts[dominant_script] / total
    return {'script': dominant_script, 'confidence': round(confidence, 2)}

def main():
    with open('repo_analysis_results.json', encoding='utf-8') as f:
        data = json.load(f)
    elements = data['repository_elements']
    results = {}
    english_count = 0
    non_english_count = 0
    total_count = 0
    
    # Process elements
    for key, items in elements.items():
        results[key] = []
        for item in items:
            info = classify_string(item)
            results[key].append({'value': item, 'script': info['script'], 'confidence': info['confidence']})
            total_count += 1
            if info['script'] == 'English/ASCII':
                english_count += 1
            else:
                non_english_count += 1

    # Create structured output
    output = {
        "overall_statistics": {
            "total_elements": total_count,
            "english_ascii": {
                "count": english_count,
                "percentage": round(english_count/total_count*100, 2)
            },
            "non_english": {
                "count": non_english_count,
                "percentage": round(non_english_count/total_count*100, 2)
            }
        },
        "english_ascii_parts": {},
        "non_english_parts": {}
    }

    # Group English and non-English parts
    for key, items in results.items():
        english_items = [entry for entry in items if entry['script'] == 'English/ASCII']
        non_english_items = [entry for entry in items if entry['script'] != 'English/ASCII']
        
        if english_items:
            output["english_ascii_parts"][key] = {
                "instances": len(english_items),
                "confidence_score": round(sum(entry['confidence'] for entry in english_items) / len(english_items), 2),
                "parsed_instances": [entry['value'] for entry in english_items],
                "total_count": len(english_items)
            }
        
        if non_english_items:
            output["non_english_parts"][key] = {
                "instances": len(non_english_items),
                "confidence_score": round(sum(entry['confidence'] for entry in non_english_items) / len(non_english_items), 2),
                "parsed_instances": [f"{entry['value']}: {entry['script']} (confidence: {entry['confidence']})" 
                                  for entry in non_english_items],
                "total_count": len(non_english_items)
            }

    # Save to file
    with open('language_classification_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Print the results in a readable format
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
