# Hong Kong Public Transport ETA CLI

A simple, fast, and user-friendly command-line interface (CLI) to get real-time Estimated Time of Arrival (ETA) for major public transport services in Hong Kong.

Built with Python, this tool provides a pure-text interface that is perfect for developers, terminal enthusiasts, or anyone who wants quick access to transport schedules without a graphical browser.

![Screenshot of a terminal running the HK Transport ETA CLI, showing the main menu for KMB, Citybus, GMB, and MTR.](https://github.com/herolch07/int2067_eta_system/blob/main/main%20menu.png)  

## Features

- **Multi-Provider Support**: Get ETAs for KMB, Citybus, GMB, and MTR.
- **Interactive CLI**: Easy-to-navigate menus for selecting routes, directions, and stops.
- **Auto-Refreshing ETAs**: The ETA display automatically loops and refreshes until you choose to exit.
- **Dynamic Dependency Check**: Automatically installs required Python libraries (`requests`, `tabulate`) on first run.
- **User-Friendly**: Includes loading spinners for network requests and clear "To [Destination]" formats.
- **Robust and Lightweight**: Built with standard Python libraries for maximum compatibility and speed.
- **Favorites System**: Save your most-used routes and stops to a local 'favorites.json' file for instant access without re-typing route numbers.
- **Search History**: Automatically keeps track of your last 20 queries, allowing you to quickly jump back into a previous search.

## How It Works

This CLI application works by fetching real-time Estimated Time of Arrival (ETA) data directly from the official public transport APIs provided by KMB, Citybus, GMB, and MTR.

1.  **API Clients**: Dedicated Python classes (`KMBClient`, `CitybusClient`, `GMBClient`, `MTRClient`) are implemented to interact with each transport provider's specific API endpoints.
2.  **HTTP Requests**: The underlying `BaseClient` uses the `requests` library to make HTTP GET requests to these APIs, including retry logic and session management for efficiency.
3.  **Data Fetching**: When you select a route and stop, the application sends a request to the relevant API.
4.  **Data Processing**: The API typically returns data in JSON format. The application parses this JSON response, extracts relevant information (like arrival times, destinations, remarks), and converts raw timestamps into human-readable local times and minutes remaining.
5.  **Real-time Display**: The processed ETA data is then presented in a clean, tabular format, updating automatically at regular intervals.
6.  **Access shortcuts**: From the main menu, select "5" for Favorites or "6" for History to view and launch saved routes immediately.

## Supported Services

-  Kowloon Motor Bus (KMB)
- Citybus
- Green Minibus (GMB)
- Mass Transit Railway (MTR)

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- `pip` (which is included with modern Python installations)

## Installation and usage

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

### Option 1: Pull from Docker Hub (Recommended)

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
python project.py
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

## Test Cases

To evaluate the application's functionality, usability, and error handling, please follow the test cases below. Run the program in your terminal using `python project.py`. 

*Note: In the sample sessions below, the user's input is marked with grey background.*
>that's user input

*Note2: All output of sample sessions in this file may affected by the size of the window, recommend to have a look on the sample photo. Photo of sample be the standard of display.*

### Test Case 1: Standard Route Query (Happy Path)
**Objective:** Verify that the system successfully fetches real-time ETAs from the KMB API and displays them in a formatted table.

**Steps for Instructor:** 
1. Select KMB provider (1).
2. Enter a valid route (e.g., 1A).
3. Select the outbound direction (1).
4. Select a stop sequence from the list (5).

**Sample Session (Terminal Output):**

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

> Input: <u>1</u>

=== KMB (Kowloon Motor Bus) ===
Enter Route No. (e.g. 74K) (Type 'b' to back, 'q' to quit):

> Input: <u>74K</u>

Select Direction for Route 74K:
1. To SAM MUN TSAI (CIRCULAR) (from TAI PO MARKET STATION) [Type 1]
2. To SAM MUN TSAI (CIRCULAR) (from TAI PO MARKET STATION) [Type 2]

Select Index (Type 'b' to back, 'q' to quit):
> Input: <u>1</u>

Stops List:
 1. TAI PO MARKET STATION BUS TERMINUS (TP942) (大埔墟站巴士總站 (TP942))
 2. TAI PO HUI MARKET (TP286) (大埔墟街市 (TP286))
 3. PO HEUNG STREET TAI PO (TP300) (大埔寶鄉街 (TP300))
 4. KWONG FUK ROAD BBI - PO HEUNG BRIDGE (TP305) (廣福道轉車站 - 寶鄉橋 (TP305))
 5. TAI PO CENTRAL BUS TERMINUS (TP900) (大埔中心總站 (TP900))
 6. YEE NGA COURT (TP618) (怡雅苑 (TP618))
 7. YUE KOK (TP619) (魚角 (TP619))
 8. FUNG YUEN ROAD (TP620) (鳳園路 (TP620))
 9. HA HANG (TP621) (下坑 (TP621))
10. DAI KWAI STREET (TP622) (大貴街 (TP622))
11. TAI PO EAST FIRE STATION (TP623) (大埔東消防局 (TP623))
12. THE EDUCATION UNIVERSITY OF HK (TP893) (香港教育大學 (TP893))
13. LO FAI ROAD TAI PO (TP624) (大埔露輝路 (TP624))
14. FORTUNE GARDEN (TP625) (雅景花園 (TP625))
15. YU ON STREET SAM MUN TSAI (TP690) (三門仔漁安街 (TP690))
16. SHUEN WAN TYPHOON SHELTER (TP691) (船灣避風塘 (TP691))
17. SHA LAN ROAD (TP692) (沙欄路 (TP692))
18. SAM MUN TSAI (TP710) (三門仔 (TP710))
19. SHA LAN ROAD (TP711) (沙欄路 (TP711))
20. SHUEN WAN TYPHOON SHELTER (TP712) (船灣避風塘 (TP712))
21. YU ON STREET SAM MUN TSAI (TP713) (三門仔漁安街 (TP713))
22. FORTUNE GARDEN (TP732) (雅景花園 (TP732))
23. LO FAI ROAD TAI PO (TP733) (大埔露輝路 (TP733))
24. TAI PO INDUSTRIAL ESTATE (TP734) (大埔工業邨 (TP734))
25. HA HANG (TP735) (下坑 (TP735))
26. DAI FAT STREET TAI PO (TP736) (大埔大發街 (TP736))
27. YUE KOK (TP737) (魚角 (TP737))
28. KAU YAN COLLEGE (TP738) (救恩書院 (TP738))
29. YEE NGA COURT (TP739) (怡雅苑 (TP739))
30. TAI PO CENTRAL BUS TERMINUS (TP909) (大埔中心總站 (TP909))
31. ON CHEUNG ROAD TAI PO (TP537) (大埔安祥路 (TP537))
32. KWONG FUK ROAD BBI (TP564) (廣福道轉車站 (TP564))
33. WAN TAU STREET TAI PO (TP590) (大埔運頭街 (TP590))
34. TAI PO MARKET (TP591) (大埔墟 (TP591))
35. TAI PO MARKET STATION BUS TERMINUS (TP935) (大埔墟站巴士總站 (TP935))
36. TAI PO MARKET STATION BUS TERMINUS (TP942) (大埔墟站巴士總站 (TP942))

Enter Stop Sequence Number (Type 'b' to back, 'q' to quit):
> Input: <u>1</u>

Save this search to favorites? (y/n):
> Input: <u>n</u>

======== [74K] @ TAI PO MARKET STATION BUS TERMINUS (TP942) (大埔墟站巴士總站 (TP942)) ======== (23:40:33)
Route  -------  Destination              -------------------------Time        -----Min  Remark

74K  SAM MUN TSAI (CIRCULAR)  23:40:00     0     
74K  SAM MUN TSAI (CIRCULAR)  00:10:00     30  -Scheduled Bus

Press ENTER to refresh, 'b' to back, 'q' to quit:

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 1](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%201.png) 

