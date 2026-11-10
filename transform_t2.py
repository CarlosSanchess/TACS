import math
from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    HadamardGate,
    PauliXGate,
    CXGate,
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
    """Extract (coefficient, variable) pairs from one constraint."""

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

            linked_term = connected_object(
                variable_link, "terms"
            )

            if linked_term == term_obj:
                variable = connected_object(
                    variable_link, "variable"
                )
                break

        if variable is None:
            raise ValueError(
                f"Term {term_obj.name} has no decision variable."
            )

        result.append((term_obj.coef, variable))

    return result


def find_target_qubit(op):
    """Extract target qubit from BESSER operation object."""
    if hasattr(op, "target_qubits") and op.target_qubits:
        return op.target_qubits[0]
    if hasattr(op, "target_qubit") and op.target_qubit:
        return op.target_qubit
    return None


def get_qubit_label(circuit, qubit_obj):
    """Identify register name and index for any qubit reference."""
    if qubit_obj is None:
        return "N/A"
    for qreg in circuit.qregs:
        if qubit_obj in qreg.qubits:
            idx = qreg.qubits.index(qubit_obj)
            return f"{qreg.name}[{idx}]"
    return str(qubit_obj)


def add_constant_to_register(circuit, target_reg, constant_val):
    """
    Applies bitwise X gates to target_reg to add/subtract a constant value in two's complement.
    """
    val = constant_val & ((1 << target_reg.size) - 1)
    for bit_idx in range(target_reg.size):
        if (val >> bit_idx) & 1:
            circuit.add_operation(PauliXGate(target_qubit=target_reg.qubits[bit_idx]))


def build_compute_oracle(circuit, decision_reg, accum_reg, terms, constant_val):
    """
    Step 1: Compute phase.
    Adds constant_val plus (coef * variable) for each term into accum_reg.
    """
    add_constant_to_register(circuit, accum_reg, constant_val)

    curr_dec_idx = 0
    for coef, var_obj in terms:
        dec_qubit = decision_reg.qubits[curr_dec_idx]
        coef_val = coef & ((1 << accum_reg.size) - 1)
        for bit_idx in range(accum_reg.size):
            if (coef_val >> bit_idx) & 1:
                circuit.add_operation(
                    CXGate(control_qubit=dec_qubit, target_qubit=accum_reg.qubits[bit_idx])
                )
        curr_dec_idx += var_obj.bitWidth


def build_mark_oracle(circuit, accum_reg, mark_qubit, operator="=="):
    """
    Step 2: Mark phase.
    Checks if accum_reg satisfies operator (e.g. accum_reg == 0) and flips mark_qubit.
    """
    if operator == "==":
        for q in accum_reg.qubits:
            circuit.add_operation(PauliXGate(target_qubit=q))
        
        circuit.add_operation(
            PauliXGate(target_qubit=mark_qubit, control_qubits=list(accum_reg.qubits))
        )
        
        for q in accum_reg.qubits:
            circuit.add_operation(PauliXGate(target_qubit=q))


def build_uncompute_oracle(circuit, decision_reg, accum_reg, terms, constant_val):
    """
    Step 3: Uncompute phase.
    Reverses build_compute_oracle operations in exact reverse order.
    """
    curr_dec_idx = sum(var_obj.bitWidth for _, var_obj in terms)
    for coef, var_obj in reversed(terms):
        curr_dec_idx -= var_obj.bitWidth
        dec_qubit = decision_reg.qubits[curr_dec_idx]
        coef_val = coef & ((1 << accum_reg.size) - 1)
        for bit_idx in reversed(range(accum_reg.size)):
            if (coef_val >> bit_idx) & 1:
                circuit.add_operation(
                    CXGate(control_qubit=dec_qubit, target_qubit=accum_reg.qubits[bit_idx])
                )

    add_constant_to_register(circuit, accum_reg, constant_val)


def build_diffuser(circuit, decision_reg):
    """
    Step 4: Grover Diffuser (Inversion about the mean) on decision_register.
    H^n -> X^n -> Multi-controlled Z -> X^n -> H^n
    """
    for q in decision_reg.qubits:
        circuit.add_operation(HadamardGate(target_qubit=q))
    for q in decision_reg.qubits:
        circuit.add_operation(PauliXGate(target_qubit=q))

    target_q = decision_reg.qubits[-1]
    control_qs = list(decision_reg.qubits[:-1])

    circuit.add_operation(HadamardGate(target_qubit=target_q))
    circuit.add_operation(PauliXGate(target_qubit=target_q, control_qubits=control_qs))
    circuit.add_operation(HadamardGate(target_qubit=target_q))

    for q in decision_reg.qubits:
        circuit.add_operation(PauliXGate(target_qubit=q))
    for q in decision_reg.qubits:
        circuit.add_operation(HadamardGate(target_qubit=q))


def transform_t2(lac_model):
    """
    T2 Transformation: Generates complete Grover Search quantum circuit
    from a Linear Arithmetic Constraint (LAC) solution model.
    """

    variables = [
        obj for obj in lac_model.instances
        if obj.classifier == decision_var
    ]

    constraints = [
        obj for obj in lac_model.instances
        if obj.classifier == constraint
    ]

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

    accumulator_width = signed_bit_width(
        minimum, maximum
    )

    # Instantiate Quantum Circuit and Registers
    circuit = QuantumCircuit(
        name="Grover_Linear_Constraint_Search"
    )

    decision_register = QuantumRegister(
        name="decision",
        size=sum(v.bitWidth for v in variables),
    )

    accumulator_register = QuantumRegister(
        name="accumulator",
        size=accumulator_width,
    )

    mark_register = QuantumRegister(
        name="mark",
        size=1,
    )

    classical_register = ClassicalRegister(
        name="result",
        size=sum(v.bitWidth for v in variables),
    )

    circuit.add_qreg(decision_register)
    circuit.add_qreg(accumulator_register)
    circuit.add_qreg(mark_register)
    circuit.add_creg(classical_register)

    # 1. State preparation
    for qubit in decision_register.qubits:
        circuit.add_operation(HadamardGate(target_qubit=qubit))

    mark_qubit = mark_register.qubits[0]
    circuit.add_operation(PauliXGate(target_qubit=mark_qubit))
    circuit.add_operation(HadamardGate(target_qubit=mark_qubit))

    # 2. Grover Iteration Loop Calculation
    num_decision_bits = decision_register.size
    num_solutions = 1 
    num_iterations = max(
        1, int(math.floor((math.pi / 4.0) * math.sqrt((2 ** num_decision_bits) / num_solutions)))
    )

    # 3. Add Grover Iterations (Compute -> Mark -> Uncompute -> Diffuser)
    for _ in range(num_iterations):
        build_compute_oracle(
            circuit, decision_register, accumulator_register, terms, constraint_obj.const
        )
        build_mark_oracle(
            circuit, accumulator_register, mark_qubit, constraint_obj.oper
        )
        build_uncompute_oracle(
            circuit, decision_register, accumulator_register, terms, constraint_obj.const
        )
        build_diffuser(circuit, decision_register)

    # 4. Measurement
    for i in range(num_decision_bits):
        circuit.add_operation(
            Measurement(
                target_qubit=decision_register.qubits[i],
                output_bit=classical_register.bits[i]  # Fixed: output_bit & .bits[i]
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
        "decision_variables": [
            variable.name for variable in variables
        ],
        "accumulator_width": accumulator_width,
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