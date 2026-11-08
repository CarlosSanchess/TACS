
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    PauliXGate,
    ControlState,
)
from besser.generators.qiskit import QiskitGenerator

circuit = QuantumCircuit("Test_Multi_Controlled_X")

qreg = QuantumRegister("q", 5)
circuit.add_qreg(qreg)

gate = PauliXGate(
    target_qubit=4,
    control_qubits=[0, 1, 2, 3],
    control_states=[
        ControlState.CONTROL,
        ControlState.CONTROL,
        ControlState.CONTROL,
        ControlState.CONTROL,
    ],
)

circuit.add_operation(gate)

generator = QiskitGenerator(
    circuit,
    output_dir="generated_multi_control_test",
)

generator.generate()

print("Multi-controlled X test generated.")
