#!/usr/bin/env python3
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/signup",
                json={"email": "test123@test.com", "password": "SecurePass123"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test())
