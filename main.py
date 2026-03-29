#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==========================================
# Hong Kong Public Transport ETA CLI
# ==========================================
# Features:
# 1. Full English UI for perfect table alignment.
# 2. "To [Destination]" format for directions.
# 3. Auto-refreshing ETA loop with current time.
# 4. Loading spinners for all network actions.
# 5. Robust error handling and clean code structure.
# 6. Favorites and History persistence with JSON file I/O.
# 7. Launch real-time ETA from saved favorites/history.
# ==========================================


# ==========================================
# 0. Environment Auto-Setup
# ==========================================
def ensure_dependencies():
    # Check and install required libraries if not present.
    required = {
        "requests": "requests",
        "tabulate": "tabulate"
    }

    import importlib
    import subprocess
    import sys

    missing_libs = []
    for lib_name, pip_name in required.items():
        try:
            importlib.import_module(lib_name)
        except ImportError:
            missing_libs.append(pip_name)

    # Return early if all dependencies are satisfied
    if (not missing_libs):
        return True

    # Show missing libraries prompt
    print("\nMissing required libraries:")
    for lib in missing_libs:
        print(f"  - {lib}")

    print("\nOptions:")
    print("  1. Auto-install missing libraries now")
    print("  2. Exit and install manually (pip install -r requirements.txt)")

    while (True):
        choice = input("\nSelect (1/2): ").strip()
        if (choice == "2"):
            print("\nPlease run: pip install -r requirements.txt")
            return False
        elif (choice == "1"):
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    # Install missing libraries
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


# Run dependency check before importing third-party libraries
if (not ensure_dependencies()):
    raise SystemExit(1)


# ==========================================
# 1. Imports
# ==========================================
import logging
import time
import re
import sys
import threading
import itertools
import math
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta, tzinfo
from typing import Any, Dict, List, Optional, Tuple

import requests
from tabulate import tabulate

# Set logging to only show critical errors
logging.basicConfig(level=logging.ERROR)


# ==========================================
# 2. Timezone Setup
# ==========================================
# Try to use zoneinfo for Hong Kong timezone, fallback to custom class
try:
    from zoneinfo import ZoneInfo
    HKT = ZoneInfo("Asia/Hong_Kong")
except (ImportError, Exception):
    # Fallback: Custom Hong Kong timezone class (UTC+8)
    class HKTimeZone(tzinfo):
        def utcoffset(self, dt):
            return timedelta(hours=8)

        def dst(self, dt):
            return timedelta(0)

        def tzname(self, dt):
            return "HKT"

    HKT = HKTimeZone()


# ==========================================
# 3. Global Data and Path Setup
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
MTR_DATA_PATH = BASE_DIR / "mtr_data.json"
FAVORITES_PATH = BASE_DIR / "favorites.json"
HISTORY_PATH = BASE_DIR / "history.json"

