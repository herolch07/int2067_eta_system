#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hong Kong Public Transport ETA CLI

Features:
1.  Full English UI for perfect table alignment.
2.  "To [Destination]" format for directions.
3.  Auto-refreshing ETA loop with current time.
4.  Loading spinners for all network actions.
5.  Robust error handling and clean code structure.
"""

# ==========================================
# 0. Environment Auto-Setup
# ==========================================
def ensure_dependencies():
    """Check and install required libraries if not present."""
    required = {
        "requests": "requests",
        "tabulate": "tabulate"
    }

    import importlib
    import subprocess

    missing_libs = []
    for lib_name, pip_name in required.items():
        try:
            importlib.import_module(lib_name)
        except ImportError:
            missing_libs.append(pip_name)

    if not missing_libs:
        return True

    print("\nMissing required libraries:")
    for lib in missing_libs:
        print(f"  - {lib}")

    print("\nOptions:")
    print("  1. Auto-install missing libraries now")
    print("  2. Exit and install manually (pip install -r requirements.txt)")

    while True:
        choice = input("\nSelect (1/2): ").strip()
        if choice == "2":
            print("\nPlease run: pip install -r requirements.txt")
            return False
        elif choice == "1":
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    print()
    for pip_name in missing_libs:
        print(f"--- Installing {pip_name}... ---")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"--- {pip_name} installed successfully! ---")
        except Exception as e:
            print(f"--- Failed to install {pip_name}: {e} ---")
            print("\nPlease install manually: pip install -r requirements.txt")
            return False

    return True

# ==========================================
# 1. Imports
# ==========================================
import logging          # Log errors
import time             # Delays
import re               # Regex for sorting
import sys              # System exit
import threading        # Background animation
import itertools        # Animation cycle
import math             # Math for ceiling calculation
import json             # JSON handling for MTR data
from pathlib import Path# For robust path handling
from datetime import datetime, timezone, timedelta, tzinfo # Time handling
from typing import Any, Dict, List, Optional, Tuple        # Type hinting



# Set logging to only show critical errors
logging.basicConfig(level=logging.ERROR)


# ==========================================
# 2. Timezone Setup
# ==========================================
try:
    from zoneinfo import ZoneInfo
    HKT = ZoneInfo("Asia/Hong_Kong")
except (ImportError, Exception):
    # Fallback for systems without zoneinfo
    class HKTimeZone(tzinfo):
        def utcoffset(self, dt): return timedelta(hours=8)
        def dst(self, dt): return timedelta(0)
        def tzname(self, dt): return "HKT"
    HKT = HKTimeZone()


# ==========================================
# 3. Global Data and Path Setup
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
MTR_DATA_PATH = BASE_DIR / "mtr_data.json"

MTR_LINES = {}
MTR_STATIONS = {}
try:
    with open(MTR_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        MTR_LINES = data.get("MTR_LINES", {})
        MTR_STATIONS = data.get("MTR_STATIONS", {})
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading MTR data from {MTR_DATA_PATH}: {e}", file=sys.stderr)


# ==========================================
# 4. Loading Animation
# ==========================================
class LoadingSpinner:
    """
    Context manager to show a rotating spinner ( | / - \\ ) 
    while a blocking network task is running.
    """
    def __init__(self, message="Loading..."):
        self.message = message
        self.stop_running = False
        self.thread = threading.Thread(target=self._animate)

    def __enter__(self):
        self.stop_running = False
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_running = True
        self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def _animate(self):
        for char in itertools.cycle(['|', '/', '-', '\\']):
            if self.stop_running: break
            sys.stdout.write(f'\r{self.message} {char}')
            sys.stdout.flush()
            time.sleep(0.1)


# ==========================================
# 5. Base Network Client
# ==========================================
class BaseClient:
    """
    Handles all HTTP requests with retry logic and session reuse.
    """
    def __init__(self, base_url: str = "", timeout: int = 10, max_retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _full_url(self, path: str) -> str:
        if not path.startswith("http"):
            return f"{self.base_url}/{path.lstrip('/')}"
        return path

    def get_json(self, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
        url = self._full_url(path)
        attempt = 0
        while attempt <= self.max_retries:
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout, 
                    headers={"User-Agent": "HKTransportCLI/1.0"}
                )
                if not response.ok:
                    # Retry on server errors (5xx)
                    if 500 <= response.status_code < 600 and attempt < self.max_retries:
                        attempt += 1; time.sleep(1); continue
                    return None
                return response.json()
            except (requests.Timeout, requests.ConnectionError):
                if attempt < self.max_retries: attempt += 1; time.sleep(1); continue
                return None
            except Exception: return None
        return None


# ==========================================
# 6. Helper Functions
# ==========================================

def parse_iso(timestamp_str: str) -> Optional[datetime]:
    """ Parses ISO timestamp string to datetime object. """
    if not timestamp_str: return None
    try:
        if timestamp_str.endswith("Z"): timestamp_str = timestamp_str[:-1] + "+00:00"
        return datetime.fromisoformat(timestamp_str)
    except: return None

def minutes_until(target_time: datetime) -> int:
    """ 
    Calculates minutes remaining.
    Uses math.ceil (Rounding Up) for a safety buffer.
    e.g., 4m01s -> 5 min.
    """ 
    if not target_time: return 0
    now = datetime.now(timezone.utc)
    diff_seconds = (target_time - now).total_seconds()
    
    if diff_seconds <= 0: return 0
    return math.ceil(diff_seconds / 60)

def natural_sort_key(s: str) -> Tuple[int, str]:
    """ Sorts 'Route 10' after 'Route 2'. """
    match = re.match(r"(\d+)?(.*)", str(s))
    if match: return (int(match.group(1)) if match.group(1) else 0, match.group(2))
    return (0, str(s))


# ==========================================
# 7. UI Helpers 
# ==========================================

class GoBack(Exception): pass
class QuitProgram(Exception): pass

NAV_HINT = " (Type 'b' to back, 'q' to quit)"

def ask_input(prompt: str) -> str:
    """ Standardized input with blank line for readability. """
    print() 
    while True:
        try:
            user_input = input(f"{prompt}{NAV_HINT}: ").strip()
            if user_input.lower() == 'b': raise GoBack()
            if user_input.lower() == 'q': raise QuitProgram()
            if user_input: return user_input
            print("Input cannot be empty.")
        except (KeyboardInterrupt, EOFError): raise QuitProgram()

def ask_index(max_index: int, prompt: str = "Select Index") -> int:
    """ Standardized number selection. """
    while True:
        index_input = ask_input(prompt)
        try:
            idx = int(index_input)
            if 1 <= idx <= max_index: return idx
            print(f"Please enter a number between 1 and {max_index}.")
        except ValueError: print("Invalid number.")

def wait_for_enter() -> None:
    """ Pauses execution for refresh or navigation. """
    print()
    # No while True needed here, as exceptions will bubble up.
    command = input("Press ENTER to refresh, 'b' to back, 'q' to quit: ").strip().lower()
    if command == "": return
    if command == "b": raise GoBack()
    if command == "q": raise QuitProgram()
    # If any other key is pressed, just re-ask by doing nothing and letting the loop continue.
    # The parent loop in display_eta_loop will call wait_for_enter again.


# ==========================================
# 8. API Clients 
# ==========================================

class KMBClient(BaseClient):
    def __init__(self):
        super().__init__("https://data.etabus.gov.hk/v1/transport/kmb")
        self.stop_cache = {}
    
    def list_routes(self):
        data = self.get_json("route")
        return data.get("data", []) if data else []
    
    def list_stops(self, route, bound, service_type="1"):
        bound_map = {"O": "outbound", "I": "inbound"}
        bound_str = bound_map.get(bound.upper(), bound)
        data = self.get_json(f"route-stop/{route}/{bound_str}/{service_type}")
        return sorted(data.get("data", []) if data else [], key=lambda x: int(x.get("seq", 0)))
    
    def get_stop_name(self, stop_id):
        if stop_id in self.stop_cache:
            return self.stop_cache[stop_id]
        
        data = self.get_json(f"stop/{stop_id}")
        stop_data = data.get("data", {}) if data else {}
        if stop_data:
            self.stop_cache[stop_id] = stop_data
        return stop_data
    
    def get_eta(self, stop_id, route, service_type="1"):
        data = self.get_json(f"eta/{stop_id}/{route}/{service_type}")
        return data.get("data", []) if data else []

class CitybusClient(BaseClient):
    def __init__(self):
        super().__init__("https://rt.data.gov.hk/v2/transport/citybus")
        self.stop_cache = {}
    
    def get_route(self, route_no): 
        data = self.get_json(f"route/CTB/{route_no}")
        if not data: return None
        result = data.get("data")
        if isinstance(result, list) and result: return result[0]
        if isinstance(result, dict): return result
        return None
    
    def get_stops(self, route_no, direction):
        data = self.get_json(f"route-stop/CTB/{route_no}/{direction}")
        return sorted(data.get("data", []) if data else [], key=lambda x: int(x.get("seq", 999)))
    
    def get_stop_detail(self, stop_id):
        if stop_id in self.stop_cache:
            return self.stop_cache[stop_id]
            
        data = self.get_json(f"stop/{stop_id}")
        stop_data = data.get("data", {}) if data else {}
        if stop_data:
            self.stop_cache[stop_id] = stop_data
        return stop_data
    
    def get_eta(self, stop_id, route_no):
        data = self.get_json(f"eta/CTB/{stop_id}/{route_no}")
        return data.get("data", []) if data else []

class GMBClient(BaseClient):
    def __init__(self): super().__init__("https://data.etagmb.gov.hk")
    
    def get_routes(self, region):
        data = self.get_json(f"route/{region}")
        routes = (data.get("data") or {}).get("routes") or []
        return sorted(routes, key=natural_sort_key)
    
    def get_details(self, region, route_code):
        data = self.get_json(f"route/{region}/{route_code}")
        return data.get("data", []) if data else []
    
    def get_stops(self, route_id, route_seq):
        data = self.get_json(f"route-stop/{route_id}/{route_seq}")
        stops = (data.get("data") or {}).get("route_stops") or []
        return sorted(stops, key=lambda x: int(x.get("stop_seq", 999)))
    
    def get_eta(self, route_id, route_seq, stop_seq):
        data = self.get_json(f"eta/route-stop/{route_id}/{route_seq}/{stop_seq}")
        return data.get("data", {}) if data else {}

class MTRClient(BaseClient):
    def __init__(self): super().__init__("https://rt.data.gov.hk")
    
    def get_schedule(self, line, station):
        data = self.get_json("v1/transport/mtr/getSchedule.php", params={"line": line, "sta": station, "lang": "EN"})
        if not data or data.get("status") != 1: return {}
        schedule_data = data.get("data", {})
        key = next(iter(schedule_data.keys()), None)
        return schedule_data.get(key, {}) if key else {}


# ==========================================
# 9. Display Loop and Handlers 
# ==========================================

def display_eta_loop(header: str, eta_fetcher, data_processor, table_headers: List[str]):
    """
    Generic loop to display real-time ETA data in a table.
    """
    while True:
        with LoadingSpinner("Refreshing..."):
            raw_data = eta_fetcher()
        
        time_now = datetime.now(HKT).strftime('%H:%M:%S')
        print(f"\n{header} ({time_now})")
        
        table_data, message = data_processor(raw_data)
        
        if table_data:
            print(tabulate(table_data, headers=table_headers, tablefmt="simple"))
        else:
            print(f"  {message or 'No data available.'}")
            
        wait_for_enter() # Can raise GoBack or QuitProgram

def handle_kmb():
    """ KMB Logic """
    print("\n=== KMB (Kowloon Motor Bus) ===")
    client = KMBClient()
    
    with LoadingSpinner("Downloading KMB Route Data..."):
        routes = client.list_routes()
    if not routes: 
        print("Failed to download KMB routes.")
        return

    route_input = ask_input("Enter Route No. (e.g. 74K)").upper()
    candidates = [r for r in routes if r.get("route","").upper() == route_input]
    if not candidates: 
        print("Route not found.")
        return

    print(f"\nSelect Direction for Route {route_input}:")
    for i, r in enumerate(candidates, 1):
        print(f"{i}. To {r.get('dest_en')} (from {r.get('orig_en')}) [Type {r.get('service_type')}]")
    
    selected_route = candidates[ask_index(len(candidates)) - 1]
    
    with LoadingSpinner("Fetching stops..."):
        stops = client.list_stops(selected_route['route'], selected_route['bound'], selected_route.get('service_type','1'))
    
    stop_map = {}
    print("\nStops List:")
    for s in stops:
        seq = int(s.get("seq"))
        sid = s.get("stop")
        meta = client.get_stop_name(sid)
        name_en = meta.get("name_en", sid)
        name_tc = meta.get("name_tc", "")
        display_name = f"{name_en} ({name_tc})" if name_tc else name_en
        print(f"{seq:>2}. {display_name}")
        stop_map[seq] = {"id": sid, "name": display_name}

    target_seq = int(ask_input("Enter Stop Sequence Number"))
    if target_seq not in stop_map:
        print("Invalid sequence.")
        return

    stop_info = stop_map[target_seq]
    header = f"======== [{route_input}] @ {stop_info['name']} ========"

    def process_kmb_eta(etas):
        filtered = [e for e in etas if (e.get("dir") or "").upper() == selected_route['bound'].upper() and str(e.get("seq")) == str(target_seq)]
        filtered.sort(key=lambda x: (int(x.get("eta_seq", 99)), x.get("eta")))
        
        table_data = []
        for e in filtered:
            eta_time = parse_iso(e.get("eta"))
            table_data.append([
                e.get("route",""), 
                e.get("dest_en"), 
                eta_time.astimezone(HKT).strftime("%H:%M:%S") if eta_time else "-", 
                minutes_until(eta_time) if eta_time else "-", 
                e.get("rmk_en") or ""
            ])
        return table_data, "No ETA info available for this stop."

    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_eta(stop_info['id'], selected_route['route'], selected_route.get('service_type','1')),
        data_processor=process_kmb_eta,
        table_headers=["Route", "Destination", "Time", "Min", "Remark"]
    )


def handle_citybus():
    """ Citybus Logic """
    print("\n=== Citybus ===")
    client = CitybusClient()
    
    route_input = ask_input("Enter Route No. (e.g. 102)").upper()
    
    with LoadingSpinner("Finding route..."):
        route_info = client.get_route(route_input)
    if not route_info: 
        print("Route not found.")
        return
    
    orig = route_info.get('orig_en')
    dest = route_info.get('dest_en')
    
    print(f"\nRoute: {route_info.get('route')}")
    print(f"1. To {dest} (from {orig})")
    print(f"2. To {orig} (from {dest})")
    
    direction = "inbound" if ask_index(2) == 2 else "outbound"

    with LoadingSpinner("Fetching stops..."):
        stops = client.get_stops(route_input, direction)
        
    stop_list = []
    print("\nStops:")
    for s in stops:
        meta = client.get_stop_detail(s.get("stop"))
        name = f"{meta.get('name_en')} ({meta.get('name_tc')})"
        seq = int(s.get("seq"))
        print(f"{seq:>2}. {name}")
        stop_list.append({"seq": seq, "id": s.get("stop"), "name": name})
    
    target_seq = int(ask_input("Enter Stop Sequence Number"))
    selected_stop = next((x for x in stop_list if x["seq"] == target_seq), None)
    if not selected_stop: 
        print("Invalid stop.")
        return

    header = f"======== [{route_input}] @ {selected_stop['name']} ========"
    target_dir = "I" if direction == "inbound" else "O"

    def process_citybus_eta(etas):
        filtered = [e for e in etas if (e.get("dir") or "").upper() == target_dir]
        table_data = []
        for e in filtered:
            eta_time = parse_iso(e.get("eta"))
            table_data.append([
                e.get("route",""), 
                e.get("dest_en"), 
                eta_time.astimezone(HKT).strftime("%H:%M:%S") if eta_time else "-", 
                minutes_until(eta_time) if eta_time else "-", 
                e.get("rmk_en") or ""
            ])
        return table_data, "No ETA info available."

    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_eta(selected_stop['id'], route_input),
        data_processor=process_citybus_eta,
        table_headers=["Route", "Destination", "Time", "Min", "Remark"]
    )


def handle_gmb():
    """ GMB Logic """
    print("\n=== Green Minibus ===")
    client = GMBClient()
    
    print("1. Hong Kong Island (HKI)")
    print("2. Kowloon (KLN)")
    print("3. New Territories (NT)")
    region = ["HKI", "KLN", "NT"][ask_index(3) - 1]
    
    with LoadingSpinner(f"Downloading {region} routes..."):
        routes = client.get_routes(region)
    if not routes: 
        print("No routes found for this region.")
        return
    
    route_input = ask_input(f"Enter Route No. (e.g. {routes[0]})").upper()
    
    with LoadingSpinner("Fetching details..."):
        details = client.get_details(region, route_input)
    if not details: 
        print("Details not found.")
        return
    
    print("\nSelect Route Variant:")
    for i, d in enumerate(details, 1):
        print(f"{i}. {d.get('description_en')}")
    selected_variant = details[ask_index(len(details)) - 1]
    
    directions = selected_variant.get("directions", [])
    print("\nSelect Direction:")
    for i, d in enumerate(directions, 1):
        print(f"{i}. To {d.get('dest_en')} (from {d.get('orig_en')})")
    selected_dir = directions[ask_index(len(directions)) - 1]
    
    with LoadingSpinner("Fetching stops..."):
        stops = client.get_stops(selected_variant.get("route_id"), selected_dir.get("route_seq"))
        
    print("\nStops:")
    for s in stops: print(f"{s.get('stop_seq'):>2}. {s.get('name_en')} ({s.get('name_tc')})")
    
    target_seq = int(ask_input("Enter Stop Sequence"))
    stop_match = next((s for s in stops if int(s.get('stop_seq')) == target_seq), None)
    if not stop_match:
        print("Invalid sequence.")
        return
    stop_name_display = f"{stop_match.get('name_en')} ({stop_match.get('name_tc')})"

    header = f"======== [{route_input}] @ {stop_name_display} ========"
    
    def process_gmb_eta(data):
        eta_list = data.get("eta", []) if data else []
        table_data = [[
            route_input,
            selected_dir.get('dest_en'),
            (parse_iso(e.get("timestamp")) or datetime.now()).astimezone(HKT).strftime("%H:%M:%S"),
            e.get("diff", "-"),
            e.get("remarks_en")
        ] for e in eta_list]
        return table_data, "No ETA info available."

    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_eta(selected_variant.get("route_id"), selected_dir.get("route_seq"), target_seq),
        data_processor=process_gmb_eta,
        table_headers=["Route", "Destination", "Time", "Min", "Remark"]
    )


def handle_mtr():
    """ MTR Logic """
    print("\n=== MTR Next Train ===")
    if not MTR_LINES or not MTR_STATIONS:
        print("MTR data is not available. Please check 'mtr_data.json'.")
        return

    client = MTRClient()
    lines = sorted(MTR_LINES.keys())
    for i, l in enumerate(lines, 1): print(f"{i}. {l}")
    
    selected_line_key = lines[ask_index(len(lines)) - 1]
    line_info = MTR_LINES[selected_line_key]
    
    stations = line_info["stations"]
    for i, s in enumerate(stations, 1):
        print(f"{i}. {MTR_STATIONS.get(s, s)} ({s})")
    
    selected_station_code = stations[ask_index(len(stations)) - 1]
    station_name = MTR_STATIONS.get(selected_station_code, selected_station_code)
    
    header = f"======== {selected_line_key} @ {station_name} ========"
    
    def process_mtr_data(schedule):
        if not schedule:
            return [], "No trains available."
        
        all_trains = []
        for direction, trains in schedule.items():
            if not isinstance(trains, list) or not trains: continue
            
            # Use a subheader row that can be handled by tabulate
            all_trains.append([f"--- To: {trains[0].get('dest')} ---", "", "", ""])
            for t in trains:
                all_trains.append([
                    t.get("time"),
                    MTR_STATIONS.get(t.get("dest"), t.get("dest")),
                    t.get("plat"),
                    t.get("ttnt")
                ])
        return all_trains, "No schedule data."

    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_schedule(line_info["code"], selected_station_code),
        data_processor=process_mtr_data,
        table_headers=["Time", "Dest", "Plat", "Min"]
    )


# ==========================================
# 10. Main Loop
# ==========================================

def main():
    # Check and optionally install dependencies
    if not ensure_dependencies():
        sys.exit(1)

    # Import libraries after ensuring they are installed
    import requests
    from tabulate import tabulate

    handlers = {"1": handle_kmb, "2": handle_citybus, "3": handle_gmb, "4": handle_mtr}
    
    while True:
        print("\n==================================================")
        print(" HK Public Transport ETA CLI (English)")
        print("==================================================")
        print("1. KMB (Kowloon Motor Bus)")
        print("2. Citybus")
        print("3. GMB (Green Minibus)")
        print("4. MTR (Mass Transit Railway)")
        print("q. Quit")
        
        try:
            user_choice = input("\nSelect: ").strip().lower()
            if user_choice == 'q': raise QuitProgram()
            if user_choice in handlers:
                handlers[user_choice]()
            else:
                print("Invalid selection.")
        except GoBack:
            continue # Go back to the main menu
        except (KeyboardInterrupt, EOFError, QuitProgram):
            print("\nBye!")
            sys.exit(0)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}", exc_info=True)
            input("An error occurred. Press Enter to return to the main menu.")

if __name__ == "__main__":
    main()
