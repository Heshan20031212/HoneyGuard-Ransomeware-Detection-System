"""
HoneyGuard File Monitor View
Live telemetry stream showing real-time file system actions and process attribution.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from honeyguard.file_monitoring.event_bus import get_event_bus
from honeyguard.ui.styles import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_MONO
)


class FileMonitorView(ttk.Frame):
    """Real-time File Activity Monitor."""

    def __init__(self, parent, watcher_ref=None):
        super().__init__(parent, style="TFrame")
        self.watcher = watcher_ref
        self.is_paused = False
        self._build_ui()

        # Subscribe to live event bus
        get_event_bus().subscribe(self._on_live_event)

    def _build_ui(self):
        # Header & Controls
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = tk.Label(
            header_frame,
            text="Live File System Activity Monitor",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK
        )
        title_lbl.pack(side="left")

        # Controls
        ctrl_frame = tk.Frame(self, bg=BG_DARK)
        ctrl_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.pause_btn = ttk.Button(ctrl_frame, text="⏸ Pause Feed", command=self._toggle_pause)
        self.pause_btn.pack(side="left", padx=(0, 10))

        clear_btn = ttk.Button(ctrl_frame, text="Clear View", command=self._clear_events)
        clear_btn.pack(side="left")

        self.status_lbl = tk.Label(
            ctrl_frame,
            text="STATUS: STREAMING LIVE TELEMETRY",
            font=FONT_HEADING,
            fg=ACCENT_GREEN,
            bg=BG_DARK
        )
        self.status_lbl.pack(side="right")

        # Events Table
        table_container = tk.Frame(self, bg=BG_PANEL, bd=1, relief="solid")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("timestamp", "event_type", "path", "decoy", "pid_process", "risk")
        self.monitor_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.monitor_tree.heading("timestamp", text="TIMESTAMP")
        self.monitor_tree.heading("event_type", text="EVENT")
        self.monitor_tree.heading("path", text="PATH")
        self.monitor_tree.heading("decoy", text="CANARY DECOY")
        self.monitor_tree.heading("pid_process", text="PROCESS (PID)")
        self.monitor_tree.heading("risk", text="RISK CONTRIBUTION")

        self.monitor_tree.column("timestamp", width=140, anchor="center")
        self.monitor_tree.column("event_type", width=110, anchor="center")
        self.monitor_tree.column("path", width=380, anchor="w")
        self.monitor_tree.column("decoy", width=110, anchor="center")
        self.monitor_tree.column("pid_process", width=180, anchor="center")
        self.monitor_tree.column("risk", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.monitor_tree.yview)
        self.monitor_tree.configure(yscrollcommand=scrollbar.set)

        self.monitor_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Color tags
        self.monitor_tree.tag_configure("DECOY_HIT", foreground=ACCENT_RED)
        self.monitor_tree.tag_configure("NORMAL", foreground=TEXT_PRIMARY)
        self.monitor_tree.tag_configure("SUSPICIOUS", foreground=ACCENT_YELLOW)

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶ Resume Feed")
            self.status_lbl.config(text="STATUS: FEED PAUSED", fg=ACCENT_YELLOW)
        else:
            self.pause_btn.config(text="⏸ Pause Feed")
            self.status_lbl.config(text="STATUS: STREAMING LIVE TELEMETRY", fg=ACCENT_GREEN)

    def _clear_events(self):
        for item in self.monitor_tree.get_children():
            self.monitor_tree.delete(item)

    def _on_live_event(self, event: Dict[str, Any]):
        """Receive enriched event from background EventBus thread and insert into GUI table."""
        if self.is_paused:
            return

        def update_gui():
            ts = event.get("timestamp")
            ts_str = ts.strftime("%H:%M:%S.%f")[:-3] if hasattr(ts, "strftime") else str(ts)
            etype = event.get("event_type", "UNKNOWN")
            path = event.get("source_path", "")
            is_decoy = "YES (CANARY)" if event.get("is_decoy") else "NO"

            pid = event.get("pid")
            pname = event.get("process_name")
            p_str = f"{pname} (PID: {pid})" if pid else "UNRESOLVED"

            risk = f"+{event.get('risk_contribution', 0)}"

            tag = "DECOY_HIT" if event.get("is_decoy") else ("SUSPICIOUS" if etype == "EXTENSION_CHANGE" else "NORMAL")

            # Insert at top (reverse chronological)
            self.monitor_tree.insert(
                "",
                0,
                values=(ts_str, etype, path, is_decoy, p_str, risk),
                tags=(tag,)
            )

            # Limit rows to 100
            children = self.monitor_tree.get_children()
            if len(children) > 100:
                self.monitor_tree.delete(children[-1])

        # Schedule on tkinter main thread safely
        self.after(0, update_gui)