# MTR line and station data loaded from JSON
MTR_LINES = {}
MTR_STATIONS = {}
try:
    if (MTR_DATA_PATH.exists()):
        with open(MTR_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            MTR_LINES = data.get("MTR_LINES", {})
            MTR_STATIONS = data.get("MTR_STATIONS", {})
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Note: MTR data file not found or invalid at {MTR_DATA_PATH}. MTR features may be limited.", file=sys.stderr)


# ==========================================
# 4. Loading Animation
# ==========================================
class LoadingSpinner:
    # Context manager to show a rotating spinner (| / - \)
    # while a blocking network task is running.
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
        # Clear the spinner line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def _animate(self):
        # Cycle through spinner characters
        for char in itertools.cycle(['|', '/', '-', '\\']):
            if (self.stop_running):
                break
            sys.stdout.write(f'\r{self.message} {char}')
            sys.stdout.flush()
            time.sleep(0.1)


# ==========================================
# 5. Base Network Client
# ==========================================
class BaseClient:
    # Handles all HTTP requests with retry logic and session reuse.
    def __init__(self, base_url: str = "", timeout: int = 10, max_retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _full_url(self, path: str) -> str:
        # Construct full URL from base_url and path
        if (not path.startswith("http")):
            return f"{self.base_url}/{path.lstrip('/')}"
        return path

    def get_json(self, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
        # Perform GET request with retry logic
        url = self._full_url(path)
        attempt = 0
        while (attempt <= self.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    headers={"User-Agent": "HKTransportCLI/1.0"}
                )
                # Retry on server errors (5xx)
                if (not response.ok):
                    if (500 <= response.status_code < 600 and attempt < self.max_retries):
                        attempt += 1
                        time.sleep(1)
                        continue
                    return None
                return response.json()
            except (requests.Timeout, requests.ConnectionError):
                # Retry on network errors
                if (attempt < self.max_retries):
                    attempt += 1
                    time.sleep(1)
                    continue
                return None
            except Exception:
                return None
        return None


# ==========================================
# 6. Helper Functions
# ==========================================
def parse_iso(timestamp_str: str) -> Optional[datetime]:
    # Parse ISO timestamp string to datetime object.
    if (not timestamp_str):
        return None
    try:
        # Convert 'Z' suffix to '+00:00' for Python compatibility
        if (timestamp_str.endswith("Z")):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        return datetime.fromisoformat(timestamp_str)
    except Exception:
        return None


def minutes_until(target_time: datetime) -> int:
    # Calculate minutes remaining until target time.
    # Uses math.ceil (rounding up) for a safety buffer.
    # Example: 4m01s -> 5 min
    if (not target_time):
        return 0
    now = datetime.now(timezone.utc)
    diff_seconds = (target_time - now).total_seconds()

    if (diff_seconds <= 0):
        return 0
    return math.ceil(diff_seconds / 60)


def natural_sort_key(s: str) -> Tuple[int, str]:
    # Natural sort key for route numbers.
    # Ensures 'Route 10' comes after 'Route 2'.
    match = re.match(r"(\d+)?(.*)", str(s))
    if (match):
        return (int(match.group(1)) if match.group(1) else 0, match.group(2))
    return (0, str(s))


# ==========================================
# 6A. Persistence Helpers
# ==========================================
def load_json_file(path: Path, default):
    # Load JSON data safely, returning default on error.
    try:
        if (path.exists()):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {path}: {e}", exc_info=True)
    return default


def save_json_file(path: Path, data) -> bool:
    # Save JSON data safely.
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to save {path}: {e}", exc_info=True)
        return False


def load_favorites() -> List[Dict[str, Any]]:
    data = load_json_file(FAVORITES_PATH, [])
    return data if isinstance(data, list) else []


def save_favorites(favorites: List[Dict[str, Any]]) -> bool:
    return save_json_file(FAVORITES_PATH, favorites)


def load_history() -> List[Dict[str, Any]]:
    data = load_json_file(HISTORY_PATH, [])
    return data if isinstance(data, list) else []


def save_history(history: List[Dict[str, Any]]) -> bool:
    return save_json_file(HISTORY_PATH, history)


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    # Normalize record for duplicate comparison.
    # Remove 'saved_at' field when comparing.
    cloned = dict(record)
    cloned.pop("saved_at", None)
    return cloned


def add_to_history(record: Dict[str, Any], limit: int = 20) -> None:
    # Add a search record to history, maintaining a maximum limit.
    history = load_history()
    record_to_save = dict(record)
    record_to_save["saved_at"] = datetime.now(HKT).strftime("%Y-%m-%d %H:%M:%S")

    # Insert at the beginning and trim to limit
    history.insert(0, record_to_save)
    history = history[:limit]
    save_history(history)


def add_to_favorites(record: Dict[str, Any]) -> None:
    # Add a search record to favorites if not already exists.
    favorites = load_favorites()
    normalized_new = normalize_record(record)

    # Check for duplicates
    for fav in favorites:
        if (normalize_record(fav) == normalized_new):
            print("This search is already in favorites.")
            return

    record_to_save = dict(record)
    record_to_save["saved_at"] = datetime.now(HKT).strftime("%Y-%m-%d %H:%M:%S")
    favorites.append(record_to_save)

    if (save_favorites(favorites)):
        print("Added to favorites.")
    else:
        print("Failed to save favorite.")


def ask_save_favorite(record: Dict[str, Any]) -> None:
    # Prompt user to save the current search to favorites.
    while (True):
        choice = input("\nSave this search to favorites? (y/n): ").strip().lower()
        if (choice in ("y", "yes")):
            add_to_favorites(record)
            return
        elif (choice in ("n", "no", "")):
            return
        else:
            print("Please enter y or n.")


# ==========================================
# 7. UI Helpers
# ==========================================
class GoBack(Exception):
    # Exception to signal returning to previous menu.
    pass


class QuitProgram(Exception):
    # Exception to signal program termination.
    pass


NAV_HINT = " (Type 'b' to back, 'q' to quit)"


def ask_input(prompt: str) -> str:
    # Standardized input with blank line for readability.
    print()
    while (True):
        try:
            user_input = input(f"{prompt}{NAV_HINT}: ").strip()
            if (user_input.lower() == 'b'):
                raise GoBack()
            if (user_input.lower() == 'q'):
                raise QuitProgram()
            if (user_input):
                return user_input
            print("Input cannot be empty.")
        except (KeyboardInterrupt, EOFError):
            raise QuitProgram()


def ask_index(max_index: int, prompt: str = "Select Index") -> int:
    # Standardized number selection (1-based index).
    while (True):
        index_input = ask_input(prompt)
        try:
            idx = int(index_input)
            if (1 <= idx <= max_index):
                return idx
            print(f"Please enter a number between 1 and {max_index}.")
        except ValueError:
            print("Invalid number.")


def wait_for_enter() -> None:
    # Pause execution for refresh or navigation.
    print()
    command = input("Press ENTER to refresh, 'b' to back, 'q' to quit: ").strip().lower()
    if (command == ""):
        return
    if (command == "b"):
        raise GoBack()
    if (command == "q"):
        raise QuitProgram()


# ==========================================
# 8. API Clients
# ==========================================
class KMBClient(BaseClient):
    # Client for KMB (Kowloon Motor Bus) API.
    def __init__(self):
        super().__init__("https://data.etabus.gov.hk/v1/transport/kmb")
        self.stop_cache = {}

    def list_routes(self):
        data = self.get_json("route")
        return data.get("data", []) if data else []

    def list_stops(self, route, bound, service_type="1"):
        # Convert bound code to API format
        bound_map = {"O": "outbound", "I": "inbound"}
        bound_str = bound_map.get(bound.upper(), bound)
        data = self.get_json(f"route-stop/{route}/{bound_str}/{service_type}")
        return sorted(data.get("data", []) if data else [], key=lambda x: int(x.get("seq", 0)))

    def get_stop_name(self, stop_id):
        # Get stop details with caching
        if (stop_id in self.stop_cache):
            return self.stop_cache[stop_id]

        data = self.get_json(f"stop/{stop_id}")
        stop_data = data.get("data", {}) if data else {}
        if (stop_data):
            self.stop_cache[stop_id] = stop_data
        return stop_data

    def get_eta(self, stop_id, route, service_type="1"):
        data = self.get_json(f"eta/{stop_id}/{route}/{service_type}")
        return data.get("data", []) if data else []


class CitybusClient(BaseClient):
    # Client for Citybus API.
    def __init__(self):
        super().__init__("https://rt.data.gov.hk/v2/transport/citybus")
        self.stop_cache = {}

    def get_route(self, route_no):
        data = self.get_json(f"route/CTB/{route_no}")
        if (not data):
            return None
        result = data.get("data")
        # Handle both list and dict responses
        if (isinstance(result, list) and result):
            return result[0]
        if (isinstance(result, dict)):
            return result
        return None

    def get_stops(self, route_no, direction):
        data = self.get_json(f"route-stop/CTB/{route_no}/{direction}")
        return sorted(data.get("data", []) if data else [], key=lambda x: int(x.get("seq", 999)))

    def get_stop_detail(self, stop_id):
        # Get stop details with caching
        if (stop_id in self.stop_cache):
            return self.stop_cache[stop_id]

        data = self.get_json(f"stop/{stop_id}")
        stop_data = data.get("data", {}) if data else {}
        if (stop_data):
            self.stop_cache[stop_id] = stop_data
        return stop_data

    def get_eta(self, stop_id, route_no):
        data = self.get_json(f"eta/CTB/{stop_id}/{route_no}")
        return data.get("data", []) if data else []


class GMBClient(BaseClient):
    # Client for Green Minibus (GMB) API.
    def __init__(self):
        super().__init__("https://data.etagmb.gov.hk")

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
    # Client for MTR (Mass Transit Railway) API.
    def __init__(self):
        super().__init__("https://rt.data.gov.hk")

    def get_schedule(self, line, station):
        data = self.get_json(
            "v1/transport/mtr/getSchedule.php",
            params={"line": line, "sta": station, "lang": "EN"}
        )
        if (not data or data.get("status") != 1):
            return {}
        schedule_data = data.get("data", {})
        key = next(iter(schedule_data.keys()), None)
        return schedule_data.get(key, {}) if key else {}


# ==========================================
# 9. Logic Refactoring & Display Loop
# ==========================================
def display_eta_loop(header: str, eta_fetcher, data_processor, table_headers: List[str]):
    # Generic loop to display real-time ETA data in a table.
    while (True):
        with LoadingSpinner("Refreshing..."):
            raw_data = eta_fetcher()

        time_now = datetime.now(HKT).strftime('%H:%M:%S')
        print(f"\n{header} ({time_now})")

        table_data, message = data_processor(raw_data)

        if (table_data):
            print(tabulate(table_data, headers=table_headers, tablefmt="simple"))
        else:
            print(f"  {message or 'No data available.'}")

        wait_for_enter()


def process_kmb_eta(etas, bound, target_seq):
    # Process KMB ETA data into table format.
    # Filter by direction and stop sequence.
    filtered = [
        e for e in etas
        if ((e.get("dir") or "").upper() == bound.upper()
            and str(e.get("seq")) == str(target_seq))
    ]
    filtered.sort(key=lambda x: (int(x.get("eta_seq", 99)), x.get("eta")))

    table_data = []
    for e in filtered:
        eta_time = parse_iso(e.get("eta"))
        table_data.append([
            e.get("route", ""),
            e.get("dest_en"),
            eta_time.astimezone(HKT).strftime("%H:%M:%S") if eta_time else "-",
            minutes_until(eta_time) if eta_time else "-",
            e.get("rmk_en") or ""
        ])
    return table_data, "No ETA info available for this stop."


def process_citybus_eta(etas, target_dir):
    # Process Citybus ETA data into table format.
    # Filter by direction.
    filtered = [e for e in etas if ((e.get("dir") or "").upper() == target_dir)]

    table_data = []
    for e in filtered:
        eta_time = parse_iso(e.get("eta"))
        table_data.append([
            e.get("route", ""),
            e.get("dest_en"),
            eta_time.astimezone(HKT).strftime("%H:%M:%S") if eta_time else "-",
            minutes_until(eta_time) if eta_time else "-",
            e.get("rmk_en") or ""
        ])
    return table_data, "No ETA info available."


def process_gmb_eta(data, route_input, dest_en):
    # Process GMB ETA data into table format.
    eta_list = data.get("eta", []) if data else []
    table_data = []
    for e in eta_list:
        eta_time = parse_iso(e.get("timestamp"))
        table_data.append([
            route_input,
            dest_en,
            (eta_time or datetime.now()).astimezone(HKT).strftime("%H:%M:%S"),
            e.get("diff", "-"),
            e.get("remarks_en")
        ])
    return table_data, "No ETA info available."


def process_mtr_data(schedule):
    # Process MTR schedule data into table format.
    if (not schedule):
        return [], "No trains available."

    all_trains = []
    for direction, trains in schedule.items():
        if (not isinstance(trains, list) or not trains):
            continue

        # Add direction header row
        all_trains.append([f"--- To: {trains[0].get('dest')} ---", "", "", ""])
        for t in trains:
            all_trains.append([
                t.get("time"),
                MTR_STATIONS.get(t.get("dest"), t.get("dest")),
                t.get("plat"),
                t.get("ttnt")
            ])
    return all_trains, "No schedule data."


# ==========================================
# 9B. Handlers
# ==========================================
def handle_kmb():
    # Handle KMB route search workflow.
    print("\n=== KMB (Kowloon Motor Bus) ===")
    client = KMBClient()

    # Download all KMB routes
    with LoadingSpinner("Downloading KMB Route Data..."):
        routes = client.list_routes()
    if (not routes):
        print("Failed to download KMB routes.")
        return

    route_input = ask_input("Enter Route No. (e.g. 74K)").upper()
    candidates = [r for r in routes if (r.get("route", "").upper() == route_input)]
    if (not candidates):
        print("Route not found.")
        return

    # Display direction options
    print(f"\nSelect Direction for Route {route_input}:")
    for i, r in enumerate(candidates, 1):
        print(f"{i}. To {r.get('dest_en')} (from {r.get('orig_en')}) [Type {r.get('service_type')}]")

    selected_route = candidates[ask_index(len(candidates)) - 1]

    # Fetch stops for selected route
    with LoadingSpinner("Fetching stops..."):
        stops = client.list_stops(
            selected_route['route'],
            selected_route['bound'],
            selected_route.get('service_type', '1')
        )

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

    try:
        target_seq = int(ask_input("Enter Stop Sequence Number"))
    except ValueError:
        print("Invalid sequence.")
        return

    if (target_seq not in stop_map):
        print("Invalid sequence.")
        return

    stop_info = stop_map[target_seq]
    header = f"======== [{route_input}] @ {stop_info['name']} ========"

    # Save search record
    search_record = {
        "mode": "KMB",
        "label": f"KMB {route_input} @ {stop_info['name']} -> {selected_route.get('dest_en')}",
        "params": {
            "route": selected_route['route'],
            "bound": selected_route['bound'],
            "service_type": selected_route.get('service_type', '1'),
            "stop_id": stop_info['id'],
            "stop_seq": target_seq,
            "stop_name": stop_info['name'],
            "dest_en": selected_route.get('dest_en'),
            "orig_en": selected_route.get('orig_en')
        }
    }
    add_to_history(search_record)
    ask_save_favorite(search_record)

    # Start ETA display loop
    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_eta(
            stop_info['id'],
            selected_route['route'],
            selected_route.get('service_type', '1')
        ),
        data_processor=lambda etas: process_kmb_eta(etas, selected_route['bound'], target_seq),
        table_headers=["Route", "Destination", "Time", "Min", "Remark"]
    )


def handle_citybus():
    # Handle Citybus route search workflow.
    print("\n=== Citybus ===")
    client = CitybusClient()

    route_input = ask_input("Enter Route No. (e.g. 102)").upper()

    with LoadingSpinner("Finding route..."):
        route_info = client.get_route(route_input)
    if (not route_info):
        print("Route not found.")
        return

    orig = route_info.get('orig_en')
    dest = route_info.get('dest_en')

    print(f"\nRoute: {route_info.get('route')}")
    print(f"1. To {dest} (from {orig})")
    print(f"2. To {orig} (from {dest})")

    direction = "inbound" if (ask_index(2) == 2) else "outbound"

    # Fetch stops for selected direction
    with LoadingSpinner("Fetching stops..."):
        stops = client.get_stops(route_input, direction)

    stop_list = []
    print("\nStops:")
    for s in stops:
        meta = client.get_stop_detail(s.get("stop"))
        name_en = meta.get('name_en', s.get("stop"))
        name_tc = meta.get('name_tc', "")
        name = f"{name_en} ({name_tc})" if name_tc else name_en
        seq = int(s.get("seq"))
        print(f"{seq:>2}. {name}")
        stop_list.append({"seq": seq, "id": s.get("stop"), "name": name})

    try:
        target_seq = int(ask_input("Enter Stop Sequence Number"))
    except ValueError:
        print("Invalid stop.")
        return

    selected_stop = next((x for x in stop_list if (x["seq"] == target_seq)), None)
    if (not selected_stop):
        print("Invalid stop.")
        return

    header = f"======== [{route_input}] @ {selected_stop['name']} ========"
    target_dir = "I" if (direction == "inbound") else "O"

    # Save search record
    search_record = {
        "mode": "Citybus",
        "label": f"Citybus {route_input} @ {selected_stop['name']} -> {dest if direction == 'outbound' else orig}",
        "params": {
            "route": route_input,
            "direction": direction,
            "stop_id": selected_stop['id'],
            "stop_seq": target_seq,
            "stop_name": selected_stop['name'],
            "orig_en": orig,
            "dest_en": dest
        }
    }
    add_to_history(search_record)
    ask_save_favorite(search_record)

    # Start ETA display loop
    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_eta(selected_stop['id'], route_input),
        data_processor=lambda etas: process_citybus_eta(etas, target_dir),
        table_headers=["Route", "Destination", "Time", "Min", "Remark"]
    )


def handle_gmb():
    # Handle Green Minibus route search workflow.
    print("\n=== Green Minibus ===")
    client = GMBClient()

    # Select region
    print("1. Hong Kong Island (HKI)")
    print("2. Kowloon (KLN)")
    print("3. New Territories (NT)")
    region = ["HKI", "KLN", "NT"][ask_index(3) - 1]

    with LoadingSpinner(f"Downloading {region} routes..."):
        routes = client.get_routes(region)
    if (not routes):
        print("No routes found for this region.")
        return

    route_input = ask_input(f"Enter Route No. (e.g. {routes[0]})").upper()

    with LoadingSpinner("Fetching details..."):
        details = client.get_details(region, route_input)
    if (not details):
        print("Details not found.")
        return

    # Display route variants
    print("\nSelect Route Variant:")
    for i, d in enumerate(details, 1):
        print(f"{i}. {d.get('description_en')}")

    selected_variant = details[ask_index(len(details)) - 1]

    directions = selected_variant.get("directions", [])
    if (not directions):
        print("No directions available.")
        return

    # Display direction options
    print("\nSelect Direction:")
    for i, d in enumerate(directions, 1):
        print(f"{i}. To {d.get('dest_en')} (from {d.get('orig_en')})")

    selected_dir = directions[ask_index(len(directions)) - 1]

    # Fetch stops
    with LoadingSpinner("Fetching stops..."):
        stops = client.get_stops(selected_variant.get("route_id"), selected_dir.get("route_seq"))

    if (not stops):
        print("No stops found.")
        return

    print("\nStops:")
    for s in stops:
        print(f"{s.get('stop_seq'):>2}. {s.get('name_en')} ({s.get('name_tc')})")

    try:
        target_seq = int(ask_input("Enter Stop Sequence"))
    except ValueError:
        print("Invalid sequence.")
        return

    stop_match = next((s for s in stops if (int(s.get('stop_seq')) == target_seq)), None)
    if (not stop_match):
        print("Invalid sequence.")
        return

    stop_name_display = f"{stop_match.get('name_en')} ({stop_match.get('name_tc')})"
    header = f"======== [{route_input}] @ {stop_name_display} ========"

    # Save search record
    search_record = {
        "mode": "GMB",
        "label": f"GMB {route_input} @ {stop_name_display} -> {selected_dir.get('dest_en')}",
        "params": {
            "region": region,
            "route": route_input,
            "route_id": selected_variant.get("route_id"),
            "route_seq": selected_dir.get("route_seq"),
            "stop_seq": target_seq,
            "stop_name": stop_name_display,
            "dest_en": selected_dir.get("dest_en"),
            "orig_en": selected_dir.get("orig_en"),
            "description_en": selected_variant.get("description_en")
        }
    }
    add_to_history(search_record)
    ask_save_favorite(search_record)

    # Start ETA display loop
    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_eta(
            selected_variant.get("route_id"),
            selected_dir.get("route_seq"),
            target_seq
        ),
        data_processor=lambda data: process_gmb_eta(data, route_input, selected_dir.get('dest_en')),
        table_headers=["Route", "Destination", "Time", "Min", "Remark"]
    )


