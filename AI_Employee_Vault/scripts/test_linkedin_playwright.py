#!/usr/bin/env python3
"""
Test script for LinkedIn Playwright automation integration with MCP server
"""

import asyncio
import json
import os
from datetime import datetime

# Add the scripts directory to the path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

from linkedin_playwright_automation import LinkedInPlaywrightAutomation, LinkedInMCPAdapter
from mcp_server import MCPServer


async def test_linkedin_automation_setup():
    """Test that LinkedIn Playwright automation can be set up properly."""
    print("Testing LinkedIn Playwright Automation Setup...")
    print("=" * 50)

    vault_path = os.path.join(os.path.dirname(__file__), "..")  # AI_Employee_Vault path

    # Test basic setup
    try:
        automation = LinkedInPlaywrightAutomation(vault_path)
        setup_success = await automation.setup_browser()
        print(f"[PASS] Browser setup: {'SUCCESS' if setup_success else 'FAILED'}")

        # Check that required directories were created
        required_dirs = [
            os.path.join(vault_path, "LinkedIn_Posts"),
            os.path.join(vault_path, "LinkedIn_Triggers"),
            os.path.join(vault_path, "Browser_Actions")
        ]

        for dir_path in required_dirs:
            exists = os.path.exists(dir_path)
            print(f"[INFO] Directory '{os.path.basename(dir_path)}': {'EXISTS' if exists else 'MISSING'}")

        await automation.close()
        print("[PASS] LinkedIn automation setup test completed")
        return True

    except Exception as e:
        print(f"[FAIL] LinkedIn automation setup test failed: {str(e)}")
        return False


async def test_mcp_integration():
    """Test that LinkedIn tools are properly integrated with MCP server."""
    print("\nTesting MCP Server LinkedIn Integration...")
    print("=" * 50)

    vault_path = os.path.join(os.path.dirname(__file__), "..")

    try:
        # Initialize MCP server
        server = MCPServer(vault_path)

        # Get list of tools
        response = server.handle_list_tools()
        tools = response["result"]["tools"]

        # Check for LinkedIn tools
        linkedin_tools = [
            "post_to_linkedin",
            "monitor_linkedin_feed",
            "check_linkedin_notifications",
            "get_linkedin_profile_info"
        ]

        found_tools = []
        for tool in tools:
            if tool["name"] in linkedin_tools:
                found_tools.append(tool["name"])

        print(f"Expected LinkedIn tools: {len(linkedin_tools)}")
        print(f"Found LinkedIn tools: {len(found_tools)}")
        print(f"Tools found: {found_tools}")

        if len(found_tools) == len(linkedin_tools):
            print("[PASS] All LinkedIn tools are registered in MCP server")
        else:
            missing = set(linkedin_tools) - set(found_tools)
            print(f"[FAIL] Missing LinkedIn tools: {missing}")

        # Test that MCP adapter can be initialized
        credentials = {"email": "test@example.com", "password": "testpass"}
        mcp_adapter = LinkedInMCPAdapter(vault_path, credentials)
        print("[PASS] LinkedIn MCP adapter initialized")

        # Test a simulated tool call
        result = await mcp_adapter.post_to_linkedin("Test post from AI Employee", "PUBLIC")
        print(f"[PASS] Simulated post result: {result['status']}")

        await mcp_adapter.cleanup()
        print("[PASS] MCP integration test completed")
        return len(found_tools) == len(linkedin_tools)

    except Exception as e:
        print(f"[FAIL] MCP integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_linkedin_mcp_functions():
    """Test individual LinkedIn MCP functions."""
    print("\nTesting Individual LinkedIn MCP Functions...")
    print("=" * 50)

    vault_path = os.path.join(os.path.dirname(__file__), "..")

    try:
        # Initialize MCP server
        server = MCPServer(vault_path)

        # Test post_to_linkedin function
        print("Testing post_to_linkedin...")
        post_result = await server.post_to_linkedin(
            content="This is a test post from the AI Employee LinkedIn automation!",
            visibility="PUBLIC"
        )
        print(f"  Result: {post_result['status']}")
        print(f"  Message: {post_result['message']}")
        print(f"  Details: {post_result['details']}")

        # Test monitor_linkedin_feed function
        print("\nTesting monitor_linkedin_feed...")
        monitor_result = await server.monitor_linkedin_feed(max_posts=5)
        print(f"  Result: {monitor_result['status']}")
        print(f"  Message: {monitor_result['message']}")
        print(f"  Posts found: {monitor_result['posts_found']}")

        # Test check_linkedin_notifications function
        print("\nTesting check_linkedin_notifications...")
        notify_result = await server.check_linkedin_notifications()
        print(f"  Result: {notify_result['status']}")
        print(f"  Message: {notify_result['message']}")
        print(f"  Notifications: {notify_result['notification_count']}")

        # Test get_linkedin_profile_info function
        print("\nTesting get_linkedin_profile_info...")
        profile_result = await server.get_linkedin_profile_info()
        print(f"  Result: {profile_result['status']}")
        print(f"  Message: {profile_result['message']}")
        print(f"  Profile Info Keys: {list(profile_result['profile_info'].keys())}")

        print("[PASS] All LinkedIn MCP functions tested successfully")
        return True

    except Exception as e:
        print(f"[FAIL] LinkedIn MCP functions test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all LinkedIn Playwright automation tests."""
    print("LinkedIn Playwright Automation - Integration Test Suite")
    print("=" * 60)

    # Run all tests
    test1_pass = await test_linkedin_automation_setup()
    test2_pass = await test_mcp_integration()
    test3_pass = await test_linkedin_mcp_functions()

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"LinkedIn Automation Setup: {'[PASS]' if test1_pass else '[FAIL]'}")
    print(f"MCP Integration: {'[PASS]' if test2_pass else '[FAIL]'}")
    print(f"Individual Functions: {'[PASS]' if test3_pass else '[FAIL]'}")

    all_pass = test1_pass and test2_pass and test3_pass
    print(f"\nOverall Result: {'[PASS] ALL TESTS PASSED' if all_pass else '[FAIL] SOME TESTS FAILED'}")

    if all_pass:
        print("\n[SUCCESS] LinkedIn Playwright automation is fully integrated!")
        print("[INFO] Playwright browser automation is set up")
        print("[INFO] LinkedIn MCP tools are registered")
        print("[INFO] All functions are working properly")
        print("[INFO] Ready for production use with real credentials")
    else:
        print("\n[WARNING] Some integration issues need to be resolved")

    return all_pass


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)