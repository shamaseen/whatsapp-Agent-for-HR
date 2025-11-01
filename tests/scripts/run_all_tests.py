#!/usr/bin/env python3
"""
Master Test Runner for WhatsApp HR Assistant
Runs all comprehensive test suites and generates a combined report
"""

import sys
import asyncio
import subprocess
from datetime import datetime

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_banner():
    """Print test runner banner"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'WHATSAPP HR ASSISTANT - MASTER TEST RUNNER'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    print(f"{CYAN}Comprehensive Testing Suite{RESET}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def print_section(title: str):
    """Print a section header"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{CYAN}{title.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

async def run_test_script(script_name: str, description: str):
    """Run a test script and capture results"""
    print(f"{CYAN}Running: {description}{RESET}")
    print(f"Command: python {script_name}\n")

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        output = []
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            decoded = line.decode('utf-8')
            print(decoded, end='')
            output.append(decoded)

        await process.wait()

        # Parse results
        success = process.returncode == 0

        # Extract test statistics from output
        passed = 0
        failed = 0
        for line in output:
            if 'Passed:' in line and 'Failed:' in line:
                try:
                    parts = line.split('Passed:')
                    if len(parts) > 1:
                        failed_part = parts[1].split('Failed:')
                        if len(failed_part) > 1:
                            passed = int(failed_part[0].strip())
                            failed = int(failed_part[1].split('Success Rate:')[0].strip())
                except:
                    pass

        print(f"\n{'='*80}\n")
        if success:
            print(f"{GREEN}✓ {description} - PASSED{RESET}")
        else:
            print(f"{RED}✗ {description} - FAILED{RESET}")

        return {
            'name': description,
            'script': script_name,
            'success': success,
            'passed': passed,
            'failed': failed,
            'output': '\n'.join(output)
        }

    except Exception as e:
        print(f"\n{RED}✗ {description} - ERROR: {str(e)}{RESET}\n")
        return {
            'name': description,
            'script': script_name,
            'success': False,
            'passed': 0,
            'failed': 0,
            'error': str(e)
        }

def print_summary_report(results):
    """Print comprehensive summary report"""
    print_section("COMPREHENSIVE TEST SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests

    # Calculate overall statistics
    total_passes = sum(r['passed'] for r in results)
    total_failures = sum(r['failed'] for r in results)
    total_individual_tests = total_passes + total_failures

    print(f"{CYAN}=== OVERALL RESULTS ==={RESET}\n")
    print(f"Test Suites: {total_tests}")
    print(f"{GREEN}Passed: {passed_tests}{RESET}")
    print(f"{RED}Failed: {failed_tests}{RESET}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

    print(f"\n{CYAN}=== INDIVIDUAL TEST RESULTS ==={RESET}\n")
    print(f"Total Individual Tests Run: {total_individual_tests}")
    print(f"{GREEN}Total Passed: {total_passes}{RESET}")
    print(f"{RED}Total Failed: {total_failures}{RESET}")
    print(f"Success Rate: {(total_passes/total_individual_tests*100):.1f}%" if total_individual_tests > 0 else "N/A")

    print(f"\n{CYAN}=== DETAILED RESULTS ==={RESET}\n")
    print(f"{'Test Suite':<40} {'Status':<10} {'Passed':<10} {'Failed':<10}")
    print(f"{'-'*80}")

    for result in results:
        status = f"{GREEN}PASS{RESET}" if result['success'] else f"{RED}FAIL{RESET}"
        passed = result.get('passed', 0)
        failed = result.get('failed', 0)
        print(f"{result['name']:<40} {status:<10} {passed:<10} {failed:<10}")

    print(f"\n{CYAN}=== FAILURE DETAILS ==={RESET}\n")

    failures = [r for r in results if not r['success']]
    if failures:
        for failure in failures:
            print(f"{RED}✗ {failure['name']}{RESET}")
            if 'error' in failure:
                print(f"   Error: {failure['error']}")
            print()
    else:
        print(f"{GREEN}All tests passed! No failures to report.{RESET}")

    print(f"\n{BLUE}{'='*80}{RESET}")
    if passed_tests == total_tests:
        print(f"{GREEN}{'🎉 ALL TEST SUITES PASSED! 🎉'.center(80)}{RESET}")
    else:
        print(f"{YELLOW}{'⚠️  SOME TEST SUITES FAILED'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    return passed_tests == total_tests

def print_action_items(results):
    """Print suggested action items"""
    failures = [r for r in results if not r['success']]

    if not failures:
        return

    print_section("SUGGESTED ACTIONS")

    print(f"{YELLOW}The following test suites failed:{RESET}\n")

    for failure in failures:
        print(f"{RED}✗ {failure['name']}{RESET}")
        print(f"   Script: {failure['script']}")
        if 'error' in failure:
            print(f"   Error: {failure['error']}")
        print()

    print(f"{CYAN}Troubleshooting Steps:{RESET}\n")
    print(f"1. Check the error output above for specific failures")
    print(f"2. Verify configuration files (.env, config/tools.yaml)")
    print(f"3. Ensure all dependencies are installed: pip install -r requirements.txt")
    print(f"4. Check database connectivity (DATABASE_URL)")
    print(f"5. Verify Google API credentials (client_secret.json, token.pickle)")
    print(f"6. Review individual test output for detailed diagnostics")
    print()

async def main():
    """Main test runner"""
    print_banner()

    # Define all test suites
    test_suites = [
        ("comprehensive_test_suite.py", "Complete System Test Suite"),
        ("test_mcp_comprehensive.py", "MCP Protocol Tests"),
        ("test_agents_comprehensive.py", "Agent System Tests"),
        ("test_tools_comprehensive.py", "Tools System Tests"),
        ("test_memory_comprehensive.py", "Memory System Tests"),
    ]

    results = []

    # Run each test suite
    for script, description in test_suites:
        try:
            result = await run_test_script(script, description)
            results.append(result)
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Testing interrupted by user.{RESET}\n")
            break
        except Exception as e:
            print(f"\n{RED}Unexpected error running {description}: {str(e)}{RESET}\n")
            results.append({
                'name': description,
                'script': script,
                'success': False,
                'error': str(e)
            })

    # Print comprehensive summary
    all_passed = print_summary_report(results)

    # Print action items if needed
    if not all_passed:
        print_action_items(results)

    # Exit with appropriate code
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
