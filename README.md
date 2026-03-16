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

Simply run the `main.py` script from your terminal:

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
