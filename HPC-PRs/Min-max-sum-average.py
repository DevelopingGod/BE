import multiprocessing
import random
import time
import sys
import os

# ==========================================
# 1. WORKER FUNCTION (Executes on specific Core)
# ==========================================
def reduction_worker(chunk):
    """
    Computes local min, max, and sum for a specific chunk of data.
    Returns: (local_min, local_max, local_sum, count)
    """
    if not chunk:
        return None
        
    p_name = multiprocessing.current_process().name
    pid = os.getpid()
    print(f"  [Worker] {p_name} (PID: {pid}) processing chunk of size {len(chunk)}")
    # <----------------------------------------------------------->
    
    # Initialize local variables
    local_min = chunk[0]
    local_max = chunk[0]
    local_sum = 0
    count = len(chunk)

    # Process the chunk
    for num in chunk:
        if num < local_min:
            local_min = num
        if num > local_max:
            local_max = num
        local_sum += num
        
    return (local_min, local_max, local_sum, count)

# ==========================================
# 2. PARALLEL MANAGER
# ==========================================
def parallel_reduction(data):
    # Determine how to split the work
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(data) // num_processes

    # 1. Data Decomposition (Splitting data into chunks)
    chunks = []
    for i in range(num_processes):
        start = i * chunk_size
        # Ensure the last chunk gets any remaining elements (e.g., if odd length)
        end = (i + 1) * chunk_size if i != num_processes - 1 else len(data)
        chunks.append(data[start:end])

    # 2. Parallel Execution
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Map the worker function to the chunks
        results = pool.map(reduction_worker, chunks)

    # 3. Final Reduction (Aggregating results from all cores)
    # Initialize global values with the first result
    global_min = results[0][0]
    global_max = results[0][1]
    global_sum = 0
    total_count = 0

    for res in results:
        if res is None: continue
        
        l_min, l_max, l_sum, l_cnt = res
        
        # Combine results
        if l_min < global_min: global_min = l_min
        if l_max > global_max: global_max = l_max
        global_sum += l_sum
        total_count += l_cnt

    # Calculate Average
    global_avg = global_sum / total_count if total_count > 0 else 0
    
    return global_min, global_max, global_sum, global_avg

# ==========================================
# 3. UTILITIES & MAIN
# ==========================================
def print_data(data):
    """Prints the data nicely, truncating if too large."""
    print(f"\n--- Generated Numbers ({len(data)}) ---")
    if len(data) <= 20:
        print(data)
    else:
        # Show first 10 and last 10
        print(f"{data[:10]} ... {data[-10:]}")
        print("(List truncated for display clarity)")

def main():
    print("===========================================")
    print("   Parallel Reduction (Min, Max, Sum, Avg) ")
    print("===========================================")
    
    try:
        user_input = input("Enter number of elements (e.g., 20 or 1000000): ")
        n = int(user_input) if user_input.strip() else 20
    except ValueError:
        print("Invalid input, using default 20.")
        n = 20

    print(f"\nGenerating {n} random integers...")
    data = [random.randint(1, 100) for _ in range(n)]
    
    # --- SHOW THE NUMBERS ---
    print_data(data)

    # --- Sequential Execution (For Verification) ---
    print("\n[Sequential] Calculating...")
    start_seq = time.time()
    seq_min = min(data)
    seq_max = max(data)
    seq_sum = sum(data)
    seq_avg = seq_sum / len(data)
    end_seq = time.time()
    
    print(f"Time: {end_seq - start_seq:.5f} sec")
    print(f"Min: {seq_min}, Max: {seq_max}, Sum: {seq_sum}, Avg: {seq_avg:.2f}")

    # --- Parallel Execution ---
    print(f"\n[Parallel] Calculating using {multiprocessing.cpu_count()} cores...")
    start_par = time.time()
    par_min, par_max, par_sum, par_avg = parallel_reduction(data)
    end_par = time.time()
    
    print(f"Time: {end_par - start_par:.5f} sec")
    print(f"Min: {par_min}, Max: {par_max}, Sum: {par_sum}, Avg: {par_avg:.2f}")

    print("\n===========================================")

if __name__ == "__main__":
    main()
