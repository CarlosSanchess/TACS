
from test_oracle import build_oracle


# Qubit layout:
# 0-3: decision qubits
# 4-9: six-bit accumulator
# 10: phase-marking qubit

DECISION_QUBITS = 4
ACCUMULATOR_START = 4
ACCUMULATOR_SIZE = 6
PHASE_QUBIT = 10

WEIGHTS = [4, 6, 10, 12]
INITIAL_VALUE = -16


def expected_expression(assignment):
    """Calculate the expression using ordinary Python arithmetic."""
    return sum(
        weight * bit
        for weight, bit in zip(WEIGHTS, assignment)
    ) + INITIAL_VALUE


def controls_are_satisfied(operation, bits):
    """Check whether all control conditions of an operation are satisfied."""
    for qubit, state in zip(
        operation.control_qubits or [],
        operation.control_states or []
    ):
        state_value = state.value

        if state_value == "CONTROL" and bits[qubit] != 1:
            return False

        if state_value == "ANTI_CONTROL" and bits[qubit] != 0:
            return False

    return True


def simulate_oracle_basis_input(circuit, assignment):
    """
    Simulate the oracle's X operations on a computational-basis input.

    The phase qubit is treated as already prepared in |->.
    Therefore, an X operation targeting it changes the phase sign.
    """

    bits = [0] * 11

    # Set the four decision qubits.
    for i, bit in enumerate(assignment):
        bits[i] = bit

    phase_sign = 1

    # Skip the first two operations (X and H on the phase qubit).
    # They prepare the phase qubit in |->.
    for operation in circuit.operations[2:]:

        targets = operation.target_qubits or []

        if not controls_are_satisfied(operation, bits):
            continue

        for target in targets:

            if target == PHASE_QUBIT:
                # X|-> = -|-> : phase kickback
                phase_sign *= -1
            else:
                # Ordinary controlled-X on a computational-basis bit.
                bits[target] ^= 1

    accumulator = bits[
        ACCUMULATOR_START:
        ACCUMULATOR_START + ACCUMULATOR_SIZE
    ]

    decision_bits = bits[:DECISION_QUBITS]

    return decision_bits, accumulator, phase_sign


def main():
    circuit = build_oracle()

    print("Exhaustive oracle verification")
    print("=" * 55)

    successful_tests = 0
    marked_assignments = []

    for number in range(2 ** DECISION_QUBITS):

        # Convert integer into four little-endian decision bits.
        assignment = [
            (number >> i) & 1
            for i in range(DECISION_QUBITS)
        ]

        expression = expected_expression(assignment)

        expected_mark = -1 if expression == 0 else 1

        final_decisions, final_accumulator, phase_sign = (
            simulate_oracle_basis_input(circuit, assignment)
        )

        decisions_unchanged = final_decisions == assignment
        accumulator_restored = all(bit == 0 for bit in final_accumulator)
        phase_correct = phase_sign == expected_mark

        passed = (
            decisions_unchanged
            and accumulator_restored
            and phase_correct
        )

        if expression == 0:
            marked_assignments.append(assignment)

        if passed:
            successful_tests += 1

        bit_string = "".join(str(bit) for bit in reversed(assignment))

        print(
            f"{bit_string} | "
            f"E={expression:3d} | "
            f"phase={phase_sign:+d} | "
            f"accumulator={final_accumulator} | "
            f"{'PASS' if passed else 'FAIL'}"
        )

    print("=" * 55)
    print(f"Successful tests: {successful_tests}/16")

    print(
        "Marked assignments:",
        [
            "".join(str(bit) for bit in reversed(a))
            for a in marked_assignments
        ]
    )

    if successful_tests == 16:
        print("\nALL ORACLE TESTS PASSED")
    else:
        raise AssertionError("Oracle verification failed!")


if __name__ == "__main__":
    main()
