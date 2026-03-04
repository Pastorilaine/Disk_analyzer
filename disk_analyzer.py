import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import platform
import subprocess
import time
import csv
import datetime
import json


class UltimateDiskScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1050x720")
        self.root.minsize(950, 650)

        self.style = ttk.Style(self.root)
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        else:
            self.style.theme_use("clam")

        self.config_file = os.path.join(
            os.path.expanduser("~"), ".levyanalysoija_config.json"
        )

        # Sanakirja kaikille käyttöliittymän teksteille
        self.texts = {
            "fi": {
                "title": "Levytilan Analysoija Ultimate v5.0",
                "settings": "Asetukset",
                "lang_label": "Kieli / Language:",
                "target": "Skannattava kohde:",
                "browse": "Selaa...",
                "save_dir": "Raportin tallennuskansio:",
                "filter_label": "Mitä etsitään?",
                "top_x_label": "Näytä tuloksia (Top X):",
                "hide_subs": "Piilota sisäkkäiset alikansiot tuloksista (Älykäs suodatus)",
                "open_after": "Avaa Excel/CSV automaattisesti valmistuttua",
                "start": "▶ Aloita skannaus",
                "cancel": "🛑 Peruuta",
                "canceling": "Pysäytetään skannausta, odota hetki...",
                "ready": "Valmiina aloittamaan.",
                "stats_init": "Aika: 00:00 | Skannattu: 0 kpl",
                "stats_live": "Aika: {m:02d}:{s:02d} | Skannattu: {scanned} kpl | Nopeus: {speed} kpl/s",
                "msg_prep": "Valmistellaan skannausta...",
                "msg_canceled": "Skannaus peruutettu. Tallennettu: {filename}",
                "msg_done": "Skannaus valmis ({m}m {s}s). Tallennettu: {filename}",
                "err_title": "Virhe",
                "err_perms": "Käyttöoikeusvirhe",
                "ask_target": "Valitse skannattava kansio",
                "ask_save": "Valitse tallennuskansio raportille",
                "col_type": "Tyyppi",
                "col_name": "Tiedoston / Kansion Nimi",
                "col_size": "Koko (GB)",
                "col_path": "Sijainti",
                "type_folder": "[Kansio]",
                "type_file": "[Tiedosto]",
                "filters": [
                    "Kaikki (Kansiot ja Tiedostot)",
                    "Vain Videot (.mp4, .mkv, .avi)",
                    "Asennuspaketit (.exe, .msi, .iso)",
                    "Paketoidut (.zip, .rar, .7z)",
                    "Kuvat (.jpg, .png, .gif)",
                ],
            },
            "en": {
                "title": "Disk Space Analyzer Ultimate v5.0",
                "settings": "Settings",
                "lang_label": "Language / Kieli:",
                "target": "Target to scan:",
                "browse": "Browse...",
                "save_dir": "Report save folder:",
                "filter_label": "What to look for?",
                "top_x_label": "Show results (Top X):",
                "hide_subs": "Hide nested subfolders from results (Smart Filtering)",
                "open_after": "Open Excel/CSV automatically when done",
                "start": "▶ Start scan",
                "cancel": "🛑 Cancel",
                "canceling": "Stopping scan, please wait...",
                "ready": "Ready to start.",
                "stats_init": "Time: 00:00 | Scanned: 0 items",
                "stats_live": "Time: {m:02d}:{s:02d} | Scanned: {scanned} items | Speed: {speed} items/s",
                "msg_prep": "Preparing scan...",
                "msg_canceled": "Scan cancelled. Saved: {filename}",
                "msg_done": "Scan complete ({m}m {s}s). Saved: {filename}",
                "err_title": "Error",
                "err_perms": "Permission Error",
                "ask_target": "Select folder to scan",
                "ask_save": "Select save folder for report",
                "col_type": "Type",
                "col_name": "File / Folder Name",
                "col_size": "Size (GB)",
                "col_path": "Full Path",
                "type_folder": "[Folder]",
                "type_file": "[File]",
                "filters": [
                    "All (Folders and Files)",
                    "Videos Only (.mp4, .mkv, .avi)",
                    "Installers (.exe, .msi, .iso)",
                    "Archives (.zip, .rar, .7z)",
                    "Images (.jpg, .png, .gif)",
                ],
            },
        }

        # Ladataan asetukset (kieli ja tallennuskansio)
        settings = self.load_settings()
        self.lang_var = tk.StringVar(value=settings.get("lang", "fi"))
        self.save_dir = tk.StringVar(
            value=settings.get(
                "save_dir", os.path.join(os.path.expanduser("~"), "Desktop")
            )
        )

        self.target_dir = tk.StringVar(value="C:/")
        self.open_after = tk.BooleanVar(value=True)
        self.top_x_var = tk.StringVar(value="100")
        self.filter_idx = (
            0  # Seurataan suodattimen indeksiä tekstin sijaan kielen takia
        )
        self.hide_subfolders = tk.BooleanVar(value=True)

        self.is_scanning = False
        self.cancel_requested = False
        self.last_update_time = 0
        self.start_time = 0
        self.items_scanned = 0

        self.create_widgets()
        self.update_ui_language()  # Asetetaan tekstit oikealle kielelle heti alussa

    def _t(self, key):
        """Hakee oikean käännöksen sanakirjasta."""
        return self.texts[self.lang_var.get()][key]

    def load_settings(self):
        default_settings = {
            "save_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "lang": "fi",
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_settings.update(data)
            except Exception:
                pass
        return default_settings

    def save_settings(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"save_dir": self.save_dir.get(), "lang": self.lang_var.get()}, f
                )
        except Exception as e:
            print(f"Asetusten tallennus epäonnistui: {e}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill="both", expand=True)

        self.lbl_frame_settings = ttk.LabelFrame(main_frame, padding="10")
        self.lbl_frame_settings.pack(fill="x", pady=(0, 10))

        # Kielen valinta oikeaan yläkulmaan
        self.lbl_lang = ttk.Label(self.lbl_frame_settings)
        self.lbl_lang.grid(row=0, column=5, sticky="e", padx=(20, 5))
        self.cb_lang = ttk.Combobox(
            self.lbl_frame_settings,
            textvariable=self.lang_var,
            values=["fi", "en"],
            state="readonly",
            width=5,
        )
        self.cb_lang.grid(row=0, column=6, pady=5)
        self.cb_lang.bind("<<ComboboxSelected>>", self.change_language)

        self.lbl_target = ttk.Label(self.lbl_frame_settings)
        self.lbl_target.grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(self.lbl_frame_settings, textvariable=self.target_dir, width=35).grid(
            row=0, column=1, padx=5, pady=5
        )
        self.btn_browse_target = ttk.Button(
            self.lbl_frame_settings, command=self.browse_target
        )
        self.btn_browse_target.grid(row=0, column=2, padx=5, pady=5)

        self.lbl_save = ttk.Label(self.lbl_frame_settings)
        self.lbl_save.grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(self.lbl_frame_settings, textvariable=self.save_dir, width=35).grid(
            row=1, column=1, padx=5, pady=5
        )
        self.btn_browse_save = ttk.Button(
            self.lbl_frame_settings, command=self.browse_save
        )
        self.btn_browse_save.grid(row=1, column=2, padx=5, pady=5)

        self.lbl_filter = ttk.Label(self.lbl_frame_settings)
        self.lbl_filter.grid(row=0, column=3, sticky="e", padx=(20, 5))
        self.cb_filter = ttk.Combobox(
            self.lbl_frame_settings, state="readonly", width=28
        )
        self.cb_filter.grid(row=0, column=4, pady=5)
        self.cb_filter.bind("<<ComboboxSelected>>", self.update_filter_idx)

        self.lbl_topx = ttk.Label(self.lbl_frame_settings)
        self.lbl_topx.grid(row=1, column=3, sticky="e", padx=(20, 5))
        ttk.Combobox(
            self.lbl_frame_settings,
            textvariable=self.top_x_var,
            values=["10", "50", "100", "500", "1000"],
            state="readonly",
            width=8,
        ).grid(row=1, column=4, sticky="w", pady=5)

        self.chk_hide_subs = ttk.Checkbutton(
            self.lbl_frame_settings, variable=self.hide_subfolders
        )
        self.chk_hide_subs.grid(row=2, column=0, columnspan=3, sticky="w", pady=(5, 0))

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)

        self.columns = ("col0", "col1", "col2", "col3")
        self.tree = ttk.Treeview(
            table_frame, columns=self.columns, show="headings", selectmode="extended"
        )

        self.tree.column("col0", width=80, anchor="center")
        self.tree.column("col1", width=250)
        self.tree.column("col2", width=80, anchor="e")
        self.tree.column("col3", width=350)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(10, 0))

        controls_frame = ttk.Frame(bottom_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        self.chk_open_after = ttk.Checkbutton(controls_frame, variable=self.open_after)
        self.chk_open_after.pack(side="left")

        self.btn_scan = ttk.Button(controls_frame, command=self.toggle_scan)
        self.btn_scan.pack(side="right")

        self.progress = ttk.Progressbar(
            bottom_frame, orient="horizontal", mode="indeterminate"
        )
        self.progress.pack(fill="x", pady=(0, 5))

        status_container = ttk.Frame(bottom_frame)
        status_container.pack(fill="x")

        self.lbl_status = ttk.Label(
            status_container, foreground="#555555", font=("Segoe UI", 9)
        )
        self.lbl_status.pack(side="left", fill="x", expand=True)

        self.lbl_stats = ttk.Label(
            status_container, font=("Segoe UI", 9, "bold"), foreground="#005a9e"
        )
        self.lbl_stats.pack(side="right", padx=(10, 0))

    def change_language(self, event=None):
        """Kutsutaan kun kieli vaihtuu comboboxista."""
        self.save_settings()
        self.update_ui_language()

    def update_filter_idx(self, event=None):
        """Tallentaa ylös monesko filtteri on valittuna."""
        self.filter_idx = self.cb_filter.current()

    def update_ui_language(self):
        """Päivittää kaikki käyttöliittymän tekstit valitulle kielelle."""
        self.root.title(self._t("title"))
        self.lbl_frame_settings.config(text=self._t("settings"))
        self.lbl_lang.config(text=self._t("lang_label"))
        self.lbl_target.config(text=self._t("target"))
        self.btn_browse_target.config(text=self._t("browse"))
        self.lbl_save.config(text=self._t("save_dir"))
        self.btn_browse_save.config(text=self._t("browse"))
        self.lbl_filter.config(text=self._t("filter_label"))
        self.lbl_topx.config(text=self._t("top_x_label"))
        self.chk_hide_subs.config(text=self._t("hide_subs"))
        self.chk_open_after.config(text=self._t("open_after"))

        if self.is_scanning:
            self.btn_scan.config(text=self._t("cancel"))
        else:
            self.btn_scan.config(text=self._t("start"))
            self.lbl_status.config(text=self._t("ready"))
            self.lbl_stats.config(text=self._t("stats_init"))

        # Päivitetään filtterit (pidetään valittu indeksi samana)
        self.cb_filter.config(values=self._t("filters"))
        self.cb_filter.current(self.filter_idx)

        # Päivitetään taulukon otsikot
        self.tree.heading("col0", text=self._t("col_type"))
        self.tree.heading("col1", text=self._t("col_name"))
        self.tree.heading("col2", text=self._t("col_size"))
        self.tree.heading("col3", text=self._t("col_path"))

    def browse_target(self):
        folder = filedialog.askdirectory(title=self._t("ask_target"))
        if folder:
            self.target_dir.set(folder)

    def browse_save(self):
        folder = filedialog.askdirectory(title=self._t("ask_save"))
        if folder:
            self.save_dir.set(folder)
            self.save_settings()

    def update_status_text(self, current_path):
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:
            display_path = current_path
            if len(display_path) > 60:
                display_path = "..." + display_path[-57:]

            elapsed = current_time - self.start_time
            m, s = divmod(int(elapsed), 60)
            speed = int(self.items_scanned / elapsed) if elapsed > 0 else 0

            formatted_scanned = f"{self.items_scanned:,}".replace(",", " ")
            formatted_speed = f"{speed:,}".replace(",", " ")

            # Haetaan live-statistiikan teksti oikealla kielellä ja muotoillaan se
            stats_text = self._t("stats_live").format(
                m=m, s=s, scanned=formatted_scanned, speed=formatted_speed
            )

            self.root.after(0, self.lbl_status.config, {"text": display_path})
            self.root.after(0, self.lbl_stats.config, {"text": stats_text})

            self.last_update_time = current_time

    def toggle_scan(self):
        if self.is_scanning:
            self.cancel_requested = True
            self.btn_scan.config(state="disabled", text=self._t("canceling"))
            self.lbl_status.config(text=self._t("canceling"), foreground="red")
        else:
            self.start_scan_thread()

    def start_scan_thread(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.is_scanning = True
        self.cancel_requested = False

        self.btn_scan.config(text=self._t("cancel"), state="normal")
        self.progress.start(10)
        self.lbl_status.config(text=self._t("msg_prep"), foreground="#000000")

        self.start_time = time.time()
        self.items_scanned = 0

        thread = threading.Thread(target=self.run_scan)
        thread.daemon = True
        thread.start()

    def filter_subfolders(self, results, t_file, t_folder):
        files = [r for r in results if r[2] == t_file]
        folders = [r for r in results if r[2] == t_folder]

        folders.sort(key=lambda x: len(x[0]))

        filtered_folders = []
        for current_folder in folders:
            current_path = current_folder[0]
            is_subfolder = False
            for parent_folder in filtered_folders:
                parent_path = parent_folder[0]
                if (
                    current_path.startswith(parent_path + os.sep)
                    or current_path == parent_path
                ):
                    is_subfolder = True
                    break

            if not is_subfolder:
                filtered_folders.append(current_folder)

        final_results = files + filtered_folders
        final_results.sort(key=lambda x: x[1], reverse=True)
        return final_results

    def run_scan(self):
        target_path = os.path.normpath(self.target_dir.get())
        save_folder = self.save_dir.get()
        top_x = int(self.top_x_var.get())
        hide_subs = self.hide_subfolders.get()

        # Haetaan oikeat termit kielen mukaan raporteille
        t_folder = self._t("type_folder")
        t_file = self._t("type_file")

        safe_name = (
            target_path.replace(":\\", "_drive")
            .replace(":/", "_drive")
            .replace("\\", "_")
            .replace("/", "_")
            .replace(":", "")
        )
        if not safe_name:
            safe_name = "Disk"

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"DiskReport_{safe_name}_{timestamp}.csv"
        output_file = os.path.join(save_folder, filename)

        # Määritetään etsittävät päätteet valitun indeksin mukaan (indeksi ei riipu kielestä!)
        ext_filters = []
        if self.filter_idx == 1:
            ext_filters = [".mp4", ".mkv", ".avi", ".mov"]
        elif self.filter_idx == 2:
            ext_filters = [".exe", ".msi", ".iso"]
        elif self.filter_idx == 3:
            ext_filters = [".zip", ".rar", ".7z", ".tar"]
        elif self.filter_idx == 4:
            ext_filters = [".jpg", ".jpeg", ".png", ".gif"]

        skip_folders = [
            "c:\\windows",
            "c:\\$recycle.bin",
            "c:\\system volume information",
            "c:\\pagefile.sys",
            "c:\\hiberfil.sys",
        ]

        results = []
        folder_totals = {target_path: 0}
        stack = [target_path]

        try:
            while stack:
                if self.cancel_requested:
                    break

                current_path = stack.pop()
                self.update_status_text(current_path)

                try:
                    with os.scandir(current_path) as it:
                        for entry in it:
                            if self.cancel_requested:
                                break

                            try:
                                if entry.is_dir(follow_symlinks=False):
                                    if entry.path.lower() not in skip_folders:
                                        stack.append(entry.path)
                                        folder_totals[entry.path] = 0
                                        self.items_scanned += 1

                                elif entry.is_file(follow_symlinks=False):
                                    self.items_scanned += 1
                                    sz = entry.stat(follow_symlinks=False).st_size

                                    if not ext_filters or any(
                                        entry.name.lower().endswith(ext)
                                        for ext in ext_filters
                                    ):
                                        results.append((entry.path, sz, t_file))

                                    if not ext_filters:
                                        curr = current_path
                                        while curr.startswith(target_path):
                                            folder_totals[curr] = (
                                                folder_totals.get(curr, 0) + sz
                                            )
                                            parent = os.path.dirname(curr)
                                            if parent == curr:
                                                break
                                            curr = parent
                            except OSError:
                                pass
                except OSError:
                    pass

        except Exception as e:
            self.root.after(
                0, messagebox.showerror, self._t("err_title"), f"Error:\n{e}"
            )
            self.root.after(0, self.reset_ui)
            return

        if not ext_filters:
            for folder, sz in folder_totals.items():
                if folder != target_path:
                    if os.path.dirname(folder) == target_path and target_path == "C:\\":
                        pass
                    else:
                        results.append((folder, sz, t_folder))

        if hide_subs and not ext_filters:
            results = self.filter_subfolders(results, t_file, t_folder)
        else:
            results.sort(key=lambda x: x[1], reverse=True)

        top_results = results[:top_x]

        try:
            for path, size, type_str in top_results:
                size_gb = size / (1024**3)
                if size_gb > 0.001:
                    name = os.path.basename(path) or path
                    self.root.after(
                        0,
                        self.tree.insert,
                        "",
                        "end",
                        values=(type_str, name, f"{size_gb:.2f}", path),
                    )

            if top_results:
                with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f, delimiter=";")
                    writer.writerow(
                        [
                            self._t("col_type"),
                            self._t("col_name"),
                            self._t("col_size"),
                            self._t("col_path"),
                        ]
                    )
                    for path, size, type_str in top_results:
                        size_gb = size / (1024**3)
                        if size_gb > 0.001:
                            name = os.path.basename(path) or path
                            size_str = f"{size_gb:.2f}".replace(".", ",")
                            writer.writerow([type_str, name, size_str, path])

            total_time = time.time() - self.start_time
            m, s = divmod(int(total_time), 60)

            if self.cancel_requested:
                msg = self._t("msg_canceled").format(filename=filename)
                color = "#d97706"
            else:
                msg = self._t("msg_done").format(m=m, s=s, filename=filename)
                color = "green"

            self.root.after(
                0, self.lbl_status.config, {"text": msg, "foreground": color}
            )

            if self.open_after.get() and top_results:
                if platform.system() == "Windows":
                    os.startfile(output_file)
                else:
                    subprocess.call(["open", output_file])

        except Exception as e:
            self.root.after(
                0,
                messagebox.showerror,
                self._t("err_title"),
                self._t("err_save").format(e=e),
            )

        self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.progress.stop()
        self.is_scanning = False
        self.cancel_requested = False
        self.btn_scan.config(state="normal", text=self._t("start"))


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateDiskScannerApp(root)
    root.mainloop()
