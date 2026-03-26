# Hong Kong Public Transport ETA CLI

A simple, fast, and user-friendly command-line interface (CLI) to get real-time Estimated Time of Arrival (ETA) for major public transport services in Hong Kong.

Built with Python, this tool provides a pure-text interface that is perfect for developers, terminal enthusiasts, or anyone who wants quick access to transport schedules without a graphical browser.

![Screenshot of a terminal running the HK Transport ETA CLI, showing the main menu for KMB, Citybus, GMB, and MTR.](https://github.com/herolch07/int2067_eta_system/blob/main/Screenshot%202026-03-16%20161834.png)  

## Features

- **Multi-Provider Support**: Get ETAs for KMB, Citybus, GMB, and MTR.
- **Interactive CLI**: Easy-to-navigate menus for selecting routes, directions, and stops.
- **Auto-Refreshing ETAs**: The ETA display automatically loops and refreshes until you choose to exit.
- **Dynamic Dependency Check**: Automatically installs required Python libraries (`requests`, `tabulate`) on first run.
- **User-Friendly**: Includes loading spinners for network requests and clear "To [Destination]" formats.
- **Robust and Lightweight**: Built with standard Python libraries for maximum compatibility and speed.

## How It Works

This CLI application works by fetching real-time Estimated Time of Arrival (ETA) data directly from the official public transport APIs provided by KMB, Citybus, GMB, and MTR.

1.  **API Clients**: Dedicated Python classes (`KMBClient`, `CitybusClient`, `GMBClient`, `MTRClient`) are implemented to interact with each transport provider's specific API endpoints.
2.  **HTTP Requests**: The underlying `BaseClient` uses the `requests` library to make HTTP GET requests to these APIs, including retry logic and session management for efficiency.
3.  **Data Fetching**: When you select a route and stop, the application sends a request to the relevant API.
4.  **Data Processing**: The API typically returns data in JSON format. The application parses this JSON response, extracts relevant information (like arrival times, destinations, remarks), and converts raw timestamps into human-readable local times and minutes remaining.
5.  **Real-time Display**: The processed ETA data is then presented in a clean, tabular format, updating automatically at regular intervals.

## Supported Services

-  Kowloon Motor Bus (KMB)
- Citybus
- Green Minibus (GMB)
- Mass Transit Railway (MTR)

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- `pip` (which is included with modern Python installations)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/herolch07/int2067_eta_system.git
    cd your-repo-name
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    The script will attempt to install dependencies for you. However, it's good practice to install them manually via `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Option 1: Pull from Docker Hub (Easiest)

Pull and run directly from Docker Hub:

```bash
docker run -it --rm herolch07/hk-transport-eta:latest
```

This downloads the pre-built image and runs it immediately.

---

### Option 2: Build Locally

If you prefer to build from source:

#### Prerequisites

- [Docker](https://www.docker.com/get-started/) installed on your machine

#### Build the Docker Image

```bash
docker build -t hk-transport-eta .
```

#### Run the CLI

```bash
docker run -it --rm hk-transport-eta
```

#### Quick One-Liner (Build & Run)

```bash
docker build -t hk-transport-eta . && docker run -it --rm hk-transport-eta
```

```bash
python main.py
```

You will be presented with a main menu. Just follow the on-screen prompts:
1.  Select a transport provider (e.g., "1" for KMB).
2.  Enter the route number you want to check.
3.  Select the direction of travel.
4.  Choose your bus stop from the list by its sequence number.
5.  The tool will then display a live, auto-refreshing table of upcoming arrival times.

- To **go back** to the previous menu at any time, type `b` and press Enter.
- To **quit** the program, type `q` and press Enter.
- To **refresh** the ETA list manually, press Enter.

## Data Sources and Attribution

This project fetches real-time data from the following sources, made available by the HKSAR Government's public data portal, [DATA.GOV.HK](https://data.gov.hk/):

*   **Kowloon Motor Bus (KMB)**: `https://data.etabus.gov.hk/v1/transport/kmb/`
*   **Citybus**: `https://rt.data.gov.hk/v2/transport/citybus/`
*   **Green Minibus (GMB)**: `https://data.etagmb.gov.hk/`
*   **Mass Transit Railway (MTR)**: `https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php`

This application is not affiliated with or endorsed by any of the transport operators or the HKSAR Government. The data is provided "as is" and its accuracy is subject to the data providers.

## Author

**Hero Lam** ([@herolch07](https://github.com/herolch07))
**Liu Fangrui** ([@Liu Andy](https://github.com/themereu))

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Test Cases

To evaluate the application's functionality, usability, and error handling, please follow the test cases below. Run the program in your terminal using `python project.py`. 

*Note: In the sample sessions below, the user's input is marked with an <u>underline</u>.*

### Test Case 1: Standard Route Query (Happy Path)
**Objective:** Verify that the system successfully fetches real-time ETAs from the KMB API and displays them in a formatted table.
**Steps for Instructor:** 1. Select KMB provider (1).
2. Enter a valid route (e.g., 1A).
3. Select the outbound direction (1).
4. Select a stop sequence from the list (5).

**Sample Session (VS Code Output):**
Select Provider (1: KMB, 2: Citybus, 3: GMB, 4: MTR, q: Quit)
> Input: <u>1</u>

Enter Route Number (b: Back, q: Quit)
> Input: <u>1A</u>

Select Direction:
1. To Sau Mau Ping (Central)
2. To Star Ferry
> Input: <u>1</u>

Select Stop Sequence (1-30):
> Input: <u>5</u>

[Loading ETAs...]
=========================================
Route 1A to Sau Mau Ping (Central)
Stop: Mong Kok Railway Station
-----------------------------------------
ETA 1: 3 mins (14:05)
ETA 2: 10 mins (14:12)
ETA 3: 18 mins (14:20)
=========================================
Press Enter to refresh, 'b' to go back, 'q' to quit.


### Test Case 2: Invalid Route (Error Handling)
**Objective:** Verify that the program handles API "Not Found" errors gracefully without crashing, prompting the user to try again.
**Steps for Instructor:** Select a provider and enter a non-existent route (e.g., 999XYZ).

**Sample Session:**
Select Provider (1: KMB, 2: Citybus, 3: GMB, 4: MTR, q: Quit)
> Input: <u>1</u>

Enter Route Number (b: Back, q: Quit)
> Input: <u>999XYZ</u>

[Loading...]
Error: Route '999XYZ' not found. Please check the route number and try again.

Enter Route Number (b: Back, q: Quit)
> Input: <u>b</u>


### Test Case 3: Empty Input & Out-of-Bounds (Boundary Cases)
**Objective:** Ensure the system does not break when encountering empty inputs, incorrect data types (letters instead of numbers), or out-of-range menu selections.
**Steps for Instructor:** 1. Press `Enter` without typing anything.
2. Type a letter (e.g., 'A') when a number is expected.
3. Type a number outside the valid menu range (e.g., 99).

**Sample Session:**
Select Provider (1: KMB, 2: Citybus, 3: GMB, 4: MTR, q: Quit)
> Input: <u></u>
Error: Input cannot be empty. Please enter a valid choice.

Select Provider (1: KMB, 2: Citybus, 3: GMB, 4: MTR, q: Quit)
> Input: <u>A</u>
Error: Invalid selection. Please enter a number between 1 and 4, or 'q' to quit.

Select Provider (1: KMB, 2: Citybus, 3: GMB, 4: MTR, q: Quit)
> Input: <u>1</u>

Enter Route Number (b: Back, q: Quit)
> Input: <u>1A</u>

Select Direction:
1. To Sau Mau Ping (Central)
2. To Star Ferry
> Input: <u>99</u>
Error: Invalid choice. Please select 1 or 2.

Select Direction:
> Input: <u>b</u>


### Test Case 4: Navigation and Auto-Refresh (Usability)
**Objective:** Verify that the user can seamlessly refresh the live data, return to previous menus, and safely exit the application.
**Steps for Instructor:** From the ETA display table, press `Enter` to refresh, then type `b` to go back, and `q` to quit.

**Sample Session:**
=========================================
Route 1A to Sau Mau Ping (Central)
Stop: Mong Kok Railway Station
-----------------------------------------
ETA 1: 3 mins (14:05)
=========================================
Press Enter to refresh, 'b' to go back, 'q' to quit.
> Input: <u></u>

[Refreshing Data...]
=========================================
Route 1A to Sau Mau Ping (Central)
Stop: Mong Kok Railway Station
-----------------------------------------
ETA 1: 2 mins (14:05)
=========================================
Press Enter to refresh, 'b' to go back, 'q' to quit.
> Input: <u>b</u>

Select Stop Sequence (1-30):
> Input: <u>q</u>

Exiting HK Transport ETA CLI. Goodbye!
