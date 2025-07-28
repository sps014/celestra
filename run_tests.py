#!/usr/bin/env python3
"""
K8s-Gen DSL Test Execution Script

This script provides a simple way to run the comprehensive test suite.
"""

import sys
import os
import subprocess

def main():
    """Main test execution function."""
    print("🧪 K8s-Gen DSL Comprehensive Test Suite")
    print("=" * 50)
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add src to Python path
    src_path = os.path.join(script_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        # Run the comprehensive test suite
        print("🚀 Starting test execution...")
        result = subprocess.run([
            sys.executable, 
            "src/test/test_run_all.py"
        ] + sys.argv[1:], check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests completed successfully!")
            print("🎉 K8s-Gen DSL is ready for use!")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            print("🔧 Please review and fix any issues before proceeding.")
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: Test runner not found. Please ensure the test suite is properly installed.")
        return 1
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 