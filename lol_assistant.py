import requests
import urllib3
import time
import threading
import tkinter as tk

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GUI_DATA = {
    "hedef_cs": 0,
    "esyalar": [],
    "ejder_zaman": 0,
    "baron_zaman": 0,
    "oyun_suresi": 0
}

def get_all_items_from_ddragon():
    try:
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        latest_version = requests.get(versions_url).json()[0]
        items_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/tr_TR/item.json"
        items_data = requests.get(items_url).json()

        item_db = {}
        for item_id, info in items_data['data'].items():
            item_db[int(item_id)] = {'name': info['name'], 'price': info['gold']['total']}
        return item_db
    except:
        return {}

def minyon_kocu_hesapla(oyun_suresi_saniye, secilen_rol):
    if oyun_suresi_saniye < 70: return 0
    hedefler = {"TOP": 9.0, "MID": 8.0, "ADC": 9.0, "JUNGLE": 6.0, "SUPPORT": 1.0}
    return int(((oyun_suresi_saniye - 90) / 60.0) * hedefler.get(secilen_rol, 8.0))

def backend_loop(oyuncu_ismi, secilen_rol):
    item_db = get_all_items_from_ddragon()
    inventory_state = {}
    processed_events = set()

    dragon_60s_alerted = False
    dragon_20s_alerted = False
    baron_60s_alerted = False
    baron_20s_alerted = False

    url_player = "https://127.0.0.1:2999/liveclientdata/playerlist"
    url_stats = "https://127.0.0.1:2999/liveclientdata/gamestats"
    url_events = "https://127.0.0.1:2999/liveclientdata/eventdata"

    while True:
        try:
            p_res = requests.get(url_player, verify=False, timeout=2)
            s_res = requests.get(url_stats, verify=False, timeout=2)
            e_res = requests.get(url_events, verify=False, timeout=2)

            if p_res.status_code == 200 and s_res.status_code == 200:
                players = p_res.json()
                oyun_suresi = s_res.json().get('gameTime', 0)
                events = e_res.json().get('Events', [])

                GUI_DATA["oyun_suresi"] = oyun_suresi
                GUI_DATA["hedef_cs"] = minyon_kocu_hesapla(oyun_suresi, secilen_rol)

                if 0 < oyun_suresi < 300 and GUI_DATA["ejder_zaman"] == 0:
                    GUI_DATA["ejder_zaman"] = 300

                if 0 < oyun_suresi < 1200 and GUI_DATA["baron_zaman"] == 0:
                    GUI_DATA["baron_zaman"] = 1200

                for player in players:
                    s_name = player['summonerName']
                    c_items = [i.get('itemID') for i in player.get('items', [])]

                    if s_name not in inventory_state:
                        inventory_state[s_name] = c_items
                        continue

                    old = inventory_state[s_name]
                    temp = old.copy()
                    new_purchases = [i for i in c_items if not (i in temp and not temp.remove(i))]

                    for nid in new_purchases:
                        info = item_db.get(nid, {'name': 'Bilinmeyen', 'price': 0})
                        metin = f"{s_name.split('#')[0]} -> {info['name']}"

                        GUI_DATA["esyalar"].append({"metin": metin, "fiyat": info['price']})
                        if len(GUI_DATA["esyalar"]) > 5:
                            GUI_DATA["esyalar"].pop(0)

                    inventory_state[s_name] = c_items

                for event in events:
                    ev_id = event.get('EventID')
                    if ev_id not in processed_events:
                        processed_events.add(ev_id)
                        name = event.get('EventName')
                        time_val = event.get('EventTime', 0)

                        if name == 'DragonKill':
                            GUI_DATA["ejder_zaman"] = time_val + 300
                            dragon_60s_alerted = False
                            dragon_20s_alerted = False
                        elif name == 'BaronKill':
                            GUI_DATA["baron_zaman"] = time_val + 360
                            baron_60s_alerted = False
                            baron_20s_alerted = False

                if GUI_DATA["ejder_zaman"] > 0:
                    kalan_ejder = GUI_DATA["ejder_zaman"] - oyun_suresi
                    if not dragon_60s_alerted and 20 < kalan_ejder <= 60:
                        print("\n[ALARM] Ejderhanın doğmasına son 1 dakika!")
                        dragon_60s_alerted = True
                    elif not dragon_20s_alerted and 0 < kalan_ejder <= 20:
                        print("\n[ALARM] Ejderhanın doğmasına son 20 saniye!")
                        dragon_20s_alerted = True

                if GUI_DATA["baron_zaman"] > 0:
                    kalan_baron = GUI_DATA["baron_zaman"] - oyun_suresi
                    if not baron_60s_alerted and 20 < kalan_baron <= 60:
                        print("\n[ALARM] Baron'un doğmasına son 1 dakika!")
                        baron_60s_alerted = True
                    elif not baron_20s_alerted and 0 < kalan_baron <= 20:
                        print("\n[ALARM] Baron'un doğmasına son 20 saniye!")
                        baron_20s_alerted = True

        except:
            pass

        time.sleep(1)


