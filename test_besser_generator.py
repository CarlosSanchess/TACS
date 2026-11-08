
from pathlib import Path

from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    HadamardGate,
    PauliXGate,
    Measurement,
    ControlState,
)

from besser.generators.qiskit.qiskit_generator import QiskitGenerator


def main():
    # Create a small zero-qubit test circuit.
    circuit = QuantumCircuit(
        name="BESSER_Generator_Test",
        qubits=0
    )

    # Create quantum and classical registers.
    quantum_register = QuantumRegister("q", 2)
    classical_register = ClassicalRegister("c", 1)

    circuit.add_qreg(quantum_register)
    circuit.add_creg(classical_register)

    # Put qubit 0 into superposition.
    circuit.add_operation(
        HadamardGate(target_qubit=0)
    )

    # Apply a controlled-X:
    # if q0 = 1, flip q1.
    circuit.add_operation(
        PauliXGate(
            target_qubit=1,
            control_qubits=[0],
            control_states=[ControlState.CONTROL],
        )
    )

    # Measure qubit 1 into classical bit 0.
    circuit.add_operation(
        Measurement(
            target_qubit=1,
            output_bit=0,
            basis="Z",
        )
    )

    # Generate Qiskit code.
    output_directory = "generated_besser_test"

    generator = QiskitGenerator(
        model=circuit,
        output_dir=output_directory,
        backend_type="aer_simulator",
        shots=1024,
    )

    generator.generate()

    generated_file = (
        Path(output_directory) / "qiskit_circuit.py"
    )

    print("\nBESSER generation test")
    print("======================")
    print("Quantum registers:", len(circuit.qregs))
    print("Classical registers:", len(circuit.cregs))
    print("Operations:", len(circuit.operations))
    print("Generated file:", generated_file.resolve())
    print("File exists:", generated_file.exists())


if __name__ == "__main__":
    main()