### Test Case 2: Invalid Route (Error Handling)
**Objective:** Verify that the program handles API "Not Found" errors gracefully without crashing, prompting the us
1   er to try again.
**Steps for Instructor:** Select a provider and enter a non-existent route (e.g., 999XYZ).

**Sample Session:**

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit
> Input: <u>1</u>

=== KMB (Kowloon Motor Bus) ===

Enter Route No. (e.g. 74K) (Type 'b' to back, 'q' to quit):
> Input: <u>999XYZ</u>

Route not found.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 2](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%202.png) 

### Test Case 3: Empty Input & Out-of-Bounds (Boundary Cases)
**Objective:** Ensure the system does not break when encountering empty inputs, incorrect data types (letters instead of numbers), or out-of-range menu selections.

**Steps for Instructor:** 1. Press `Enter` without typing anything.
2. Type a letter (e.g., 'A') when a number is expected.
3. Type a number outside the valid menu range (e.g., 99).

**Sample Session:**
HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

> Input: <u></u>

Invalid selection.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

> Input: <u>A</u>

Invalid selection.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:
> Input: <u>1</u>

=== KMB (Kowloon Motor Bus) ===

Enter Route No. (e.g. 74K) (Type 'b' to back, 'q' to quit):
> Input: <u>1A</u>

