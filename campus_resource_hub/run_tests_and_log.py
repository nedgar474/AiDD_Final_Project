"""Script to run tests and save results to tests_log.txt"""
import subprocess
import sys
import os
from pathlib import Path

# Change to the campus_resource_hub directory
test_dir = Path(__file__).parent
os.chdir(test_dir)

# Run pytest
result = subprocess.run(
    ['python', '-m', 'pytest', 'tests/', '-v', '--ignore=tests/ai_eval', '--tb=short'],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

# Combine stdout and stderr
output = result.stdout + result.stderr

# Save to file
with open('tests_log.txt', 'w', encoding='utf-8') as f:
    f.write(output)

# Print summary
print(f"Tests completed with exit code: {result.returncode}")
print(f"Results saved to: {test_dir / 'tests_log.txt'}")
print(f"\nSummary:")
print(f"  Total output lines: {len(output.splitlines())}")

# Print last 20 lines as preview
lines = output.splitlines()
if len(lines) > 20:
    print(f"\nLast 20 lines of output:")
    for line in lines[-20:]:
        print(f"  {line}")
else:
    print(f"\nFull output:")
    print(output)

sys.exit(result.returncode)

