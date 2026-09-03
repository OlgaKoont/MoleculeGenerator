from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys_path_note = "run from site/"

def run():
    import runpy
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    for name in [
        "import_xlsx",
        "seed_tasks",
        "seed_workflows",
        "seed_architectures",
        "seed_glossary",
        "enrich_tools",
    ]:
        runpy.run_module(name, run_name="__main__")


if __name__ == "__main__":
    run()
