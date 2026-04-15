import requests
import sys
import json # Added to handle saving to a file

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Make sure base_url has NO trailing slash!
api_token= "apitoke"
base_url = "https://<Enter MSSP ID HERE>.sentinelone.net/"
site_id = "123456789"

def get_site_applications():
    # UPDATE: Changed to the correct site-wide application endpoint
    endpoint = f"{base_url}/web/api/v2.1/installed-applications"
    
    headers = {
        "Authorization": f"ApiToken {api_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "siteIds": site_id,
        "limit": 1000 
    }
    
    all_applications = []
    page_count = 1

    print(f"[*] Starting application inventory pull for Site ID: {site_id}")

    # ==========================================
    # 2. PAGINATION & DATA FETCHING
    # ==========================================
    while True:
        print(f"[*] Fetching page {page_count}...")
        
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status() 
            data = response.json()
            
        except requests.exceptions.HTTPError as errh:
            print(f"\n[!] HTTP Error Encountered: {errh}")
            print(f"[!] Server Response: {response.text}")
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            print(f"\n[!] Network Error: {err}")
            sys.exit(1)

        # Extract the array of applications
        items = data.get('data', [])
        all_applications.extend(items)
        
        # Handle Pagination
        next_cursor = data.get('pagination', {}).get('nextCursor')
        if next_cursor:
            params['cursor'] = next_cursor
            page_count += 1
        else:
            break

    return all_applications

# ==========================================
# 3. EXECUTION & SAVE TO JSON
# ==========================================
if __name__ == "__main__":
    inventory = get_site_applications()
    
    if inventory:
        output_filename = "site_inventory.json"
        
        # Write the list of dictionaries to a JSON file
        with open(output_filename, "w") as json_file:
            json.dump(inventory, json_file, indent=4)
            
        print(f"\n[+] Scan complete. Retrieved {len(inventory)} application records.")
        print(f"[+] Data successfully saved to '{output_filename}' in your current directory.")
