from git_cloner import RepoParser
from language_detector import LanguageDetector
from typing import Dict, List, Any
import json
from dataclasses import asdict, dataclass
from collections import defaultdict

@dataclass
class ElementSummary:
    total_count: int
    non_english_count: int
    language_distribution: Dict[str, int]
    instances: List[str]

@dataclass
class FileAnalysis:
    file_path: str
    primary_language: str
    elements_analysis: Dict[str, Any]
    language_breakdown: Dict[str, float]
    #script_matches: Dict[str, List[str]]

class RepoLanguageAnalyzer:
    def __init__(self):
        self.repo_parser = RepoParser()
        self.language_detector = LanguageDetector()
    
    def analyze_file_elements(self, elements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze each type of code element for language composition."""
        analysis = {}
        
        for element_type, items in elements.items():
            if not items:
                continue
                
            items_text = ' '.join(str(item) for item in items)
            detection_result = self.language_detector.analyze_text(items_text)
            
            # script_matches = {
            #     script: list(matches) 
            #     for script, matches in detection_result.script_matches.items()
            # }
            
            analysis[element_type] = {
                'primary_language': detection_result.primary_language,
                'confidence': detection_result.confidence,
                'language_breakdown': detection_result.language_breakdown,
                #'script_matches': script_matches,
                'instances': items  # Store the actual instances
            }
        
        return analysis

    def create_element_summary(self, instances: List[str], lang_analysis: Dict) -> ElementSummary:
        """Create a summary for a specific element type."""
        total_count = len(instances)
        non_english_count = 0
        lang_dist = defaultdict(int)

        # Count instances by language
        for instance in instances:
            detection = self.language_detector.analyze_text(instance)
            if detection.primary_language != 'en':
                non_english_count += 1
            lang_dist[detection.primary_language] += 1

        return ElementSummary(
            total_count=total_count,
            non_english_count=non_english_count,
            language_distribution=dict(lang_dist),
            instances=instances
        )

    def analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """Analyze a repository for language usage across different code elements."""
        repo_path = self.repo_parser.clone_repo(repo_url)
        if not repo_path:
            return {'error': 'Failed to clone repository'}

        files = self.repo_parser.find_supported_files(repo_path)
        
        # Initialize repository-wide element collectors
        repo_elements = defaultdict(list)
        file_analyses = []
        
        # Analyze each file and collect elements
        for file_path in files:
            parse_result = self.repo_parser.parse_file(file_path)
            if not parse_result:
                continue
                
            elements_analysis = self.analyze_file_elements(parse_result['elements'])
            
            # Collect elements for repository-wide analysis
            for element_type, analysis in elements_analysis.items():
                repo_elements[element_type].extend(analysis['instances'])
            
            # Create file analysis
            all_text = ' '.join(
                ' '.join(str(item) for item in items)
                for items in parse_result['elements'].values()
                if items
            )
            file_lang_result = self.language_detector.analyze_text(all_text)
            
            analysis = FileAnalysis(
                file_path=file_path,
                primary_language=file_lang_result.primary_language,
                elements_analysis=elements_analysis,
                language_breakdown=file_lang_result.language_breakdown,
                #script_matches={k: list(v) for k, v in file_lang_result.script_matches.items()}
            )
            file_analyses.append(asdict(analysis))

        # Create repository-wide summary
        element_summaries = {}
        for element_type, instances in repo_elements.items():
            element_analysis = self.analyze_file_elements({element_type: instances})[element_type]
            element_summaries[element_type] = asdict(
                self.create_element_summary(instances, element_analysis)
            )

        return {
            'repository_url': repo_url,
            'total_files_analyzed': len(files),
            'summary': {
                'element_counts': {
                    element_type: {
                        'total': summary['total_count'],
                        'non_english': summary['non_english_count'],
                        'language_distribution': summary['language_distribution']
                    }
                    for element_type, summary in element_summaries.items()
                }
            },
            'detailed_elements': {
                element_type: {
                    'instances': summary['instances']
                }
                for element_type, summary in element_summaries.items()
            },
            'file_analyses': file_analyses
        }

def format_summary(results: Dict[str, Any]) -> str:
    """Format the analysis results into a readable summary."""
    summary = []
    summary.append(f"Repository Analysis Summary for: {results['repository_url']}")
    summary.append(f"Total Files Analyzed: {results['total_files_analyzed']}\n")
    
    summary.append("Element Statistics:")
    summary.append("-" * 50)
    
    for element_type, counts in results['summary']['element_counts'].items():
        summary.append(f"\n{element_type.upper()}:")
        summary.append(f"  Total Count: {counts['total']}")
        summary.append(f"  Non-English Count: {counts['non_english']}")
        summary.append("  Language Distribution:")
        for lang, count in counts['language_distribution'].items():
            summary.append(f"    - {lang}: {count}")
    
    summary.append("\n" + "=" * 50 + "\n")
    summary.append("Detailed Instances by Category:")
    summary.append("=" * 50)
    
    for element_type, details in results['detailed_elements'].items():
        summary.append(f"\n{element_type.upper()} INSTANCES:")
        for instance in details['instances']:
            summary.append(f"  - {instance}")
    
    return "\n".join(summary)

def main():
    analyzer = RepoLanguageAnalyzer()
    
    repo_url = input("Enter GitHub repository URL: ")
    results = analyzer.analyze_repo(repo_url)
    
    # Save detailed results to JSON
    json_output_file = "language_analysis_results.json"
    with open(json_output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save formatted summary to text file
    summary_output_file = "language_analysis_summary.txt"
    with open(summary_output_file, 'w', encoding='utf-8') as f:
        f.write(format_summary(results))
    
    print(f"\nAnalysis complete!")
    print(f"Detailed results saved to: {json_output_file}")
    print(f"Formatted summary saved to: {summary_output_file}")
    
    # Print summary to console
    print("\nSummary:")
    print("=" * 50)
    print(format_summary(results))

if __name__ == "__main__":
    main() 