def handle_mtr():
    # Handle MTR schedule search workflow.
    print("\n=== MTR Next Train ===")
    if (not MTR_LINES or not MTR_STATIONS):
        print("MTR data is not available. Please check 'mtr_data.json'.")
        return

    client = MTRClient()

    # Display available lines
    lines = sorted(MTR_LINES.keys())
    for i, l in enumerate(lines, 1):
        print(f"{i}. {l}")

    selected_line_key = lines[ask_index(len(lines)) - 1]
    line_info = MTR_LINES[selected_line_key]

    # Display stations on selected line
    stations = line_info["stations"]
    for i, s in enumerate(stations, 1):
        print(f"{i}. {MTR_STATIONS.get(s, s)} ({s})")

    selected_station_code = stations[ask_index(len(stations)) - 1]
    station_name = MTR_STATIONS.get(selected_station_code, selected_station_code)

    header = f"======== {selected_line_key} @ {station_name} ========"

    # Save search record
    search_record = {
        "mode": "MTR",
        "label": f"MTR {selected_line_key} @ {station_name}",
        "params": {
            "line_key": selected_line_key,
            "line_code": line_info["code"],
            "station_code": selected_station_code,
            "station_name": station_name
        }
    }
    add_to_history(search_record)
    ask_save_favorite(search_record)

    # Start ETA display loop
    display_eta_loop(
        header=header,
        eta_fetcher=lambda: client.get_schedule(line_info["code"], selected_station_code),
        data_processor=process_mtr_data,
        table_headers=["Time", "Dest", "Plat", "Min"]
    )


