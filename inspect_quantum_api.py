
import inspect
import besser.BUML.metamodel.quantum as quantum

print("========== BESSER QUANTUM METAMODEL ==========")
print("Module location:", quantum.__file__)

print("\nAvailable quantum classes and operations:")

for name in dir(quantum):
    if any(word in name.lower() for word in (
        "gate", "register", "circuit", "measurement",
        "adder", "control", "qubit", "subcircuit",
        "swap", "phase", "not"
    )):
        obj = getattr(quantum, name)

        if inspect.isclass(obj):
            try:
                signature = inspect.signature(obj)
            except (TypeError, ValueError):
                signature = "(signature unavailable)"

            print(f"\n{name}{signature}")

print("\n========== END ==========")