Select Direction for Route 1A:
1. To STAR FERRY (from SAU MAU PING (CENTRAL)) [Type 1]
2. To SAU MAU PING (CENTRAL) (from STAR FERRY) [Type 1]

Select Index (Type 'b' to back, 'q' to quit):
> Input: <u>99</u>

Please enter a number between 1 and 2.
Select Index (Type 'b' to back, 'q' to quit):
> Input: <u>b</u>

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 3](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%203.png) 

### Test Case 4: Navigation and Auto-Refresh (Usability)
**Objective:** Verify that the user can seamlessly refresh the live data, return to previous menus, and safely exit the application.

**Steps for Instructor:** From the ETA display table, press `Enter` to refresh, then type `b` to go back, and `q` to quit.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

Press Enter to refresh, 'b' to go back, 'q' to quit.
> Input: <u>1</u>

=== KMB (Kowloon Motor Bus) ===

Enter Route No. (e.g. 74K) (Type 'b' to back, 'q' to quit): 
> Input: <u>1A</u>

Select Direction for Route 1A:
1. To STAR FERRY (from SAU MAU PING (CENTRAL)) [Type 1]
2. To SAU MAU PING (CENTRAL) (from STAR FERRY) [Type 1]

Select Index (Type 'b' to back, 'q' to quit):
> Input: <u>1</u>

Save this search to favorites? (y/n):
> Input: <u>n</u>

Stops List:
 1. SAU MAU PING (CENTRAL) (KT975) (中秀茂坪 (KT975))
 2. SAU ON HOUSE (KT390) (秀安樓 (KT390))
 3. SAU MING HOUSE (KT393) (秀明樓 (KT393))
 4. LEUNG SHEK CHEE COLLEGE (KT512) (梁式芝書院 (KT512))
 5. HIU LAI COURT (KT513) (曉麗苑 (KT513))
 6. CHEUNG WO COURT (KT533) (祥和苑 (KT533))
 7. WO LOK ESTATE (KT537) (和樂邨 (KT537))
 8. YUE MAN SQUARE (KT557) (裕民坊 (KT557))
 9. KWUN TONG BBI - MILLENNIUM CITY (KT637) (觀塘轉車站 - 創紀之城 (KT637))
10. TING FU STREET, KWUN TONG (KT646) (觀塘定富街 (KT646))
11. LOWER NGAU TAU KOK ESTATE (KT654) (牛頭角下邨 (KT654))
12. TELFORD GARDENS (KT657) (德福花園 (KT657))
13. KOWLOON BAY  STATION (KT671) (九龍灣站 (KT671))
14. KAI YIP ESTATE (KT683) (啟業邨 (KT683))
15. RICHLAND GARDENS (WT692) (麗晶花園 (WT692))
16. RHYTHM GARDEN (WT695) (采頤花園 (WT695))
17. THE LATITUDE (WT698) (譽．港灣 (WT698))
18. KOWLOON CITY BBI - REGAL ORIENTAL HOTEL (KC709) (九龍城轉車站-富豪東方酒店)
19. HAU WONG ROAD (KC735) (侯王道 (KC735))
20. LA SALLE ROAD (KC738) (喇沙利道 (KC738))
21. EARL STREET (KC740) (伯爵街 (KC740))
22. KNIGHT STREET (KC742) (勵德街 (KC742))
23. DIOCESAN BOYS' SCHOOL, PRINCE EDWARD ROAD WEST (拔萃男書院,太子道西 (KC743))
24. HEEP WOH PRIMARY SCHOOL, MOKO (MK750) (協和小學, MOKO (MK750))
25. PRINCE EDWARD STATION, FLOWER MARKET (MK751) (太子站, 旺角花墟 (MK751))
26. NELSON STREET MONG KOK (MK515) (旺角奶路臣街 (MK515))
27. SOY STREET MONG KOK (MK523) (旺角豉油街 (MK523))
28. WING SING LANE YAU MA TEI (YT542) (油麻地永星里 (YT542))
29. CHEONG LOK STREET YAU MA TEI (YT552) (油麻地長樂街 (YT552))
30. TAK SHING STREET TSIM SHA TSUI (YT555) (尖沙咀德成街 (YT555))
31. CAMERON ROAD, KOWLOON MOSQUE (YT560) (金馬倫道,清真寺 (YT560))
32. TSIM SHA TSUI BBI - MIDDLE ROAD (YT562) (尖沙咀轉車站 - 中間道 (YT562))
33. HONG KONG CULTURAL CENTRE (YT634) (香港文化中心 (YT634))
34. STAR FERRY, HARBOUR CITY (YT901) (尖沙咀碼頭,海港城 (YT901))

