from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph import build_index
from load import load_catalog
from validate import validate_catalog


def main() -> int:
    catalog = load_catalog()
    index = build_index(catalog)
    errors = validate_catalog(catalog, index)
    if errors:
        print("VALIDATION FAILED")
        print("\n".join(errors))
        return 1
    print(f"OK: {len(catalog.tools)} tools, {len(catalog.tasks)} tasks, {len(catalog.workflows)} workflows, {len(catalog.papers)} papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
