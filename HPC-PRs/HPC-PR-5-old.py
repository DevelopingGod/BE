import multiprocessing
import random
import time
import math

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def calculate_distance(p1, p2):
    """Euclidean distance between two 2D points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def generate_data(n):
    """Generates N random 2D data points"""
    print(f"Generating {n} random 2D points...")
    data = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
    return data

# ==========================================
# 2. WORKER KERNEL (Runs on Cores)
# ==========================================

def assign_clusters_worker(args):
    """
    Worker function to assign each point in a chunk to the nearest centroid.
    Args: (chunk_of_points, current_centroids)
    Returns: A list of cluster_indices for the chunk
    """
    points_chunk, centroids = args
    local_assignments = []

    for point in points_chunk:
        min_dist = float('inf')
        closest_centroid_idx = -1
        
        # Find nearest centroid for this point
        for idx, centroid in enumerate(centroids):
            dist = calculate_distance(point, centroid)
            if dist < min_dist:
                min_dist = dist
                closest_centroid_idx = idx
        
        local_assignments.append(closest_centroid_idx)
    
    return local_assignments

# ==========================================
# 3. K-MEANS ALGORITHMS
# ==========================================

def sequential_kmeans(data, k, max_iters=10):
    # Initialize Centroids Randomly
    centroids = random.sample(data, k)
    assignments = [0] * len(data)

    for i in range(max_iters):
        # E-Step: Assign points to nearest centroid
        for idx, point in enumerate(data):
            min_dist = float('inf')
            closest = -1
            for c_idx, centroid in enumerate(centroids):
                dist = calculate_distance(point, centroid)
                if dist < min_dist:
                    min_dist = dist
                    closest = c_idx
            assignments[idx] = closest
        
        # M-Step: Update centroids
        new_centroids = [[0, 0] for _ in range(k)]
        counts = [0] * k
        
        for idx, cluster_id in enumerate(assignments):
            new_centroids[cluster_id][0] += data[idx][0]
            new_centroids[cluster_id][1] += data[idx][1]
            counts[cluster_id] += 1
        
        for c_idx in range(k):
            if counts[c_idx] > 0:
                new_centroids[c_idx][0] /= counts[c_idx]
                new_centroids[c_idx][1] /= counts[c_idx]
            else:
                new_centroids[c_idx] = centroids[c_idx] # Keep old if empty
        
        centroids = [tuple(c) for c in new_centroids]
    
    return centroids

def parallel_kmeans(data, k, max_iters=10):
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(data) // num_processes
    
    # Pre-split data into chunks
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Initialize Centroids
    centroids = random.sample(data, k)
    
    # Create Pool ONCE (Creating inside loop kills performance)
    pool = multiprocessing.Pool(processes=num_processes)

    for i in range(max_iters):
        # Prepare arguments: Each worker gets a chunk + current centroids
        tasks = [(chunk, centroids) for chunk in chunks]
        
        # Parallel E-Step: Map workers to chunks
        results = pool.map(assign_clusters_worker, tasks)
        
        # Flatten results (list of lists -> single list)
        assignments = [item for sublist in results for item in sublist]
        
        # M-Step: Update centroids (Usually fast enough to do sequentially)
        new_centroids = [[0, 0] for _ in range(k)]
        counts = [0] * k
        
        # Combine results to update centroids
        # Note: We iterate through the original data and the new assignments
        # In a real massive HPC app, this reduction would also be parallelized
        for idx, cluster_id in enumerate(assignments):
            # Safe check in case of uneven chunks
            if idx < len(data):
                new_centroids[cluster_id][0] += data[idx][0]
                new_centroids[cluster_id][1] += data[idx][1]
                counts[cluster_id] += 1
        
        for c_idx in range(k):
            if counts[c_idx] > 0:
                new_centroids[c_idx][0] /= counts[c_idx]
                new_centroids[c_idx][1] /= counts[c_idx]
            else:
                new_centroids[c_idx] = centroids[c_idx]
        
        centroids = [tuple(c) for c in new_centroids]
    
    pool.close()
    pool.join()
    return centroids

# ==========================================
# 4. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    print("===========================================")
    print("   HPC AI/ML: Parallel K-Means Clustering")
    print("===========================================")
    
    try:
        n_str = input("Enter number of data points (Default 200,000): ")
        n = int(n_str) if n_str.strip() else 200000
        
        k_str = input("Enter number of clusters K (Default 3): ")
        k = int(k_str) if k_str.strip() else 3
    except ValueError:
        n = 200000
        k = 3

    # Generate Data
    data = generate_data(n)
    
    print("\n--- Sample Data Points (First 5) ---")
    for p in data[:5]:
        print(f"({p[0]:.2f}, {p[1]:.2f})")

    # Sequential
    print(f"\n[Sequential] Running K-Means (K={k})...")
    start_seq = time.time()
    final_centroids_seq = sequential_kmeans(data, k)
    end_seq = time.time()
    print(f"Time Taken: {end_seq - start_seq:.4f} seconds")
    print("Centroids:", [f"({c[0]:.1f}, {c[1]:.1f})" for c in final_centroids_seq])

    # Parallel
    print(f"\n[Parallel] Running K-Means on {multiprocessing.cpu_count()} cores...")
    start_par = time.time()
    final_centroids_par = parallel_kmeans(data, k)
    end_par = time.time()
    print(f"Time Taken: {end_par - start_par:.4f} seconds")
    print("Centroids:", [f"({c[0]:.1f}, {c[1]:.1f})" for c in final_centroids_par])

    print("\n===========================================")
    
    
"""
Understanding the Visual LogicScatter: We have thousands of points (blue dots).
Centroids: We place K Red Dots (centroids) randomly.
Parallel Distance Check:
Core 1 checks the first 50,000 points: "Are you closer to Red Dot A, B, or C?"
Core 2 checks the next 50,000 points simultaneously.Update: We move the Red Dots to the center of their new groups.
Repeat: We repeat this process until the Red Dots stop moving.

"""