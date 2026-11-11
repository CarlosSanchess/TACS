import math
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    HadamardGate,
    PauliXGate,
    Measurement,
    ControlState,
)
from problem_object_model import problem_instance
from transform_t1 import transform_t1

from models_solution import (
    decision_var,
    constraint,
    term,
    constraint_has_terms,
    term_ref_var,
)


def connected_object(link, end_name):
    """Get the object connected to a named association end."""
    for connection in link.connections:
        if connection.name == end_name:
            return connection.object

    raise ValueError(
        f"Association link has no connection named '{end_name}'."
    )


def signed_bit_width(minimum, maximum):
    """Find the smallest signed two's-complement width for a range."""
    width = 1

    while (
        minimum < -(2 ** (width - 1))
        or maximum > (2 ** (width - 1)) - 1
    ):
        width += 1

    return width


def extract_constraint_terms(model, constraint_obj):
    """Extract (coefficient, variable) pairs from one constraint sorted by variable name."""
    result = []

    for link in model.links:
        if link.association != constraint_has_terms:
            continue

        linked_constraint = connected_object(link, "constraint")

        if linked_constraint != constraint_obj:
            continue

        term_obj = connected_object(link, "terms")

        variable = None

        for variable_link in model.links:
            if variable_link.association != term_ref_var:
                continue
            linked_term = connected_object(variable_link, "terms")
            if linked_term == term_obj:
                variable = connected_object(variable_link, "variable")
                break

        if variable is None:
            raise ValueError(f"Term {term_obj.name} has no decision variable.")

        result.append((term_obj.coef, variable))

    result.sort(key=lambda item: item[1].name)
    return result

def get_qubit_label(circuit, qubit_obj):
    """Identify register name and index for any qubit reference."""
    if isinstance(qubit_obj, int):
        return f"q[{qubit_obj}]"
    if qubit_obj is None:
        return "N/A"
    for qreg in circuit.qregs:
        if qubit_obj in qreg.qubits:
            idx = qreg.qubits.index(qubit_obj)
            return f"{qreg.name}[{idx}]"
    return str(qubit_obj)


def find_target_qubit(op):
    """Extract target qubit from BESSER operation object."""
    if hasattr(op, "target_qubits") and op.target_qubits:
        return op.target_qubits[0]
    if hasattr(op, "target_qubit") and op.target_qubit is not None:
        return op.target_qubit
    return None


# ==============================================================================
# REVERSIBLE ARITHMETIC & GROVER OPERATORS
# ==============================================================================

def add_controlled_increment(circuit, decision_qubit, accumulator_qubits):
    """
    Add 1 to the accumulator with carry propagation if decision_qubit is 1.
    accumulator_qubits are little-endian.
    """
    n = len(accumulator_qubits)
    for i in range(n - 1, 0, -1):
        controls = [decision_qubit] + accumulator_qubits[:i]
        circuit.add_operation(
            PauliXGate(
                target_qubit=accumulator_qubits[i],
                control_qubits=controls,
                control_states=[ControlState.CONTROL for _ in controls],
            )
        )
    circuit.add_operation(
        PauliXGate(
            target_qubit=accumulator_qubits[0],
            control_qubits=[decision_qubit],
            control_states=[ControlState.CONTROL],
        )
    )


def add_weighted_terms(circuit, decision_qubits, accumulator_qubits, terms):
    """Add each job's weight conditionally with carry propagation."""
    for (coef, _), decision_qubit in zip(terms, decision_qubits):
        for _ in range(coef):
            add_controlled_increment(circuit, decision_qubit, accumulator_qubits)


def add_zero_phase_marker(circuit, accumulator_qubits, mark_qubit):
    """Flip phase of mark_qubit when all accumulator qubits are zero."""
    for q in accumulator_qubits:
        circuit.add_operation(PauliXGate(target_qubit=q))

    circuit.add_operation(
        PauliXGate(
            target_qubit=mark_qubit,
            control_qubits=accumulator_qubits,
            control_states=[ControlState.CONTROL for _ in accumulator_qubits],
        )
    )

    for q in accumulator_qubits:
        circuit.add_operation(PauliXGate(target_qubit=q))


def build_diffuser(circuit, decision_qubits):
    """Grover Diffuser on decision_register: H^n -> X^n -> MCZ -> X^n -> H^n."""
    for q in decision_qubits:
        circuit.add_operation(HadamardGate(target_qubit=q))
    for q in decision_qubits:
        circuit.add_operation(PauliXGate(target_qubit=q))

    target_q = decision_qubits[-1]
    control_qs = decision_qubits[:-1]

    circuit.add_operation(HadamardGate(target_qubit=target_q))
    circuit.add_operation(
        PauliXGate(
            target_qubit=target_q,
            control_qubits=control_qs,
            control_states=[ControlState.CONTROL for _ in control_qs],
        )
    )
    circuit.add_operation(HadamardGate(target_qubit=target_q))

    for q in decision_qubits:
        circuit.add_operation(PauliXGate(target_qubit=q))
    for q in decision_qubits:
        circuit.add_operation(HadamardGate(target_qubit=q))


# ==============================================================================
# MAIN TRANSFORMATION T2
# ==============================================================================

