
import inspect
import besser.BUML.metamodel.quantum as quantum

print("========== ARITHMETIC GATE INSPECTION ==========")

for name in dir(quantum):
    cls = getattr(quantum, name)

    if not inspect.isclass(cls):
        continue

    try:
        is_arithmetic = issubclass(
            cls, quantum.ArithmeticGate
        )
    except TypeError:
        is_arithmetic = False

    if is_arithmetic or name in (
        "MultiBitGate",
        "PrimitiveGate",
        "SingleBitGate",
        "CNOT",
        "CXGate",
        "PauliXGate",
    ):
        print(f"\n{name}")
        print("Signature:", inspect.signature(cls))

        try:
            print(inspect.getsource(cls))
        except (OSError, TypeError):
            print("Source unavailable")

print("\n========== AVAILABLE GATE MODULE ==========")
print(quantum.__file__)
