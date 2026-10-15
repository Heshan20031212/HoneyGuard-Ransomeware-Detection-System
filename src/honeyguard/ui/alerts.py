"""
HoneyGuard Detection & Alert Window (Figure 6)
Surfaces verified ransomware-like detections, risk score breakdown, matched indicators,
and operator-controlled mitigation actions.
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from honeyguard.database.repositories import AlertRepository
from honeyguard.response.containment import ContainmentManager
from honeyguard.ui.styles import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_MONO
)


class AlertsView(ttk.Frame):
    """Detection & Alert Screen corresponding to Wireframe Figure 6."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.containment_mgr = ContainmentManager()
        self.current_alert: Optional[Dict[str, Any]] = None
        self._build_ui()
        self.refresh_alerts()

    def _build_ui(self):
        # Top banner frame
        self.banner_frame = tk.Frame(self, bg=ACCENT_RED, height=50)
        self.banner_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.banner_lbl = tk.Label(
            self.banner_frame,
            text="⚠ RANSOMWARE-LIKE ACTIVITY DETECTED",
            font=("Segoe UI", 14, "bold"),
            fg="#ffffff",
            bg=ACCENT_RED,
            pady=10
        )
        self.banner_lbl.pack()

        # Split pane: Left = Alert List, Right = Detailed Alert Card (Figure 6)
        content_frame = tk.Frame(self, bg=BG_DARK)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left Column: Active Alerts Tree
        left_frame = tk.Frame(content_frame, bg=BG_PANEL, width=320, bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", padx=(0, 10))

        tk.Label(left_frame, text="Active Detection Alerts", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(padx=10, pady=10, anchor="w")

        self.alert_tree = ttk.Treeview(left_frame, columns=("alert_id", "risk", "status"), show="headings", height=15)
        self.alert_tree.heading("alert_id", text="ALERT ID")
        self.alert_tree.heading("risk", text="SCORE")
        self.alert_tree.heading("status", text="STATUS")
        self.alert_tree.column("alert_id", width=140, anchor="w")
        self.alert_tree.column("risk", width=60, anchor="center")
        self.alert_tree.column("status", width=80, anchor="center")
        self.alert_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.alert_tree.bind("<<TreeviewSelect>>", self._on_alert_selected)

        # Right Column: Detailed Alert Inspection (Figure 6 Wireframe Card)
        self.right_frame = tk.Frame(content_frame, bg=BG_PANEL, bd=1, relief="solid", padx=20, pady=15)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.detail_title = tk.Label(self.right_frame, text="Select an alert to inspect breakdown", font=FONT_SUBTITLE, fg=TEXT_MUTED, bg=BG_PANEL)
        self.detail_title.pack(anchor="w", pady=(0, 10))

        # Details Grid
        self.info_frame = tk.Frame(self.right_frame, bg=BG_SURFACE, padx=15, pady=10)
        self.info_frame.pack(fill="x", pady=5)

        self.lbl_file = self._add_info_row(self.info_frame, "Affected File (Decoy):", "—", 0)
        self.lbl_proc = self._add_info_row(self.info_frame, "Suspicious Process:", "—", 1)
        self.lbl_time = self._add_info_row(self.info_frame, "Detection Timestamp:", "—", 2)

        # Risk Score Breakdown Table
        tk.Label(self.right_frame, text="Risk Score Breakdown", font=FONT_HEADING, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w", pady=(15, 5))

        self.score_table = tk.Frame(self.right_frame, bg=BG_SURFACE, padx=10, pady=8)
        self.score_table.pack(fill="x")

        self.row_ht = self._add_score_row(self.score_table, "Honeytoken Interaction Weight", "0", 0)
        self.row_hf = self._add_score_row(self.score_table, "High-Frequency File Activity Weight", "0", 1)
        self.row_re = self._add_score_row(self.score_table, "Rename / Extension Change Weight", "0", 2)
        self.row_en = self._add_score_row(self.score_table, "Content / Entropy Indicator Weight", "0", 3)

        # Total Score Banner
        self.total_banner = tk.Frame(self.right_frame, bg="#2d1314", padx=15, pady=8, bd=1, relief="solid")
        self.total_banner.pack(fill="x", pady=10)

        self.total_score_lbl = tk.Label(
            self.total_banner,
            text="TOTAL RISK SCORE: 0  |  THRESHOLD: 70  |  VERDICT: NORMAL",
            font=("Segoe UI", 11, "bold"),
            fg=ACCENT_RED,
            bg="#2d1314"
        )
        self.total_score_lbl.pack()

        # Indicators Matched Checklist
        tk.Label(self.right_frame, text="Indicators Matched", font=FONT_HEADING, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w", pady=(10, 5))

        self.indicators_box = tk.Text(self.right_frame, height=4, bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_MONO, relief="flat", padx=10, pady=8)
        self.indicators_box.pack(fill="x")
        self.indicators_box.config(state="disabled")

        # Action Buttons (Figure 6)
        action_btn_frame = tk.Frame(self.right_frame, bg=BG_PANEL)
        action_btn_frame.pack(fill="x", pady=(20, 0))

        self.btn_terminate = ttk.Button(
            action_btn_frame,
            text="🚨 Isolate & Terminate Process",
            style="Danger.TButton",
            command=self._act_terminate
        )
        self.btn_terminate.pack(side="left", padx=(0, 10))

        self.btn_quarantine = ttk.Button(
            action_btn_frame,
            text="📦 Quarantine File",
            command=self._act_quarantine
        )
        self.btn_quarantine.pack(side="left", padx=10)

        self.btn_ignore = ttk.Button(
            action_btn_frame,
            text="Log Only (Ignore)",
            command=self._act_ignore
        )
        self.btn_ignore.pack(side="right")

    def _add_info_row(self, parent: tk.Widget, label_text: str, val_text: str, row_idx: int) -> tk.Label:
        tk.Label(parent, text=label_text, font=FONT_HEADING, fg=TEXT_MUTED, bg=BG_SURFACE).grid(row=row_idx, column=0, sticky="w", pady=2)
        val_lbl = tk.Label(parent, text=val_text, font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_SURFACE)
        val_lbl.grid(row=row_idx, column=1, sticky="w", padx=15, pady=2)
        return val_lbl

    def _add_score_row(self, parent: tk.Widget, desc_text: str, score_val: str, row_idx: int) -> tk.Label:
        tk.Label(parent, text=desc_text, font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_SURFACE).grid(row=row_idx, column=0, sticky="w", pady=2)
        val_lbl = tk.Label(parent, text=score_val, font=FONT_HEADING, fg=ACCENT_BLUE, bg=BG_SURFACE)
        val_lbl.grid(row=row_idx, column=1, sticky="e", padx=30, pady=2)
        parent.grid_columnconfigure(0, weight=1)
        return val_lbl

    def display_alert(self, alert_data: Dict[str, Any]):
        """Populate the detail view with a specific alert record."""
        self.current_alert = alert_data

        self.detail_title.config(text=f"Alert Incident: {alert_data['alert_id']}", fg=TEXT_PRIMARY)
        self.lbl_file.config(text=alert_data.get("affected_file", "UNKNOWN"))

        pid = alert_data.get("pid")
        pname = alert_data.get("process_name")
        p_str = f"{pname} (PID: {pid})" if pid else "UNRESOLVED"
        self.lbl_proc.config(text=p_str)

        ts = alert_data.get("timestamp")
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
        self.lbl_time.config(text=ts_str)

        # Update breakdown weights
        self.row_ht.config(text=str(alert_data.get("honeytoken_weight", 0)))
        self.row_hf.config(text=str(alert_data.get("file_activity_weight", 0)))
        self.row_re.config(text=str(alert_data.get("rename_extension_weight", 0)))
        self.row_en.config(text=str(alert_data.get("entropy_weight", 0)))

        # Total score
        score = alert_data.get("risk_score", 0)
        thresh = alert_data.get("configured_threshold", 70)
        level = alert_data.get("risk_level", "HIGH")
        self.total_score_lbl.config(text=f"TOTAL SCORE: {score}  |  THRESHOLD: {thresh}  |  VERDICT: {level} RISK")

        # Matched indicators
        matched = alert_data.get("matched_indicators", [])
        if isinstance(matched, str):
            try:
                matched = json.loads(matched)
            except Exception:
                matched = [matched]

        self.indicators_box.config(state="normal")
        self.indicators_box.delete("1.0", "end")
        for m in matched:
            self.indicators_box.insert("end", f"✓ {m}\n")
        self.indicators_box.config(state="disabled")

    def refresh_alerts(self):
        """Fetch active alerts from MySQL and populate tree."""
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)

        try:
            alerts = AlertRepository.get_recent(limit=30)
            for a in alerts:
                self.alert_tree.insert(
                    "",
                    "end",
                    values=(a["alert_id"], a["risk_score"], a["alert_status"])
                )
            if alerts and not self.current_alert:
                self.display_alert(alerts[0])
        except Exception:
            pass

    def _on_alert_selected(self, event):
        selected = self.alert_tree.selection()
        if not selected:
            return
        alert_id = self.alert_tree.item(selected[0])["values"][0]
        try:
            for a in AlertRepository.get_recent(limit=50):
                if a["alert_id"] == alert_id:
                    self.display_alert(a)
                    break
        except Exception:
            pass

    def _act_terminate(self):
        if not self.current_alert:
            messagebox.showwarning("No Alert", "No alert currently selected.")
            return

        pid = self.current_alert.get("pid")
        pname = self.current_alert.get("process_name", "Unknown")

        # Confirmation Modal (Figure 7 requirement)
        msg = (
            f"⚠ RESPONSE & PREVENTION — CONTAINMENT ACTION\n\n"
            f"This will:\n"
            f"• Terminate verified hostile process '{pname}' (PID: {pid})\n"
            f"• Isolate affected workspace directory\n"
            f"• Record forensic memory snapshot\n"
            f"• Create incident audit entry in MySQL\n\n"
            f"Continue with controlled containment?"
        )
        if messagebox.askyesno("Confirm Containment Action", msg):
            res = self.containment_mgr.execute_containment(
                self.current_alert,
                action_type="TERMINATE_PROCESS",
                operator_confirmed=True
            )
            messagebox.showinfo("Containment Result", res["result"])
            self.refresh_alerts()

    def _act_quarantine(self):
        if not self.current_alert:
            return
        res = self.containment_mgr.execute_containment(
            self.current_alert,
            action_type="QUARANTINE",
            operator_confirmed=True
        )
        messagebox.showinfo("Quarantine Result", res["result"])
        self.refresh_alerts()

    def _act_ignore(self):
        if not self.current_alert:
            return
        res = self.containment_mgr.execute_containment(
            self.current_alert,
            action_type="LOG_ONLY",
            operator_confirmed=True
        )
        messagebox.showinfo("Logged", "Alert recorded as LOG_ONLY.")
        self.refresh_alerts()
