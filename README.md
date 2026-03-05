
```markdown
# 🚀 Ultimate Disk Space Analyzer

🌍 *[Lue suomeksi alhaalta](#-levytilan-analysoija-ultimate-suomeksi)*

A lightning-fast, GUI-based desktop application built with Python and Tkinter to help you find and manage space-hogging files and folders. Highly optimized for modern NVMe and SSD drives.

## ✨ Features
* **Blazing Fast Scanning:** Uses Python's `os.scandir()` instead of traditional `os.walk()`, allowing the program to scan up to 25,000+ items per second on modern NVMe drives.
* **Modern GUI & Live Stats:** Built with `tkinter.ttk` for a native Windows look. Features a real-time statistics panel showing elapsed time, items scanned, and scanning speed.
* **Smart Subfolder Filtering:** Automatically hides nested subfolders if their parent folder is already in the results, keeping your report clean and readable.
* **File Type Filters:** Search specifically for Videos, Installers, Archives, or Images.
* **Excel / CSV Export:** Automatically saves the results as a `.csv` file with a timestamp and opens it automatically upon completion.
* **Memory Function:** Remembers your last used save directory using a local JSON config file.
* **Safe & Threaded:** Runs the heavy scanning in a separate background thread to keep the UI responsive. Can be cancelled mid-scan while still saving the partial results.

## 🛠️ Requirements
* Python 3.8 or newer
* Standard Python libraries only (no external `pip` packages required for the source code to run).

## 🚀 How to Run

**1. Run as a Python script:**
```bash
python isot_tiedostot.py

```

**2. Compile into a standalone Windows `.exe`:**
You can easily turn this tool into a standalone executable that works on any Windows PC without requiring Python installation.

```bash
# Install PyInstaller
python -m pip install pyinstaller

# Compile the code
python -m PyInstaller --noconsole --onefile --name "Disk Space Analyzer" isot_tiedostot.py

```

The compiled `.exe` will be located in the newly created `dist` folder.

---

# 🇫🇮 Levytilan Analysoija Ultimate (Suomeksi)

Salamannopea, graafisella käyttöliittymällä varustettu Python-työpöytäsovellus, joka auttaa löytämään tietokoneen tilaa vievät tiedostot ja kansiot. Optimoitu erityisesti nykyaikaisille NVMe- ja SSD-levyille.

## ✨ Ominaisuudet

* **Huippunopea skannaus:** Hyödyntää Pythonin `os.scandir()`-metodia perinteisen `os.walk()`-metodin sijaan. Mahdollistaa jopa yli 25 000 kohteen skannaamisen sekunnissa NVMe-levyillä.
* **Moderni käyttöliittymä ja live-tilastot:** Rakennettu `tkinter.ttk`-kirjastolla natiivin Windows-ulkoasun saavuttamiseksi. Näyttää reaaliaikaisesti kuluneen ajan, skannattujen kohteiden määrän ja nopeuden.
* **Älykäs suodatus:** Piilottaa tuloksista sisäkkäiset alikansiot, jos niiden isäntäkansio on jo listalla. Pitää raportin selkeänä.
* **Tiedostotyyppien suodattimet:** Etsi pelkkiä videoita, asennuspaketteja, pakattuja tiedostoja tai kuvia.
* **Excel / CSV -vienti:** Tallentaa tulokset automaattisesti kellonajalla varustettuun `.csv`-tiedostoon ja avaa sen heti skannauksen päätyttyä.
* **Asetusten muistaminen:** Ohjelma muistaa viimeksi käytetyn tallennuskansion paikallisen JSON-tiedoston avulla.
* **Säikeistetty ja turvallinen:** Skannaus tapahtuu taustasäikeessä, joten käyttöliittymä ei jäädy. Skannauksen voi keskeyttää napista, ja ohjelma näyttää siihen mennessä löydetyt tulokset.

## 🛠️ Vaatimukset

* Python 3.8 tai uudempi
* Käyttää vain Pythonin vakiokirjastoja (ei vaadi erillisiä asennuksia lähdekoodin ajamiseen).

## 🚀 Käyttöohjeet

**1. Ajaminen Python-skriptinä:**

```bash
python isot_tiedostot.py

```

**2. Kääntäminen itsenäiseksi `.exe`-ohjelmaksi:**
Voit kääntää ohjelman `.exe`-tiedostoksi, jota voi ajaa millä tahansa Windows-koneella ilman Pythonin asennusta.

```bash
# Asenna PyInstaller
python -m pip install pyinstaller

# Käännä ohjelma
python -m PyInstaller --noconsole --onefile --name "Levytilan Analysoija" isot_tiedostot.py

```

Valmis `.exe`-ohjelma löytyy automaattisesti luodusta `dist`-kansiosta.

---

*Created by Pastorilaine and Gemini*


