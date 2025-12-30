import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command safely and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error code {e.returncode}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ {description} failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    steps = [
        ([sys.executable, "data/generate_dummy_invoices.py"], "Generate dummy invoices"),
        ([sys.executable, "src/model/train.py"], "Train model"),
        ([sys.executable, "src/api/app.py"], "Start Flask API")
    ]
    
    for cmd, description in steps:
        if not run_command(cmd, description):
            print(f"\nStopping pipeline at: {description}")
            sys.exit(1)