Enter Stop Sequence Number (Type 'b' to back, 'q' to quit):
> Input: <u>1</u>

======== [1A] @ SAU MAU PING (CENTRAL) (KT975) (中秀茂坪 (KT975)) ======== (23:55:31)
Route    Destination    Time    Min    Remark
-------  -------------  ------  -----  -----------------------------------------
1A       STAR FERRY     -       -      The final bus has departed from this stop

Press ENTER to refresh, 'b' to back, 'q' to quit:

> Press: <u></u>

[1A] @ SAU MAU PING (CENTRAL) (KT975) (中秀茂坪 (KT975)) (23:55:43)
Route    Destination    Time    Min    Remark

1A       STAR FERRY     -       -      The final bus has departed from this stop

Press ENTER to refresh, 'b' to back, 'q' to quit:
> Input: <u>q</u>

Bye!

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 4](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%204.png) 

### Test Case 5: Favorite line function test
**Objective:** Verify that the user can directly access to the ETA of the stop saved in the favorite.

**Steps for Instructor:** Supposed saved at least one line in the favorite already, press 5 in the main menu to access all lines in favorite and enter the index to access it directly.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

Press Enter to refresh, 'b' to go back, 'q' to quit.
> Input: <u>5</u>

=== Favorites ===
1. KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY  [saved: 2026-04-02 00:22:23]

Options:
  Enter number to view real-time ETA
  d - Delete a favorite
  b - Back to main menu

Select: 1

======== [LIVE] KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY ======== (00:22:40)
Route    Destination    Time    Min    Remark

1A       STAR FERRY     -       -      The final bus has departed from this stop

Press ENTER to refresh, 'b' to back, 'q' to quit: 
> Input: q

Bye!

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 5](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%205.png) 

### Test Case 6: History test
**Objective:** Verify that the user can directly access to the ETA of the stop saved in the history.

**Steps for Instructor:** Supposed saved at least one line in the history already, press 6 in the main menu to access all lines in history and enter the index to access it directly.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

Press Enter to refresh, 'b' to go back, 'q' to quit.
> Input: <u>6</u>

=== Search History ===
1. KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY  [time: 2026-04-02 00:22:21]

Options:
  Enter number to view real-time ETA
  c - Clear all history
  b - Back to main menu

Select: 1

======== [LIVE] KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY ======== (00:27:15)
Route    Destination    Time    Min    Remark
-------  -------------  ------  -----  --------
1A       STAR FERRY     -       -

Press ENTER to refresh, 'b' to back, 'q' to quit: q

Bye!

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 6](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%206.png) 

### Test Case 7: History test(boundary case)
**Objective:** Verify that there's no error when user input invalid option.

**Steps for Instructor:**  Input whatever he/she want in history function.

HK Public Transport ETA CLI (English)

[1]. KMB (Kowloon Motor Bus)

[2]. Citybus

[3]. GMB (Green Minibus)

[4]. MTR (Mass Transit Railway)

[5]. Favorites

[6]. History

[q]. Quit

Select:

Press Enter to refresh, 'b' to go back, 'q' to quit.
> Input: <u>6</u>

=== Search History ===
1. KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY  [time: 2026-04-02 00:22:21]

Options:
  Enter number to view real-time ETA
  c - Clear all history
  b - Back to main menu

Select: 
> Input: 2

Invalid index. Please select 1-1.

=== Search History ===
1. KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY  [time: 2026-04-02 00:22:21]

Options:
  Enter number to view real-time ETA
  c - Clear all history
  b - Back to main menu

Select: 
> Input: vv

Invalid input.

=== Search History ===
1. KMB 1A @ SAU ON HOUSE (KT390) (秀安樓 (KT390)) -> STAR FERRY  [time: 2026-04-02 00:22:21]

Options:
  Enter number to view real-time ETA
  c - Clear all history
  b - Back to main menu

Select: 
> Input: b

![Screenshot of terminal running the HK Transport ETA CLI, showing the test case 7](https://github.com/herolch07/int2067_eta_system/blob/main/test%20case%207.png) 

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
