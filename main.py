import os
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from File_parser import RepoElementParser
from language_detection import classify_string
import subprocess

def setup_directories(repo_name: str, repo_number: int) -> tuple:
    """Create necessary directories for output with repository-specific folders."""
    base_dir = f"output/repo_{repo_number}_{repo_name}"
    directories = {
        'base': base_dir,
        'json': os.path.join(base_dir, 'json'),
        'charts': os.path.join(base_dir, 'charts'),
        'file_charts': os.path.join(base_dir, 'charts', 'file_distributions')
    }
    
    for directory in directories.values():
        os.makedirs(directory, exist_ok=True)
    
    return directories

def load_repositories() -> list:
    """Load repository URLs from a configuration file."""
    try:
        with open('repositories.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: repositories.txt not found. Please create it with repository URLs.")
        return []

def create_file_element_bar_chart(file_name: str, english_elements: dict, non_english_elements: dict, output_dir: str):
    """Create a bar chart showing English vs Non-English distribution across parsed categories for a single file."""
    categories = ["identifiers", "variables", "literals", "comments", "docstrings", "functions", "classes"]
    
    # Prepare data for plotting
    english_counts = [len(english_elements.get(cat, [])) for cat in categories]
    non_english_counts = [len(non_english_elements.get(cat, [])) for cat in categories]
    
    # Create figure and axis
    plt.figure(figsize=(15, 8))
    x = np.arange(len(categories))
    width = 0.35
    
    # Create bars
    plt.bar(x - width/2, english_counts, width, label='English', color='#2ecc71')
    plt.bar(x + width/2, non_english_counts, width, label='Non-English', color='#e74c3c')
    
    # Customize the chart
    plt.xlabel('Element Categories')
    plt.ylabel('Count')
    plt.title(f'Language Distribution in {file_name}')
    plt.xticks(x, categories, rotation=45, ha='right')
    plt.legend()
    
    # Add value labels on top of bars
    for i, v in enumerate(english_counts):
        plt.text(i - width/2, v, str(v), ha='center', va='bottom')
    for i, v in enumerate(non_english_counts):
        plt.text(i + width/2, v, str(v), ha='center', va='bottom')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{file_name}_language_distribution.png'))
    plt.close()

def create_overall_language_pie_chart(english_count: int, non_english_count: int, output_path: str, repo_name: str):
    """Create a pie chart for overall English vs Non-English distribution in the repository."""
    labels = ['English/ASCII', 'Non-English']
    sizes = [english_count, non_english_count]
    total = english_count + non_english_count
    
    if total == 0:
        print(f"No elements to plot for overall language distribution in {repo_name}.")
        return

    percentages = [s / total * 100 for s in sizes]

    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=[f'{l} ({p:.1f}%)' for l, p in zip(labels, percentages)], autopct='', startangle=90, colors=['#2ecc71', '#e74c3c'])
    plt.axis('equal')
    plt.title(f'Overall Language Distribution in {repo_name}')
    plt.savefig(output_path)
    plt.close()

def create_programming_language_pie_chart(language_distribution: dict, output_path: str, repo_name: str):
    """Create a pie chart for programming language distribution in the repository."""
    if not language_distribution:
        print(f"No programming languages to plot for {repo_name}.")
        return
    
    languages = list(language_distribution.keys())
    counts = list(language_distribution.values())
    total = sum(counts)
    percentages = [c / total * 100 for c in counts]

    plt.figure(figsize=(10, 8))
    plt.pie(counts, labels=[f'{l} ({p:.1f}%)' for l, p in zip(languages, percentages)], autopct='', startangle=90)
    plt.axis('equal')
    plt.title(f'Programming Language Distribution in {repo_name}')
    plt.savefig(output_path)
    plt.close()

def create_script_pie_chart(non_english_elements: dict, output_path: str, repo_name: str):
    """Create a pie chart for non-English script distribution in the repository."""
    script_counts = defaultdict(int)
    for script, element_types in non_english_elements.items():
        for elements in element_types.values():
            script_counts[script] += len(elements)

    if not script_counts:
        print(f"No non-English scripts to plot for {repo_name}.")
        return
    
    scripts = list(script_counts.keys())
    counts = list(script_counts.values())
    total = sum(counts)
    percentages = [c / total * 100 for c in counts]

    plt.figure(figsize=(10, 8))
    plt.pie(counts, labels=[f'{s} ({p:.1f}%)' for s, p in zip(scripts, percentages)], autopct='', startangle=90)
    plt.axis('equal')
    plt.title(f'Non-English Script Distribution in {repo_name}')
    plt.savefig(output_path)
    plt.close()

