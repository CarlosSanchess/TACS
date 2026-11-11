
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    PauliXGate,
    ControlState,
)
from besser.generators.qiskit import QiskitGenerator


# Problem data
WEIGHTS = [4, 6, 10, 12]
NUM_DECISIONS = len(WEIGHTS)
ACCUMULATOR_BITS = 6
INITIAL_VALUE = -16


def add_controlled_increment(circuit, decision_qubit, accumulator_qubits):
    """
    Add 1 to the accumulator if decision_qubit is 1.

    accumulator_qubits are little-endian:
    index 0 is the least significant bit.
    """
    n = len(accumulator_qubits)

    # Carry operations, from the highest bit down.
    for i in range(n - 1, 0, -1):
        controls = [decision_qubit] + accumulator_qubits[:i]

        circuit.add_operation(
            PauliXGate(
                target_qubit=accumulator_qubits[i],
                control_qubits=controls,
                control_states=[
                    ControlState.CONTROL for _ in controls
                ],
            )
        )

    # Conditional flip of the least significant bit.
    circuit.add_operation(
        PauliXGate(
            target_qubit=accumulator_qubits[0],
            control_qubits=[decision_qubit],
            control_states=[ControlState.CONTROL],
        )
    )


def add_weighted_terms(circuit, decision_qubits, accumulator_qubits):
    """
    Add each job's weight conditionally.

    If decision_qubits[i] = 1, add WEIGHTS[i].
    """
    for decision_qubit, weight in zip(decision_qubits, WEIGHTS):
        for _ in range(weight):
            add_controlled_increment(
                circuit,
                decision_qubit,
                accumulator_qubits,
            )


def classical_weighted_sum(decision_value):
    """
    Calculate the expected constraint expression classically.

    Bit i of decision_value represents decision variable y_i.
    """
    result = INITIAL_VALUE

    for i, weight in enumerate(WEIGHTS):
        decision = (decision_value >> i) & 1
        result += decision * weight

    return result



def exhaustive_test(circuit):
    """Test all 16 assignments using actual BESSER operations."""

    for decision_value in range(1 << NUM_DECISIONS):
        expected = classical_weighted_sum(decision_value)

        actual = simulate_besser_circuit(
            circuit,
            decision_value,
        )

        if actual != expected:
            raise AssertionError(
                f"Assignment {decision_value:04b}: "
                f"expected {expected}, got {actual}"
            )

    print("PASS: all 16 assignments passed the BESSER circuit test.")

    print("\nVerified constraint values:")

    for value in range(1 << NUM_DECISIONS):
        actual = simulate_besser_circuit(circuit, value)

        print(f"  {value:04b} -> {actual:3d}")



def build_quantum_circuit():
    """Build the BESSER circuit model."""
    circuit = QuantumCircuit("Load_Balancing_Weighted_Adder")

    # Four decision qubits followed by six accumulator qubits.
    decision_register = QuantumRegister(
        "decisions",
        NUM_DECISIONS,
    )
    accumulator_register = QuantumRegister(
        "accumulator",
        ACCUMULATOR_BITS,
    )

    circuit.add_qreg(decision_register)
    circuit.add_qreg(accumulator_register)

    decision_qubits = list(range(NUM_DECISIONS))

    accumulator_qubits = list(
        range(
            NUM_DECISIONS,
            NUM_DECISIONS + ACCUMULATOR_BITS,
        )
    )

    # Initialise accumulator to -16.
    # Six-bit two's-complement representation:
    # -16 = 110000 (binary).
    #
    # Little-endian ordering means bits 4 and 5 are set.
    for bit in (4, 5):
        circuit.add_operation(
            PauliXGate(target_qubit=accumulator_qubits[bit])
        )

    # Add the weighted decision variables.
    add_weighted_terms(
        circuit,
        decision_qubits,
        accumulator_qubits,
    )

    return circuit


def simulate_besser_circuit(circuit, decision_value):
    """
    Simulate the circuit's X gates and controlled-X gates
    on a computational-basis input.

    This checks the actual operations stored in BESSER.
    """
    bits = [0] * circuit.num_qubits

    # Initialise the four decision qubits.
    for i in range(NUM_DECISIONS):
        bits[i] = (decision_value >> i) & 1

    # Apply every operation in circuit order.
    for operation in circuit.operations:
        targets = operation.target_qubits
        controls = operation.control_qubits or []
        states = operation.control_states or []

        # Check all control conditions.
        enabled = True

        for control_index, control_qubit in enumerate(controls):
            if states:
                required = (
                    1
                    if states[control_index] == ControlState.CONTROL
                    else 0
                )
            else:
                required = 1

            if bits[control_qubit] != required:
                enabled = False
                break

        # Apply X to the target if controls are satisfied.
        if enabled:
            for target in targets:
                bits[target] ^= 1

    # Decode the accumulator (little-endian).
    accumulator = 0

    for i in range(ACCUMULATOR_BITS):
        accumulator |= (
            bits[NUM_DECISIONS + i] << i
        )

    # Convert from six-bit two's complement.
    if accumulator >= (1 << (ACCUMULATOR_BITS - 1)):
        accumulator -= (1 << ACCUMULATOR_BITS)

    return accumulator

if __name__ == "__main__":
    
    circuit = build_quantum_circuit()

    exhaustive_test(circuit)

    print("\nQuantum circuit model:")
    print("  Qubits:", circuit.num_qubits)
    print("  Operations:", len(circuit.operations))

    # Generate Qiskit source code.
    generator = QiskitGenerator(
        circuit,
        output_dir="generated_weighted_adder",
    )

    generator.generate()

    print("\nWeighted adder generated successfully.")
