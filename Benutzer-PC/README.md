# Benutzer-PC (Supporter/Controller)

Diese Anwendung ist ein **sichtbarer Python-Wrapper** für RustDesk im Supporter-Kontext.

## Zweck

- Eingabe einer Ziel-ID
- Start eines RustDesk-Verbindungsversuchs zum Ziel-PC
- Optionale lokale Historie zuletzt genutzter Ziel-IDs

## Sicherheitseigenschaften

- Keine Server-Komponente.
- Keine versteckten Funktionen.
- Keine Speicherung von Passwörtern im Klartext.
- Nur minimales lokales Logging ohne sensible Inhalte.
- Steuerung nur von freigegebenen Ziel-PCs über legitimen RustDesk-Workflow.

## Ordnerinhalt

- `app.py` – GUI und Verbindungsstart
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

- **Ziel-ID**: ID des zu unterstützenden Ziel-PCs
- **Verbinden**: startet RustDesk mit Ziel-ID
- **Status**: zeigt den aktuellen Zustand
- **Letzte Ziel-IDs**: lokale, optionale Verlaufsliste (`last_ids.json`)

## Rollenmodell

Diese App dient nur zur Verbindung auf einen freigegebenen Ziel-PC.
Die Gegenrichtung wird nicht von dieser App bereitgestellt; die Gegenrolle liegt im separaten Ordner `Ziel-PC/`.
