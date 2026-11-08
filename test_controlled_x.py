
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    PauliXGate,
    ControlState,
)
from besser.generators.qiskit import QiskitGenerator

# Create a circuit with three qubits
circuit = QuantumCircuit("Test_Controlled_X")
qreg = QuantumRegister("q", 3)
circuit.add_qreg(qreg)

# Apply X to q2, controlled by q0 and q1
gate = PauliXGate(
    target_qubit=2,
    control_qubits=[0, 1],
    control_states=[
        ControlState.CONTROL,
        ControlState.CONTROL,
    ],
)

circuit.add_operation(gate)

# Generate Qiskit code
generator = QiskitGenerator(
    circuit,
    output_dir="generated_test",
)

generator.generate()

print("Controlled-X test circuit generated.")
