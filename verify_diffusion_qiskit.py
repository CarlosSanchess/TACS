
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import numpy as np


N = 4


def build_diffusion():
    """Build the four-qubit Grover diffusion operator."""

    qc = QuantumCircuit(N)

    # H on every decision qubit.
    for q in range(N):
        qc.h(q)

    # X on every decision qubit.
    for q in range(N):
        qc.x(q)

    # Multi-controlled Z, implemented as H-MCX-H.
    target = N - 1
    controls = list(range(N - 1))

    # Multi-controlled Z phase flip.
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)

    # Undo X.
    for q in range(N):
        qc.x(q)

    # Undo H.
    for q in range(N):
        qc.h(q)

    return qc


def main():
    print("Qiskit diffusion statevector verification")
    print("=" * 55)

    diffusion = build_diffusion()

    print("Number of qubits:", diffusion.num_qubits)
    print("Number of operations:", diffusion.size())

    # Test 1: Apply diffusion to |0000>.
    initial_state = Statevector.from_label("0000")
    final_state = initial_state.evolve(diffusion)

    expected = np.full(2 ** N, -1 / 8, dtype=complex)
    expected[0] = 7 / 8

    error = np.max(np.abs(final_state.data - expected))

    print("\nTest 1: Diffusion applied to |0000>")
    print("Expected amplitude of |0000>: +7/8")
    print("Actual amplitude of |0000>:", final_state.data[0])
    print("Maximum amplitude error:", error)

    assert np.allclose(final_state.data, expected, atol=1e-10)
    print("PASS")

    # Test 2: The uniform superposition is unchanged by diffusion.
    uniform_circuit = QuantumCircuit(N)
    uniform_circuit.h(range(N))

    uniform_state = Statevector.from_instruction(uniform_circuit)
    diffused_uniform = uniform_state.evolve(diffusion)

    uniform_error = np.max(
        np.abs(diffused_uniform.data - uniform_state.data)
    )

    print("\nTest 2: Diffusion applied to uniform superposition")
    print("Maximum amplitude error:", uniform_error)

    assert np.allclose(
        diffused_uniform.data,
        -uniform_state.data,
        atol=1e-10
    )
    print("Expected: negative of the original uniform state")
    print("PASS")

    print("\nALL QISKIT DIFFUSION TESTS PASSED")


if __name__ == "__main__":
    main()
