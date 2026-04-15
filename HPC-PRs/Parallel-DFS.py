# 2. Parallel Depth First Search (DFS)
# Logic: Parallelizing DFS is trickier because it is recursive. In Python, spawning a process for every node is too slow (overhead). The standard HPC strategy is to parallelize the sub-trees. The root node spawns separate processes for its immediate children, and those processes run sequential DFS on their respective sub-trees.

import multiprocessing
import time

# Sequential DFS for the worker processes
def sequential_dfs(node, graph, visited, path):
    if node not in visited:
        visited.add(node)
        path.append(node)
        if node in graph:
            for neighbor in graph[node]:
                sequential_dfs(neighbor, graph, visited, path)
    return path

# Wrapper to handle process arguments
def dfs_wrapper(args):
    node, graph, visited_global = args
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

if __name__ == '__main__':
    # Same graph
    graph = {
        0: [1, 2],
        1: [3, 4],   # Branch 1
        2: [5, 6],   # Branch 2
        3: [], 4: [], 5: [], 6: []
    }

    print("\nRunning Parallel DFS on Linux...")
    start_time = time.time()
    parallel_dfs(graph, 0)
    print(f"Time taken: {time.time() - start_time:.4f} seconds")