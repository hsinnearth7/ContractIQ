"""CLI: Generate synthetic contracts for demo and testing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contractiq.config import get_settings
from contractiq.data.synthetic_generator import generate_contracts


def main():
    settings = get_settings()
    output_dir = settings.sample_contracts_dir
    count = 20

    print(f"ContractIQ - Synthetic Contract Generator")
    print(f"Output directory: {output_dir}")
    print(f"Count: {count}")
    print("-" * 50)

    files = generate_contracts(output_dir, count=count)

    print(f"\nDone! Generated {len(files)} contracts.")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    main()
