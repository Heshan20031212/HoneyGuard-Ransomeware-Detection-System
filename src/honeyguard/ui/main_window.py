"""
HoneyGuard Desktop Management Console (Main Window)
Integrates navigation rail, persistent status badges, real-time watchdog monitoring,
and full view notebooks conforming to the official Software Stack wireframes (Figures 4–7).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

from honeyguard.database.connection import is_db_connected
from honeyguard.database.repositories import DirectoryRepository, DecoyRepository, AlertRepository
from honeyguard.detection.alert_manager import AlertManager
from honeyguard.file_monitoring.event_bus import get_event_bus
from honeyguard.file_monitoring.watcher import FileSystemWatcher
from honeyguard.ui.alerts import AlertsView
from honeyguard.ui.benchmarking import BenchmarkingView
from honeyguard.ui.dashboard import DashboardView
from honeyguard.ui.decoy_manager import DecoyManagerView
from honeyguard.ui.file_monitor import FileMonitorView
from honeyguard.ui.incident_logs import IncidentLogsView
from honeyguard.ui.settings import SettingsView
from honeyguard.ui.styles import (
    apply_soc_dark_theme,
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_MONO
)
from honeyguard.utils.logger import get_logger

logger = get_logger("HoneyGuard.UI")


class HoneyGuardMainWindow(tk.Tk):
    """Primary Desktop Application Window."""

    def __init__(self):
        super().__init__()
        self.title("HoneyGuard — Honeytoken-Based Ransomware Detection & Prevention System")
        self.geometry("1280x800")
        self.minsize(1024, 680)

        # Apply SOC dark theme
        apply_soc_dark_theme(self)

        # Initialize background monitoring and detection pipeline
        self.event_bus = get_event_bus()
        self.alert_manager = AlertManager()
        self.event_bus.subscribe(self.alert_manager.process_event)
        self.alert_manager.subscribe(self._on_high_risk_alert)

        self.watcher = FileSystemWatcher()

        self._build_layout()
        self._start_system_monitoring()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        # Master Horizontal Split: Left Nav Rail, Right Content Notebook
        master_pane = tk.Frame(self, bg=BG_DARK)
        master_pane.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # Left Navigation Rail (Wireframe Figure 4)
        # -------------------------------------------------------------
        self.nav_rail = tk.Frame(master_pane, bg=BG_PANEL, width=240, bd=0)
        self.nav_rail.pack(side="left", fill="y")
        self.nav_rail.pack_propagate(False)

        # Brand / Title Block
        brand_frame = tk.Frame(self.nav_rail, bg=BG_PANEL, pady=18, padx=15)
        brand_frame.pack(fill="x")

        brand_title = tk.Label(
            brand_frame,
            text="🛡 HoneyGuard",
            font=("Segoe UI", 15, "bold"),
            fg=ACCENT_BLUE,
            bg=BG_PANEL
        )
        brand_title.pack(anchor="w")

        brand_sub = tk.Label(
            brand_frame,
            text="Ransomware Early-Warning",
            font=("Segoe UI", 8),
            fg=TEXT_MUTED,
            bg=BG_PANEL
        )
        brand_sub.pack(anchor="w")

        # Persistent Protection Status Box
        self.status_box = tk.Frame(self.nav_rail, bg=BG_SURFACE, padx=12, pady=10, bd=1, relief="solid")
        self.status_box.pack(fill="x", padx=12, pady=5)

        self.lbl_prot_status = tk.Label(
            self.status_box,
            text="● PROTECTION ACTIVE",
            font=("Segoe UI", 9, "bold"),
            fg=ACCENT_GREEN,
            bg=BG_SURFACE
        )
        self.lbl_prot_status.pack(anchor="w")

        self.lbl_db_status = tk.Label(
            self.status_box,
            text="● DB: CONNECTED",
            font=("Segoe UI", 8),
            fg=ACCENT_GREEN if is_db_connected() else ACCENT_RED,
            bg=BG_SURFACE
        )
        self.lbl_db_status.pack(anchor="w", pady=(3, 0))

        # Nav Buttons
        nav_btn_frame = tk.Frame(self.nav_rail, bg=BG_PANEL, pady=10)
        nav_btn_frame.pack(fill="x")

        self.nav_buttons = {}
        items = [
            ("dashboard", "📊 Dashboard"),
            ("decoys", "🍯 Decoy Manager"),
            ("monitor", "👁 File Monitor"),
            ("alerts", "🚨 Alerts"),
            ("logs", "📜 Incident Logs"),
            ("benchmarking", "⚡ Benchmarking"),
            ("settings", "⚙ Settings")
        ]

        for key, text in items:
            btn = tk.Button(
                nav_btn_frame,
                text=text,
                font=FONT_HEADING,
                fg=TEXT_PRIMARY,
                bg=BG_PANEL,
                activebackground=BG_SURFACE,
                activeforeground=ACCENT_BLUE,
                relief="flat",
                anchor="w",
                padx=15,
                pady=9,
                cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        # Bottom Info Box
        bottom_frame = tk.Frame(self.nav_rail, bg=BG_PANEL, padx=15, pady=15)
        bottom_frame.pack(side="bottom", fill="x")

        self.quick_info_lbl = tk.Label(
            bottom_frame,
            text="SLIIT IE3092 | Group 15\nVersion 1.0.0 (MySQL)",
            font=("Segoe UI", 8),
            fg=TEXT_MUTED,
            bg=BG_PANEL,
            justify="left"
        )
        self.quick_info_lbl.pack(anchor="w")

        # -------------------------------------------------------------
        # Right Views Deck
        # -------------------------------------------------------------
        self.views_container = tk.Frame(master_pane, bg=BG_DARK)
        self.views_container.pack(side="right", fill="both", expand=True)

        self.views = {
            "dashboard": DashboardView(self.views_container),
            "decoys": DecoyManagerView(self.views_container),
            "monitor": FileMonitorView(self.views_container, watcher_ref=self.watcher),
            "alerts": AlertsView(self.views_container),
            "logs": IncidentLogsView(self.views_container),
            "benchmarking": BenchmarkingView(self.views_container),
            "settings": SettingsView(self.views_container)
        }

        # Show Dashboard by default
        self.show_view("dashboard")

    def show_view(self, view_key: str):
        """Switch active view in the deck and highlight active nav button."""
        for k, v in self.views.items():
            v.pack_forget()

        if view_key in self.views:
            self.views[view_key].pack(fill="both", expand=True)
            # Trigger refresh if view supports it
            if hasattr(self.views[view_key], "refresh_metrics"):
                self.views[view_key].refresh_metrics()
            elif hasattr(self.views[view_key], "refresh_decoys"):
                self.views[view_key].refresh_decoys()
            elif hasattr(self.views[view_key], "refresh_logs"):
                self.views[view_key].refresh_logs()
            elif hasattr(self.views[view_key], "refresh_alerts"):
                self.views[view_key].refresh_alerts()

        # Update button highlights
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.config(bg=BG_SURFACE, fg=ACCENT_BLUE)
            else:
                btn.config(bg=BG_PANEL, fg=TEXT_PRIMARY)

    def _start_system_monitoring(self):
        """Start watchdog file monitoring across all registered protected directories."""
        try:
            dirs = DirectoryRepository.get_all()
            if not dirs:
                # Register demo workspace default
                from honeyguard.utils.paths import get_demo_workspace
                demo_dir = get_demo_workspace() / "Finance"
                demo_dir.mkdir(parents=True, exist_ok=True)
                DirectoryRepository.add_directory(str(demo_dir), "Finance Department (Demo)", True)
                dirs = DirectoryRepository.get_all()

            self.watcher.start(dirs)
            logger.info("Real-time monitoring started for HoneyGuard.")
        except Exception as exc:
            logger.error(f"Failed to start filesystem monitoring: {exc}")

    def _on_high_risk_alert(self, alert_data: Dict[str, Any]):
        """Callback invoked when AlertManager verifies a high-risk ransomware alert."""
        def handle():
            # Update alerts count
            self.nav_buttons["alerts"].config(fg=ACCENT_RED, text=f"🚨 Alerts (NEW!)")
            self.views["alerts"].display_alert(alert_data)
            self.views["alerts"].refresh_alerts()
            self.views["dashboard"].refresh_metrics()
            # Bring alerts tab forward
            self.show_view("alerts")
            # Audio bell
            try:
                self.bell()
            except Exception:
                pass

        self.after(0, handle)

    def _on_close(self):
        """Clean shutdown when application closes."""
        try:
            self.watcher.stop()
            self.event_bus.stop()
        except Exception as exc:
            logger.debug(f"Shutdown notice: {exc}")
        self.destroy()
