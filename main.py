import os
import time
import ocrmypdf
import fitz  # PyMuPDF für Text-Extraktion
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import openai
import shutil
import re
from openaikey import openaikey

# OpenAI API-Schlüssel
openai.api_key = openaikey

# Funktion zur Bereinigung des Dateinamens
def sanitize_filename(filename):
    # Ersetze alle ungültigen Zeichen durch einen Unterstrich
    return re.sub(r'[\/:*?"<>|]', '_', filename)

# Funktion, die darauf wartet, dass die Datei nicht mehr gesperrt ist
def wait_for_file_access(file_path, timeout=10, check_interval=0.5):
    """Warte, bis die Datei zugänglich ist oder das Timeout abgelaufen ist."""
    start_time = time.time()
    while True:
        try:
            with open(file_path, 'rb'):
                break  # Wenn die Datei geöffnet werden kann, beenden wir die Schleife
        except PermissionError:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout: Die Datei {file_path} ist weiterhin gesperrt.")
            time.sleep(check_interval)

# GPT-Extraktionsfunktion, die das Datum im Format YYYY-MM-DD zurückgibt
def extract_info_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # oder gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extrahiere das Datum, den Absender und den Grund aus folgendem Text. Gib das Datum immer im Format YYYY-MM-DD zurück. Begrenze Absender und Grund auf maximal 3 sinnvolle Wörter:\n{text}"}
        ],
        max_tokens=100
    )
    return response['choices'][0]['message']['content']

# Funktion zur Extraktion von Text aus einer durchsuchbaren PDF mit PyMuPDF (fitz)
def extract_text_from_pdf(pdf_path, max_length=6000):
    doc = fitz.open(pdf_path)  # Öffne die durchsuchbare PDF
    text = ""
    for page in doc:
        text += page.get_text()  # Extrahiere den Text von jeder Seite
    doc.close()
    
    # Kürze den Text, wenn er zu lang ist
    if len(text) > max_length:
        text = text[:max_length]  # Kürze den Text auf die ersten max_length Zeichen
    return text

# Funktion, um eine durchsuchbare PDF im PDF/A-Format zu speichern
def save_searchable_pdf(pdf_path):
    # Warte, bis die Datei nicht mehr gesperrt ist
    wait_for_file_access(pdf_path)

    # Führe OCRmyPDF aus, um den Textlayer hinzuzufügen und die PDF als PDF/A zu speichern
    temp_output = pdf_path.replace("New", "Temp")  # Temporärer Output-Pfad, um den Textlayer hinzuzufügen
    ocrmypdf.ocr(pdf_path, temp_output, deskew=True, force_ocr=True, language='deu')

    # Extrahiere den Text aus der durchsuchbaren PDF
    ocr_text = extract_text_from_pdf(temp_output)

    # GPT für die Extraktion von Datum, Absender und Grund
    extracted_info = extract_info_with_gpt(ocr_text)
    
    # Annahme: GPT gibt Infos wie "Datum: 2024-01-29, Absender: Max Mustermann, Grund: Rechnung September" zurück
    lines = extracted_info.split('\n')
    
    # Extrahiere Datum, Absender und Grund
    document_date = ""
    sender = ""
    reason = ""
    
    for line in lines:
        if "Datum" in line:
            document_date = line.split(":")[1].strip()  # Das Datum kommt bereits im Format YYYY-MM-DD
        if "Absender" in line:
            sender = ' '.join(line.split(":")[1].strip().split()[:3])  # Maximal 3 Wörter
        if "Grund" in line:
            reason = ' '.join(line.split(":")[1].strip().split()[:3])  # Maximal 3 Wörter

    # Heutiges Datum
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Generiere den Dateinamen im gewünschten Format und bereinige ihn
    file_name = f"{document_date}__{today_date}__{sender}__{reason}.pdf"
    file_name = sanitize_filename(file_name)  # Bereinige den Dateinamen
    output_path = os.path.join("D:\\PyDMS\\Processed", file_name)  # Output Ordner

    # Verschiebe die durchsuchbare PDF an den endgültigen Speicherort
    shutil.move(temp_output, output_path)
    print(f"Durchsuchbare PDF wurde gespeichert als: {output_path}")

    # Nach Fertigstellung: Warte erneut auf den Dateizugriff und verschiebe die Originaldatei
    wait_for_file_access(pdf_path)
    archive_path = os.path.join("D:\\PyDMS\\Archive", os.path.basename(pdf_path))
    shutil.move(pdf_path, archive_path)
    print(f"Original PDF wurde nach {archive_path} verschoben.")

# Klasse für die Überwachung des Ordners
class Watcher:
    def __init__(self, folder_to_watch):
        self.folder_to_watch = folder_to_watch
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.folder_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        elif event.src_path.endswith(".pdf"):
            print(f"Neue Datei erkannt: {event.src_path}")
            save_searchable_pdf(event.src_path)

# Starte die Überwachung
if __name__ == "__main__":
    folder_to_watch = r"D:\PyDMS\New"  # Ordner für eingehende PDFs
    w = Watcher(folder_to_watch)
    w.run()
