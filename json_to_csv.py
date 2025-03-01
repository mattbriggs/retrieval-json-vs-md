import json
import csv

def convert_json_to_csv(json_file, csv_file):
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract the "detailed_results" array
    results = data.get("results", [])
    
    # Define CSV column headers
    fieldnames = ["question", "expected_answer", "retrieved_answer", "f1_score"]
    
    # Write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"CSV file '{csv_file}' has been created successfully.")

# Example usage
json_file = "json_f1_result-vector-related.json"  # Change this to your actual JSON file path
csv_file = "json_f1_result-vector-related.csv"   # Change this to your desired output file name
convert_json_to_csv(json_file, csv_file)