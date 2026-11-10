from transform_t1 import transform_t1
from transform_t2 import transform_t2
from problem_object_model import problem_instance
from besser.BUML.metamodel.quantum import PauliXGate

def test_t2_structure():
    lac_model = transform_t1(problem_instance)
    quantum_model = transform_t2(lac_model)
    
    # 1. Check Register Sizes
    reg_dict = {reg.name: reg.size for reg in quantum_model.qregs}
    assert (
        "decision" in reg_dict and reg_dict["decision"] == 4
    ), "Decision register size mismatch"
    assert "accumulator" in reg_dict, "Missing accumulator register"
    assert "mark" in reg_dict and reg_dict["mark"] == 1, "Mark register size mismatch"
    
    # 2. Check Operation Types Present
    op_names = [op.__class__.__name__ for op in quantum_model.operations]
    assert "HadamardGate" in op_names, "Missing Hadamard state preparation"

    has_controlled_x = any(
        isinstance(op, PauliXGate) and bool(op.control_qubits)
        for op in quantum_model.operations
    )
    assert (
        has_controlled_x
    ), "Missing multi-controlled oracle/diffuser gates (PauliXGate with controls)"

    assert "Measurement" in op_names, "Missing measurement operations"

    print("✓ T2.2 Circuit Structure Test Passed!")

if __name__ == "__main__":
    test_t2_structure()