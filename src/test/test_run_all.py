#!/usr/bin/env python3
"""
Test Runner for Celestraa DSL Comprehensive Test Suite.

This script runs all test suites and provides comprehensive reporting.
"""

import sys
import time
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import json


class TestRunner:
    """Comprehensive test runner for Celestraa DSL."""
    
    def __init__(self):
        self.test_modules = [
            "test_core_components",
            "test_workloads", 
            "test_networking",
            "test_security",
            "test_observability",
            "test_advanced_features",
            "test_output_formats",
            "test_plugins",
            "test_validation",
            "test_integration",
            "test_examples"
        ]
        
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self, verbose: bool = True, fail_fast: bool = False) -> bool:
        """Run all test suites and return overall success status."""
        print("🧪 Celestraa DSL Comprehensive Test Suite")
        print("=" * 65)
        print(f"🎯 Running {len(self.test_modules)} test modules")
        print("=" * 65)
        
        self.start_time = time.time()
        overall_success = True
        
        for module in self.test_modules:
            print(f"\n📋 Running {module}...")
            success, stats = self._run_test_module(module, verbose)
            
            self.results[module] = {
                "success": success,
                "stats": stats,
                "timestamp": time.time()
            }
            
            if success:
                print(f"✅ {module}: PASSED ({stats.get('passed', 0)} tests)")
            else:
                print(f"❌ {module}: FAILED ({stats.get('failed', 0)} failures)")
                overall_success = False
                
                if fail_fast:
                    print(f"\n🛑 Stopping due to failure in {module} (fail-fast mode)")
                    break
        
        self.end_time = time.time()
        self._print_summary()
        
        return overall_success
    
    def _run_test_module(self, module: str, verbose: bool) -> Tuple[bool, Dict]:
        """Run a single test module and return success status and stats."""
        try:
            # Construct pytest command
            cmd = [
                sys.executable, "-m", "pytest",
                f"src/test/{module}.py",
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header",
                "--json-report",
                "--json-report-file=/tmp/pytest_report.json"
            ]
            
            # Run the test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per module
            )
            
            # Parse results
            stats = self._parse_pytest_output(result.stdout, result.stderr)
            success = result.returncode == 0
            
            return success, stats
            
        except subprocess.TimeoutExpired:
            return False, {"error": "Test timeout"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> Dict:
        """Parse pytest output to extract statistics."""
        stats = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "duration": 0.0
        }
        
        # Try to parse JSON report if available
        try:
            if os.path.exists("/tmp/pytest_report.json"):
                with open("/tmp/pytest_report.json", "r") as f:
                    report = json.load(f)
                
                summary = report.get("summary", {})
                stats.update({
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "skipped": summary.get("skipped", 0),
                    "errors": summary.get("error", 0),
                    "total": summary.get("total", 0),
                    "duration": report.get("duration", 0.0)
                })
                
                # Clean up temp file
                os.remove("/tmp/pytest_report.json")
                return stats
        except Exception:
            pass
        
        # Fallback to parsing stdout
        lines = stdout.split('\n')
        for line in lines:
            if "passed" in line and "failed" in line:
                # Try to extract numbers from summary line
                words = line.split()
                for i, word in enumerate(words):
                    if word == "passed" and i > 0:
                        try:
                            stats["passed"] = int(words[i-1])
                        except ValueError:
                            pass
                    elif word == "failed" and i > 0:
                        try:
                            stats["failed"] = int(words[i-1])
                        except ValueError:
                            pass
                    elif word == "skipped" and i > 0:
                        try:
                            stats["skipped"] = int(words[i-1])
                        except ValueError:
                            pass
        
        stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"] + stats["errors"]
        return stats
    
    def _print_summary(self):
        """Print comprehensive test summary."""
        total_duration = self.end_time - self.start_time
        
        print("\n🎉 TEST SUITE SUMMARY")
        print("=" * 65)
        
        # Calculate totals
        total_passed = sum(r["stats"].get("passed", 0) for r in self.results.values())
        total_failed = sum(r["stats"].get("failed", 0) for r in self.results.values())
        total_skipped = sum(r["stats"].get("skipped", 0) for r in self.results.values())
        total_errors = sum(r["stats"].get("errors", 0) for r in self.results.values())
        total_tests = total_passed + total_failed + total_skipped + total_errors
        
        successful_modules = sum(1 for r in self.results.values() if r["success"])
        total_modules = len(self.results)
        
        print(f"📊 OVERALL RESULTS:")
        print(f"  🧪 Total Tests: {total_tests}")
        print(f"  ✅ Passed: {total_passed}")
        print(f"  ❌ Failed: {total_failed}")
        print(f"  ⏭️  Skipped: {total_skipped}")
        print(f"  🚨 Errors: {total_errors}")
        print(f"  📁 Modules: {successful_modules}/{total_modules} successful")
        print(f"  ⏱️  Duration: {total_duration:.2f} seconds")
        
        # Success rate
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Module breakdown
        print(f"\n📋 MODULE BREAKDOWN:")
        for module, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            stats = result["stats"]
            passed = stats.get("passed", 0)
            failed = stats.get("failed", 0)
            total_module = stats.get("total", 0)
            duration = stats.get("duration", 0.0)
            
            print(f"  {status} {module}: {passed}/{total_module} tests ({duration:.2f}s)")
            if failed > 0:
                print(f"    └─ {failed} failures")
        
        # Overall status
        print(f"\n🏆 OVERALL STATUS:")
        if successful_modules == total_modules and total_failed == 0:
            print(f"  🌟 ALL TESTS PASSED! Celestraa DSL is fully functional!")
        elif total_failed == 0:
            print(f"  ✅ All tests passed, but some modules had issues")
        else:
            print(f"  ⚠️  {total_failed} test failures detected - review required")
        
        # Performance summary
        if total_duration > 0:
            tests_per_second = total_tests / total_duration
            print(f"\n⚡ PERFORMANCE:")
            print(f"  🏃 Test Execution Rate: {tests_per_second:.1f} tests/second")
            print(f"  📊 Average Module Duration: {total_duration/total_modules:.2f} seconds")
        
        # Next steps
        print(f"\n🎯 NEXT STEPS:")
        if total_failed > 0:
            print(f"  1. Review failed tests and fix implementation issues")
            print(f"  2. Run individual test modules for detailed debugging")
            print(f"  3. Check logs for specific error details")
        else:
            print(f"  1. ✅ All tests passing - ready for production use!")
            print(f"  2. 📚 Review coverage reports for any gaps")
            print(f"  3. 🚀 Deploy with confidence!")
    
    def run_specific_modules(self, modules: List[str], verbose: bool = True) -> bool:
        """Run specific test modules."""
        print(f"🧪 Running specific test modules: {', '.join(modules)}")
        print("=" * 65)
        
        self.start_time = time.time()
        overall_success = True
        
        for module in modules:
            if module not in self.test_modules:
                print(f"⚠️  Warning: {module} is not a valid test module")
                continue
            
            print(f"\n📋 Running {module}...")
            success, stats = self._run_test_module(module, verbose)
            
            self.results[module] = {
                "success": success,
                "stats": stats,
                "timestamp": time.time()
            }
            
            if success:
                print(f"✅ {module}: PASSED")
            else:
                print(f"❌ {module}: FAILED")
                overall_success = False
        
        self.end_time = time.time()
        self._print_summary()
        
        return overall_success
    
    def generate_report(self, output_file: str = "test_report.json"):
        """Generate detailed test report."""
        report = {
            "timestamp": time.time(),
            "duration": self.end_time - self.start_time if self.end_time and self.start_time else 0,
            "modules": self.results,
            "summary": {
                "total_modules": len(self.results),
                "successful_modules": sum(1 for r in self.results.values() if r["success"]),
                "total_tests": sum(r["stats"].get("total", 0) for r in self.results.values()),
                "passed_tests": sum(r["stats"].get("passed", 0) for r in self.results.values()),
                "failed_tests": sum(r["stats"].get("failed", 0) for r in self.results.values()),
                "skipped_tests": sum(r["stats"].get("skipped", 0) for r in self.results.values())
            }
        }
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Test report generated: {output_file}")


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Celestraa DSL Test Runner")
    parser.add_argument("--modules", nargs="+", help="Specific modules to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("--report", help="Generate JSON report file")
    parser.add_argument("--list", action="store_true", help="List available test modules")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        print("Available test modules:")
        for module in runner.test_modules:
            print(f"  - {module}")
        return
    
    # Run tests
    if args.modules:
        success = runner.run_specific_modules(args.modules, args.verbose)
    else:
        success = runner.run_all_tests(args.verbose, args.fail_fast)
    
    # Generate report if requested
    if args.report:
        runner.generate_report(args.report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 