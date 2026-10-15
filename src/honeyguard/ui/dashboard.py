"""
HoneyGuard Dashboard View (Figure 4)
Displays live KPI metrics (Decoys Deployed, Files Monitored, Active Alerts, Processes Contained)
and real-time reverse-chronological security event feed with severity badges.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from honeyguard.database.repositories import (
    DecoyRepository,
    AlertRepository,
    IncidentRepository,
    EventRepository,
    DirectoryRepository
)
from honeyguard.ui.styles import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_MONO
)


class DashboardView(ttk.Frame):
    """Early-Warning Dashboard with real MySQL data binding."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self.refresh_metrics()

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = tk.Label(
            header_frame,
            text="Ransomware Early-Warning Dashboard",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK
        )
        title_lbl.pack(side="left")

        refresh_btn = ttk.Button(header_frame, text="⟳ Refresh Data", command=self.refresh_metrics)
        refresh_btn.pack(side="right")

        # KPI Cards Frame
        kpi_frame = tk.Frame(self, bg=BG_DARK)
        kpi_frame.pack(fill="x", padx=20, pady=10)

        # Card 1: Decoys Deployed
        self.card_decoys = self._create_kpi_card(kpi_frame, "DECOYS DEPLOYED", "0", ACCENT_BLUE)
        self.card_decoys.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Card 2: Files Monitored
        self.card_files = self._create_kpi_card(kpi_frame, "FILES MONITORED", "0", ACCENT_GREEN)
        self.card_files.pack(side="left", fill="both", expand=True, padx=10)

        # Card 3: Active Alerts
        self.card_alerts = self._create_kpi_card(kpi_frame, "ACTIVE ALERTS", "0", ACCENT_RED)
        self.card_alerts.pack(side="left", fill="both", expand=True, padx=10)

        # Card 4: Processes Contained
        self.card_contained = self._create_kpi_card(kpi_frame, "PROCESSES CONTAINED", "0", ACCENT_YELLOW)
        self.card_contained.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # Recent Events Section
        feed_lbl = tk.Label(
            self,
            text="Recent Security Events",
            font=FONT_SUBTITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK
        )
        feed_lbl.pack(anchor="w", padx=20, pady=(20, 5))

        # Treeview / List of events
        table_container = tk.Frame(self, bg=BG_PANEL, bd=1, relief="solid")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("severity", "timestamp", "description")
        self.event_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=12
        )
        self.event_tree.heading("severity", text="SEVERITY")
        self.event_tree.heading("timestamp", text="TIMESTAMP")
        self.event_tree.heading("description", text="EVENT DESCRIPTION")

        self.event_tree.column("severity", width=120, anchor="center")
        self.event_tree.column("timestamp", width=180, anchor="center")
        self.event_tree.column("description", width=600, anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.event_tree.yview)
        self.event_tree.configure(yscrollcommand=scrollbar.set)

        self.event_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Define color tags for Treeview
        self.event_tree.tag_configure("CRITICAL", foreground=ACCENT_RED)
        self.event_tree.tag_configure("RESPONSE", foreground=ACCENT_BLUE)
        self.event_tree.tag_configure("WARNING", foreground=ACCENT_YELLOW)
        self.event_tree.tag_configure("INFO", foreground=TEXT_PRIMARY)

    def _create_kpi_card(self, parent: tk.Widget, title: str, initial_value: str, color: str) -> tk.Frame:
        """Create a stylized KPI card box."""
        card = tk.Frame(parent, bg=BG_PANEL, bd=1, relief="solid", padx=15, pady=15)

        val_lbl = tk.Label(card, text=initial_value, font=("Segoe UI", 28, "bold"), fg=color, bg=BG_PANEL)
        val_lbl.pack(anchor="center")

        title_lbl = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=BG_PANEL)
        title_lbl.pack(anchor="center", pady=(5, 0))

        card.val_label = val_lbl
        return card

    def refresh_metrics(self):
        """Fetch live statistics from MySQL and populate dashboard."""
        try:
            decoys_count = DecoyRepository.count_active()
            alerts_count = AlertRepository.count_active()
            contained_count = IncidentRepository.count_contained()
            events_count = EventRepository.count_total()

            # Update KPI card values
            self.card_decoys.val_label.config(text=str(decoys_count))
            self.card_files.val_label.config(text=str(events_count + decoys_count))
            self.card_alerts.val_label.config(text=str(alerts_count))
            self.card_contained.val_label.config(text=str(contained_count))

            # Fetch recent events
            for row in self.event_tree.get_children():
                self.event_tree.delete(row)

            recent_events = EventRepository.get_recent(limit=30)
            for ev in recent_events:
                sev = "INFO"
                desc = f"File {ev['event_type']} on {ev['source_path']}"
                if ev.get("is_decoy"):
                    sev = "CRITICAL" if ev['event_type'] in ("MODIFY", "DELETE", "EXTENSION_CHANGE") else "WARNING"
                    desc = f"[CANARY TOUCHED] Decoy {ev['event_type']} -> {ev['source_path']} (PID: {ev.get('pid') or 'UNRESOLVED'})"
                elif ev['event_type'] == "EXTENSION_CHANGE":
                    sev = "CRITICAL"
                    desc = f"[SUSPICIOUS EXTENSION] Renamed to {ev.get('destination_path')} (PID: {ev.get('pid') or 'UNRESOLVED'})"

                ts_str = ev["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(ev["timestamp"], "strftime") else str(ev["timestamp"])

                self.event_tree.insert(
                    "",
                    "end",
                    values=(sev, ts_str, desc),
                    tags=(sev,)
                )

        except Exception as exc:
            pass  # Fail safely if DB is busy or loading
