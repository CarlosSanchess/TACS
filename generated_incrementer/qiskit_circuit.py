import sys
import os
sys.path = [p.strip() for p in sys.path if p]
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit import Instruction

from qiskit_aer import AerSimulator

from qiskit.circuit.library import *
from qiskit.circuit.library.standard_gates import GlobalPhaseGate
import numpy as np










# Function Gate Definitions



# Initialize Registers

accumulator = QuantumRegister(6, 'accumulator')



# Initialize Circuit
qc = QuantumCircuit(accumulator)

# Operations

qc.append(XGate().control(5, ctrl_state='11111'), [q[0], q[1], q[2], q[3], q[4], q[5]])

qc.append(XGate().control(4, ctrl_state='1111'), [q[0], q[1], q[2], q[3], q[4]])

qc.append(XGate().control(3, ctrl_state='111'), [q[0], q[1], q[2], q[3]])

qc.append(XGate().control(2, ctrl_state='11'), [q[0], q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate(), [q[0]])


# Draw
print(qc.draw())


# Execution (Local Aer Simulator)
print("Simulating circuit with Aer Simulator...")
simulator = AerSimulator()
transpiled_qc = transpile(qc, simulator)
result = simulator.run(transpiled_qc, shots=1024).result()
counts = result.get_counts()
print("Counts:", counts)