# ==========================================
# 9C. Activation (Universal for Fav/History)
# ==========================================
def launch_record(record: Dict[str, Any]):
    # Launch real-time ETA display from a saved record.
    # Works for both favorites and history items.
    mode = record.get("mode")
    p = record.get("params", {})
    header = f"======== [LIVE] {record.get('label')} ========"

    if (mode == "KMB"):
        client = KMBClient()
        display_eta_loop(
            header,
            lambda: client.get_eta(p['stop_id'], p['route'], p['service_type']),
            lambda etas: process_kmb_eta(etas, p['bound'], p['stop_seq']),
            ["Route", "Destination", "Time", "Min", "Remark"]
        )
    elif (mode == "Citybus"):
        client = CitybusClient()
        target_dir = "I" if (p['direction'] == "inbound") else "O"
        display_eta_loop(
            header,
            lambda: client.get_eta(p['stop_id'], p['route']),
            lambda etas: process_citybus_eta(etas, target_dir),
            ["Route", "Destination", "Time", "Min", "Remark"]
        )
    elif (mode == "GMB"):
        client = GMBClient()
        display_eta_loop(
            header,
            lambda: client.get_eta(p['route_id'], p['route_seq'], p['stop_seq']),
            lambda data: process_gmb_eta(data, p['route'], p['dest_en']),
            ["Route", "Destination", "Time", "Min", "Remark"]
        )
    elif (mode == "MTR"):
        client = MTRClient()
        display_eta_loop(
            header,
            lambda: client.get_schedule(p['line_code'], p['station_code']),
            process_mtr_data,
            ["Time", "Dest", "Plat", "Min"]
        )


