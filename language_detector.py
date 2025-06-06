import re
import langid
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import Counter

@dataclass
class LanguageDetectionResult:
    primary_language: str
    confidence: float
    language_breakdown: Dict[str, float]
    script_matches: Dict[str, Set[str]]  # Maps script name to matched text

class LanguageDetector:
    # Unicode ranges for different scripts
    SCRIPT_PATTERNS = {
        'Chinese': (r'[\u4E00-\u9FFF]', 'zh'),
        'Japanese': (r'[\u3040-\u30FF\u4E00-\u9FFF]', 'ja'),
        'Korean': (r'[\uAC00-\uD7AF]', 'ko'),
        'Arabic': (r'[\u0600-\u06FF]', 'ar'),
        'Hebrew': (r'[\u0590-\u05FF]', 'he'),
        'Hindi': (r'[\u0900-\u097F]', 'hi'),
        'Tamil': (r'[\u0B80-\u0BFF]', 'ta'),
        'Thai': (r'[\u0E00-\u0E7F]', 'th'),
        'Russian': (r'[\u0400-\u04FF]', 'ru'),
        'Greek': (r'[\u0370-\u03FF]', 'el'),
        'Bengali': (r'[\u0980-\u09FF]', 'bn'),
        'Gujarati': (r'[\u0A80-\u0AFF]', 'gu'),
    }

    def __init__(self):
        """Initialize the language detector with compiled regex patterns."""
        self.compiled_patterns = {
            name: re.compile(pattern) 
            for name, (pattern, _) in self.SCRIPT_PATTERNS.items()
        }

    def detect_script_matches(self, text: str) -> Dict[str, Set[str]]:
        """Detect script matches using regex patterns."""
        matches = {}
        for script_name, pattern in self.compiled_patterns.items():
            found_matches = set(pattern.findall(text))
            if found_matches:
                matches[script_name] = found_matches
        return matches

    def detect_language_langid(self, text: str) -> Tuple[str, float]:
        """Detect language using langid for Latin-based languages."""
        # langid requires at least some meaningful text
        if not text.strip():
            return 'unknown', 0.0
        
        lang, confidence = langid.classify(text)
        return lang, confidence

    def analyze_text(self, text: str) -> LanguageDetectionResult:
        """Analyze text using both regex patterns and langid."""
        # First check for script matches
        script_matches = self.detect_script_matches(text)
        
        # If we found specific script matches, use those
        if script_matches:
            # Count occurrences of each script
            script_counts = Counter()
            for script, matches in script_matches.items():
                script_counts[self.SCRIPT_PATTERNS[script][1]] += len(matches)
            
            total = sum(script_counts.values())
            if total > 0:
                language_breakdown = {
                    lang: count/total 
                    for lang, count in script_counts.most_common()
                }
                primary_lang = max(language_breakdown.items(), key=lambda x: x[1])[0]
                return LanguageDetectionResult(
                    primary_language=primary_lang,
                    confidence=max(language_breakdown.values()),
                    language_breakdown=language_breakdown,
                    script_matches=script_matches
                )

        # If no specific scripts found, use langid for Latin-based languages
        lang, conf = self.detect_language_langid(text)
        return LanguageDetectionResult(
            primary_language=lang,
            confidence=conf,
            language_breakdown={lang: conf},
            script_matches=script_matches
        )

    def analyze_code_elements(self, 
                            identifiers: List[str], 
                            comments: List[str], 
                            docstrings: List[str], 
                            string_literals: List[str]) -> Dict[str, LanguageDetectionResult]:
        """Analyze different code elements separately."""
        results = {}
        if keywords_argument:
            results['keywords_argument'] = self.analyze_text(' '.join(keywords_argument))
        if classes:
            results['classes'] = self.analyze_text(' '.join(classes))
        if functions:
            results['functions'] = self.analyze_text(' '.join(functions))
        if variables:
            results['variables'] = self.analyze_text(' '.join(variables))
        if literals:
            results['literals'] = self.analyze_text(' '.join(literals))
        if identifiers:
            results['identifiers'] = self.analyze_text(' '.join(identifiers))
        
        if comments:
            results['comments'] = self.analyze_text(' '.join(comments))
            
        if docstrings:
            results['docstrings'] = self.analyze_text(' '.join(docstrings))
            
        if string_literals:
            results['string_literals'] = self.analyze_text(' '.join(string_literals))
            
        return results 