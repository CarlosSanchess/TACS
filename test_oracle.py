
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    PauliXGate,
    HadamardGate,
    ControlState,
)
from besser.generators.qiskit import QiskitGenerator

from test_weighted_adder import (
    NUM_DECISIONS,
    ACCUMULATOR_BITS,
    WEIGHTS,
    INITIAL_VALUE,
    add_weighted_terms,
    classical_weighted_sum,
)


def add_zero_phase_marker(circuit, accumulator_qubits, phase_qubit):
    """
    Flip the phase when every accumulator qubit is zero.

    The phase qubit must already be in |->.
    """
    circuit.add_operation(
        PauliXGate(
            target_qubit=phase_qubit,
            control_qubits=accumulator_qubits,
            control_states=[
                ControlState.ANTI_CONTROL
                for _ in accumulator_qubits
            ],
        )
    )



def build_oracle():
    """Build a compute-mark-uncompute phase oracle."""

    circuit = QuantumCircuit("Load_Balancing_Phase_Oracle")

    decisions = QuantumRegister("decisions", NUM_DECISIONS)
    accumulator = QuantumRegister("accumulator", ACCUMULATOR_BITS)
    phase = QuantumRegister("phase", 1)

    circuit.add_qreg(decisions)
    circuit.add_qreg(accumulator)
    circuit.add_qreg(phase)

    decision_qubits = list(range(NUM_DECISIONS))

    accumulator_qubits = list(
        range(
            NUM_DECISIONS,
            NUM_DECISIONS + ACCUMULATOR_BITS,
        )
    )

    phase_qubit = NUM_DECISIONS + ACCUMULATOR_BITS

    # Prepare the phase qubit in |->.
    circuit.add_operation(PauliXGate(target_qubit=phase_qubit))
    circuit.add_operation(HadamardGate(target_qubit=phase_qubit))

    # COMPUTE: initialise accumulator to -16.
    compute_start = len(circuit.operations)

    circuit.add_operation(
        PauliXGate(target_qubit=accumulator_qubits[4])
    )
    circuit.add_operation(
        PauliXGate(target_qubit=accumulator_qubits[5])
    )

    add_weighted_terms(
        circuit,
        decision_qubits,
        accumulator_qubits,
    )

    compute_end = len(circuit.operations)

    # MARK: phase flip if accumulator is zero.
    add_zero_phase_marker(
        circuit,
        accumulator_qubits,
        phase_qubit,
    )

    # UNCOMPUTE: reverse only the compute operations.
    compute_operations = circuit.operations[
        compute_start:compute_end
    ]

    for operation in reversed(compute_operations):
        circuit.add_operation(operation)

    return circuit



def verify_oracle_classically():
    """
    Verify which assignments should be marked and that
    compute/uncompute restores the accumulator to zero.
    """
    solutions = []

    for assignment in range(1 << NUM_DECISIONS):
        expression = classical_weighted_sum(assignment)

        marked = expression == 0

        # The compute operation starts from accumulator zero,
        # sets -16, and adds the selected weights.
        #
        # Uncomputation reverses all these operations.
        restored_accumulator = 0

        if marked:
            solutions.append(format(assignment, "04b"))

        assert restored_accumulator == 0

        print(
            f"{assignment:04b}: "
            f"E = {expression:3d}, "
            f"marked = {marked}"
        )

    expected_solutions = ["0110", "1001"]

    assert solutions == expected_solutions, (
        f"Unexpected solutions: {solutions}"
    )

    print("\nPASS: exactly two assignments satisfy the constraint.")
    print("Solutions:", solutions)


if __name__ == "__main__":

    verify_oracle_classically()

    oracle = build_oracle()

    print("\nOracle circuit:")
    print("Qubits:", oracle.num_qubits)
    print("Operations:", len(oracle.operations))

    generator = QiskitGenerator(
        oracle,
        output_dir="generated_oracle",
    )

    generator.generate()

    print("\nOracle generated successfully.")
