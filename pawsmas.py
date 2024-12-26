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
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop PAWSMAS")
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
    }
    return api_request(url, method="POST", headers=headers, data=payload)

def get_user_data(auth_token):
    url = "https://api.paws.community/v1/user"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }
    return api_request(url, method="GET", headers=headers)

def get_quests(auth_token):
    url = "https://api.paws.community/v1/quests/list?type=christmas"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }
    return api_request(url, method="GET", headers=headers)

def complete_quest(auth_token, quest_id):
    url = "https://api.paws.community/v1/quests/completed"
    payload = {"questId": quest_id}
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }
    return api_request(url, method="POST", headers=headers, data=payload)

def claim_quest(auth_token, quest_id):
    url = "https://api.paws.community/v1/quests/claim"
    payload = {"questId": quest_id}
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
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

            if user_data:
                user_info = user_data["data"]
                print(Fore.GREEN + "Data Pengguna:")
                print(Fore.CYAN + f"  Nama Pengguna  : {user_info['userData']['username']}")
                print(Fore.CYAN + f"  Jumlah Referral: {user_info['referralData']['referralsCount']}")
                print(Fore.CYAN + f"  Balance        : {user_info['gameData']['balance']}")
                print(Fore.CYAN + f"  Balance Hari Ini: {user_info['gameData']['todayBalance']}")
                print(Fore.CYAN + f"  Premium Status : {'Yes' if user_info['allocationData']['telegram']['premium'] else 'No'}")
                print(Fore.CYAN + f"  Alokasi Total  : {user_info['allocationData']['total']}")

                while True:
                    quests = get_quests(auth_token)
                    if not quests:
                        break

                    for quest in quests["data"]:
                        quest_id = quest["_id"]
                        title = quest["title"]
                        claimed = quest["progress"]["claimed"]

                        print(Fore.CYAN + f"\nQuest: {title}")

                        # Fokus hanya pada `claimed == False`
                        if not claimed:
                            complete_result = complete_quest(auth_token, quest_id)
                            if complete_result and complete_result.get("success"):
                                print(Fore.GREEN + "Quest berhasil diselesaikan.")
                                claim_result = claim_quest(auth_token, quest_id)
                                if claim_result and claim_result.get("success"):
                                    print(Fore.GREEN + "Quest berhasil diklaim.")
                                    # Refresh the quest list to check for new available quests
                                    break
                                else:
                                    print(Fore.RED + "Gagal mengklaim quest.")
                            else:
                                print(Fore.RED + "Gagal menyelesaikan quest.")
                        else:
                            print(Fore.YELLOW + "Quest sudah diklaim.")
                    else:
                        # Break the while loop if no quests were processed
                        break
        else:
            print(Fore.RED + "Gagal mengautentikasi akun.")

        time.sleep(150)  # Kurangi delay menjadi 150 detik

if __name__ == "__main__":
    print_welcome_message()
    process_accounts()
