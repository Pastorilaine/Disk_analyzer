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
        self.root.title("Levytilan Analysoija Ultimate v4.0 (Asetukset tallentuvat)")
        self.root.geometry("850x700")
        self.root.minsize(800, 650)

        self.style = ttk.Style(self.root)
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        else:
            self.style.theme_use("clam")

        # Asetustiedoston sijainti (Käyttäjän kotikansio, esim. C:\Users\Käyttäjä\)
        self.config_file = os.path.join(
            os.path.expanduser("~"), ".levyanalysoija_config.json"
        )

        # Muuttujat
        self.target_dir = tk.StringVar(value="C:/")

        # Ladataan tallennettu kansio tai käytetään oletuksena Työpöytää
        saved_dir = self.load_settings()
        self.save_dir = tk.StringVar(value=saved_dir)

        self.open_after = tk.BooleanVar(value=True)
        self.top_x_var = tk.StringVar(value="100")
        self.filter_var = tk.StringVar(value="Kaikki (Kansiot ja Tiedostot)")
        self.hide_subfolders = tk.BooleanVar(value=True)

        self.is_scanning = False
        self.cancel_requested = False
        self.last_update_time = 0
        self.start_time = 0
        self.items_scanned = 0

        self.create_widgets()

    def load_settings(self):
        """Lataa tallennetun asetuksen JSON-tiedostosta."""
        default_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("save_dir", default_dir)
            except Exception:
                pass
        return default_dir

    def save_settings(self, new_dir):
        """Tallentaa uuden sijainnin JSON-tiedostoon."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"save_dir": new_dir}, f)
        except Exception as e:
            print(f"Asetusten tallennus epäonnistui: {e}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill="both", expand=True)

        settings_frame = ttk.LabelFrame(main_frame, text="Asetukset", padding="10")
        settings_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(settings_frame, text="Skannattava kohde:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        ttk.Entry(settings_frame, textvariable=self.target_dir, width=40).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(settings_frame, text="Selaa...", command=self.browse_target).grid(
            row=0, column=2, padx=5, pady=5
        )

        ttk.Label(settings_frame, text="Raportin tallennuskansio:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        ttk.Entry(settings_frame, textvariable=self.save_dir, width=40).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Button(settings_frame, text="Selaa...", command=self.browse_save).grid(
            row=1, column=2, padx=5, pady=5
        )

        filters = [
            "Kaikki (Kansiot ja Tiedostot)",
            "Vain Videot (.mp4, .mkv, .avi, .mov)",
            "Asennuspaketit (.exe, .msi, .iso)",
            "Paketoidut (.zip, .rar, .7z, .tar)",
            "Kuvat (.jpg, .png, .gif)",
        ]
        ttk.Label(settings_frame, text="Mitä etsitään?").grid(
            row=0, column=3, sticky="e", padx=(20, 5)
        )
        ttk.Combobox(
            settings_frame,
            textvariable=self.filter_var,
            values=filters,
            state="readonly",
            width=30,
        ).grid(row=0, column=4, pady=5)

        ttk.Label(settings_frame, text="Näytä tuloksia (Top X):").grid(
            row=1, column=3, sticky="e", padx=(20, 5)
        )
        ttk.Combobox(
            settings_frame,
            textvariable=self.top_x_var,
            values=["10", "50", "100", "500", "1000"],
            state="readonly",
            width=10,
        ).grid(row=1, column=4, sticky="w", pady=5)

        ttk.Checkbutton(
            settings_frame,
            text="Piilota sisäkkäiset alikansiot tuloksista (Älykäs suodatus)",
            variable=self.hide_subfolders,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("Tyyppi", "Nimi", "Koko", "Polku")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="extended"
        )

        self.tree.heading("Tyyppi", text="Tyyppi")
        self.tree.column("Tyyppi", width=80, anchor="center")
        self.tree.heading("Nimi", text="Tiedoston / Kansion Nimi")
        self.tree.column("Nimi", width=250)
        self.tree.heading("Koko", text="Koko (GB)")
        self.tree.column("Koko", width=80, anchor="e")
        self.tree.heading("Polku", text="Koko Sijainti")
        self.tree.column("Polku", width=350)

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

        ttk.Checkbutton(
            controls_frame,
            text="Avaa Excel/CSV automaattisesti valmistuttua",
            variable=self.open_after,
        ).pack(side="left")

        self.scan_button = ttk.Button(
            controls_frame, text="▶ Aloita skannaus", command=self.toggle_scan
        )
        self.scan_button.pack(side="right")

        self.progress = ttk.Progressbar(
            bottom_frame, orient="horizontal", mode="indeterminate"
        )
        self.progress.pack(fill="x", pady=(0, 5))

        status_container = ttk.Frame(bottom_frame)
        status_container.pack(fill="x")

        self.status_label = ttk.Label(
            status_container,
            text="Valmiina aloittamaan.",
            foreground="#555555",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        self.stats_label = ttk.Label(
            status_container,
            text="Aika: 00:00 | Skannattu: 0 kpl",
            font=("Segoe UI", 9, "bold"),
            foreground="#005a9e",
        )
        self.stats_label.pack(side="right", padx=(10, 0))

    def browse_target(self):
        folder = filedialog.askdirectory(title="Valitse skannattava kansio")
        if folder:
            self.target_dir.set(folder)

    def browse_save(self):
        folder = filedialog.askdirectory(title="Valitse tallennuskansio raportille")
        if folder:
            self.save_dir.set(folder)
            # UUSI: Tallennetaan valinta asetuksiin heti, kun se muutetaan
            self.save_settings(folder)

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

            stats_text = f"Aika: {m:02d}:{s:02d} | Skannattu: {formatted_scanned} kpl | Nopeus: {formatted_speed} kpl/s"

            self.root.after(0, self.status_label.config, {"text": display_path})
            self.root.after(0, self.stats_label.config, {"text": stats_text})

            self.last_update_time = current_time

    def toggle_scan(self):
        if self.is_scanning:
            self.cancel_requested = True
            self.scan_button.config(state="disabled", text="Peruutetaan...")
            self.status_label.config(
                text="Pysäytetään skannausta, odota hetki...", foreground="red"
            )
        else:
            self.start_scan_thread()

    def start_scan_thread(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.is_scanning = True
        self.cancel_requested = False

        self.scan_button.config(text="🛑 Peruuta", state="normal")
        self.progress.start(10)
        self.status_label.config(
            text="Valmistellaan skannausta...", foreground="#000000"
        )

        self.start_time = time.time()
        self.items_scanned = 0

        thread = threading.Thread(target=self.run_scan)
        thread.daemon = True
        thread.start()

    def filter_subfolders(self, results):
        files = [r for r in results if r[2] == "[Tiedosto]"]
        folders = [r for r in results if r[2] == "[Kansio]"]

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
        filter_choice = self.filter_var.get()
        hide_subs = self.hide_subfolders.get()

        safe_name = (
            target_path.replace(":\\", "_asema")
            .replace(":/", "_asema")
            .replace("\\", "_")
            .replace("/", "_")
            .replace(":", "")
        )
        if not safe_name:
            safe_name = "Levy"

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Levyraportti_{safe_name}_{timestamp}.csv"
        output_file = os.path.join(save_folder, filename)

        ext_filters = []
        if "Videot" in filter_choice:
            ext_filters = [".mp4", ".mkv", ".avi", ".mov"]
        elif "Asennus" in filter_choice:
            ext_filters = [".exe", ".msi", ".iso"]
        elif "Paketoidut" in filter_choice:
            ext_filters = [".zip", ".rar", ".7z", ".tar"]
        elif "Kuvat" in filter_choice:
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
                                        results.append((entry.path, sz, "[Tiedosto]"))

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
            self.root.after(0, messagebox.showerror, "Virhe", f"Tapahtui virhe:\n{e}")
            self.root.after(0, self.reset_ui)
            return

        if not ext_filters:
            for folder, sz in folder_totals.items():
                if folder != target_path:
                    if os.path.dirname(folder) == target_path and target_path == "C:\\":
                        pass
                    else:
                        results.append((folder, sz, "[Kansio]"))

        if hide_subs and not ext_filters:
            results = self.filter_subfolders(results)
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
                    writer.writerow(["Tyyppi", "Nimi", "Koko (GB)", "Polku"])
                    for path, size, type_str in top_results:
                        size_gb = size / (1024**3)
                        if size_gb > 0.001:
                            name = os.path.basename(path) or path
                            size_str = f"{size_gb:.2f}".replace(".", ",")
                            writer.writerow([type_str, name, size_str, path])

            total_time = time.time() - self.start_time
            m, s = divmod(int(total_time), 60)

            if self.cancel_requested:
                msg = f"Skannaus peruutettu. Raportti tallennettiin: {filename}"
                color = "#d97706"
            else:
                msg = f"Skannaus valmis ({m}m {s}s). Tallennettu: {filename}"
                color = "green"

            self.root.after(
                0, self.status_label.config, {"text": msg, "foreground": color}
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
                "Tallennusvirhe",
                f"Raportin tallennus epäonnistui:\n{e}",
            )

        self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.progress.stop()
        self.is_scanning = False
        self.cancel_requested = False
        self.scan_button.config(state="normal", text="▶ Aloita skannaus")


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateDiskScannerApp(root)
    root.mainloop()
