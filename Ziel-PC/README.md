# Ziel-PC (Empfänger)

Diese Anwendung ist ein **sichtbarer Python-Wrapper** für RustDesk im Empfänger-Kontext.

## Zweck

- Startet RustDesk lokal auf dem Ziel-PC.
- Zeigt Statusinformationen in einer einfachen GUI.
- **Keine Controller-Funktionen**: Diese App kann absichtlich **keinen anderen PC steuern**.

## Sicherheitseigenschaften

- Nur sichtbare Nutzung mit GUI.
- Optionaler Bestätigungsdialog vor Sitzungsstart.
- Keine Persistenz, kein Autostart, keine Tarnung.
- Kein Download von Binärdateien aus dem Internet.
- Nur minimales lokales Logging ohne sensible Inhalte.

## Ordnerinhalt

- `app.py` – GUI und RustDesk-Startlogik
- `config.example.json` – Beispielkonfiguration
- `requirements.txt` – Abhängigkeiten (nur Standardbibliothek)
- `start.bat` – Windows-Startskript
- `bin/` – hier muss `rustdesk.exe` manuell abgelegt werden

## Voraussetzungen

- Windows mit Python 3.11+
- RustDesk-Binärdatei: `bin/rustdesk.exe`

## Einrichtung

1. Offizielle RustDesk-Version herunterladen (manuell, außerhalb dieses Projekts).
2. Datei als `bin/rustdesk.exe` in diesen Ordner legen.
3. `config.example.json` nach `config.json` kopieren und bei Bedarf anpassen.

## Start

- Doppelklick auf `start.bat`
- oder in der Konsole:

```bat
py -3 app.py
```

## GUI-Funktionen

- **Support starten**: startet RustDesk für eingehende Support-Sitzungen
- **ID kopieren**: kopiert die angezeigte RustDesk-ID (falls verfügbar)
- **Beenden**: schließt die App und beendet den gestarteten RustDesk-Prozess

## Rollenmodell

Diese App ist absichtlich auf die Ziel-PC-Rolle begrenzt.
Sie stellt **keine Eingabefelder oder Funktionen** bereit, um selbst fremde Systeme zu steuern.
Dadurch wird die Trennung gegenüber `Benutzer-PC/` technisch und organisatorisch klar umgesetzt.
