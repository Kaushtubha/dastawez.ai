#!/usr/bin/env python3
"""
Dastawez.ai (DocuMind) - Automated Test Suite Runner
Discovers and executes all unit, parser, API, and chunker benchmark tests.
Supports execution via pytest (if installed) or standalone pure-Python execution.

Usage:
    python scripts/run_tests.py
    python scripts/run_tests.py --standalone
"""

import sys
import os
import time
import inspect
import importlib
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure test fixtures and shim are registered
try:
    import tests.conftest
except Exception:
    pass

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_standalone():
    print("=" * 70)
    print("   🧪 DASTAWEZ.AI (DOCUMIND) — STANDALONE TEST RUNNER")
    print("=" * 70)
    print(f"[*] Workspace Root: {PROJECT_ROOT}")
    print(f"[*] Python Runtime: {sys.version.split()[0]}")
    print("-" * 70)

    test_dir = PROJECT_ROOT / "tests"
    test_files = sorted(test_dir.glob("test_*.py"))

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    start_total_time = time.perf_counter()

    results = []

    for test_file in test_files:
        module_name = f"tests.{test_file.stem}"
        print(f"\n📂 Suite: {test_file.name}")

        try:
            mod = importlib.import_module(module_name)
        except Exception as e:
            print(f"  ❌ Failed to import {module_name}: {e}")
            results.append((test_file.name, "IMPORT_ERROR", 0, str(e)))
            total_failed += 1
            continue

        # Find test functions
        test_funcs = [
            (name, func) for name, func in inspect.getmembers(mod, inspect.isfunction)
            if name.startswith("test_")
        ]

        if not test_funcs:
            print("  ⚠️  No test_* functions discovered.")
            continue

        for name, func in test_funcs:
            t0 = time.perf_counter()
            try:
                # Check parameters - skip pytest fixture-dependent tests if running standalone
                sig = inspect.signature(func)
                if len(sig.parameters) > 0:
                    # Function requires fixtures that standalone runner doesn't mock
                    print(f"  ⏭️  {name:<45} [SKIPPED - requires pytest fixture]")
                    total_skipped += 1
                    continue

                func()
                duration_ms = (time.perf_counter() - t0) * 1000
                print(f"  ✅ {name:<45} [PASS] ({duration_ms:.1f}ms)")
                total_passed += 1
                results.append((f"{test_file.name}::{name}", "PASS", duration_ms, None))
            except AssertionError as ae:
                duration_ms = (time.perf_counter() - t0) * 1000
                print(f"  ❌ {name:<45} [FAIL] ({duration_ms:.1f}ms)")
                print(f"     Assertion: {ae}")
                total_failed += 1
                results.append((f"{test_file.name}::{name}", "FAIL", duration_ms, str(ae)))
            except Exception as ex:
                duration_ms = (time.perf_counter() - t0) * 1000
                print(f"  💥 {name:<45} [ERROR] ({duration_ms:.1f}ms)")
                print(f"     Exception: {ex}")
                total_failed += 1
                results.append((f"{test_file.name}::{name}", "ERROR", duration_ms, str(ex)))

    elapsed = time.perf_counter() - start_total_time

    print("\n" + "=" * 70)
    print("                     TEST EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Total Tests Executed : {total_passed + total_failed}")
    print(f"Passed               : {total_passed} ✅")
    print(f"Failed / Errored     : {total_failed} ❌")
    print(f"Skipped (Fixtures)   : {total_skipped} ⏭️")
    print(f"Elapsed Wall Time    : {elapsed:.3f} seconds")
    print("=" * 70)

    if total_failed > 0:
        print("\n❌ SOME TESTS FAILED. Review output above.")
        return 1
    else:
        print("\n🎉 ALL DISCOVERED TESTS PASSED SUCCESSFULLY!")
        return 0


def main():
    use_standalone = "--standalone" in sys.argv
    if not use_standalone:
        try:
            import pytest
            print("[*] Pytest detected. Executing via pytest runner...")
            sys.exit(pytest.main(["-v", str(PROJECT_ROOT / "tests")]))
        except ImportError:
            print("[!] Pytest not installed in current environment. Running standalone test discovery...")

    sys.exit(run_standalone())


if __name__ == "__main__":
    main()