def create_overall_element_bar_chart(english_elements: dict, non_english_elements: dict, output_path: str, repo_name: str):
    """Create a bar chart for overall English vs Non-English element distribution by category in the repository."""
    categories = ["identifiers", "variables", "literals", "comments", "docstrings", "functions", "classes"]
    
    # Aggregate counts for the entire repository
    overall_english_counts = [sum(len(english_elements.get(cat, [])) for file_data in [english_elements] for cat in categories if cat in file_data) for cat in categories]
    overall_non_english_counts = [sum(len(non_english_elements.get(script, {}).get(cat, [])) for script in non_english_elements for cat in categories if cat in non_english_elements.get(script, {})) for cat in categories]

    # The above aggregation logic is flawed if `english_elements` and `non_english_elements` are already the *flattened* repo-level summaries.
    # Let's assume the passed `english_elements` and `non_english_elements` are the aggregated ones, as intended for `analyze_repository`.
    # Correct aggregation:
    overall_english_counts = [len(english_elements.get(cat, [])) for cat in categories]
    # For non_english_elements, we need to flatten across scripts first, then count by category.
    # This should be handled by `flatten_by_category` before passing.
    # Let's ensure non_english_elements is already flattened when passed to this function, or flatten it here.
    
    # Re-using the flatten_by_category logic for non_english_elements to get total counts per category.
    flattened_non_english_for_chart = {
        cat: list(set(
            element
            for script_elements in non_english_elements.values()
            for element in script_elements.get(cat, [])
        ))
        for cat in categories
    }
    overall_non_english_counts = [len(flattened_non_english_for_chart.get(cat, [])) for cat in categories]


    if not any(overall_english_counts) and not any(overall_non_english_counts):
        print(f"No elements to plot for overall element distribution bar chart in {repo_name}.")
        return

    plt.figure(figsize=(15, 8))
    x = np.arange(len(categories))
    width = 0.35
    
    plt.bar(x - width/2, overall_english_counts, width, label='English', color='#2ecc71')
    plt.bar(x + width/2, overall_non_english_counts, width, label='Non-English', color='#e74c3c')
    
    plt.xlabel('Element Categories')
    plt.ylabel('Count')
    plt.title(f'Overall Language Distribution by Element Category in {repo_name}')
    plt.xticks(x, categories, rotation=45, ha='right')
    plt.legend()
    
    for i, v in enumerate(overall_english_counts):
        if v > 0: # Only show label if count is greater than 0
            plt.text(i - width/2, v, str(v), ha='center', va='bottom')
    for i, v in enumerate(overall_non_english_counts):
        if v > 0: # Only show label if count is greater than 0
            plt.text(i + width/2, v, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def analyze_repository(repo_url: str, repo_number: int) -> dict:
    """Analyze a single repository and generate all required outputs."""
    try:
        # Setup directories
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        directories = setup_directories(repo_name, repo_number)
        
        # Define categories for consistent use
        categories = ["identifiers", "variables", "literals", "comments", "docstrings", "functions", "classes"]

        # Initialize parser and analyze repository
        parser = RepoElementParser()
        analysis_results = parser.analyze_repo(repo_url)
        
        if not analysis_results or not analysis_results.get('success', False):
            print(f"Error analyzing repository: {analysis_results.get('error', 'Unknown error')}")
            return None
            
        # Process language classification
        language_stats = defaultdict(int)
        file_stats = {}
        total_english = 0
        total_non_english = 0
        total_elements = 0
        
        # Initialize categorized elements for repository-level summary
        non_english_elements = defaultdict(lambda: defaultdict(list))
        english_elements = defaultdict(list)
        
        # Process each file's elements
        for file_analysis in analysis_results['file_analyses']:
            if not file_analysis['success']:
                continue
                
            file_path = file_analysis['file_path']
            file_name = os.path.basename(file_path)
            language = file_analysis['language']
            language_stats[language] += 1
            
            # Initialize file-specific element collections
            file_english_elements = defaultdict(list)
            file_non_english_elements = defaultdict(list)
            
            # Process each element type
            for element_type, elements in file_analysis['elements'].items():
                for element in elements:
                    if isinstance(element, (str, int, float)):
                        classification = classify_string(str(element))
                        if classification['script'] == 'English/ASCII':
                            total_english += 1
                            english_elements[element_type].append(str(element))
                            file_english_elements[element_type].append(str(element))
                        else:
                            total_non_english += 1
                            non_english_elements[classification['script']][element_type].append(str(element))
                            file_non_english_elements[element_type].append(str(element))
                        total_elements += 1
            
            # Create bar chart for this file
            create_file_element_bar_chart(
                file_name,
                file_english_elements,
                file_non_english_elements,
                directories['file_charts']
            )
            
            # Calculate percentages for this file
            total_file_elements = sum(len(file_english_elements.get(cat, [])) for cat in categories) + \
                                  sum(len(file_non_english_elements.get(cat, [])) for cat in categories)

            if total_file_elements > 0:
                file_stats[file_name] = {
                    'total_elements': total_file_elements
                }
            else:
                file_stats[file_name] = {
                    'total_elements': 0
                }
        
        # Create repository summary
        repo_summary = {
            'repository_url': repo_url,
            'repository_name': repo_name,
            'total_files': analysis_results['total_files'],
            'analyzed_files': analysis_results['analyzed_files'],
            'total_elements': total_elements,
            'language_distribution': dict(language_stats),
            'file_statistics': file_stats
        }
        
        # Group non-English and English elements by their parsed categories for JSON output
        def flatten_by_category_for_json(elements_dict):
            categories = ["identifiers", "variables", "literals", "comments", "docstrings", "functions", "classes"]
            result = defaultdict(list)
            if isinstance(elements_dict, defaultdict):
                for script_elements in elements_dict.values(): # Iterate through scripts
                    if isinstance(script_elements, defaultdict):
                        for cat, elements in script_elements.items():
                            if isinstance(elements, list):
                                result[cat].extend(elements)
            else: # If it's already flattened (e.g., english_elements)
                for cat, elements in elements_dict.items():
                    if isinstance(elements, list):
                        result[cat].extend(elements)
            return {cat: list(set(val)) for cat, val in result.items()}

        # Create structured output
        output = {
            "repository_summary": {
                "repository_url": repo_url,
                "repository_name": repo_name,
                "total_files": analysis_results['total_files'],
                "analyzed_files": analysis_results['analyzed_files'],
                "total_elements": total_elements,
                "language_distribution": dict(language_stats)
            },
            "detected_scripts": list(set(script for script in non_english_elements.keys())),
            "non_english_characters": flatten_by_category_for_json(non_english_elements),
            "english_characters": flatten_by_category_for_json(english_elements)
        }
        
        # Save structured output
        output_file = os.path.join(directories['json'], 'analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        
        # Generate overall charts
        create_overall_language_pie_chart(total_english, total_non_english, 
                                          os.path.join(directories['charts'], 'overall_language_distribution.png'), repo_name)
        create_programming_language_pie_chart(language_stats, 
                                              os.path.join(directories['charts'], 'programming_language_distribution.png'), repo_name)
        create_script_pie_chart(non_english_elements, 
                                  os.path.join(directories['charts'], 'non_english_script_distribution.png'), repo_name)
        create_overall_element_bar_chart(english_elements, non_english_elements, 
                                         os.path.join(directories['charts'], 'overall_element_distribution.png'), repo_name)

        return repo_summary
        
    except Exception as e:
        print(f"Error analyzing repository {repo_url}: {str(e)}")
        return None

def main():
    # Load repositories
    repositories = load_repositories()
    if not repositories:
        return
    
    # Process each repository
    for i, repo_url in enumerate(repositories, 1):
        print(f"\nProcessing repository {i}: {repo_url}")
        analyze_repository(repo_url, i)
    
    print("\nAnalysis Complete!")
    print("="*50)

if __name__ == "__main__":
    main()
