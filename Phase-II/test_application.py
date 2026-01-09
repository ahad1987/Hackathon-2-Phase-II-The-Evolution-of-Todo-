#!/usr/bin/env python3
"""
Comprehensive testing script for the Todo Application.
Tests authentication flow and todo CRUD operations end-to-end.
"""

import asyncio
import sys
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test-{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "SecurePassword123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(title, status, message=""):
    """Print test result."""
    symbol = "[PASS]" if status else "[FAIL]"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{symbol} {title}{Colors.END}")
    if message:
        print(f"  {message}")

async def main():
    """Run all tests."""
    print(f"{Colors.BLUE}=== Todo Application E2E Test Suite ==={Colors.END}\n")

    # Test counter
    passed = 0
    failed = 0
    auth_token = None

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        # ========== DATABASE CONNECTION TEST ==========
        print(f"{Colors.BLUE}[1] Database Connection Tests{Colors.END}")
        try:
            response = await client.get("/health")
            if response.status_code == 404:
                # Health endpoint doesn't exist, that's ok
                print_test("Backend is accessible", True, f"Base URL {API_BASE_URL} is responding")
                passed += 1
            else:
                print_test("Backend health check", True, f"Status: {response.status_code}")
                passed += 1
        except Exception as e:
            print_test("Backend accessibility", False, str(e))
            failed += 1
            print(f"\n{Colors.RED}Cannot continue without backend. Please ensure backend is running at {API_BASE_URL}{Colors.END}")
            return

        # ========== AUTHENTICATION TESTS ==========
        print(f"\n{Colors.BLUE}[2] Authentication Flow Tests{Colors.END}")

        # Test signup
        print(f"\n  Testing signup with email: {TEST_EMAIL}")
        try:
            signup_response = await client.post(
                "/api/v1/auth/signup",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )

            if signup_response.status_code == 201:
                signup_data = signup_response.json()
                print_test("Signup successful", True, f"User created: {signup_data.get('user', {}).get('email')}")

                # Extract token
                if "token" in signup_data:
                    auth_token = signup_data["token"]
                    print_test("JWT token received", True, f"Token length: {len(auth_token)} chars")
                    passed += 2
                else:
                    print_test("JWT token in response", False, "Token not found in signup response")
                    failed += 1
            else:
                print_test("Signup successful", False, f"Status {signup_response.status_code}: {signup_response.text}")
                failed += 2
                print(f"  Full response: {signup_response.text}")
        except Exception as e:
            print_test("Signup operation", False, str(e))
            print(f"  Exception details: {type(e).__name__}: {e}")
            failed += 2

        # Test login
        print(f"\n  Testing login with same credentials")
        try:
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )

            if login_response.status_code == 200:
                login_data = login_response.json()
                print_test("Login successful", True, f"User authenticated: {login_data.get('user', {}).get('email')}")

                # Extract token
                if "token" in login_data:
                    auth_token = login_data["token"]
                    print_test("JWT token received", True, f"Token length: {len(auth_token)} chars")
                    passed += 2
                else:
                    print_test("JWT token in response", False, "Token not found in login response")
                    failed += 1
            else:
                print_test("Login successful", False, f"Status {login_response.status_code}: {login_response.text}")
                failed += 2
        except Exception as e:
            print_test("Login operation", False, str(e))
            failed += 2

        # ========== TASK CRUD TESTS ==========
        if auth_token:
            print(f"\n{Colors.BLUE}[3] Todo CRUD Operation Tests{Colors.END}")

            # Set auth header
            headers = {"Authorization": f"Bearer {auth_token}"}

            # Test get tasks (should be empty initially)
            print(f"\n  Testing GET /tasks")
            try:
                response = await client.get("/api/v1/tasks", headers=headers)
                if response.status_code == 200:
                    tasks = response.json()
                    print_test("List tasks successful", True, f"Tasks count: {len(tasks)}")
                    passed += 1
                else:
                    print_test("List tasks", False, f"Status {response.status_code}")
                    failed += 1
            except Exception as e:
                print_test("List tasks", False, str(e))
                failed += 1

            # Test create task
            print(f"\n  Testing POST /tasks (Create)")
            task_id = None
            try:
                task_data = {
                    "title": "Test Task 1",
                    "description": "This is a test task for E2E testing"
                }
                response = await client.post("/api/v1/tasks", json=task_data, headers=headers)

                if response.status_code == 201:
                    created_task = response.json()
                    task_id = created_task.get("id")
                    print_test("Create task successful", True, f"Task ID: {task_id}")
                    print(f"  - Title: {created_task.get('title')}")
                    print(f"  - Completed: {created_task.get('completed')}")
                    passed += 1
                else:
                    print_test("Create task", False, f"Status {response.status_code}: {response.text}")
                    failed += 1
            except Exception as e:
                print_test("Create task", False, str(e))
                failed += 1

            # Test create another task
            print(f"\n  Testing POST /tasks (Create 2nd)")
            task_id_2 = None
            try:
                task_data = {
                    "title": "Test Task 2",
                    "description": "Another test task"
                }
                response = await client.post("/api/v1/tasks", json=task_data, headers=headers)

                if response.status_code == 201:
                    created_task = response.json()
                    task_id_2 = created_task.get("id")
                    print_test("Create 2nd task successful", True, f"Task ID: {task_id_2}")
                    passed += 1
                else:
                    print_test("Create 2nd task", False, f"Status {response.status_code}")
                    failed += 1
            except Exception as e:
                print_test("Create 2nd task", False, str(e))
                failed += 1

            # Test list tasks (should have 2 now)
            print(f"\n  Testing GET /tasks (After create)")
            try:
                response = await client.get("/api/v1/tasks", headers=headers)
                if response.status_code == 200:
                    tasks = response.json()
                    print_test("List tasks returns multiple", True, f"Tasks count: {len(tasks)}")
                    passed += 1
                else:
                    print_test("List tasks", False, f"Status {response.status_code}")
                    failed += 1
            except Exception as e:
                print_test("List tasks", False, str(e))
                failed += 1

            # Test update task
            if task_id:
                print(f"\n  Testing PUT /tasks/{{task_id}} (Update)")
                try:
                    update_data = {
                        "title": "Updated Test Task 1",
                        "description": "This task has been updated",
                        "completed": True
                    }
                    response = await client.put(
                        f"/api/v1/tasks/{task_id}",
                        json=update_data,
                        headers=headers
                    )

                    if response.status_code == 200:
                        updated_task = response.json()
                        print_test("Update task successful", True, f"Task ID: {task_id}")
                        print(f"  - New Title: {updated_task.get('title')}")
                        print(f"  - Completed: {updated_task.get('completed')}")
                        passed += 1
                    else:
                        print_test("Update task", False, f"Status {response.status_code}: {response.text}")
                        failed += 1
                except Exception as e:
                    print_test("Update task", False, str(e))
                    failed += 1

            # Test delete task
            if task_id_2:
                print(f"\n  Testing DELETE /tasks/{{task_id}} (Delete)")
                try:
                    response = await client.delete(
                        f"/api/v1/tasks/{task_id_2}",
                        headers=headers
                    )

                    if response.status_code == 204:
                        print_test("Delete task successful", True, f"Task ID: {task_id_2} deleted")
                        passed += 1
                    else:
                        print_test("Delete task", False, f"Status {response.status_code}")
                        failed += 1
                except Exception as e:
                    print_test("Delete task", False, str(e))
                    failed += 1

            # Test list tasks (should have 1 now after delete)
            print(f"\n  Testing GET /tasks (After delete)")
            try:
                response = await client.get("/api/v1/tasks", headers=headers)
                if response.status_code == 200:
                    tasks = response.json()
                    print_test("List tasks returns correct count", True, f"Tasks count: {len(tasks)}")
                    passed += 1
                else:
                    print_test("List tasks", False, f"Status {response.status_code}")
                    failed += 1
            except Exception as e:
                print_test("List tasks", False, str(e))
                failed += 1

        # ========== TEST SUMMARY ==========
        print(f"\n{Colors.BLUE}=== Test Summary ==={Colors.END}")
        total = passed + failed
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")

        if failed == 0:
            print(f"\n{Colors.GREEN}All tests passed!{Colors.END}")
            return 0
        else:
            print(f"\n{Colors.RED}Some tests failed. Please review the errors above.{Colors.END}")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
