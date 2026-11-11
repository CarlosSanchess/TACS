
from test_oracle import build_oracle
from besser.BUML.metamodel.quantum import PauliXGate, ControlState

oracle = build_oracle()

print("Total operations:", len(oracle.operations))

for i, operation in enumerate(oracle.operations):

    if not isinstance(operation, PauliXGate):
        continue

    if operation.control_qubits == [4, 5, 6, 7, 8, 9]:
        if operation.control_states and all(
            state == ControlState.ANTI_CONTROL
            for state in operation.control_states
        ):
            print("\nZERO DETECTOR FOUND")
            print("Operation index:", i)
            print("Target:", operation.target_qubits)
            print("Controls:", operation.control_qubits)
            print("Control states:", operation.control_states)
