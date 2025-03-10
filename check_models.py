import requests

API_URL = "https://openrouter.ai/api/v1/models"
HEADERS = {"Authorization": "Bearer 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"}

try:
    response = requests.get(API_URL, headers=HEADERS, verify=False)  # Disables SSL verification
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
