
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    HadamardGate,
    PauliXGate,
    ControlState,
)


DECISION_QUBITS = 4


def add_diffusion(circuit, decision_qubits):
    """
    Add Grover's diffusion operator to the decision qubits.

    Implements:
        H^n X^n MCZ X^n H^n

    MCZ is implemented using H-MCX-H on the final decision qubit.
    """

    # Step 1: Apply Hadamard to all decision qubits.
    for qubit in decision_qubits:
        circuit.add_operation(HadamardGate(target_qubit=qubit))

    # Step 2: Apply X to all decision qubits.
    for qubit in decision_qubits:
        circuit.add_operation(PauliXGate(target_qubit=qubit))

    # Step 3: Convert the multi-controlled X into a phase flip.
    target = decision_qubits[-1]
    controls = decision_qubits[:-1]

    circuit.add_operation(HadamardGate(target_qubit=target))

    circuit.add_operation(
        PauliXGate(
            target_qubit=target,
            control_qubits=controls,
            control_states=[
                ControlState.CONTROL for _ in controls
            ],
        )
    )

    circuit.add_operation(HadamardGate(target_qubit=target))

    # Step 4: Undo the X gates.
    for qubit in decision_qubits:
        circuit.add_operation(PauliXGate(target_qubit=qubit))

    # Step 5: Undo the initial Hadamard gates.
    for qubit in decision_qubits:
        circuit.add_operation(HadamardGate(target_qubit=qubit))


def build_diffusion_circuit():
    """Build a circuit containing only the diffusion operator."""

    circuit = QuantumCircuit(name="Grover_Diffusion", qubits=DECISION_QUBITS)

    decision_qubits = list(range(DECISION_QUBITS))

    add_diffusion(circuit, decision_qubits)

    return circuit


def main():
    circuit = build_diffusion_circuit()

    print("Grover diffusion circuit")
    print("=" * 45)
    print("Decision qubits:", DECISION_QUBITS)
    print("Total qubits:", DECISION_QUBITS)
    print("Total operations:", len(circuit.operations))

    print("\nOperations:")
    for index, operation in enumerate(circuit.operations):
        print(
            index,
            type(operation).__name__,
            "target =", operation.target_qubits,
            "controls =", operation.control_qubits,
        )

    print("\nDiffusion circuit created successfully.")


if __name__ == "__main__":
    main()