# ==========================================
# 9D. Favorites / History Handlers
# ==========================================
def show_favorites():
    # Display and manage saved favorites.
    favorites = load_favorites()
    if (not favorites):
        print("\nNo favorites saved yet.")
        return

    while (True):
        print("\n=== Favorites ===")
        for i, fav in enumerate(favorites, 1):
            print(f"{i}. {fav.get('label', 'Unnamed')}  [saved: {fav.get('saved_at', '-')}]")

        print("\nOptions:")
        print("  Enter number to view real-time ETA")
        print("  d - Delete a favorite")
        print("  b - Back to main menu")

        choice = input("\nSelect: ").strip().lower()

        if (choice == 'b'):
            return
        elif (choice == 'd'):
            idx = ask_index(len(favorites), "Enter favorite index to delete") - 1
            removed = favorites.pop(idx)
            if (save_favorites(favorites)):
                print(f"Deleted favorite: {removed.get('label', 'Unnamed')}")
            else:
                print("Failed to delete favorite.")

            if (not favorites):
                print("No favorites saved yet.")
                return
        else:
            try:
                idx = int(choice) - 1
                if (0 <= idx < len(favorites)):
                    try:
                        launch_record(favorites[idx])
                    except GoBack:
                        continue
                else:
                    print("Invalid index.")
            except ValueError:
                print("Invalid input.")