class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LoL Canlı Maç Asistanı")
        self.root.geometry("300x250+20+20")

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.configure(bg="#1a1a1a")

        self.cs_label = tk.Label(root, text="İdeal Hedef CS: 0", font=("Helvetica", 16, "bold"), fg="#00ffcc",
                                 bg="#1a1a1a")
        self.cs_label.pack(pady=10)

        self.obj_frame = tk.Frame(root, bg="#1a1a1a")
        self.obj_frame.pack(anchor="w", padx=15, pady=5)

        self.ejder_label = tk.Label(self.obj_frame, text="Ejderha: Hazır", font=("Helvetica", 12), fg="#ff5555",
                                    bg="#1a1a1a")
        self.ejder_label.pack(anchor="w")

        self.baron_label = tk.Label(self.obj_frame, text="Baron: Hazır", font=("Helvetica", 12), fg="#aa00ff",
                                    bg="#1a1a1a")
        self.baron_label.pack(anchor="w")

        self.item_frame = tk.Frame(root, bg="#1a1a1a")
        self.item_frame.pack(anchor="w", padx=15, pady=10)
        self.item_labels = []

        self.update_ui()

    def format_zaman(self, saniye):
        if saniye <= 0: return "Hazır"
        m, s = divmod(int(saniye), 60)
        return f"{m:02d}:{s:02d}"

    def update_ui(self):
        self.cs_label.config(text=f"İdeal Hedef CS: {GUI_DATA['hedef_cs']}")

        su_an = GUI_DATA["oyun_suresi"]
        kalan_ejder = max(0, GUI_DATA["ejder_zaman"] - su_an) if GUI_DATA["ejder_zaman"] > 0 else 0
        kalan_baron = max(0, GUI_DATA["baron_zaman"] - su_an) if GUI_DATA["baron_zaman"] > 0 else 0

        self.ejder_label.config(text=f"Ejderha: {self.format_zaman(kalan_ejder)}")
        self.baron_label.config(text=f"Baron: {self.format_zaman(kalan_baron)}")

        for label in self.item_labels:
            label.destroy()
        self.item_labels.clear()

        for esya in GUI_DATA["esyalar"]:
            renk = "#ffa500" if esya["fiyat"] >= 2000 else "#888888"
            lbl = tk.Label(self.item_frame, text=esya["metin"], font=("Helvetica", 10), fg=renk, bg="#1a1a1a")
            lbl.pack(anchor="w")
            self.item_labels.append(lbl)

        self.root.after(1000, self.update_ui)

if __name__ == "__main__":
    secilen_oyuncu = ""
    secilen_rol = "MID"

    threading.Thread(target=backend_loop, args=(secilen_oyuncu, secilen_rol), daemon=True).start()

    root = tk.Tk()
    app = OverlayApp(root)
    root.mainloop()