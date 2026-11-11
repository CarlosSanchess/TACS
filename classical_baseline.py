"""
classical_baseline.py
Classical Baselines for Class C4: Load Balancing (Partition Problem)

Implementations:
1. Dynamic Programming (DP): Pseudo-polynomial O(n * S) solver for feasibility and assignment.
2. Brute-Force Search: Exponential O(2^n) search returning all ground-truth solution bitstrings.
3. BESSER ObjectModel Adapters: Directly parses Problem DSL and Solution DSL instances.

Traceability:
- Karp (1972): NP-completeness of Partition problem.
- QMDE Annex A (Class C): Reversible arithmetic ground-truth verification.
"""

import time
from typing import List, Tuple, Optional


# 1. Classical Solvers

def solve_partition_dp(loads: List[int]) -> Tuple[bool, Optional[List[int]], float]:
    """
    Solves 2-machine Partition via 2D Dynamic Programming.
    Time Complexity: O(n * S/2), Space Complexity: O(n * S/2)
    
    Returns:
        (is_feasible, sample_assignment_vector, execution_time_seconds)
    """
    start_time = time.perf_counter()
    total_sum = sum(loads)
    
    # If total sum is odd, equal 2-machine partition is impossible
    if total_sum % 2 != 0:
        elapsed = time.perf_counter() - start_time
        return False, None, elapsed

    target = total_sum // 2
    n = len(loads)
    
    # dp[i][w] = True if target load w can be formed using a subset of first i jobs
    dp = [[False] * (target + 1) for _ in range(n + 1)]
    dp[0][0] = True

    for i in range(1, n + 1):
        current_load = loads[i - 1]
        for w in range(target + 1):
            if current_load <= w:
                dp[i][w] = dp[i - 1][w] or dp[i - 1][w - current_load]
            else:
                dp[i][w] = dp[i - 1][w]

    elapsed = time.perf_counter() - start_time
    if not dp[n][target]:
        return False, None, elapsed

    # Backtrack to recover binary assignment vector y (1 = Machine 1, 0 = Machine 2)
    w = target
    assignment = [0] * n
    for i in range(n, 0, -1):
        if not dp[i - 1][w]:
            assignment[i - 1] = 1
            w -= loads[i - 1]

    return True, assignment, elapsed


def solve_partition_brute_force(loads: List[int]) -> Tuple[bool, List[str], float]:
    """
    Exhaustively evaluates all 2^n binary assignment strings.
    
    Returns:
        (is_feasible, list_of_valid_bitstrings, execution_time_seconds)
    """
    start_time = time.perf_counter()
    total_sum = sum(loads)
    
    if total_sum % 2 != 0:
        elapsed = time.perf_counter() - start_time
        return False, [], elapsed

    target = total_sum // 2
    n = len(loads)
    valid_bitstrings = []

    # Iterate over all 2^n bit combinations
    for decimal_val in range(1 << n):
        # Format as binary string y_1 y_2 ... y_n
        bitstring = format(decimal_val, f'0{n}b')
        subset_sum = sum(loads[i] for i in range(n) if bitstring[i] == '1')
        
        if subset_sum == target:
            valid_bitstrings.append(bitstring)

    elapsed = time.perf_counter() - start_time
    is_feasible = len(valid_bitstrings) > 0
    return is_feasible, valid_bitstrings, elapsed


# 2. BESSER Model Extraction Helpers

def extract_problem_loads(problem_object_model) -> List[int]:
    """
    Extracts job loads from a BESSER Problem DSL ObjectModel instance,
    sorted deterministically by Job ID (j1, j2, ...).
    """
    # Handle attribute name variance (objects vs instances)
    raw_objs = getattr(problem_object_model, "instances", None)
    if raw_objs is None:
        raw_objs = getattr(problem_object_model, "objects", set())

    # Filter and sort job objects by ID
    job_objs = [
        obj for obj in raw_objs 
        if getattr(obj.classifier, "name", "") == "Job" and hasattr(obj, "load")
    ]
    job_objs.sort(key=lambda j: getattr(j, "id", getattr(j, "name", "")))

    return [int(j.load) for j in job_objs]


def extract_solution_coefficients(solution_object_model) -> Tuple[List[int], int]:
    """
    Extracts term coefficients and constraint constant from a BESSER Solution DSL
    ObjectModel instance, sorted deterministically by decision variable name (y1, y2, ...).
    """
    raw_objs = getattr(solution_object_model, "instances", None)
    if raw_objs is None:
        raw_objs = getattr(solution_object_model, "objects", set())

    target_const = 0
    term_var_pairs = []

    for obj in raw_objs:
        obj_type = getattr(obj.classifier, "name", "")
        if obj_type == "Constraint" and hasattr(obj, "const"):
            target_const = abs(int(obj.const))
        elif obj_type == "Term" and hasattr(obj, "coef"):
            # Attempt to resolve linked decision variable name for sorting
            var_name = getattr(obj, "name", "")
            term_var_pairs.append((var_name, int(obj.coef)))

    # Sort terms by decision variable name if available
    term_var_pairs.sort(key=lambda item: item[0])
    coefs = [coef for _, coef in term_var_pairs]

    return coefs, target_const

# 3. Benchmark Execution & Demonstration

def run_benchmark_suite():
    """Runs classical baseline verification across all test instances."""
    print("======================================================================")
    print("      CLASSICAL BASELINE VERIFICATION FOR QUANTUM MODELING (CLASS C4)  ")
    print("======================================================================\n")

    # Define standard project benchmark test cases
    benchmarks = {
        "Instance 1 (Tiny — 4 Jobs)": [2, 3, 5, 6],
        "Instance 2 (Medium — 6 Jobs)": [3, 7, 11, 12, 15, 20],
        "Instance 3 (Large — 8 Jobs)": [12, 18, 25, 31, 37, 42, 50, 65],
    }

    for name, loads in benchmarks.items():
        total_load = sum(loads)
        target = total_load // 2 if total_load % 2 == 0 else "N/A"
        print(f"--- Benchmark: {name} ---")
        print(f"Loads: {loads} | Total Sum: {total_load} | Target Machine Load: {target}")

        # DP Solver
        feasible_dp, sample_sol, time_dp = solve_partition_dp(loads)
        # Brute Force Solver
        feasible_bf, all_solutions, time_bf = solve_partition_brute_force(loads)

        print(f"  [Dynamic Programming] Feasible: {feasible_dp} | Time: {time_dp * 1000:.4f} ms")
        if sample_sol:
            print(f"    Sample Solution Vector (y): {sample_sol}")
        
        print(f"  [Brute-Force]           Feasible: {feasible_bf} | Time: {time_bf * 1000:.4f} ms")
        print(f"    Total Feasible Bitstrings (M): {len(all_solutions)}")
        print(f"    Ground-Truth Oracle Solutions: {all_solutions}")
        print()

    # Verify BESSER problem_object_model integration
    try:
        from problem_object_model import problem_instance
        parsed_loads = extract_problem_loads(problem_instance)
        print("--- Verification: BESSER Problem DSL ObjectModel ('problem_object_model.py') ---")
        print(f"Parsed Loads from BESSER ObjectModel: {parsed_loads}")
        _, sol_bits, _ = solve_partition_brute_force(parsed_loads)
        print(f"Verified Solutions for ObjectModel: {sol_bits}\n")
    except ImportError:
        print("Note: 'problem_object_model.py' not found in path for auto-verification.\n")


if __name__ == "__main__":
    run_benchmark_suite()