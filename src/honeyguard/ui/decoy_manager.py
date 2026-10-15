"""
HoneyGuard Decoy Manager View (Figure 5)
Provides decoy file management: deploying synthetic honeytokens, verifying cryptographic integrity,
and listing deployed canaries with real-time status (INTACT / ACCESSED / MODIFIED / DELETED).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any

from honeyguard.database.repositories import DecoyRepository, DirectoryRepository
from honeyguard.decoy_generation.registry import DecoyRegistry
from honeyguard.decoy_generation.templates import get_available_templates
from honeyguard.ui.styles import (
    BG_DARK, BG_PANEL, BG_SURFACE,
    TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY
)


class DecoyManagerView(ttk.Frame):
    """Decoy Management Screen corresponding to Wireframe Figure 5."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self.refresh_decoys()

    def _build_ui(self):
        # Header & Toolbar
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = tk.Label(
            header_frame,
            text="Decoy Manager — Monitored Honeytoken Files",
            font=FONT_TITLE,
            fg=TEXT_PRIMARY,
            bg=BG_DARK
        )
        title_lbl.pack(side="left")

        # Toolbar Buttons
        btn_frame = tk.Frame(self, bg=BG_DARK)
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        deploy_btn = ttk.Button(
            btn_frame,
            text="+ Deploy New Decoy",
            style="Primary.TButton",
            command=self._open_deploy_dialog
        )
        deploy_btn.pack(side="left", padx=(0, 10))

        verify_btn = ttk.Button(
            btn_frame,
            text="Verify All Decoys",
            style="Success.TButton",
            command=self._verify_all_decoys
        )
        verify_btn.pack(side="left", padx=10)

        remove_btn = ttk.Button(
            btn_frame,
            text="Remove Decoy",
            style="Danger.TButton",
            command=self._remove_selected_decoy
        )
        remove_btn.pack(side="left", padx=10)

        refresh_btn = ttk.Button(
            btn_frame,
            text="⟳ Refresh",
            command=self.refresh_decoys
        )
        refresh_btn.pack(side="right")

        # Decoys Table
        table_container = tk.Frame(self, bg=BG_PANEL, bd=1, relief="solid")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("decoy_id", "filename", "type", "location", "status", "created", "verified")
        self.decoy_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.decoy_tree.heading("decoy_id", text="DECOY ID")
        self.decoy_tree.heading("filename", text="FILE NAME")
        self.decoy_tree.heading("type", text="TYPE")
        self.decoy_tree.heading("location", text="LOCATION")
        self.decoy_tree.heading("status", text="STATUS")
        self.decoy_tree.heading("created", text="CREATED")
        self.decoy_tree.heading("verified", text="LAST VERIFIED")

        self.decoy_tree.column("decoy_id", width=120, anchor="center")
        self.decoy_tree.column("filename", width=220, anchor="w")
        self.decoy_tree.column("type", width=70, anchor="center")
        self.decoy_tree.column("location", width=340, anchor="w")
        self.decoy_tree.column("status", width=100, anchor="center")
        self.decoy_tree.column("created", width=140, anchor="center")
        self.decoy_tree.column("verified", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.decoy_tree.yview)
        self.decoy_tree.configure(yscrollcommand=scrollbar.set)

        self.decoy_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Color tags
        self.decoy_tree.tag_configure("INTACT", foreground=ACCENT_GREEN)
        self.decoy_tree.tag_configure("ACCESSED", foreground=ACCENT_YELLOW)
        self.decoy_tree.tag_configure("MODIFIED", foreground=ACCENT_RED)
        self.decoy_tree.tag_configure("DELETED", foreground=TEXT_MUTED)

    def refresh_decoys(self):
        """Fetch all decoys from MySQL."""
        for row in self.decoy_tree.get_children():
            self.decoy_tree.delete(row)

        try:
            decoys = DecoyRepository.get_all()
            for d in decoys:
                created_str = d["creation_timestamp"].strftime("%Y-%m-%d %H:%M") if hasattr(d["creation_timestamp"], "strftime") else str(d["creation_timestamp"])
                verified_str = d["last_verified_timestamp"].strftime("%Y-%m-%d %H:%M") if hasattr(d["last_verified_timestamp"], "strftime") else str(d["last_verified_timestamp"])
                status = d.get("status", "INTACT")

                self.decoy_tree.insert(
                    "",
                    "end",
                    values=(
                        d["decoy_id"],
                        d["filename"],
                        d["file_type"],
                        d["absolute_path"],
                        status,
                        created_str,
                        verified_str
                    ),
                    tags=(status,)
                )
        except Exception as exc:
            pass

    def _verify_all_decoys(self):
        """Trigger cryptographic verification across all decoys."""
        try:
            results = DecoyRegistry.verify_all_decoys()
            self.refresh_decoys()
            messagebox.showinfo("Integrity Verification", f"Successfully verified {len(results)} decoy files.")
        except Exception as exc:
            messagebox.showerror("Verification Error", str(exc))

    def _remove_selected_decoy(self):
        """Remove selected decoy from database and disk."""
        selected = self.decoy_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a decoy to remove.")
            return

        item = self.decoy_tree.item(selected[0])
        decoy_id = item["values"][0]
        filename = item["values"][1]

        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove decoy '{filename}' ({decoy_id})?"):
            DecoyRegistry.remove_decoy(decoy_id, delete_from_disk=True)
            self.refresh_decoys()

    def _open_deploy_dialog(self):
        """Open modal window to choose category and deploy new decoy."""
        dialog = tk.Toplevel(self)
        dialog.title("Deploy Synthetic Honeytoken Decoy")
        dialog.geometry("450x320")
        dialog.configure(bg=BG_PANEL)
        dialog.transient(self)
        dialog.grab_set()

        lbl = tk.Label(dialog, text="Deploy New Decoy", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_PANEL)
        lbl.pack(pady=15)

        # Department selector
        tk.Label(dialog, text="Department Template Pack:", font=FONT_HEADING, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", padx=30, pady=(5, 2))
        category_var = tk.StringVar(value="Finance")
        cat_combo = ttk.Combobox(dialog, textvariable=category_var, values=["Finance", "HR", "Legal", "General"], state="readonly")
        cat_combo.pack(fill="x", padx=30, pady=5)

        # Target directory selector
        tk.Label(dialog, text="Target Protected Directory:", font=FONT_HEADING, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", padx=30, pady=(10, 2))
        dirs = DirectoryRepository.get_all()
        if not dirs:
            messagebox.showwarning("No Protected Directories", "Please register a protected directory in Settings first.")
            dialog.destroy()
            return

        dir_map = {f"{d['display_name']} ({d['directory_path']})": d["directory_id"] for d in dirs}
        dir_var = tk.StringVar(value=list(dir_map.keys())[0])
        dir_combo = ttk.Combobox(dialog, textvariable=dir_var, values=list(dir_map.keys()), state="readonly")
        dir_combo.pack(fill="x", padx=30, pady=5)

        def do_deploy():
            chosen_dir_id = dir_map[dir_var.get()]
            chosen_cat = category_var.get()
            try:
                deployed = DecoyRegistry.deploy_default_canary_pack(chosen_dir_id, chosen_cat)
                dialog.destroy()
                self.refresh_decoys()
                messagebox.showinfo("Success", f"Deployed {len(deployed)} {chosen_cat} decoys successfully!")
            except Exception as exc:
                messagebox.showerror("Deployment Error", str(exc))

        deploy_act_btn = ttk.Button(dialog, text="Deploy Decoys", style="Primary.TButton", command=do_deploy)
        deploy_act_btn.pack(pady=25)
