# PyDMS - Dokumentenmanagement mit OCR und PDF-Verarbeitung

Dieses Python-Skript automatisiert die Texterkennung (OCR) und die Umwandlung von PDFs in durchsuchbare PDFs. Es überwacht einen Ordner auf neue PDFs, extrahiert relevante Informationen mithilfe von GPT, und speichert die verarbeiteten PDFs in einem definierten Ordner.

## Voraussetzungen

Bevor du das Skript ausführst, stelle sicher, dass folgende Programme und Python-Pakete installiert sind:

### 1. **Ghostscript**:
Ghostscript ist notwendig, damit `OCRmyPDF` korrekt funktioniert. Installiere Ghostscript und füge es zu deinem `PATH` hinzu.

- **Download**: [Ghostscript Download](https://www.ghostscript.com/download/gsdnld.html)
- Installiere Ghostscript und füge den Installationspfad zu deinem System-PATH hinzu (z.B. `C:\Program Files\gs\gs9.55.0\bin`).

### 2. **Tesseract-OCR**:
Tesseract ist die OCR-Engine, die von `OCRmyPDF` verwendet wird.

- **Download**: [Tesseract-OCR Download](https://github.com/tesseract-ocr/tesseract)
- Installiere Tesseract und füge den Installationspfad zu deinem System-PATH hinzu (z.B. `C:\Program Files\Tesseract-OCR`).
- Stelle sicher, dass das deutsche Sprachpaket installiert ist:
  ```bash
  tesseract --list-langs
  ```
  Wenn `deu` nicht aufgelistet ist, lade es [hier](https://github.com/tesseract-ocr/tessdata) herunter und füge es in den `tessdata`-Ordner von Tesseract hinzu.

### 3. **Python-Pakete**

Folgende Python-Pakete müssen installiert werden. Verwende den Befehl `pip install`, um sie zu installieren:

```bash
pip install ocrmypdf pytesseract openai watchdog PyMuPDF
```

### Zusammenfassung der zu installierenden Abhängigkeiten:
- **Ghostscript**
- **Tesseract-OCR** (inkl. deutschem Sprachpaket)
- Python-Pakete:
  - `ocrmypdf`
  - `pytesseract`
  - `openai`
  - `watchdog`
  - `PyMuPDF`

## Installation

1. Klone dieses Repository:
   ```bash
   git clone https://github.com/dein-benutzername/pyDMS.git
   ```

2. Installiere die oben aufgeführten Abhängigkeiten.

3. Hinterlege deinen **OpenAI API-Schlüssel** in der Datei `openaikey.py`, indem du ihn in folgender Struktur speicherst:
   ```python
   # openaikey.py
   api_key = "dein-openai-api-schlüssel"
   ```

4. Starte das Skript:
   ```bash
   python main.py
   ```

## Funktionsweise

- Das Skript überwacht den Ordner `D:\PyDMS\New` auf neue PDFs.
- Sobald eine PDF erkannt wird, wird eine Texterkennung (OCR) mithilfe von Tesseract und OCRmyPDF durchgeführt.
- Die extrahierten Informationen (Datum, Absender, Grund) werden mit GPT analysiert.
- Die durchsuchbare PDF wird im Ordner `D:\PyDMS\Processed` gespeichert.
- Die Originaldatei wird in den Ordner `D:\PyDMS\Archive` verschoben.

## Konfiguration

1. Passe den überwachten Ordner, den Output-Ordner sowie den Archiv-Ordner im Skript an:
   - Überwachter Ordner: `D:\PyDMS\New`
   - Verarbeiteter Output: `D:\PyDMS\Processed`
   - Archiv: `D:\PyDMS\Archive`

2. **Erstelle manuell einen `Temp`-Ordner** im gleichen Verzeichnis, in dem sich auch der Ordner `New` befindet. Dieser wird benötigt, um temporär Dateien während der Verarbeitung zu speichern.

## Unterstützung und Probleme

Falls du auf Probleme stößt, öffne bitte ein Issue in diesem Repository.
