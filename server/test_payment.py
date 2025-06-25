import requests
import json

# Base URL
base_url = "http://localhost:5000"

# Create a mock session for testing
test_session_id = "test_payment"
session_data = {
    "original_path": "c:\\Users\\Arifeen\\Desktop\\Draw AI\\server\\uploads\\test_input.jpg",
    "sketch_path": "c:\\Users\\Arifeen\\Desktop\\Draw AI\\server\\temp\\sketch_test.jpg", 
    "paid": False
}

# Save the session
with open(f"temp\\{test_session_id}.json", "w") as f:
    json.dump(session_data, f)

# Create checkout session
response = requests.post(
    f"{base_url}/api/create-checkout-session", 
    json={"session_id": test_session_id}
)

if response.status_code == 200:
    data = response.json()
    checkout_url = data.get("url")
    print(f"Payment URL: {base_url}{checkout_url}")
    print("Open this URL in your browser to test the payment form")
else:
    print(f"Error creating checkout: {response.text}")
