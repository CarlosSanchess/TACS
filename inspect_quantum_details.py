
import inspect
import besser.BUML.metamodel.quantum as quantum

classes_to_inspect = [
    "QuantumCircuit",
    "QuantumRegister",
    "ClassicalRegister",
    "ArithmeticGate",
    "ComparisonGate",
    "CustomGate",
    "FunctionGate",
    "GateDefinition",
    "Measurement",
]

for class_name in classes_to_inspect:
    cls = getattr(quantum, class_name)

    print("\n" + "=" * 65)
    print(class_name)
    print("=" * 65)

    print("\nConstructor:")
    print(inspect.signature(cls))

    print("\nAttributes and methods:")
    for name in dir(cls):
        if not name.startswith("_"):
            value = getattr(cls, name)
            if not callable(value):
                print(f"  {name}: {value}")

    print("\nImplementation:")
    try:
        print(inspect.getsource(cls))
    except (OSError, TypeError):
        print("Source unavailable")
