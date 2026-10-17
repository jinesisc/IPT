"""
IPT simulations — launcher.

Run a problem by its short name:
    python main.py hourglass
    python main.py            (lists the available problems)

In PyCharm, set the default problem below and press the green Run button,
or add the name under Run > Edit Configurations > Parameters.

To add a new problem:
  1. Create problems/pNN_short_name/ with __init__.py and model.py
  2. Give model.py a main() function
  3. Add one line to PROBLEMS below
"""
import importlib
import sys

# short name -> module path (each module must define main())
PROBLEMS = {
    "hourglass": "problems.p01_magnetic_hourglass.model",
}

DEFAULT = "hourglass"   # what the green Run button runs with no arguments


def run(name: str) -> None:
    if name not in PROBLEMS:
        print(f"Unknown problem '{name}'. Available: {', '.join(PROBLEMS)}")
        sys.exit(1)
    importlib.import_module(PROBLEMS[name]).main()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "list"):
        print("Available problems:\n  " + "\n  ".join(PROBLEMS))
    else:
        run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
