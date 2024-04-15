import csv
import re

def parse_related_weaknesses(related_weaknesses_str):
    # Use regex to find all CWE ID patterns
    cwe_id_pattern = r'CWE ID:(\d+)'
    cwe_ids = re.findall(cwe_id_pattern, related_weaknesses_str)
    return cwe_ids

def construct_adjacency_list(csv_file_path):
    adjacency_list = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cwe_id = row['CWE-ID']  # Assuming the first column header is 'CWE ID'
            related_weaknesses_str = row['Related Weaknesses']
            related_cwe_ids = parse_related_weaknesses(related_weaknesses_str)
            # Initialize the list for the CWE ID if not already present
            if cwe_id not in adjacency_list:
                adjacency_list[cwe_id] = []
            
            # Add each related CWE ID to the adjacency list
            for related_cwe_id in related_cwe_ids:
                # Ensure there's no duplication and self-reference
                if related_cwe_id not in adjacency_list[cwe_id] and cwe_id != related_cwe_id:
                    adjacency_list[cwe_id].append(related_cwe_id)
                    
                # Ensure mutual adjacency if not already handled by the data
                if related_cwe_id not in adjacency_list:
                    adjacency_list[related_cwe_id] = [cwe_id]
                elif cwe_id not in adjacency_list[related_cwe_id]:
                    adjacency_list[related_cwe_id].append(cwe_id)

    return adjacency_list

# Replace 'your_cwe_data.csv' with the path to your actual CSV file
csv_file_path = '../materials/cwe1000.csv'
adjacency_list = construct_adjacency_list(csv_file_path)

# Example: Print the adjacency list
# for cwe_id, related_cwe_ids in adjacency_list.items():
#     print(f"{cwe_id}: {related_cwe_ids}")

def dfs(adjacency_list, start_cwe_id, visited=None):
    if visited is None:
        visited = set()
    visited.add(start_cwe_id)
    for related_cwe_id in adjacency_list.get(start_cwe_id, []):
        if related_cwe_id not in visited:
            dfs(adjacency_list, related_cwe_id, visited)
    return visited

# Example usage
start_cwe_id = '20'  # Input CWE ID for which you want to find all related CWE IDs
related_cwe_ids = dfs(adjacency_list, start_cwe_id)

print(f"All directly and indirectly related CWE IDs for CWE-{start_cwe_id}:")
print(len(related_cwe_ids))
for cwe_id in related_cwe_ids:
    print(f"CWE-{cwe_id}")