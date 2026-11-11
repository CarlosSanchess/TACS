import os
import sys
import subprocess
from transform_t1 import transform_t1
from transform_t2 import transform_t2
from problem_object_model import problem_instance
from besser.BUML.metamodel.quantum import PauliXGate
from besser.generators.qiskit import QiskitGenerator

def test_t2_structure():
    lac_model = transform_t1(problem_instance)
    quantum_model = transform_t2(lac_model)
    
    # 1. Test T1 -> T2 Metamodel Transformation
    reg_dict = {reg.name: reg.size for reg in quantum_model.qregs}
    assert "q" in reg_dict, "Missing quantum register 'q'"
    assert quantum_model.metadata["decision_width"] == 4, "Decision width mismatch"
    assert quantum_model.metadata["mark_width"] == 1, "Mark width mismatch"

    op_names = [op.__class__.__name__ for op in quantum_model.operations]
    assert "HadamardGate" in op_names, "Missing Hadamard state preparation"
    assert any(
        isinstance(op, PauliXGate) and bool(op.control_qubits)
        for op in quantum_model.operations
    ), "Missing multi-controlled gates"
    assert "Measurement" in op_names, "Missing measurement operations"

    print("✓ T2.2 Circuit Structure Test Passed!")

    # 2. Test M2T Code Generation & Execution (Catches NameErrors / Syntax Errors)
    test_out_dir = "test_generated_output"
    generator = QiskitGenerator(
        model=quantum_model,
        output_dir=test_out_dir,
        backend_type="aer_simulator",
        shots=100,
    )
    generator.generate()

    script_path = os.path.join(test_out_dir, "qiskit_circuit.py")

    # Force UTF-8 environment variable to prevent Windows CP1252 character map errors
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"

    res = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=sub_env
    )
    
    assert (
        res.returncode == 0
    ), f"Generated Qiskit script failed execution:\n{res.stderr}"
    print("✓ Qiskit Code Generation & Simulation Execution Test Passed!")

if __name__ == "__main__":
    test_t2_structure()