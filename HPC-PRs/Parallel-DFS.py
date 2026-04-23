# 2. Parallel Depth First Search (DFS)
# Logic: Parallelizing DFS is trickier because it is recursive. In Python, spawning a process for every node is too slow (overhead). The standard HPC strategy is to parallelize the sub-trees. The root node spawns separate processes for its immediate children, and those processes run sequential DFS on their respective sub-trees.

import multiprocessing
import time
import os

# Sequential DFS for the worker processes
def sequential_dfs(node, graph, visited, path):
    if node not in visited:
        print(f"    -> [PID: {os.getpid()}] traversing Node {node}")
        visited.add(node)
        path.append(node)
        if node in graph:
            for neighbor in graph[node]:
                sequential_dfs(neighbor, graph, visited, path)
    return path

# Wrapper to handle process arguments
def dfs_wrapper(args):
    node, graph, visited_global = args
    
    process_name = multiprocessing.current_process().name
    pid = os.getpid()
    print(f"\n  [Worker] {process_name} (PID: {pid}) starting sub-tree at Node {node}")
    
    
    # Each process needs its own local visited set to avoid massive locking overhead
    # We copy the global visited state initially
    local_visited = set(visited_global)
    path = []
    
    sequential_dfs(node, graph, local_visited, path)
    return path

def parallel_dfs(graph, start_node):
    visited = set()
    visited.add(start_node)
    print(f"DFS Start: {start_node}")

    # Get neighbors of the start node to distribute work
    root_neighbors = graph.get(start_node, [])
    
    # Prepare arguments: (neighbor, graph, current_visited)
    tasks = [(n, graph, list(visited)) for n in root_neighbors]
    
    # Use a Pool to process sub-trees in parallel
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.map(dfs_wrapper, tasks)
    
    # Print results from different branches
    # Note: The order depends on which CPU core finishes first!
    for branch_path in results:
        for node in branch_path:
            if node not in visited:
                print(f"Visited: {node}")
                visited.add(node)

def get_user_graph():
    """Prompts the user to build a graph dynamically via the terminal."""
    graph = {}
    print("--- Custom Graph Builder ---")
    print("Enter edges one by one to build an undirected graph.")
    print("Format: 'u v' (e.g., to connect node 0 and 1, type '0 1').")
    print("Press Enter on an empty line when you are finished.\n")

    while True:
        user_input = input("Enter edge (or press Enter to finish): ").strip()
        if not user_input:
            break

        try:
            u, v = map(int, user_input.split())
            
            # Initialize nodes if they don't exist
            if u not in graph: graph[u] = []
            if v not in graph: graph[v] = []

            # Add bidirectional edges (undirected graph)
            if v not in graph[u]: graph[u].append(v)
            if u not in graph[v]: graph[v].append(u)

        except ValueError:
            print("Invalid input. Please enter two integers separated by a space (e.g., '0 1').")

    return graph

if __name__ == '__main__':
    # Build the graph from user input
    graph = get_user_graph()

    if not graph:
        print("No edges were entered. Exiting program.")
    else:
        # Ask for the starting node
        try:
            start_node = int(input("\nEnter the starting node for DFS: ").strip())
            if start_node not in graph:
                print(f"Warning: Node {start_node} is not in the graph. The DFS will process this single node and exit.")
        except ValueError:
            print("Invalid input. Defaulting to the first available node.")
            start_node = list(graph.keys())

        print("\nRunning Parallel DFS on Linux...")
        start_time = time.time()
        parallel_dfs(graph, start_node)
        print(f"\nTime taken: {time.time() - start_time:.4f} seconds")
