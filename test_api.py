"""
Test script for Command Gateway API
This script demonstrates all the main features of the API.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Use the admin API key from seed output
ADMIN_API_KEY = "HnXVX7endKivrmVLnigm6i7RAPwBIGY85yDVSAd96Nec9XsPYIYavqIlC1tORf2I"

def test_health_check():
    """Test basic health check"""
    print("\n" + "="*50)
    print("TEST: Health Check")
    print("="*50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_get_user_info():
    """Test getting current user info"""
    print("\n" + "="*50)
    print("TEST: Get Admin User Info")
    print("="*50)
    headers = {"X-API-Key": ADMIN_API_KEY}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_create_member_user():
    """Test creating a new member user"""
    print("\n" + "="*50)
    print("TEST: Create Member User")
    print("="*50)
    headers = {"X-API-Key": ADMIN_API_KEY}
    data = {"username": "john_doe", "role": "member"}
    response = requests.post(f"{BASE_URL}/users/", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["api_key"]
    return None


def test_list_rules():
    """Test listing all rules"""
    print("\n" + "="*50)
    print("TEST: List All Rules")
    print("="*50)
    headers = {"X-API-Key": ADMIN_API_KEY}
    response = requests.get(f"{BASE_URL}/rules/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Number of rules: {len(response.json())}")
    for rule in response.json()[:3]:  # Show first 3 rules
        print(f"  - {rule['description']}: {rule['action']}")
    return response.status_code == 200


def test_submit_safe_command(api_key):
    """Test submitting a safe command"""
    print("\n" + "="*50)
    print("TEST: Submit Safe Command (ls -la)")
    print("="*50)
    headers = {"X-API-Key": api_key}
    data = {"command_text": "ls -la"}
    response = requests.post(f"{BASE_URL}/commands/", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201


def test_submit_dangerous_command(api_key):
    """Test submitting a dangerous command"""
    print("\n" + "="*50)
    print("TEST: Submit Dangerous Command (rm -rf /)")
    print("="*50)
    headers = {"X-API-Key": api_key}
    data = {"command_text": "rm -rf /"}
    response = requests.post(f"{BASE_URL}/commands/", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201 and response.json()["status"] == "rejected"


def test_get_user_stats(api_key):
    """Test getting user statistics"""
    print("\n" + "="*50)
    print("TEST: Get User Statistics")
    print("="*50)
    headers = {"X-API-Key": api_key}
    response = requests.get(f"{BASE_URL}/users/me/stats", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_create_rule():
    """Test creating a new rule"""
    print("\n" + "="*50)
    print("TEST: Create New Rule (Admin)")
    print("="*50)
    headers = {"X-API-Key": ADMIN_API_KEY}
    data = {
        "pattern": "^sudo\\s+",
        "action": "AUTO_REJECT",
        "description": "Sudo commands require elevation",
        "priority": 0
    }
    response = requests.post(f"{BASE_URL}/rules/", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201


def test_get_audit_logs():
    """Test getting audit logs"""
    print("\n" + "="*50)
    print("TEST: Get Audit Logs (Admin)")
    print("="*50)
    headers = {"X-API-Key": ADMIN_API_KEY}
    response = requests.get(f"{BASE_URL}/audit/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Number of audit logs: {len(response.json())}")
    for log in response.json()[:3]:  # Show first 3 logs
        print(f"  - {log['action']} by {log['username']} at {log['timestamp']}")
    return response.status_code == 200


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*50)
    print("# COMMAND GATEWAY API - TEST SUITE")
    print("#"*50)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Get admin user info
    results.append(("Get Admin Info", test_get_user_info()))
    
    # Test 3: List rules
    results.append(("List Rules", test_list_rules()))
    
    # Test 4: Create member user
    member_api_key = test_create_member_user()
    results.append(("Create Member User", member_api_key is not None))
    
    if member_api_key:
        # Test 5: Submit safe command
        results.append(("Submit Safe Command", test_submit_safe_command(member_api_key)))
        
        # Test 6: Submit dangerous command
        results.append(("Submit Dangerous Command", test_submit_dangerous_command(member_api_key)))
        
        # Test 7: Get user stats
        results.append(("Get User Stats", test_get_user_stats(member_api_key)))
    
    # Test 8: Create rule (admin)
    results.append(("Create Rule (Admin)", test_create_rule()))
    
    # Test 9: Get audit logs
    results.append(("Get Audit Logs (Admin)", test_get_audit_logs()))
    
    # Print summary
    print("\n" + "#"*50)
    print("# TEST SUMMARY")
    print("#"*50)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print("\n⚠️  Some tests failed")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
