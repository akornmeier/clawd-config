#!/usr/bin/env python3
"""
Coverage Validator - Stop Hook

Runs test coverage and blocks completion if coverage is below threshold.
This is a Stop hook - it runs when the agent tries to complete work.

Usage: uv run ~/.claude/hooks/validators/coverage_validator.py
Output: JSON with decision (allow/block) and reason

Environment variables:
  COVERAGE_THRESHOLD: Minimum coverage percentage (default: 80)
"""

import json
import os
import re
import subprocess
from pathlib import Path


DEFAULT_THRESHOLD = 80


def find_project_root() -> Path | None:
    """Find the project root by looking for package.json."""
    cwd = Path.cwd()

    for parent in [cwd] + list(cwd.parents):
        if (parent / "package.json").exists():
            return parent

    return cwd


def run_coverage(project_root: Path) -> tuple[bool, str, float | None]:
    """Run coverage and return (success, output, coverage_percentage)."""
    # Try different coverage commands
    coverage_commands = [
        ["pnpm", "test:coverage"],
        ["pnpm", "run", "test:coverage"],
        ["npm", "run", "test:coverage"],
        ["pnpm", "vitest", "run", "--coverage"],
        ["npx", "vitest", "run", "--coverage"],
    ]

    for cmd in coverage_commands:
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120
            )

            output = result.stdout + result.stderr

            # Check if command was found and ran
            if "not found" in output.lower() or "missing script" in output.lower():
                continue

            # Parse coverage from output
            coverage = parse_coverage(output)

            if coverage is not None:
                return result.returncode == 0, output, coverage

            # If tests passed but no coverage found, check for coverage files
            if result.returncode == 0:
                coverage = read_coverage_file(project_root)
                if coverage is not None:
                    return True, output, coverage

            return result.returncode == 0, output, None

        except subprocess.TimeoutExpired:
            return False, "Coverage check timed out", None
        except FileNotFoundError:
            continue
        except Exception:
            continue

    return False, "No coverage command found", None


def parse_coverage(output: str) -> float | None:
    """Parse coverage percentage from command output."""
    # Look for common coverage output patterns
    patterns = [
        r"All files\s*\|\s*([\d.]+)\s*\|",  # Vitest/Jest table format
        r"Statements\s*:\s*([\d.]+)%",        # Istanbul format
        r"Lines\s*:\s*([\d.]+)%",             # Alternative Istanbul
        r"Coverage:\s*([\d.]+)%",             # Simple format
        r"([\d.]+)%\s*coverage",              # Generic
        r"Total.*?([\d.]+)%",                 # Total row
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    return None


def read_coverage_file(project_root: Path) -> float | None:
    """Try to read coverage from coverage files."""
    coverage_paths = [
        project_root / "coverage" / "coverage-summary.json",
        project_root / "coverage" / "coverage-final.json",
    ]

    for coverage_path in coverage_paths:
        if coverage_path.exists():
            try:
                data = json.loads(coverage_path.read_text())

                # coverage-summary.json format
                if "total" in data and "lines" in data["total"]:
                    return data["total"]["lines"].get("pct", 0)

                # Try to compute from coverage-final.json
                if isinstance(data, dict) and len(data) > 0:
                    total_lines = 0
                    covered_lines = 0
                    for file_data in data.values():
                        if "s" in file_data:  # Statement coverage
                            statements = file_data["s"]
                            total_lines += len(statements)
                            covered_lines += sum(1 for v in statements.values() if v > 0)

                    if total_lines > 0:
                        return (covered_lines / total_lines) * 100

            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    return None


def main():
    threshold = int(os.environ.get("COVERAGE_THRESHOLD", DEFAULT_THRESHOLD))

    # Find project root
    project_root = find_project_root()
    if not project_root:
        # No project found, allow completion
        print(json.dumps({"decision": "allow"}))
        return

    # Check if this is a project with tests
    package_json = project_root / "package.json"
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            scripts = pkg.get("scripts", {})
            has_test = any("test" in k for k in scripts.keys())
            if not has_test:
                # No test scripts, allow completion
                print(json.dumps({"decision": "allow"}))
                return
        except (json.JSONDecodeError, IOError):
            pass

    # Run coverage
    success, output, coverage = run_coverage(project_root)

    if coverage is None:
        # Couldn't determine coverage - allow but warn
        print(json.dumps({
            "decision": "allow",
            "reason": "Could not determine test coverage. Consider adding coverage reporting."
        }))
        return

    if coverage >= threshold:
        print(json.dumps({
            "decision": "allow",
            "reason": f"Coverage: {coverage:.1f}% (threshold: {threshold}%)"
        }))
    else:
        print(json.dumps({
            "decision": "block",
            "reason": f"Coverage too low: {coverage:.1f}% (required: {threshold}%)\n\nAdd more tests to reach the coverage threshold before completing this task."
        }))


if __name__ == "__main__":
    main()
