import time
import json
import requests
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import traceback

# Initialize colorama for colored output
init(autoreset=True)

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop PAWS")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")

def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def api_request(url, method='GET', headers=None, data=None):
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(Fore.RED + f"Error on {method} request to {url}: {e}")
        traceback.print_exc()
        return None

def authenticate_user(account_data):
    url = "https://api.paws.community/v1/user/auth"
    payload = {"data": account_data}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        # add other necessary headers here
    }
    return api_request(url, method="POST", headers=headers, data=payload)

def get_user_data(auth_token):
    url = "https://api.paws.community/v1/user"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
        # add other necessary headers here
    }
    return api_request(url, method="GET", headers=headers)

def get_quests(auth_token):
    url = "https://api.paws.community/v1/quests/list"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
        # add other necessary headers here
    }
    return api_request(url, method="GET", headers=headers)

def complete_quest(auth_token, quest_id):
    url = "https://api.paws.community/v1/quests/completed"
    payload = {"questId": quest_id}
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        # add other necessary headers here
    }
    return api_request(url, method="POST", headers=headers, data=payload)

def claim_quest(auth_token, quest_id):
    url = "https://api.paws.community/v1/quests/claim"
    payload = {"questId": quest_id}
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # Add any additional headers if needed
    }
    return api_request(url, method="POST", headers=headers, data=payload)

def process_accounts():
    accounts = load_accounts()
    total_accounts = len(accounts)
    print(Fore.YELLOW + f"Jumlah akun: {total_accounts}")
    
    for idx, account in enumerate(accounts, start=1):
        print(Fore.YELLOW + f"\nMemproses akun ke-{idx} dari {total_accounts}")
        response = authenticate_user(account)
        
        if response and response.get("success"):
            auth_token = response["data"][0]
            user_data = get_user_data(auth_token)
            quests = get_quests(auth_token)

            if user_data and quests:
                # Extracting essential user data
                user_info = user_data["data"]
                print(Fore.GREEN + "Data Pengguna:")
                print(Fore.CYAN + f"  Nama Pengguna  : {user_info['userData']['username']}")
                print(Fore.CYAN + f"  Balance        : {user_info['gameData']['balance']}")
                print(Fore.CYAN + f"  Balance Hari Ini: {user_info['gameData']['todayBalance']}")
                print(Fore.CYAN + f"  Premium Status : {'Yes' if user_info['allocationData']['telegram']['premium'] else 'No'}")
                print(Fore.CYAN + f"  Alokasi Total  : {user_info['allocationData']['total']}")

                for quest in quests["data"]:
                    quest_id = quest["_id"]
                    title = quest["title"]
                    description = quest["description"]
                    claimed = quest["progress"]["claimed"]

                    print(Fore.CYAN + f"\nQuest: {title} - {description}")
                    
                    # Check if the quest is unclaimed and can be completed
                    if not claimed:
                        # Attempt to complete the quest first
                        complete_result = complete_quest(auth_token, quest_id)
                        if complete_result and complete_result.get("success"):
                            print(Fore.GREEN + "Quest berhasil diselesaikan.")
                            
                            # After completion, attempt to claim the quest
                            claim_result = claim_quest(auth_token, quest_id)
                            if claim_result and claim_result.get("success"):
                                print(Fore.GREEN + "Quest berhasil diklaim.")
                            else:
                                print(Fore.RED + "Gagal mengklaim quest.")
                        else:
                            print(Fore.RED + "Gagal menyelesaikan quest.")
                    else:
                        print(Fore.YELLOW + "Quest sudah diklaim sebelumnya.")
        else:
            print(Fore.RED + "Gagal mengautentikasi akun.")

        # Delay of 5 seconds before the next account
        time.sleep(5)
        
    # Start a countdown for 1 day
    start_countdown(24 * 60 * 60)

def start_countdown(seconds):
    end_time = datetime.now() + timedelta(seconds=seconds)
    print(Fore.YELLOW + "Hitung mundur dimulai (24 jam)...")
    while datetime.now() < end_time:
        remaining_time = end_time - datetime.now()
        print(Fore.YELLOW + f"Sisa waktu: {remaining_time}", end="\r")
        time.sleep(1)
    
    print(Fore.GREEN + "Hitung mundur selesai. Memulai ulang proses.")
    process_accounts()  # Restart the process

if __name__ == "__main__":
    print_welcome_message()
    process_accounts()
