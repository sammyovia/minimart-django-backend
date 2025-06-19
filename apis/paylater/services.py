import requests
import json
import random
import time
from datetime import datetime
from django.conf import settings

def call_crc_api(national_id: str, user_data: dict):
    """
    Simulates calling an external CRC (Credit Reference Company) API.
    In a real scenario, replace this with actual API calls to your chosen CRC.
    """
    print(f"Calling CRC API for national ID: {national_id}")

    # --- Actual CRC API Integration (Uncomment and fill in for production) ---
    # CRC_API_ENDPOINT = getattr(settings, 'CRC_API_ENDPOINT', 'https://api.crcsoftware.com/credit_check')
    # CRC_API_KEY = getattr(settings, 'CRC_API_KEY', 'your_actual_crc_api_key')
    # headers = {'Authorization': f'Bearer {CRC_API_KEY}', 'Content-Type': 'application/json'}
    # payload = {
    #     'national_id': national_id,
    #     'dob': user_data.get('date_of_birth').strftime('%Y-%m-%d') if user_data.get('date_of_birth') else None,
    #     'income_level': float(user_data.get('monthly_income', 0)) if user_data.get('monthly_income') else None,
    #     'address': user_data.get('address'),
    #     'phone_number': user_data.get('phone_number'),
    # }
    # try:
    #     response = requests.post(CRC_API_ENDPOINT, headers=headers, json=payload, timeout=30)
    #     response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
    #     crc_result = response.json()

    #     # --- LOGIC TO PARSE REAL CRC RESPONSE (Highly dependent on CRC API) ---
    #     is_approved = crc_result.get('status') == 'approved'
    #     credit_score = crc_result.get('score')
    #     decision_reason = crc_result.get('message', 'Credit check completed.')
    #     approved_limit = crc_result.get('approved_limit') # If CRC returns a limit

    #     return is_approved, credit_score, decision_reason, approved_limit, crc_result
    # except requests.exceptions.RequestException as e:
    #     print(f"CRC API call failed for {national_id}: {e}")
    #     return False, None, f"External credit check failed: {str(e)}", None, None
    # --- End Actual CRC Integration ---


    # --- SIMULATED CRC API RESPONSE (FOR DEVELOPMENT) ---
    time.sleep(random.uniform(2, 5)) # Simulate network latency

    # Increase chance of approval for testing
    simulated_approved = random.choices([True, False], weights=[0.7, 0.3], k=1)[0]
    simulated_score = random.randint(500, 850) if simulated_approved else random.randint(300, 550)
    simulated_reason = "Approved based on good credit history." if simulated_approved else "Rejected due to low credit score or insufficient history."
    simulated_limit = round(random.uniform(50000, 200000), 2) if simulated_approved else None

    simulated_response_data = {
        "status": "success" if simulated_approved else "failed",
        "score": simulated_score,
        "decision_message": simulated_reason,
        "approved_limit": simulated_limit,
        "timestamp": datetime.now().isoformat()
    }

    return simulated_approved, simulated_score, simulated_reason, simulated_limit, simulated_response_data
    # --- End Simulation ---