def show_history():
    # Display and manage search history.
    history = load_history()
    if (not history):
        print("\nNo history yet.")
        return

    while (True):
        print("\n=== Search History ===")
        for i, item in enumerate(history, 1):
            print(f"{i}. {item.get('label', 'Unnamed')}  [time: {item.get('saved_at', '-')}]")

        print("\nOptions:")
        print("  Enter number to view real-time ETA")
        print("  c - Clear all history")
        print("  b - Back to main menu")

        choice = input("\nSelect: ").strip().lower()

        if (choice == 'b'):
            return
        elif (choice == 'c'):
            save_history([])
            print("History cleared.")
            return
        else:
            try:
                idx = int(choice) - 1
                if (0 <= idx < len(history)):
                    try:
                        launch_record(history[idx])
                    except GoBack:
                        continue
                else:
                    print(f"Invalid index. Please select 1-{len(history)}.")
            except ValueError:
                print("Invalid input.")


# ==========================================
# 10. Main Loop
# ==========================================
def main():
    handlers = {
        "1": handle_kmb,
        "2": handle_citybus,
        "3": handle_gmb,
        "4": handle_mtr,
        "5": show_favorites,
        "6": show_history
    }

    while (True):
        print("\n==================================================")
        print(" HK Public Transport ETA CLI (English)")
        print("==================================================")
        print("1. KMB (Kowloon Motor Bus)")
        print("2. Citybus")
        print("3. GMB (Green Minibus)")
        print("4. MTR (Mass Transit Railway)")
        print("5. Favorites")
        print("6. History")
        print("q. Quit")

        try:
            user_choice = input("\nSelect: ").strip().lower()
            if (user_choice == 'q'):
                raise QuitProgram()
            if (user_choice in handlers):
                handlers[user_choice]()
            else:
                print("Invalid selection.")
        except GoBack:
            continue
        except (KeyboardInterrupt, EOFError, QuitProgram):
            print("\nBye!")
            sys.exit(0)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}", exc_info=True)
            input("An error occurred. Press Enter to return to the main menu.")


if __name__ == "__main__":
    main()
