"""
HoneyGuard Security & Incident Logs View (Figure 7)
Displays historical incidents, containment actions, forensic records, and export facilities (JSON/CSV).
"""

import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Dict, Any

from honeyguard.database.repositories import IncidentRepository, ResponseActionRepository
from honeyguard.utils.paths import get_exports_dir
from honeyguard.ui.styles import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_MONO
)


class IncidentLogsView(ttk.Frame):
    """Incident Logs screen supporting review, filtering, and forensic exports."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self.refresh_logs()

    def _build_ui(self):
        # Header & Toolbar
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = tk.Label(
            header_frame,
            text="Security & Incident Forensics Log",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK
        )
        title_lbl.pack(side="left")

        # Toolbar Buttons (Exports & Refresh)
        btn_frame = tk.Frame(self, bg=BG_DARK)
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        export_json_btn = ttk.Button(btn_frame, text="Export JSON", command=self._export_json)
        export_json_btn.pack(side="left", padx=(0, 10))

        export_csv_btn = ttk.Button(btn_frame, text="Export CSV", command=self._export_csv)
        export_csv_btn.pack(side="left", padx=10)

        refresh_btn = ttk.Button(btn_frame, text="⟳ Refresh Logs", command=self.refresh_logs)
        refresh_btn.pack(side="right")

        # Incidents Table
        table_container = tk.Frame(self, bg=BG_PANEL, bd=1, relief="solid")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("incident_id", "timestamp", "level", "file", "process", "containment", "latency")
        self.log_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.log_tree.heading("incident_id", text="INCIDENT ID")
        self.log_tree.heading("timestamp", text="DETECTED AT")
        self.log_tree.heading("level", text="SEVERITY")
        self.log_tree.heading("file", text="AFFECTED FILE")
        self.log_tree.heading("process", text="PROCESS (PID)")
        self.log_tree.heading("containment", text="CONTAINMENT STATUS")
        self.log_tree.heading("latency", text="LATENCY (MS)")

        self.log_tree.column("incident_id", width=140, anchor="center")
        self.log_tree.column("timestamp", width=160, anchor="center")
        self.log_tree.column("level", width=100, anchor="center")
        self.log_tree.column("file", width=280, anchor="w")
        self.log_tree.column("process", width=160, anchor="center")
        self.log_tree.column("containment", width=140, anchor="center")
        self.log_tree.column("latency", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)

        self.log_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.log_tree.tag_configure("CRITICAL", foreground=ACCENT_RED)
        self.log_tree.tag_configure("HIGH", foreground=ACCENT_RED)
        self.log_tree.tag_configure("MEDIUM", foreground=ACCENT_YELLOW)
        self.log_tree.tag_configure("LOW", foreground=ACCENT_GREEN)

    def refresh_logs(self):
        """Fetch all incidents from MySQL."""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        try:
            incidents = IncidentRepository.get_all(limit=100)
            for inc in incidents:
                ts = inc["detected_at"]
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
                pid = inc.get("pid")
                pname = inc.get("process_name")
                p_str = f"{pname} ({pid})" if pid else "UNRESOLVED"
                latency = f"{inc.get('detection_latency_ms', 0.0):.1f} ms"
                level = inc.get("risk_level", "HIGH")

                self.log_tree.insert(
                    "",
                    "end",
                    values=(
                        inc["incident_id"],
                        ts_str,
                        level,
                        inc["affected_file"],
                        p_str,
                        inc.get("containment_status", "LOG_ONLY"),
                        latency
                    ),
                    tags=(level,)
                )
        except Exception:
            pass

    def _export_json(self):
        """Export all MySQL incident records to a structured JSON file."""
        try:
            incidents = IncidentRepository.get_all(limit=1000)
            # Serialize datetimes
            cleaned = []
            for inc in incidents:
                item = dict(inc)
                for k, v in item.items():
                    if isinstance(v, datetime):
                        item[k] = v.isoformat()
                cleaned.append(item)

            export_dir = get_exports_dir()
            filename = export_dir / f"incidents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=2)

            messagebox.showinfo("Export Successful", f"Exported {len(cleaned)} incident records to:\n{filename}")
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))

    def _export_csv(self):
        """Export all MySQL incident records to a CSV file."""
        try:
            incidents = IncidentRepository.get_all(limit=1000)
            if not incidents:
                messagebox.showwarning("No Data", "No incidents available to export.")
                return

            export_dir = get_exports_dir()
            filename = export_dir / f"incidents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            fields = list(incidents[0].keys())
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for row in incidents:
                    writer.writerow(row)

            messagebox.showinfo("Export Successful", f"Exported {len(incidents)} incident records to:\n{filename}")
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))
