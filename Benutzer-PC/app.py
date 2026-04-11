import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tkinter import Tk, StringVar, messagebox
from tkinter import ttk

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
EXAMPLE_CONFIG_PATH = APP_DIR / "config.example.json"
LOG_PATH = APP_DIR / "benutzer_pc.log"
HISTORY_PATH = APP_DIR / "last_ids.json"


@dataclass
class AppConfig:
    rustdesk_executable: str = "bin/rustdesk.exe"
    connect_args_prefix: list[str] = None
    remember_last_ids: bool = True
    max_history_entries: int = 10

    def __post_init__(self) -> None:
        if self.connect_args_prefix is None:
            self.connect_args_prefix = ["--connect"]


def setup_logging() -> None:
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        logging.warning("config.json fehlt, nutze Standardwerte.")
        return AppConfig()

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logging.error("Konfiguration konnte nicht geladen werden: %s", exc)
        messagebox.showerror(
            "Konfigurationsfehler",
            "Die Datei config.json ist ungültig. Es werden Standardwerte verwendet.",
        )
        return AppConfig()

    return AppConfig(
        rustdesk_executable=data.get("rustdesk_executable", "bin/rustdesk.exe"),
        connect_args_prefix=data.get("connect_args_prefix", ["--connect"]),
        remember_last_ids=bool(data.get("remember_last_ids", True)),
        max_history_entries=int(data.get("max_history_entries", 10)),
    )


def load_history() -> list[str]:
    if not HISTORY_PATH.exists():
        return []
    try:
        raw = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(raw, list):
        return [str(entry) for entry in raw if str(entry).strip()]
    return []


def save_history(entries: list[str]) -> None:
    try:
        HISTORY_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        logging.error("Verlauf konnte nicht gespeichert werden: %s", exc)


class BenutzerPcApp:
    def __init__(self, root: Tk, config: AppConfig) -> None:
        self.root = root
        self.config = config

        self.status_text = StringVar(value="Bereit")
        self.id_input = StringVar()

        self.history = load_history() if self.config.remember_last_ids else []

        self._build_gui()

    def _build_gui(self) -> None:
        self.root.title("Benutzer-PC Support Controller")
        self.root.geometry("620x360")
        self.root.resizable(False, False)

        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="RustDesk Steuerung (Benutzer-PC)", font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        notice = "Diese App steuert nur freigegebene Ziel-PCs. Eine Sitzung erfordert die Zustimmung am Ziel-PC."
        ttk.Label(frame, text=notice, wraplength=580, foreground="#0A4D8C").pack(anchor="w", pady=(0, 12))

        entry_row = ttk.Frame(frame)
        entry_row.pack(fill="x", pady=6)
        ttk.Label(entry_row, text="Ziel-ID:", width=14).pack(side="left")
        entry = ttk.Entry(entry_row, textvariable=self.id_input, width=35)
        entry.pack(side="left", padx=(0, 10))
        entry.focus_set()

        self.connect_btn = ttk.Button(entry_row, text="Verbinden", command=self.connect_to_target)
        self.connect_btn.pack(side="left")

        status_row = ttk.Frame(frame)
        status_row.pack(fill="x", pady=8)
        ttk.Label(status_row, text="Status:", width=14).pack(side="left")
        ttk.Label(status_row, textvariable=self.status_text).pack(side="left")

        ttk.Label(frame, text="Letzte Ziel-IDs (lokal):").pack(anchor="w", pady=(14, 6))
        self.history_box = ttk.Combobox(frame, values=self.history, width=35)
        self.history_box.pack(anchor="w")
        self.history_box.bind("<<ComboboxSelected>>", self.use_selected_history)

        ttk.Button(frame, text="Beenden", command=self.root.destroy).pack(anchor="e", pady=(24, 0))

    def rustdesk_path(self) -> Path:
        return (APP_DIR / self.config.rustdesk_executable).resolve()

    def use_selected_history(self, _event=None) -> None:
        selected = self.history_box.get().strip()
        if selected:
            self.id_input.set(selected)

    def connect_to_target(self) -> None:
        target_id = self.id_input.get().strip()
        if not target_id:
            messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie eine Ziel-ID ein.")
            return

        binary = self.rustdesk_path()
        if not binary.exists():
            self.status_text.set("RustDesk fehlt")
            messagebox.showerror(
                "RustDesk fehlt",
                f"RustDesk wurde nicht gefunden:\n{binary}\n\n"
                "Bitte die offizielle rustdesk.exe in den bin-Ordner kopieren.",
            )
            logging.warning("RustDesk-Datei fehlt: %s", binary)
            return

        cmd = [str(binary), *self.config.connect_args_prefix, target_id]
        try:
            subprocess.Popen(cmd)
            self.status_text.set(f"Verbindungsversuch zu {target_id} gestartet")
            logging.info("Verbindungsversuch gestartet: %s", cmd)
            self._remember_id(target_id)
        except OSError as exc:
            self.status_text.set("Verbindung fehlgeschlagen")
            logging.error("RustDesk konnte nicht gestartet werden: %s", exc)
            messagebox.showerror("Startfehler", f"RustDesk konnte nicht gestartet werden:\n{exc}")

    def _remember_id(self, target_id: str) -> None:
        if not self.config.remember_last_ids:
            return

        deduped = [target_id] + [existing for existing in self.history if existing != target_id]
        self.history = deduped[: max(1, self.config.max_history_entries)]
        self.history_box["values"] = self.history
        save_history(self.history)


def ensure_example_config_exists() -> None:
    if EXAMPLE_CONFIG_PATH.exists():
        return

    sample = {
        "rustdesk_executable": "bin/rustdesk.exe",
        "connect_args_prefix": ["--connect"],
        "remember_last_ids": True,
        "max_history_entries": 10,
    }
    EXAMPLE_CONFIG_PATH.write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    setup_logging()
    ensure_example_config_exists()

    root = Tk()
    config = load_config()
    BenutzerPcApp(root, config)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
