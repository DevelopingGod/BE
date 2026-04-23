"""
Crucial Note on OpenMP & Python: Strictly speaking, OpenMP is a standard for C, C++, and Fortran. Python does not support OpenMP pragmas (like #pragma omp) natively. To achieve true parallelism in Python (bypassing the Global Interpreter Lock) and satisfy the "HPC" requirement of this practical, we use the multiprocessing module. This creates separate processes for CPU cores, similar to how OpenMP threads work in C++.
"""

# 1. Parallel Breadth First Search (BFS)
# Logic: We process the graph level-by-level. At every level (frontier), we use a pool of processes to find the neighbors of all current nodes simultaneously.

import multiprocessing
import time
import os

# Function to expand a node (find its unvisited neighbors)
# This runs on separate cores
def bfs_kernel(args):
    node, graph, visited = args
    
    # <-- Type this line manually:
    print(f"  [Worker] {multiprocessing.current_process().name} (PID: {os.getpid()}) exploring Node {node}")
    
    neighbors = []
    
    # Simulate processing time for HPC demonstration
    # time.sleep(0.001) 
    
    if node in graph:
        for neighbor in graph[node]:
            if neighbor not in visited:
                neighbors.append(neighbor)
    return neighbors

def parallel_bfs(graph, start_node):
    # Manager handles shared memory between processes
    with multiprocessing.Manager() as manager:
        visited = manager.list([start_node])
        frontier = [start_node]
        
        # Create a pool of workers equal to CPU cores
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        
        print(f"BFS Order: {start_node}", end=" ")

        while frontier:
        # <-- Type this line manually:
            print(f"\n--- Processing Frontier: {frontier} ---")
            # Prepare arguments for parallel processing
            # We filter out nodes already visited to avoid redundant work
            tasks = [(u, graph, visited) for u in frontier]
            
            # Map the kernel function across the frontier in parallel
            results = pool.map(bfs_kernel, tasks)
            
            next_frontier = []
            
            # Aggregate results (Must be done sequentially to update visited safely)
            # Note: In pure C++ OpenMP this aggregation can also be parallelized with critical sections
            for neighbors in results:
                for n in neighbors:
                    if n not in visited:
                        visited.append(n)
                        next_frontier.append(n)
                        print(n, end=" ")
            
            frontier = next_frontier
        
        pool.close()
        pool.join()
        print("\nBFS Completed.")

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
            start_node = int(input("\nEnter the starting node for BFS: ").strip())
            if start_node not in graph:
                print(f"Warning: Node {start_node} is not in the graph. The BFS will process this single node and exit.")
        except ValueError:
            print("Invalid input. Defaulting to the first available node.")
            start_node = list(graph.keys())

        print("\nRunning Parallel BFS on Linux...")
        start_time = time.time()
        parallel_bfs(graph, start_node)
        print(f"Time taken: {time.time() - start_time:.4f} seconds")
        
"""
Examiner: "Why did you use multiprocessing instead of threading?" You: "Python has a Global Interpreter Lock (GIL) which allows only one thread to execute Python bytecode at a time. For CPU-intensive tasks like Graph Traversal, threading would not provide true parallelism. multiprocessing spawns separate OS processes, bypassing the GIL and utilizing multiple CPU cores effectively."
"""
