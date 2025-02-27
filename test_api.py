import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000/api"

def print_response(response):
    """Print response in a formatted way"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)

def test_auth_endpoints():
    print("\n===== Testing Auth Endpoints =====\n")
    
    # Test login with admin user
    print("Login as admin:")
    login_data = {
        "username": "admin_user",
        "password": "adminpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print_response(response)
    admin_token = response.json().get("access_token")
    
    # Test login with manager user
    print("Login as manager:")
    login_data = {
        "username": "manager_user",
        "password": "managerpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print_response(response)
    manager_token = response.json().get("access_token")
    
    # Test login with regular user
    print("Login as regular user:")
    login_data = {
        "username": "regular_user",
        "password": "userpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print_response(response)
    user_token = response.json().get("access_token")
    
    # Test register new user
    print("Register new user:")
    register_data = {
        "email": "newuser@example.com",
        "username": "new_user",
        "password": "newuserpassword",
        "full_name": "New User",
        "role": "user"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response(response)
    new_user_token = response.json().get("access_token")
    
    return {
        "admin": admin_token,
        "manager": manager_token,
        "user": user_token,
        "new_user": new_user_token
    }

def test_user_endpoints(tokens):
    print("\n===== Testing User Endpoints =====\n")
    
    # Set headers for each user
    admin_headers = {"Authorization": f"Bearer {tokens['admin']}"}
    manager_headers = {"Authorization": f"Bearer {tokens['manager']}"}
    user_headers = {"Authorization": f"Bearer {tokens['user']}"}
    
    # Test get all users as admin
    print("Get all users as admin:")
    response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    print_response(response)
    
    # Test get all users as manager
    print("Get all users as manager:")
    response = requests.get(f"{BASE_URL}/users/", headers=manager_headers)
    print_response(response)
    
    # Test get all users as regular user (should fail)
    print("Get all users as regular user (should fail):")
    response = requests.get(f"{BASE_URL}/users/", headers=user_headers)
    print_response(response)
    
    # Test create user as admin
    print("Create user as admin:")
    user_data = {
        "email": "testuser@example.com",
        "username": "test_user",
        "password": "testuserpassword",
        "full_name": "Test User",
        "role": "user"
    }
    response = requests.post(f"{BASE_URL}/users/", headers=admin_headers, json=user_data)
    print_response(response)
    created_user_id = response.json().get("id")
    
    # Test get user by ID as admin
    print(f"Get user by ID as admin:")
    response = requests.get(f"{BASE_URL}/users/{created_user_id}", headers=admin_headers)
    print_response(response)
    
    # Test update user as admin
    print(f"Update user as admin:")
    update_data = {
        "full_name": "Updated Test User"
    }
    response = requests.put(f"{BASE_URL}/users/{created_user_id}", headers=admin_headers, json=update_data)
    print_response(response)
    
    # Test delete user as admin
    print(f"Delete user as admin:")
    response = requests.delete(f"{BASE_URL}/users/{created_user_id}", headers=admin_headers)
    print_response(response)

def test_resource_endpoints(tokens):
    print("\n===== Testing Resource Endpoints =====\n")
    
    # Set headers for each user
    admin_headers = {"Authorization": f"Bearer {tokens['admin']}"}
    manager_headers = {"Authorization": f"Bearer {tokens['manager']}"}
    user_headers = {"Authorization": f"Bearer {tokens['user']}"}
    
    # Test create resource as admin
    print("Create resource as admin:")
    resource_data = {
        "name": "Admin Resource",
        "description": "This is a resource created by admin"
    }
    response = requests.post(f"{BASE_URL}/resources/", headers=admin_headers, json=resource_data)
    print_response(response)
    admin_resource_id = response.json().get("id")
    
    # Test create resource as manager
    print("Create resource as manager:")
    resource_data = {
        "name": "Manager Resource",
        "description": "This is a resource created by manager"
    }
    response = requests.post(f"{BASE_URL}/resources/", headers=manager_headers, json=resource_data)
    print_response(response)
    manager_resource_id = response.json().get("id")
    
    # Test create resource as regular user (should fail)
    print("Create resource as regular user (should fail):")
    resource_data = {
        "name": "User Resource",
        "description": "This is a resource created by user"
    }
    response = requests.post(f"{BASE_URL}/resources/", headers=user_headers, json=resource_data)
    print_response(response)
    
    # Test get all resources as admin
    print("Get all resources as admin:")
    response = requests.get(f"{BASE_URL}/resources/", headers=admin_headers)
    print_response(response)
    
    # Test get all resources as regular user
    print("Get all resources as regular user:")
    response = requests.get(f"{BASE_URL}/resources/", headers=user_headers)
    print_response(response)
    
    # Test update resource as admin
    print(f"Update resource as admin:")
    update_data = {
        "description": "This is an updated resource by admin"
    }
    response = requests.put(f"{BASE_URL}/resources/{admin_resource_id}", headers=admin_headers, json=update_data)
    print_response(response)
    
    # Test update resource as manager
    print(f"Update resource as manager:")
    update_data = {
        "description": "This is an updated resource by manager"
    }
    response = requests.put(f"{BASE_URL}/resources/{manager_resource_id}", headers=manager_headers, json=update_data)
    print_response(response)
    
    # Test delete resource as admin
    print(f"Delete resource as admin:")
    response = requests.delete(f"{BASE_URL}/resources/{admin_resource_id}", headers=admin_headers)
    print_response(response)
    
    # Test delete resource as regular user (should fail)
    print(f"Delete resource as regular user (should fail):")
    response = requests.delete(f"{BASE_URL}/resources/{manager_resource_id}", headers=user_headers)
    print_response(response)

def main():
    print("Starting API tests...")
    tokens = test_auth_endpoints()
    test_user_endpoints(tokens)
    test_resource_endpoints(tokens)
    print("\nAPI tests completed!")

if __name__ == "__main__":
    main()