import requests
import csv
import os
from datetime import datetime, timedelta, timezone

# --- 1. YOUR WORKING CONFIGURATION ---
S1_URL = "https://your-console.sentinelone.net"
S1_TOKEN = "PASTE_TOKEN_HERE"
S1_SITE_ID = "YOUR_SITE_ID"

# --- 2. TIME CALCULATION ---
days_limit = 30
cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_limit)).strftime('%Y-%m-%dT%H:%M:%SZ')

headers = {
    "Authorization": f"ApiToken {S1_TOKEN}",
    "Content-Type": "application/json"
}

def find_stale_agents():
    print(f"Searching for agents in Site {S1_SITE_ID}...")
    
    # We are putting the Site ID directly into the URL this time
    endpoint = f"{S1_URL}/web/api/v2.1/agents?siteIds={S1_SITE_ID}&updatedAt__lt={cutoff_date}&isActive=True"

    response = requests.get(endpoint, headers=headers)
    
    # Check if the response is actually successful (Status 200)
    if response.status_code == 200:
        try:
            # Try to read the data
            data = response.json().get('data', [])
            return data
        except requests.exceptions.JSONDecodeError:
            # If the response is empty but successful, it usually means 0 results found
            print("Successfully connected, but no agent data was returned (Empty Response).")
            return []
    else:
        print(f"Error connecting: {response.status_code}")
        print(f"Server Message: {response.text}")
        return []

def save_to_csv(agents_list):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = os.path.join(desktop_path, "stale_agents_report.csv")
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Computer Name", "Agent ID", "Last Seen Date"])
        for agent in agents_list:
            writer.writerow([agent.get('computerName'), agent.get('id'), agent.get('updatedAt')])
            
    print(f"\n[+] SUCCESS: Report saved to Desktop: {filename}")

def decommission_agents(agent_ids):
    # --- SAFETY SWITCH ---
    # Set this to True ONLY when you are ready to delete agents
    ACTUALLY_DECOMMISSION = False 
    
    if not ACTUALLY_DECOMMISSION:
        print(f"\n[SAFETY MODE] I would have decommissioned {len(agent_ids)} agents, but the switch is OFF.")
        return

    endpoint = f"{S1_URL}/web/api/v2.1/agents/actions/decommission"
    payload = {"filter": {"siteIds": [S1_SITE_ID], "ids": agent_ids}}
    
    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Successfully decommissioned {len(agent_ids)} agents.")
    else:
        print(f"Failed to decommission: {response.text}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    stale_agents = find_stale_agents()
    
    if not stale_agents:
        print("No stale agents found. Your site is clean!")
    else:
        print(f"\nFound {len(stale_agents)} stale agents.")
        save_to_csv(stale_agents)
        
        agent_ids_to_remove = [a.get('id') for a in stale_agents]
        decommission_agents(agent_ids_to_remove)
