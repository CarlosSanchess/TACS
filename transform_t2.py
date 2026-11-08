from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
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


def transform_t2(lac_model):
    """
    T2.1: Generate the quantum circuit and derive its registers
    from a Linear Arithmetic Constraint model.

    This stage creates the register structure only.
    Oracle gates and Grover operations are added in later stages.
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
            "T2.1 currently supports one constraint at a time."
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

    # Calculate the possible range of the expression:
    # E = sum(coef * variable) + constant
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

    # Build the Quantum Circuit Model.
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

    # Store useful transformation metadata.
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
        "stage": "T2.1_register_generation",
    }

    return circuit


if __name__ == "__main__":

    print("Generating the LAC model with T1...")
    lac_model = transform_t1(problem_instance)

    print("\nGenerating the Quantum Circuit Model with T2.1...")
    quantum_model = transform_t2(lac_model)

    print("\n========== T2.1 RESULTS ==========")

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
    print(
        f"  Minimum: "
        f"{quantum_model.metadata['expression_minimum']}"
    )
    print(
        f"  Maximum: "
        f"{quantum_model.metadata['expression_maximum']}"
    )

    print(
        f"\nSigned accumulator width: "
        f"{quantum_model.metadata['accumulator_width']}"
    )

    print(
        f"Operations currently generated: "
        f"{len(quantum_model.operations)}"
    )

    print("\nT2.1 completed.")
