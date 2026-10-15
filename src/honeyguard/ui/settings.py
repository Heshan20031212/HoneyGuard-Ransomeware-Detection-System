"""
HoneyGuard Settings View
Allows operators to configure protected directories, behavioural weights,
detection thresholds, auto-containment mode, and test database connectivity.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from honeyguard.database.connection import is_db_connected
from honeyguard.database.repositories import SettingsRepository, DirectoryRepository
from honeyguard.ui.styles import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY
)


class SettingsView(ttk.Frame):
    """Configuration & Settings Management Screen."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = tk.Label(
            header_frame,
            text="System Settings & Detection Thresholds",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK
        )
        title_lbl.pack(side="left")

        save_btn = ttk.Button(header_frame, text="💾 Save All Settings", style="Primary.TButton", command=self.save_settings)
        save_btn.pack(side="right")

        content_frame = tk.Frame(self, bg=BG_DARK)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Column: Protected Directories
        left_col = tk.Frame(content_frame, bg=BG_PANEL, bd=1, relief="solid", padx=15, pady=15)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_col, text="Protected Monitored Directories", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w")

        dir_btn_frame = tk.Frame(left_col, bg=BG_PANEL)
        dir_btn_frame.pack(fill="x", pady=10)

        add_dir_btn = ttk.Button(dir_btn_frame, text="+ Add Directory", command=self._add_directory)
        add_dir_btn.pack(side="left", padx=(0, 10))

        del_dir_btn = ttk.Button(dir_btn_frame, text="Remove", command=self._remove_directory)
        del_dir_btn.pack(side="left")

        self.dir_listbox = tk.Listbox(left_col, bg=BG_SURFACE, fg=TEXT_PRIMARY, font=FONT_BODY, selectmode="browse", height=10)
        self.dir_listbox.pack(fill="both", expand=True, pady=(0, 10))

        # DB Connection Status Card
        db_card = tk.Frame(left_col, bg=BG_SURFACE, padx=10, pady=10, bd=1, relief="solid")
        db_card.pack(fill="x")

        tk.Label(db_card, text="Database Status:", font=FONT_HEADING, fg=TEXT_MUTED, bg=BG_SURFACE).pack(side="left")
        self.db_status_lbl = tk.Label(db_card, text="CHECKING...", font=FONT_HEADING, fg=ACCENT_YELLOW, bg=BG_SURFACE)
        self.db_status_lbl.pack(side="left", padx=10)

        test_db_btn = ttk.Button(db_card, text="Test Connection", command=self.check_database_connection)
        test_db_btn.pack(side="right")

        # Right Column: Risk Formula Weights & Thresholds
        right_col = tk.Frame(content_frame, bg=BG_PANEL, bd=1, relief="solid", padx=15, pady=15)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(right_col, text="Weighted Risk Scoring Formula", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w", pady=(0, 10))

        self.entry_threshold = self._add_setting_input(right_col, "Risk Alert Threshold (Default: 70):", "70")
        self.entry_honeytoken = self._add_setting_input(right_col, "Honeytoken Interaction Weight (Default: 40):", "40")
        self.entry_activity = self._add_setting_input(right_col, "High-Frequency Modification Weight (Default: 25):", "25")
        self.entry_rename = self._add_setting_input(right_col, "Rename / Extension Change Weight (Default: 20):", "20")
        self.entry_entropy = self._add_setting_input(right_col, "Content / Entropy Indicator Weight (Default: 18):", "18")

        tk.Label(right_col, text="Sliding Window & Telemetry", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w", pady=(15, 10))

        self.entry_window = self._add_setting_input(right_col, "Sliding Window (Seconds):", "3.0")
        self.entry_freq = self._add_setting_input(right_col, "Rapid Modification File Count:", "10")
        self.entry_ent_thresh = self._add_setting_input(right_col, "Shannon Entropy Threshold (0-8):", "7.2")

        # Auto-containment toggle
        self.auto_contain_var = tk.IntVar(value=0)
        self.chk_auto = tk.Checkbutton(
            right_col,
            text="Enable Autonomous Containment in Authorized Sandbox Mode",
            variable=self.auto_contain_var,
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_PANEL,
            activeforeground=TEXT_PRIMARY,
            font=FONT_HEADING
        )
        self.chk_auto.pack(anchor="w", pady=(15, 0))

    def _add_setting_input(self, parent: tk.Widget, label_text: str, default_val: str) -> ttk.Entry:
        f = tk.Frame(parent, bg=BG_PANEL)
        f.pack(fill="x", pady=4)
        tk.Label(f, text=label_text, font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_PANEL).pack(side="left")
        ent = ttk.Entry(f, width=10)
        ent.insert(0, default_val)
        ent.pack(side="right")
        return ent

    def load_settings(self):
        """Load values from MySQL."""
        self.check_database_connection()
        self._refresh_dir_listbox()

        try:
            settings = SettingsRepository.get_all()
            if "risk_threshold" in settings:
                self.entry_threshold.delete(0, "end")
                self.entry_threshold.insert(0, settings["risk_threshold"])
            if "honeytoken_weight" in settings:
                self.entry_honeytoken.delete(0, "end")
                self.entry_honeytoken.insert(0, settings["honeytoken_weight"])
            if "file_activity_weight" in settings:
                self.entry_activity.delete(0, "end")
                self.entry_activity.insert(0, settings["file_activity_weight"])
            if "rename_extension_weight" in settings:
                self.entry_rename.delete(0, "end")
                self.entry_rename.insert(0, settings["rename_extension_weight"])
            if "entropy_weight" in settings:
                self.entry_entropy.delete(0, "end")
                self.entry_entropy.insert(0, settings["entropy_weight"])
            if "frequency_window_seconds" in settings:
                self.entry_window.delete(0, "end")
                self.entry_window.insert(0, settings["frequency_window_seconds"])
            if "frequency_threshold" in settings:
                self.entry_freq.delete(0, "end")
                self.entry_freq.insert(0, settings["frequency_threshold"])
            if "entropy_threshold" in settings:
                self.entry_ent_thresh.delete(0, "end")
                self.entry_ent_thresh.insert(0, settings["entropy_threshold"])
            if "auto_containment_enabled" in settings:
                self.auto_contain_var.set(int(settings["auto_containment_enabled"]))
        except Exception:
            pass

    def save_settings(self):
        """Save settings to MySQL."""
        try:
            SettingsRepository.set("risk_threshold", self.entry_threshold.get())
            SettingsRepository.set("honeytoken_weight", self.entry_honeytoken.get())
            SettingsRepository.set("file_activity_weight", self.entry_activity.get())
            SettingsRepository.set("rename_extension_weight", self.entry_rename.get())
            SettingsRepository.set("entropy_weight", self.entry_entropy.get())
            SettingsRepository.set("frequency_window_seconds", self.entry_window.get())
            SettingsRepository.set("frequency_threshold", self.entry_freq.get())
            SettingsRepository.set("entropy_threshold", self.entry_ent_thresh.get())
            SettingsRepository.set("auto_containment_enabled", str(self.auto_contain_var.get()))

            messagebox.showinfo("Success", "Settings updated successfully in MySQL!")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save settings: {exc}")

    def check_database_connection(self):
        """Verify live MySQL connection."""
        connected = is_db_connected()
        if connected:
            self.db_status_lbl.config(text="CONNECTED (MySQL 8.0)", fg=ACCENT_GREEN)
        else:
            self.db_status_lbl.config(text="DISCONNECTED", fg=ACCENT_RED)

    def _refresh_dir_listbox(self):
        self.dir_listbox.delete(0, "end")
        try:
            dirs = DirectoryRepository.get_all()
            for d in dirs:
                self.dir_listbox.insert("end", f"{d['display_name']} -> {d['directory_path']}")
        except Exception:
            pass

    def _add_directory(self):
        dir_path = filedialog.askdirectory(title="Select Directory to Protect with HoneyGuard")
        if not dir_path:
            return
        name = Path(dir_path).name or "Monitored Directory"
        try:
            DirectoryRepository.add_directory(dir_path, name, True)
            self._refresh_dir_listbox()
            messagebox.showinfo("Directory Added", f"Registered protected directory:\n{dir_path}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _remove_directory(self):
        sel = self.dir_listbox.curselection()
        if not sel:
            return
        item_text = self.dir_listbox.get(sel[0])
        path = item_text.split(" -> ")[-1]
        try:
            record = DirectoryRepository.get_by_path(path)
            if record:
                DirectoryRepository.remove(record["directory_id"])
                self._refresh_dir_listbox()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
