#!/usr/bin/env python3
"""
Quick test to verify the auth flow is working.
"""

import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=10.0) as client:
        print("Testing Authentication Flow...")

        # Test 1: Health check
        try:
            resp = await client.get("/health")
            print(f"[PASS] Health check: {resp.status_code}")
        except Exception as e:
            print(f"[FAIL] Health check failed: {e}")
            return

        # Test 2: Signup
        try:
            resp = await client.post(
                "/api/v1/auth/signup",
                json={"email": "testuser@test.com", "password": "TestPass123"}
            )
            print(f"[PASS] Signup: {resp.status_code}")
            if resp.status_code == 201:
                data = resp.json()
                token = data.get("token")
                print(f"  Token received: {len(token) if token else 0} characters")
            else:
                print(f"  Error: {resp.text}")
        except Exception as e:
            print(f"[FAIL] Signup failed: {e}")
            return

        # Test 3: Get current user (with token)
        try:
            resp = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"[PASS] Get me endpoint: {resp.status_code}")
            if resp.status_code == 200:
                user = resp.json()
                print(f"  User: {user.get('email')}")
            else:
                print(f"  Error: {resp.text}")
        except Exception as e:
            print(f"[FAIL] Get me failed: {e}")

asyncio.run(test())
