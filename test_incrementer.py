
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    PauliXGate,
    ControlState,
)
from besser.generators.qiskit import QiskitGenerator


def add_incrementer(circuit, qubit_indices):
    """
    Add a reversible incrementer to a BESSER quantum circuit.

    qubit_indices are ordered little-endian:
    index 0 = least significant bit.

    The operation is:
        |x> -> |x + 1 mod 2^n>
    """
    n = len(qubit_indices)

    if n < 1:
        raise ValueError("The register must contain at least one qubit.")

    # Flip higher bits first, using the lower bits as controls.
    for i in range(n - 1, 0, -1):
        target = qubit_indices[i]
        controls = qubit_indices[:i]

        circuit.add_operation(
            PauliXGate(
                target_qubit=target,
                control_qubits=controls,
                control_states=[
                    ControlState.CONTROL for _ in controls
                ],
            )
        )

    # Finally flip the least significant bit.
    circuit.add_operation(
        PauliXGate(target_qubit=qubit_indices[0])
    )


def simulate_incrementer_classically(value, n):
    """
    Simulate the same reversible gate sequence on classical bits.
    This validates the logic for every computational-basis input.
    """
    bits = [(value >> i) & 1 for i in range(n)]

    # Apply multi-controlled X gates, from high to low.
    for i in range(n - 1, 0, -1):
        if all(bits[j] == 1 for j in range(i)):
            bits[i] ^= 1

    # Apply X to the least significant bit.
    bits[0] ^= 1

    return sum(bit << i for i, bit in enumerate(bits))


def exhaustive_test(n):
    """Test every possible n-bit input."""
    total = 1 << n

    for value in range(total):
        actual = simulate_incrementer_classically(value, n)
        expected = (value + 1) % total

        if actual != expected:
            raise AssertionError(
                f"Failed for input {value}: "
                f"got {actual}, expected {expected}"
            )

    print(
        f"PASS: all {total} inputs tested for "
        f"a {n}-bit incrementer."
    )


if __name__ == "__main__":
    n = 6

    # First validate the reversible logic exhaustively.
    exhaustive_test(n)

    # Build the BESSER quantum circuit.
    circuit = QuantumCircuit("Six_Bit_Reversible_Incrementer")

    qreg = QuantumRegister("accumulator", n)
    circuit.add_qreg(qreg)

    add_incrementer(circuit, list(range(n)))

    print("Number of qubits:", circuit.num_qubits)
    print("Number of operations:", len(circuit.operations))

    # Generate Qiskit source code.
    generator = QiskitGenerator(
        circuit,
        output_dir="generated_incrementer",
    )

    generator.generate()

    print("Incrementer circuit generated successfully.")