def transform_t2(lac_model, num_solutions=2):
    """
    T2 Transformation: Generates complete Grover Search quantum circuit model
    from a Linear Arithmetic Constraint (LAC) solution model.
    """
    variables = [obj for obj in lac_model.instances if obj.classifier == decision_var]
    constraints = [obj for obj in lac_model.instances if obj.classifier == constraint]

    if not variables:
        raise ValueError("The LAC model has no decision variables.")

    if not constraints:
        raise ValueError("The LAC model has no constraints.")

    if len(constraints) != 1:
        raise NotImplementedError(
            "T2 currently supports one constraint at a time."
        )

    variables.sort(key=lambda variable: variable.name)

    for variable in variables:
        if variable.bitWidth <= 0:
            raise ValueError(
                f"Invalid bit width for {variable.name}."
            )

    constraint_obj = constraints[0]

    terms = extract_constraint_terms(
        lac_model, constraint_obj
    )

    if not terms:
        raise ValueError("The constraint has no terms.")

    # Determine which variables are actually used.
    used_variables = {
        variable.name for _, variable in terms
    }

    if used_variables != {
        variable.name for variable in variables
    }:
        raise ValueError(
            "Every decision variable must appear in the constraint."
        )

    # Calculate expression bounds: E = sum(coef * variable) + constant
    minimum = constraint_obj.const
    maximum = constraint_obj.const

    for coefficient, variable in terms:
        variable_max = (2 ** variable.bitWidth) - 1

        if coefficient >= 0:
            maximum += coefficient * variable_max
        else:
            minimum += coefficient * variable_max

    accumulator_width = signed_bit_width(minimum, maximum)
    num_decision_bits = sum(v.bitWidth for v in variables)
    total_qubits = num_decision_bits + accumulator_width + 1

    # Define flat qubit indices for register 'q' (required by QiskitGenerator)
    decision_qubits = list(range(0, num_decision_bits))
    accumulator_qubits = list(range(num_decision_bits, num_decision_bits + accumulator_width))
    mark_qubit = num_decision_bits + accumulator_width

    # Instantiate Quantum Circuit with single 'q' register and Classical Register
    circuit = QuantumCircuit(name="Grover_Linear_Constraint_Search")
    qreg = QuantumRegister(name="q", size=total_qubits)
    classical_register = ClassicalRegister(name="c", size=num_decision_bits)

    circuit.add_qreg(qreg)
    circuit.add_creg(classical_register)

    # 1. State preparation
    for qubit in decision_qubits:
        circuit.add_operation(HadamardGate(target_qubit=qubit))

    circuit.add_operation(PauliXGate(target_qubit=mark_qubit))
    circuit.add_operation(HadamardGate(target_qubit=mark_qubit))

    # 2. Grover Iteration Count Calculation
    num_iterations = max(
        1, int(math.floor((math.pi / 4.0) * math.sqrt((2 ** num_decision_bits) / num_solutions)))
    )

    # 3. Grover Iterations (Compute -> Mark -> Uncompute -> Diffuser)
    for _ in range(num_iterations):
        compute_start = len(circuit.operations)

        # Load constant (-16) in two's complement into accumulator
        c_val = constraint_obj.const
        twos_comp = (c_val + (1 << accumulator_width)) % (1 << accumulator_width)
        for bit_idx in range(accumulator_width):
            if (twos_comp >> bit_idx) & 1:
                circuit.add_operation(PauliXGate(target_qubit=accumulator_qubits[bit_idx]))

        # Add weighted terms with carry propagation
        add_weighted_terms(circuit, decision_qubits, accumulator_qubits, terms)
        compute_end = len(circuit.operations)

        # Mark Phase
        add_zero_phase_marker(circuit, accumulator_qubits, mark_qubit)

        # Uncompute Phase (Reversing exact compute operations)
        compute_ops = circuit.operations[compute_start:compute_end]
        for op in reversed(compute_ops):
            circuit.add_operation(op)

        # Diffuser Layer
        build_diffuser(circuit, decision_qubits)

    # 4. Measurement
    for i in range(num_decision_bits):
        circuit.add_operation(
            Measurement(
                target_qubit=decision_qubits[i],
                output_bit=i,
            )
        )

    # Store Transformation Metadata
    circuit.metadata = {
        "algorithm": "Grover",
        "constraint": constraint_obj.name,
        "operator": constraint_obj.oper,
        "constant": constraint_obj.const,
        "expression_minimum": minimum,
        "expression_maximum": maximum,
        "decision_variables": [variable.name for variable in variables],
        "decision_width": num_decision_bits,
        "accumulator_width": accumulator_width,
        "mark_width": 1,
        "total_qubits": total_qubits,
        "grover_iterations": num_iterations,
        "stage": "T2.2_grover_circuit_generation",
    }

    return circuit


if __name__ == "__main__":

    print("Generating the LAC model with T1...")
    lac_model = transform_t1(problem_instance)

    print("\nGenerating Quantum Circuit Model with T2...")
    quantum_model = transform_t2(lac_model)

    print("\n========== T2 RESULTS ==========")
    print(f"Circuit name: {quantum_model.name}")
    print(f"Total quantum qubits: {quantum_model.num_qubits}")
    print(f"Total classical bits: {quantum_model.num_clbits}")

    print("\nQuantum registers:")
    for register in quantum_model.qregs:
        print(f"  {register.name}: {register.size} qubits")

    print("\nClassical registers:")
    for register in quantum_model.cregs:
        print(f"  {register.name}: {register.size} bits")

    print("\nExpression range:")
    print(f"  Minimum: {quantum_model.metadata['expression_minimum']}")
    print(f"  Maximum: {quantum_model.metadata['expression_maximum']}")
    print(f"Signed accumulator width: {quantum_model.metadata['accumulator_width']}")
    print(f"Grover iterations: {quantum_model.metadata['grover_iterations']}")
    print(f"Total operations generated: {len(quantum_model.operations)}")

    print("\n========== GENERATED OPERATIONS (FIRST 15) ==========")
    for i, op in enumerate(quantum_model.operations[:15]):
        target_obj = find_target_qubit(op)
        label = get_qubit_label(quantum_model, target_obj)
        print(f"  {i+1:2d}. {op.__class__.__name__} on {label}")