#!/usr/bin/env python3
"""
Test script for resource dependency mapping in SymbolGraphBuilder
"""

from graph_builder import SymbolGraphBuilder
import networkx as nx

# Sample Python code with resource dependencies
sample_code = """
import os
import sqlite3
import requests

# Database resource
def connect_db(db_path):
    """Connect to SQLite database"""
    return sqlite3.connect(db_path)

# File resource
def read_config(config_file):
    """Read configuration from file"""
    with open(config_file, 'r') as f:
        return f.read()

# HTTP resource
def fetch_api_data(url, api_key):
    """Fetch data from API"""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers)
    return response.json()

# Operation using multiple resources  
def process_data(data_file, db_path, api_url):
    """Process data using multiple resources"""
    # Read config
    config = read_config(data_file)
    
    # Connect to database
    conn = connect_db(db_path)
    
    # Fetch from API
    api_data = fetch_api_data(api_url, config['api_key'])
    
    # Process and store
    cursor = conn.cursor()
    cursor.execute("INSERT INTO processed_data VALUES (?)", (api_data,))
    conn.commit()
    conn.close()

def main():
    """Main entry point"""
    input_file = "input.json"
    database = "results.db"
    endpoint = "https://api.example.com/data"
    
    process_data(input_file, database, endpoint)

if __name__ == "__main__":
    main()
"""

def test_resource_dependencies():
    """Test the resource dependency mapping functionality"""
    
    print("=" * 60)
    print("Testing Resource Dependency Mapping")
    print("=" * 60)
    
    # Initialize the graph builder
    builder = SymbolGraphBuilder()
    
    # Parse symbols from the code
    print("\n[1] Parsing symbols from code...")
    symbols = builder.parse_symbols(sample_code)
    print(f"Found {len(symbols)} symbols:")
    for symbol in symbols:
        print(f"  - {symbol['type']}: {symbol['name']} (line {symbol['line']})")
    
    # Extract resource dependencies
    print("\n[2] Extracting resource dependencies...")
    resource_deps, op_resources = builder.extract_resource_dependencies(symbols, sample_code)
    
    print("\nResource Dependencies:")
    print("-" * 40)
    for resource, operations in resource_deps.items():
        print(f"Resource '{resource}' used by:")
        for op in operations:
            print(f"  - {op}")
    
    print("\nOperation Dependencies:")
    print("-" * 40)
    for operation, resources in op_resources.items():
        print(f"Operation '{operation}' depends on:")
        for resource in resources:
            print(f"  - {resource}")
    
    # Build and analyze the dependency graph
    print("\n[3] Building dependency graph...")
    G = builder.build_dependency_graph()
    print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Analyze dependencies for insights
    print("\n[4] Analyzing dependencies...")
    insights = builder.analyze_dependencies()
    
    print("\nDependency Analysis:")
    print("-" * 40)
    print(f"Total operations: {insights['total_operations']}")
    print(f"Total resources: {insights['total_resources']}")
    
    print("\nResource usage frequency:")
    for resource, count in insights['resource_usage'].items():
        print(f"  '{resource}': used by {count} operation(s)")
    
    print("\nShared resources (used by multiple operations):")
    if insights['shared_resources']:
        for resource, operations in insights['shared_resources'].items():
            print(f"  '{resource}': shared by {', '.join(operations)}")
    else:
        print("  No shared resources found")
    
    print("\nCritical resources (used more than average):")
    if insights['critical_resources']:
        print(f"  {', '.join(insights['critical_resources'])}")
    else:
        print("  No critical resources identified")
    
    # Generate visualization (will show if running interactively)
    print("\n[5] Generating visualization...")
    print("(Visualization will be displayed if running in an interactive environment)")
    builder.visualize_graph()
    
    # Additional graph analysis
    print("\n[6] Graph topology analysis:")
    print("-" * 40)
    
    # Find resource nodes
    resource_nodes = [n for n in G.nodes() if G.nodes[n].get('type') == 'resource']
    operation_nodes = [n for n in G.nodes() if G.nodes[n].get('type') == 'operation']
    
    print(f"Resource nodes: {len(resource_nodes)}")
    print(f"Operation nodes: {len(operation_nodes)}")
    
    # Calculate centrality measures
    if G.number_of_nodes() > 0:
        # Betweenness centrality (find critical nodes)
        betweenness = nx.betweenness_centrality(G)
        top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print("\nTop 3 nodes by betweenness centrality (critical in dependency flow):")
        for node, centrality in top_betweenness:
            node_type = G.nodes[node].get('type', 'unknown')
            print(f"  {node} ({node_type}): {centrality:.3f}")
    
    print("\n" + "=" * 60)
    print("Resource dependency mapping test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_resource_dependencies()