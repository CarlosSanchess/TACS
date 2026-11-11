
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np


WEIGHTS = [4, 6, 10, 12]
INITIAL_VALUE = -16

N_DECISION = 4
N_ACCUMULATOR = 6
N_TOTAL = N_DECISION + N_ACCUMULATOR + 1

DECISION_START = 0
ACCUMULATOR_START = 4
PHASE_QUBIT = 10

GROVER_ITERATIONS = 2


def add_controlled_increment(qc, decision_qubit, accumulator_start):
    """
    Add one to a six-bit accumulator, controlled by a decision qubit.

    Qubit order is little-endian:
    accumulator_start is the least significant bit.
    """

    # Higher bits toggle if the decision bit and all lower
    # accumulator bits are 1.
    for i in range(N_ACCUMULATOR - 1, 0, -1):
        controls = [decision_qubit] + [
            accumulator_start + j for j in range(i)
        ]
        target = accumulator_start + i
        qc.mcx(controls, target)

    # Toggle the least significant bit.
    qc.cx(decision_qubit, accumulator_start)


def add_weighted_terms(qc):
    """Add each weighted decision variable to the accumulator."""

    for i, weight in enumerate(WEIGHTS):
        decision_qubit = DECISION_START + i

        for _ in range(weight):
            add_controlled_increment(
                qc,
                decision_qubit,
                ACCUMULATOR_START
            )


def build_compute_circuit():
    """
    Build the reversible computation:

        E = 4*y0 + 6*y1 + 10*y2 + 12*y3 - 16
    """

    compute = QuantumCircuit(N_TOTAL)

    # Initialise the accumulator to -16.
    # Six-bit two's complement: 110000.
    compute.x(ACCUMULATOR_START + 4)
    compute.x(ACCUMULATOR_START + 5)

    add_weighted_terms(compute)

    return compute


def apply_oracle(qc, compute):
    """Apply the zero-testing phase oracle."""

    # Compute the expression into the accumulator.
    qc.compose(compute, inplace=True)

    # Change the zero test into an all-ones test.
    accumulator_qubits = list(
        range(
            ACCUMULATOR_START,
            ACCUMULATOR_START + N_ACCUMULATOR
        )
    )

    for qubit in accumulator_qubits:
        qc.x(qubit)

    # Flip the phase qubit only when the accumulator is zero.
    qc.mcx(accumulator_qubits, PHASE_QUBIT)

    # Undo the X gates used for the zero test.
    for qubit in accumulator_qubits:
        qc.x(qubit)

    # Uncompute the accumulator.
    qc.compose(compute.inverse(), inplace=True)


def apply_diffusion(qc):
    """Apply Grover diffusion to the four decision qubits."""

    decision_qubits = list(range(N_DECISION))

    for qubit in decision_qubits:
        qc.h(qubit)

    for qubit in decision_qubits:
        qc.x(qubit)

    target = decision_qubits[-1]
    controls = decision_qubits[:-1]

    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)

    for qubit in decision_qubits:
        qc.x(qubit)

    for qubit in decision_qubits:
        qc.h(qubit)


def build_grover_circuit():
    """Build the complete Grover search circuit."""

    decisions = QuantumRegister(N_DECISION, "decision")
    accumulator = QuantumRegister(N_ACCUMULATOR, "accumulator")
    phase = QuantumRegister(1, "phase")
    classical = ClassicalRegister(N_DECISION, "result")

    qc = QuantumCircuit(
        decisions,
        accumulator,
        phase,
        classical
    )

    compute = build_compute_circuit()

    # Prepare decision qubits in uniform superposition.
    qc.h(decisions)

    # Prepare phase qubit in |->, once only.
    qc.x(phase[0])
    qc.h(phase[0])

    # Grover iterations.
    for iteration in range(GROVER_ITERATIONS):
        qc.barrier(label=f"Oracle {iteration + 1}")
        apply_oracle(qc, compute)

        qc.barrier(label=f"Diffusion {iteration + 1}")
        apply_diffusion(qc)

    # Measure only the decision qubits.
    qc.measure(decisions, classical)

    return qc


def main():
    print("Complete Grover search")
    print("=" * 55)

    qc = build_grover_circuit()

    print("Total quantum qubits:", qc.num_qubits)
    print("Classical measurement bits:", qc.num_clbits)
    print("Grover iterations:", GROVER_ITERATIONS)
    print("Circuit operations:", qc.size())

    # Remove measurements to obtain the final statevector.
    statevector_circuit = qc.remove_final_measurements(inplace=False)
    statevector = Statevector.from_instruction(statevector_circuit)

    # Obtain probabilities for the four decision qubits.
    probabilities = statevector.probabilities(
        qargs=[0, 1, 2, 3]
    )

    print("\nDecision assignment probabilities:")

    for number, probability in enumerate(probabilities):
        assignment = format(number, "04b")[::-1]
        print(f"{assignment}: {probability:.6f}")

    solution_probability = (
        probabilities[int("0110"[::-1], 2)]
        + probabilities[int("1001"[::-1], 2)]
    )

    print("\nTotal probability of valid solutions:")
    print(f"{solution_probability:.6f}")

    # Run a shot-based simulation.
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=4096).result()
    counts = result.get_counts()

    print("\nMeasurement counts (4096 shots):")
    print(counts)

    print("\nExpected valid assignments: 0110 and 1001")

    if solution_probability > 0.8:
        print("\nGROVER STATEVECTOR TEST PASSED")
    else:
        print("\nGROVER STATEVECTOR TEST NEEDS INVESTIGATION")


if __name__ == "__main__":
    main()
