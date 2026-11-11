import os
import sys
import subprocess
import re
import ast

from problem_object_model import (
    instance_1_tiny,
    instance_2_medium,
    instance_3_unsatisfiable,
    job,
)
from transform_t1 import transform_t1
from transform_t2 import transform_t2
from besser.generators.qiskit import QiskitGenerator
from classical_baseline import (
    solve_partition_dp,
    solve_partition_brute_force,
    extract_problem_loads,
)


def get_job_name(j):
    """Retrieve job name attribute or fallback string representation."""
    return getattr(j, "name", None) or getattr(j, "id", None) or str(j)


def parse_counts_from_stdout(stdout_text: str):
    """Safely extracts measurement counts dictionary from Qiskit Aer stdout."""
    for line in stdout_text.splitlines():
        if "Counts:" in line:
            raw_dict = line.split("Counts:", 1)[1].strip()
            try:
                return ast.literal_eval(raw_dict)
            except Exception:
                pass

    match = re.search(r"(\{\s*['\"].*?\})", stdout_text, re.DOTALL)
    if match:
        try:
            return ast.literal_eval(match.group(1))
        except Exception:
            pass

    return None


def parse_domain_results(bitstring_counts, instance_model):
    """
    Translates raw Qiskit measurement counts back into Load Balancing domain terms.
    Bit '0' -> Machine 1, Bit '1' -> Machine 2.
    """
    objs = (
        instance_model.objects
        if hasattr(instance_model, "objects") and instance_model.objects
        else instance_model.instances
    )
    jobs = sorted([o for o in objs if o.classifier == job], key=get_job_name)
    total_load = sum(j.load for j in jobs)

    print("\n--- DOMAIN EVALUATION & INTERPRETATION ---")
    print(
        f"Total Jobs: {len(jobs)} | Total Workload: {total_load} | Target Load per Machine: {total_load / 2.0}"
    )
    print("Job Definitions:")
    for j in jobs:
        print(f"  • {get_job_name(j)}: load = {j.load}")

    print("\nTop Measurement Solutions:")
    total_shots = sum(bitstring_counts.values())

    sorted_counts = sorted(bitstring_counts.items(), key=lambda x: x[1], reverse=True)

    for bitstring, count in sorted_counts[:4]:
        pct = (count / total_shots) * 100

        bits = (
            [int(b) for b in bitstring[::-1]]
            if len(bitstring) == len(jobs)
            else [int(b) for b in bitstring]
        )

        m1_jobs = [jobs[i] for i, b in enumerate(bits) if b == 0]
        m2_jobs = [jobs[i] for i, b in enumerate(bits) if b == 1]

        m1_load = sum(j.load for j in m1_jobs)
        m2_load = sum(j.load for j in m2_jobs)
        imbalance = abs(m1_load - m2_load)

        status = "PERFECT BALANCE ✓" if imbalance == 0 else f"Imbalance = {imbalance}"
        print(f"  Bitstring '{bitstring}' ({pct:5.1f}% | {count:4d} shots) -> {status}")
        print(f"    • Machine 1: {[get_job_name(j) for j in m1_jobs]} (Load: {m1_load})")
        print(f"    • Machine 2: {[get_job_name(j) for j in m2_jobs]} (Load: {m2_load})")


def run_pipeline_for_instance(instance, output_dir):
    print("\n" + "=" * 70)
    print(f"RUNNING PIPELINE FOR INSTANCE: {instance.name}")
    print("=" * 70)

    # Classical Baseline Execution
    print("\n[Classical Baseline] Running Classical Solvers...")
    loads = extract_problem_loads(instance)
    dp_feasible, dp_sol, dp_time = solve_partition_dp(loads)
    bf_feasible, bf_bitstrings, bf_time = solve_partition_brute_force(loads)

    print(f"  • Job Loads: {loads} (Total Workload: {sum(loads)})")
    print(f"  • Dynamic Programming : Feasible = {dp_feasible} | Time = {dp_time * 1000:.4f} ms")
    if dp_sol:
        print(f"    Sample DP Vector (y): {dp_sol}")
    print(f"  • Brute-Force Search  : Feasible = {bf_feasible} | Time = {bf_time * 1000:.4f} ms")
    print(f"    Ground-Truth Bitstrings (M={len(bf_bitstrings)}): {bf_bitstrings}")

    # T1: DSL -> LAC
    print("\n[T1] Transforming DSL ObjectModel to LAC Model...")
    lac_model = transform_t1(instance)

    # T2: LAC -> BESSER Quantum Model
    print("[T2] Transforming LAC Model to BESSER Quantum Circuit Model...")
    num_sols = max(1, len(bf_bitstrings))
    quantum_model = transform_t2(lac_model, num_solutions=num_sols)

    print(f"  • Circuit Name: {quantum_model.name}")
    print(
        f"  • Qubits: {quantum_model.num_qubits} (Decision: {instance.name}, Accumulator: {quantum_model.metadata['accumulator_width']})"
    )
    print(f"  • Grover Iterations: {quantum_model.metadata['grover_iterations']}")

    # Code Generation
    print(f"\n[Generation] Invoking QiskitGenerator -> ./{output_dir}/qiskit_circuit.py...")
    generator = QiskitGenerator(
        model=quantum_model,
        output_dir=output_dir,
        backend_type="aer_simulator",
        shots=4096,
    )
    generator.generate()
    print("Qiskit code successfully generated.")

    # Execution
    script_path = os.path.join(output_dir, "qiskit_circuit.py")
    print("\n[Execution] Simulating circuit with Qiskit Aer (4096 shots)...")

    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=sub_env,
    )

    if result.returncode != 0:
        print(f"Execution failed for {script_path}:\n{result.stderr}")
        return

    print("Qiskit Aer Simulation Complete.")

    counts = parse_counts_from_stdout(result.stdout)
    if counts:
        parse_domain_results(counts, instance)
    else:
        print("Could not parse counts dictionary from execution output.")


def main():
    print("======================================================================")
    print("       LOAD BALANCING BESSER QUANTUM PIPELINE DEMONSTRATION          ")
    print("======================================================================")

    test_instances = [
        (instance_1_tiny, "generated_tiny"),
        (instance_2_medium, "generated_medium"),
        (instance_3_unsatisfiable, "generated_unsatisfiable"),
    ]

    for instance, out_dir in test_instances:
        run_pipeline_for_instance(instance, out_dir)

    print("\n" + "=" * 70)
    print("END-TO-END DEMONSTRATION COMPLETE FOR ALL 3 BENCHMARK INSTANCES")
    print("=" * 70)


if __name__ == "__main__":
    main()