# League of Legends: Live Match Assistant Overlay

 Built entirely in Python, this tool operates over the game (in borderless/windowed mode) to provide live tactical advantages without requiring the player to `Alt+Tab`. It seamlessly tracks objective timers, ideal minion (CS) targets based on selected roles, and enemy item power spikes.

##  Features

*   **Dynamic CS Coach:** Calculates the optimal Creep Score (CS) target in real-time based on the current game minute and the player's selected role (Top, Mid, ADC, Jungle, or Support). Displays only the target score to maintain a clean overlay.
*   **Item Power Spike Tracker:** Scans the inventories of all players in real-time. Detects newly purchased items and highlights major power spikes in orange, while displaying minor components in gray.
*   **Smart Objective Timers:** Automatically detects `DragonKill` and `BaronKill` events to start accurate countdown timers. Provides visual alerts at the 60-second and 20-second marks before an objective spawns. Includes native calculation for the initial 5-minute Dragon and 20-minute Baron spawns.
*   **Transparent Overlay UI:** Utilizes Python's Tkinter to create a transparent, borderless, "always-on-top" Heads-Up Display (HUD) that sits quietly in the corner of the screen. This part was generated with the help of artificial intelligence.

##  What I Learned Building This

This project was a massive leap in understanding how real-time applications and game states operate behind the scenes. Key takeaways include:

1.  **Local API Integration & SSL Handling:** Learned how to connect to a local game server (`127.0.0.1:2999`) and bypass self-signed SSL certificate warnings using `urllib3.disable_warnings()`.
2.  **Data Synchronization & Polling Limits:** Discovered the quirks of Riot's Live Client Data API, such as how CS updates are batched and delayed rather than updated per minion. Adapted the system architecture to focus on a continuous "Ideal Target" metric rather than real-time performance tracking.
3.  **Dynamic Database Fetching:** Instead of hardcoding hundreds of items, I wrote a script to dynamically fetch the most recent item JSON file from Riot's Data Dragon servers on startup, ensuring the tool never breaks after a game patch.

##  How to Use

1.  Clone the repository.
2.  Install the required dependencies (`pip install requests`).
3.  Ensure your League of Legends video settings are set to **Borderless** or **Windowed**.
4.  Run `main.py` once the loading screen finishes or the match starts.
5.  Edit the `secilen_oyuncu` and `secilen_rol` variables at the bottom of the script to match your Riot ID and current role.
