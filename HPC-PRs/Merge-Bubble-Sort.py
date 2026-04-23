import multiprocessing
import random
import time
import os

# ==========================================
# 1. BUBBLE SORT IMPLEMENTATIONS
# ==========================================

# Global variable to hold the shared array in worker processes
shared_arr_global = None

def init_worker(shared_arr):
    """
    Initialize the worker process by making the shared array accessible globally.
    """
    global shared_arr_global
    shared_arr_global = shared_arr

def compare_and_swap(idx):
    """
    Kernel function to compare and swap a specific pair.
    """
    global shared_arr_global
    p_name = multiprocessing.current_process().name
    print(f"  [Worker] {p_name} (PID: {os.getpid()}) comparing indices {idx} & {idx+1}")
    # <----------------------------------->	
    
    # In Odd-Even sort, indices (i, i+1) in a single phase do not overlap 
    # with other pairs, so we strictly don't need a lock for data integrity 
    # within the phase, but the array object itself might require it for access.
    # We use the raw array for speed here.
    if shared_arr_global[idx] > shared_arr_global[idx + 1]:
        # Swap
        temp = shared_arr_global[idx]
        shared_arr_global[idx] = shared_arr_global[idx + 1]
        shared_arr_global[idx + 1] = temp

def sequential_bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def parallel_bubble_sort(arr):
    n = len(arr)
    # Create a shared array in memory
    shared_arr = multiprocessing.Array('i', arr)
    
    # Initialize the pool
    pool = multiprocessing.Pool(
        processes=multiprocessing.cpu_count(),
        initializer=init_worker,
        initargs=(shared_arr,)
    )

    for i in range(n):
        # Odd phase vs Even phase
        start_index = 1 if i % 2 == 1 else 0
        
        # Indices to check: 0, 2, 4... or 1, 3, 5...
        indices = range(start_index, n - 1, 2)
        
        # Parallelize the comparison phase
        pool.map(compare_and_swap, indices)

    pool.close()
    pool.join()
    return list(shared_arr)


# ==========================================
# 2. MERGE SORT IMPLEMENTATIONS
# ==========================================

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def sequential_merge_sort(arr):
    p_name = multiprocessing.current_process().name
    if p_name != "MainProcess": print(f"  [Worker] {p_name} (PID: {os.getpid()}) sorting sub-array of length {len(arr)}")
    # <----------------------------------->
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = sequential_merge_sort(arr[:mid])
    right = sequential_merge_sort(arr[mid:])
    return merge(left, right)

def parallel_merge_sort_wrapper(arr):
    # This wrapper handles the first split to parallelize
    if len(arr) < 2:
        return arr
        
    mid = len(arr) // 2
    left_sub = arr[:mid]
    right_sub = arr[mid:]

    # Create a pool to sort the two halves in parallel
    with multiprocessing.Pool(processes=2) as pool:
        # Map sequential_merge_sort to both halves
        left, right = pool.map(sequential_merge_sort, [left_sub, right_sub])
        
        # Merge the two sorted halves
        return merge(left, right)


# ==========================================
# 3. UTILITY & MENU
# ==========================================

def print_array_safe(arr, label):
    """Helper to print array nicely"""
    print(f"\n{label}:")
    if len(arr) > 20:
        print(f"{arr[:10]} ... {arr[-10:]} (Showing first/last 10 elements)")
    else:
        print(arr)

def perform_bubble_sort():
    try:
        user_input = input("\nEnter number of elements for Bubble Sort (Default 20): ")
        n = int(user_input) if user_input else 20
        
        data = [random.randint(0, 100) for _ in range(n)]
        print_array_safe(data, "Generated Numbers")

        # --- Sequential ---
        print("\n--- Running Sequential Bubble Sort ---")
        arr_seq = data.copy()
        start = time.time()
        sorted_seq = sequential_bubble_sort(arr_seq)
        end = time.time()
        print(f"Time: {end - start:.4f} seconds")
        print_array_safe(sorted_seq, "Sorted Numbers (Sequential)")

        # --- Parallel ---
        print("\n--- Running Parallel Bubble Sort ---")
        arr_par = data.copy()
        start = time.time()
        sorted_par = parallel_bubble_sort(arr_par)
        end = time.time()
        print(f"Time: {end - start:.4f} seconds")
        print_array_safe(sorted_par, "Sorted Numbers (Parallel)")

    except ValueError:
        print("Invalid input")

def perform_merge_sort():
    try:
        user_input = input("\nEnter number of elements for Merge Sort (Default 20): ")
        n = int(user_input) if user_input else 20
        
        data = [random.randint(0, 100) for _ in range(n)]
        print_array_safe(data, "Generated Numbers")

        # --- Sequential ---
        print("\n--- Running Sequential Merge Sort ---")
        arr_seq = data.copy()
        start = time.time()
        sorted_seq = sequential_merge_sort(arr_seq)
        end = time.time()
        print(f"Time: {end - start:.4f} seconds")
        print_array_safe(sorted_seq, "Sorted Numbers (Sequential)")

        # --- Parallel ---
        print("\n--- Running Parallel Merge Sort ---")
        arr_par = data.copy()
        start = time.time()
        sorted_par = parallel_merge_sort_wrapper(arr_par)
        end = time.time()
        print(f"Time: {end - start:.4f} seconds")
        print_array_safe(sorted_par, "Sorted Numbers (Parallel)")
        
    except ValueError:
        print("Invalid input")

def main():
    while True:
        print("\n==================================")
        print("   Parallel Sorting Algorithms    ")
        print("==================================")
        print("1. Bubble Sort")
        print("2. Merge Sort")
        print("3. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            perform_bubble_sort()
        elif choice == '2':
            perform_merge_sort()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
