import requests
import json
import time
import subprocess
import random
BASE_URL = "http://127.0.0.1:8000"
random_id = str(random.randint(10000000, 99999999))
EMAIL = f"testrunner_{random_id}@craft.com"
PHONE = f"012{random_id}"
PASSWORD = "TestPass123!"

def print_header(title):
    print(f"\n{'='*50}\n- {title}\n{'='*50}")

def run_test(name, method, url, headers=None, data=None, expected_status=None):
    print(f"[{method}] {url} ... ", end="")
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=5)
        
        success = True
        if expected_status and response.status_code not in expected_status:
            success = False
            
        if success:
            print(f"[OK] {response.status_code}")
        else:
            print(f"[FAIL] {response.status_code} (Expected {expected_status})")
            print(f"   Response: {response.text[:200]}")
            
        return response
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def force_verify_user():
    print("Forcing user verification via DB...")
    # Exec into the auth_service container and set is_active=True and is_verified=True (if applicable)
    cmd = f'docker exec microservicescraft-auth_service-1 python -c "import os, django; os.environ.setdefault(\'DJANGO_SETTINGS_MODULE\', \'auth_service.settings\'); django.setup(); from accounts.models import User; User.objects.filter(email=\'{EMAIL}\').update(is_active=True, is_verified=True)"'
    subprocess.run(cmd, shell=True, capture_output=True)

def main():
    print_header("Phase 7: Health Checks (Direct Ports)")
    run_test("Auth Health", "GET", "http://127.0.0.1:8001/health/", expected_status=[200])
    run_test("Order Health", "GET", "http://127.0.0.1:8003/health/", expected_status=[200])
    run_test("Catalog Health", "GET", "http://127.0.0.1:8002/health/", expected_status=[200])
    run_test("ML Health", "GET", "http://127.0.0.1:8006/health", expected_status=[200])

    print_header("Phase 1: Authentication Service")
    reg_data = {
        "email": EMAIL,
        "first_name": "Test",
        "last_name": "Runner",
        "password": PASSWORD,
        "password2": PASSWORD,
        "PhoneNO": PHONE
    }
    res = run_test("Register Customer", "POST", f"{BASE_URL}/accounts/register_customer/", data=reg_data, expected_status=[201])
    
    force_verify_user()

    login_data = {"email": EMAIL, "password": PASSWORD}
    login_res = run_test("Login", "POST", f"{BASE_URL}/accounts/login/", data=login_data, expected_status=[200])
    
    if not login_res or login_res.status_code != 200:
        print("[ERROR] Stopping tests: Could not login.")
        return

    tokens = login_res.json()
    access_token = tokens.get("access")
    refresh_token = tokens.get("refresh")
    headers = {"Authorization": f"Bearer {access_token}"}

    run_test("Token Refresh", "POST", f"{BASE_URL}/accounts/token-refresh/", data={"refresh": refresh_token}, expected_status=[200])
    run_test("Customer Profile", "GET", f"{BASE_URL}/accounts/customer/profile/", headers=headers, expected_status=[200])

    print_header("Phase 2: Order Service")
    run_test("List Carts", "GET", f"{BASE_URL}/orders/carts/", headers=headers, expected_status=[200])
    
    cart_res = run_test("Get or Create My Cart", "GET", f"{BASE_URL}/orders/carts/my_cart/", headers=headers, expected_status=[200])
    
    add_item_data = {
        "product_id": 1,
        "Quantity": 2,
        "Color": "Red",
        "Size": "M"
    }
    run_test("Add Item to Cart", "POST", f"{BASE_URL}/orders/carts/add_item/", headers=headers, data=add_item_data, expected_status=[201, 400])
    
    order_data = {
        "payment_method": "Cash on Delivery",
        "shipping_address": {
            "street": "123 Main St",
            "city": "Cairo",
            "country": "Egypt",
            "postal_code": "11511"
        }
    }
    run_test("Create Order", "POST", f"{BASE_URL}/orders/orders/", headers=headers, data=order_data, expected_status=[201, 400])
    run_test("List My Orders", "GET", f"{BASE_URL}/orders/orders/", headers=headers, expected_status=[200])

    run_test("Clear Cart", "POST", f"{BASE_URL}/orders/carts/clear/", headers=headers, expected_status=[200])
    
    run_test("Create Wishlist", "POST", f"{BASE_URL}/orders/whishlists/", headers=headers, data={}, expected_status=[201])
    run_test("List Wishlist", "GET", f"{BASE_URL}/orders/whishlists/", headers=headers, expected_status=[200])

    print_header("Phase 3: Catalog Service")
    run_test("List Products", "GET", f"{BASE_URL}/product/products/", headers=headers, expected_status=[200])
    run_test("List Categories", "GET", f"{BASE_URL}/product/categories/", headers=headers, expected_status=[200])
    run_test("List Simple Courses", "GET", f"{BASE_URL}/course/simple-courses/", headers=headers, expected_status=[200])
    run_test("List Enrolled Courses", "GET", f"{BASE_URL}/course/enrolled-courses/", headers=headers, expected_status=[200])

    print_header("Phase 4: Platform Service (Reviews)")
    run_test("List Reviews", "GET", f"{BASE_URL}/review/reviews/", headers=headers, expected_status=[200])
    run_test("My Reviews", "GET", f"{BASE_URL}/review/reviews/my_reviews/", headers=headers, expected_status=[200])

    print_header("Phase 5: Payment Service")
    run_test("Payment History", "GET", f"{BASE_URL}/payment/history/", headers=headers, expected_status=[200])

if __name__ == "__main__":
    main()
