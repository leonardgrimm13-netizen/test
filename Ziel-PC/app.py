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
LOG_PATH = APP_DIR / "ziel_pc.log"


@dataclass
class AppConfig:
    rustdesk_executable: str = "bin/rustdesk.exe"
    support_args: list[str] = None
    show_confirmation_dialog: bool = True

    def __post_init__(self) -> None:
        if self.support_args is None:
            self.support_args = []


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
        support_args=data.get("support_args", []),
        show_confirmation_dialog=bool(data.get("show_confirmation_dialog", True)),
    )


class ZielPcApp:
    def __init__(self, root: Tk, config: AppConfig) -> None:
        self.root = root
        self.config = config
        self.process: subprocess.Popen | None = None

        self.status_text = StringVar(value="Nicht verbunden")
        self.id_text = StringVar(value="Unbekannt")
        self.connection_text = StringVar(value="Keine aktive Sitzung")

        self._build_gui()

    def _build_gui(self) -> None:
        self.root.title("Ziel-PC Support Starter")
        self.root.geometry("600x360")
        self.root.resizable(False, False)

        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="RustDesk Empfänger (Ziel-PC)", font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        notice = (
            "Diese App erlaubt nur eingehenden Support auf diesem PC. "
            "Sie enthält absichtlich keine Funktion, um andere PCs zu steuern."
        )
        ttk.Label(frame, text=notice, wraplength=560, foreground="#8B0000").pack(anchor="w", pady=(0, 12))

        self._add_status_row(frame, "Status:", self.status_text)
        self._add_status_row(frame, "Eigene RustDesk-ID:", self.id_text)
        self._add_status_row(frame, "Verbindung:", self.connection_text)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=(20, 0))

        self.start_btn = ttk.Button(button_frame, text="Support starten", command=self.start_support)
        self.start_btn.pack(side="left", padx=(0, 10))

        self.copy_btn = ttk.Button(button_frame, text="ID kopieren", command=self.copy_id)
        self.copy_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = ttk.Button(button_frame, text="Beenden", command=self.close_app)
        self.stop_btn.pack(side="right")

    @staticmethod
    def _add_status_row(parent: ttk.Frame, label: str, value_var: StringVar) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=20).pack(side="left")
        ttk.Label(row, textvariable=value_var).pack(side="left")

    def rustdesk_path(self) -> Path:
        return (APP_DIR / self.config.rustdesk_executable).resolve()

    def start_support(self) -> None:
        if self.process and self.process.poll() is None:
            messagebox.showinfo("Info", "RustDesk läuft bereits.")
            return

        binary = self.rustdesk_path()
        if not binary.exists():
            self.status_text.set("Fehlende RustDesk-Datei")
            self.connection_text.set("Start fehlgeschlagen")
            messagebox.showerror(
                "RustDesk fehlt",
                f"RustDesk wurde nicht gefunden:\n{binary}\n\n"
                "Bitte die offizielle rustdesk.exe in den bin-Ordner kopieren.",
            )
            logging.warning("RustDesk-Datei fehlt: %s", binary)
            return

        if self.config.show_confirmation_dialog:
            ok = messagebox.askyesno(
                "Sitzung bestätigen",
                "Möchten Sie den Support-Modus jetzt starten?\n"
                "Der Support bleibt sichtbar und muss aktiv freigegeben werden.",
            )
            if not ok:
                return

        cmd = [str(binary), *self.config.support_args]
        try:
            self.process = subprocess.Popen(cmd)
            self.status_text.set("Verbunden (RustDesk gestartet)")
            self.connection_text.set("Warte auf eingehende Support-Anfrage")
            self.id_text.set("In RustDesk sichtbar")
            logging.info("RustDesk gestartet: %s", cmd)
        except OSError as exc:
            self.status_text.set("Start fehlgeschlagen")
            self.connection_text.set("Fehler beim Start")
            logging.error("RustDesk konnte nicht gestartet werden: %s", exc)
            messagebox.showerror("Startfehler", f"RustDesk konnte nicht gestartet werden:\n{exc}")

    def copy_id(self) -> None:
        current = self.id_text.get()
        if not current or current == "Unbekannt":
            messagebox.showinfo("Info", "Die RustDesk-ID ist erst nach Start in RustDesk sichtbar.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(current)
        messagebox.showinfo("Kopiert", "ID wurde in die Zwischenablage kopiert.")

    def close_app(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            logging.info("RustDesk-Prozess beendet.")
        self.root.destroy()


def ensure_example_config_exists() -> None:
    if EXAMPLE_CONFIG_PATH.exists():
        return

    sample = {
        "rustdesk_executable": "bin/rustdesk.exe",
        "support_args": [],
        "show_confirmation_dialog": True,
    }
    EXAMPLE_CONFIG_PATH.write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    setup_logging()
    ensure_example_config_exists()

    root = Tk()
    config = load_config()
    app = ZielPcApp(root, config)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
