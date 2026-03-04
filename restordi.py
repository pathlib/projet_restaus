from __future__ import annotations

import csv
import json
import logging
import os
import platform
import sqlite3
import tempfile
import typing
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ─── LOGGING ──────────────────────────────────────────────────────────────────
_LOG_PATH: Path = Path.home() / "reconditionnement.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log: logging.Logger = logging.getLogger("reconditionnement")

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
liste: list[dict[str, Any]] = []

home: Path = Path.home()
if (home / "Desktop").exists():
    DB_PATH: Path = home / "Desktop" / "ma_base.db"
elif (home / "Bureau").exists():
    DB_PATH = home / "Bureau" / "ma_base.db"
else:
    DB_PATH = home / "ma_base.db"

log.debug("DB_PATH résolu → %s", DB_PATH)


# ─── BASE DE DONNÉES ──────────────────────────────────────────────────────────
def create_db() -> None:
    """Crée la table utilisateurs si elle n'existe pas encore."""
    log.info("Initialisation de la base de données : %s", DB_PATH)
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        c: sqlite3.Cursor = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS utilisateurs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            question    TEXT    NOT NULL,
            reponse     TEXT    DEFAULT 'None',
            type        TEXT    DEFAULT 'normale',
            commentaire TEXT    DEFAULT 'None',
            date        TEXT    DEFAULT ''
        )""")
        conn.commit()
        log.debug("Table 'utilisateurs' vérifiée/créée.")
    except sqlite3.Error as exc:
        log.exception("Erreur lors de la création de la base : %s", exc)
        raise
    finally:
        conn.close()


def question_existe(question: str) -> bool:
    """Retourne True si la question existe déjà en base."""
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        c: sqlite3.Cursor = conn.cursor()
        c.execute("SELECT id FROM utilisateurs WHERE question = ?", (question,))
        result: Optional[tuple[Any, ...]] = c.fetchone()
        return result is not None
    except sqlite3.Error as exc:
        log.exception("Erreur lors de la vérification d'existence : %s", exc)
        return False
    finally:
        conn.close()


def ajouter_questions_db() -> None:
    """Insère dans la base les entrées de `liste` qui n'y sont pas encore."""
    log.info("Envoi de %d entrée(s) potentielle(s) en base.", len(liste))
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        c: sqlite3.Cursor = conn.cursor()
        inserted: int = 0
        for u in liste:
            if "question" in u and not question_existe(u["question"]):
                c.execute(
                    "INSERT INTO utilisateurs (question) VALUES (?)", (u["question"],)
                )
                inserted += 1
        conn.commit()
        log.info("%d nouvelle(s) entrée(s) insérée(s).", inserted)
    except sqlite3.Error as exc:
        log.exception("Erreur lors de l'insertion en base : %s", exc)
        raise
    finally:
        conn.close()


def supprimer_question_db(id_q: int) -> None:
    """Supprime l'entrée d'id `id_q` de la base de données."""
    log.info("Suppression de l'entrée ID=%d en base.", id_q)
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        c: sqlite3.Cursor = conn.cursor()
        c.execute("DELETE FROM utilisateurs WHERE id = ?", (id_q,))
        conn.commit()
        log.debug("Entrée ID=%d supprimée (%d ligne(s) affectée(s)).", id_q, c.rowcount)
    except sqlite3.Error as exc:
        log.exception("Erreur lors de la suppression ID=%d : %s", id_q, exc)
        raise
    finally:
        conn.close()


def charger_depuis_db() -> list[dict[str, Any]]:
    """Charge toutes les entrées de la base dans la liste globale."""
    global liste
    log.info("Chargement depuis la base : %s", DB_PATH)
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        c: sqlite3.Cursor = conn.cursor()
        c.execute("SELECT id, question, reponse, type, commentaire, date FROM utilisateurs")
        rows: list[tuple[Any, ...]] = c.fetchall()
        liste = [
            {
                "id": r[0],
                "question": r[1],
                "reponse": r[2] or "None",
                "type": r[3] or "normale",
                "commentaire": r[4] or "None",
                "date": r[5] or "",
            }
            for r in rows
        ]
        log.info("%d entrée(s) chargée(s) depuis la base.", len(liste))
        return liste
    except sqlite3.Error as exc:
        log.exception("Erreur lors du chargement depuis la base : %s", exc)
        raise
    finally:
        conn.close()


def get_all_db() -> list[tuple[Any, ...]]:
    """Retourne toutes les lignes brutes de la table utilisateurs."""
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        c: sqlite3.Cursor = conn.cursor()
        c.execute("SELECT id, question, reponse, type, commentaire, date FROM utilisateurs")
        rows: list[tuple[Any, ...]] = c.fetchall()
        log.debug("get_all_db : %d ligne(s) récupérée(s).", len(rows))
        return rows
    except sqlite3.Error as exc:
        log.exception("Erreur lors de get_all_db : %s", exc)
        return []
    finally:
        conn.close()


def _get_dossier() -> Path:
    """Retourne (et crée si besoin) le dossier d'export sur le Bureau."""
    if (home / "Desktop").exists():
        bureau: Path = home / "Desktop"
    elif (home / "Bureau").exists():
        bureau = home / "Bureau"
    else:
        bureau = home
    dossier: Path = bureau / "reconditionnement"
    dossier.mkdir(exist_ok=True)
    log.debug("Dossier export : %s", dossier)
    return dossier


# ─── COULEURS & STYLE ─────────────────────────────────────────────────────────
BG = "#1a1d23"
BG2 = "#22262f"
BG3 = "#2c3140"
ACCENT = "#4f8ef7"
ACCENT2 = "#7fb3ff"
SUCCESS = "#3ecf8e"
DANGER = "#f7604f"
WARNING = "#f7c04f"
FG = "#e8eaf0"
FG2 = "#9aa3b8"
BORDER = "#3a3f50"
FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_H = ("Segoe UI", 14, "bold")
FONT_SM = ("Segoe UI", 9)


# ─── FENÊTRE RÉCAP DÉTAIL ─────────────────────────────────────────────────────
class FenetreRecap(tk.Toplevel):
    def __init__(self, master: tk.Tk, row: dict[str, Any]) -> None:
        super().__init__(master)
        self.title("📄  Récapitulatif")
        self.geometry("600x480")
        self.minsize(480, 360)
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build(row)
        self.transient(master)
        self.grab_set()
        x: int = master.winfo_rootx() + (master.winfo_width() - 600) // 2
        y: int = master.winfo_rooty() + (master.winfo_height() - 480) // 2
        self.geometry(f"+{x}+{y}")

    def _section(self, parent: tk.Frame, label: str, value: str, fg_val: str = FG) -> None:
        tk.Label(parent, text=label, bg=BG2, fg=FG2, font=FONT_SM, anchor="w").pack(
            fill="x", padx=14, pady=(10, 2)
        )
        frame_val = tk.Frame(parent, bg=BG3, padx=10, pady=8)
        frame_val.pack(fill="x", padx=14)
        txt = tk.Text(
            frame_val,
            bg=BG3,
            fg=fg_val,
            font=FONT,
            relief="flat",
            bd=0,
            wrap="word",
            height=3,
            state="normal",
        )
        txt.insert("1.0", value if value and value not in ("None", "") else "—")
        txt.configure(state="disabled")
        txt.pack(fill="x")

    def _build(self, row: dict[str, Any]) -> None:
        hdr = tk.Frame(self, bg=BG2, pady=12, padx=16)
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="📄  Récapitulatif de l'entrée", bg=BG2, fg=ACCENT2, font=FONT_H
        ).pack(side="left")
        type_val = row.get("type", "normale")
        badge_color = (
            SUCCESS
            if type_val.lower() == "true"
            else (DANGER if type_val.lower() == "false" else FG2)
        )
        tk.Label(
            hdr,
            text=f"  {type_val.upper()}  ",
            bg=badge_color,
            fg="#fff",
            font=FONT_B,
            padx=8,
            pady=4,
        ).pack(side="right", padx=6)

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG2)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)

        canvas.bind("<Configure>", _on_resize)
        inner.bind(
            "<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self._section(inner, "❓  Question", row.get("question", ""), fg_val=ACCENT2)
        self._section(inner, "✅  Réponse", row.get("reponse", ""), fg_val=SUCCESS)
        self._section(
            inner, "💬  Commentaire", row.get("commentaire", ""), fg_val=WARNING
        )

        meta = tk.Frame(inner, bg=BG2)
        meta.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(
            meta, text=f"🆔 ID : {row.get('id','—')}", bg=BG2, fg=FG2, font=FONT_SM
        ).pack(side="left", padx=(0, 20))
        tk.Label(
            meta, text=f"📅 Date : {row.get('date','—')}", bg=BG2, fg=FG2, font=FONT_SM
        ).pack(side="left")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=14, pady=8)
        ttk.Button(
            inner, text="✖  Fermer", style="Danger.TButton", command=self.destroy
        ).pack(pady=(0, 14))


# ─── APPLICATION ─────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        log.info("Démarrage de l'application Reconditionnement.")
        create_db()
        self.title("Reconditionnement")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self._style()
        self._build()
        self.refresh_table()

    def _style(self) -> None:
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(
            ".",
            background=BG,
            foreground=FG,
            font=FONT,
            troughcolor=BG2,
            bordercolor=BORDER,
            relief="flat",
        )
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=BG2)
        s.configure("TLabel", background=BG, foreground=FG, font=FONT)
        s.configure("Title.TLabel", background=BG, foreground=ACCENT2, font=FONT_H)
        s.configure("Sub.TLabel", background=BG2, foreground=FG2, font=FONT_SM)
        s.configure(
            "TButton",
            background=BG3,
            foreground=FG,
            font=FONT,
            borderwidth=0,
            focusthickness=0,
            padding=(10, 6),
        )
        s.map(
            "TButton",
            background=[("active", ACCENT), ("pressed", "#3a6fcf")],
            foreground=[("active", "#fff")],
        )
        s.configure("Accent.TButton", background=ACCENT, foreground="#fff", font=FONT_B)
        s.map("Accent.TButton", background=[("active", ACCENT2)])
        s.configure("Danger.TButton", background=DANGER, foreground="#fff", font=FONT_B)
        s.map("Danger.TButton", background=[("active", "#c94535")])
        s.configure(
            "Success.TButton", background=SUCCESS, foreground="#fff", font=FONT_B
        )
        s.map("Success.TButton", background=[("active", "#2da06a")])
        s.configure(
            "TEntry",
            fieldbackground=BG3,
            foreground=FG,
            bordercolor=BORDER,
            insertcolor=FG,
            font=FONT,
            padding=6,
        )
        s.configure("TCombobox", fieldbackground=BG3, foreground=FG, font=FONT)
        s.configure(
            "Treeview",
            background=BG2,
            foreground=FG,
            fieldbackground=BG2,
            rowheight=30,
            font=FONT,
        )
        s.configure(
            "Treeview.Heading",
            background=BG3,
            foreground=ACCENT2,
            font=FONT_B,
            relief="flat",
        )
        s.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#fff")],
        )
        s.configure("TNotebook", background=BG, tabmargins=[0, 0, 0, 0])
        s.configure(
            "TNotebook.Tab", background=BG3, foreground=FG2, font=FONT, padding=[14, 8]
        )
        s.map(
            "TNotebook.Tab",
            background=[("selected", BG2)],
            foreground=[("selected", ACCENT2)],
        )
        s.configure("TSeparator", background=BORDER)
        s.configure(
            "TScrollbar",
            background=BG3,
            troughcolor=BG2,
            arrowcolor=FG2,
            bordercolor=BORDER,
        )

    def _build(self) -> None:
        hdr = tk.Frame(self, bg=BG2, pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="⚙  Reconditionnement",
            bg=BG2,
            fg=ACCENT2,
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        self.lbl_count = tk.Label(hdr, text="", bg=BG2, fg=FG2, font=FONT_SM)
        self.lbl_count.pack(side="right", padx=10)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=8)

        self.tab_main = ttk.Frame(self.nb)
        self.tab_db = ttk.Frame(self.nb)
        self.tab_recap = ttk.Frame(self.nb)
        self.tab_export = ttk.Frame(self.nb)
        self.tab_aide = ttk.Frame(self.nb)
        self.nb.add(self.tab_main, text="  📋  Questions  ")
        self.nb.add(self.tab_db, text="  🗄️  Base de données  ")
        self.nb.add(self.tab_recap, text="  📊  Récapitulatif  ")
        self.nb.add(self.tab_export, text="  💾  Export / Import  ")
        self.nb.add(self.tab_aide, text="  ❓  Aide  ")

        self._build_main(self.tab_main)
        self._build_db(self.tab_db)
        self._build_recap(self.tab_recap)
        self._build_export(self.tab_export)
        self._build_aide(self.tab_aide)

        # Rafraîchit le récap automatiquement à chaque fois qu'on ouvre l'onglet
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    # ── Tab 1 : Questions ─────────────────────────────────────────────────────
    def _build_main(self, parent: ttk.Frame) -> None:
        left = tk.Frame(parent, bg=BG2, width=310)
        left.pack(side="left", fill="y", padx=(0, 6), pady=6)
        left.pack_propagate(False)

        tk.Label(left, text="Nouvelle entrée", bg=BG2, fg=ACCENT2, font=FONT_B).pack(
            anchor="w", padx=14, pady=(14, 6)
        )
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)

        def lbl(txt):
            tk.Label(left, text=txt, bg=BG2, fg=FG2, font=FONT_SM).pack(
                anchor="w", padx=14, pady=(10, 2)
            )

        lbl("Question *")
        self.ent_question = ttk.Entry(left, width=32)
        self.ent_question.pack(padx=14, fill="x")

        lbl("Réponse")
        self.ent_reponse = ttk.Entry(left, width=32)
        self.ent_reponse.pack(padx=14, fill="x")

        lbl("Type")
        self.cmb_type = ttk.Combobox(
            left, values=["normale", "True", "False"], state="readonly", width=30
        )
        self.cmb_type.current(0)
        self.cmb_type.pack(padx=14, fill="x")

        lbl("Commentaire")
        self.ent_comment = ttk.Entry(left, width=32)
        self.ent_comment.pack(padx=14, fill="x")

        tk.Frame(left, bg=BG2, height=12).pack()
        ttk.Button(
            left, text="➕  Ajouter", style="Accent.TButton", command=self._ajouter
        ).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=6).pack()
        ttk.Button(left, text="✏️  Modifier la sélection", command=self._modifier).pack(
            padx=14, fill="x"
        )
        tk.Frame(left, bg=BG2, height=6).pack()
        ttk.Button(
            left,
            text="🗑️  Supprimer la sélection",
            style="Danger.TButton",
            command=self._supprimer_mem,
        ).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=16).pack()
        ttk.Button(
            left,
            text="🔄  Charger depuis la BDD",
            style="Success.TButton",
            command=self._charger_db,
        ).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=6).pack()
        ttk.Button(left, text="⬆️  Envoyer liste → BDD", command=self._envoyer_db).pack(
            padx=14, fill="x"
        )
        tk.Frame(left, bg=BG2, height=16).pack()
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)
        tk.Frame(left, bg=BG2, height=8).pack()
        tk.Button(
            left,
            text="🔎  Voir le récap",
            bg=ACCENT,
            fg="#fff",
            font=FONT_B,
            relief="flat",
            bd=0,
            pady=8,
            activebackground=ACCENT2,
            activeforeground="#fff",
            cursor="hand2",
            command=self._ouvrir_recap,
        ).pack(padx=14, fill="x")

        # Right panel
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, pady=6, padx=(0, 6))

        sf = tk.Frame(right, bg=BG)
        sf.pack(fill="x", pady=(0, 6))
        tk.Label(sf, text="🔍", bg=BG, fg=FG2, font=FONT).pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.refresh_table())
        ttk.Entry(sf, textvariable=self.search_var, width=30).pack(side="left")
        tk.Button(
            sf,
            text="🔎 Récap",
            bg=ACCENT,
            fg="#fff",
            font=FONT_B,
            relief="flat",
            bd=0,
            padx=10,
            activebackground=ACCENT2,
            activeforeground="#fff",
            cursor="hand2",
            command=self._ouvrir_recap,
        ).pack(side="right", padx=6)

        cols = ("N°", "Question", "Réponse", "Type", "Commentaire", "Date")
        self.tree = ttk.Treeview(
            right, columns=cols, show="headings", selectmode="browse"
        )
        widths = [40, 230, 160, 80, 180, 150]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=30)

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(right, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._ouvrir_recap())

        self.tree.tag_configure("true", background="#1d3a2e", foreground="#3ecf8e")
        self.tree.tag_configure("false", background="#3a1d1d", foreground="#f7604f")
        self.tree.tag_configure("normale", background=BG2)

    # ── Tab 2 : Base de données ───────────────────────────────────────────────
    def _build_db(self, parent: ttk.Frame) -> None:
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", pady=(8, 4), padx=8)
        tk.Label(
            top, text="Contenu de la base SQLite", bg=BG, fg=ACCENT2, font=FONT_B
        ).pack(side="left")
        ttk.Button(top, text="🔄  Rafraîchir", command=self._refresh_db_tab).pack(
            side="left", padx=10
        )

        right_top = tk.Frame(top, bg=BG)
        right_top.pack(side="right")
        tk.Label(right_top, text="ID à supprimer :", bg=BG, fg=FG2, font=FONT_SM).pack(
            side="left"
        )
        self.ent_del_id = ttk.Entry(right_top, width=8)
        self.ent_del_id.pack(side="left", padx=4)
        ttk.Button(
            right_top,
            text="Supprimer",
            style="Danger.TButton",
            command=self._supprimer_db,
        ).pack(side="left")

        cols = ("ID", "Question", "Réponse", "Type", "Commentaire", "Date")
        self.tree_db = ttk.Treeview(parent, columns=cols, show="headings")
        widths = [45, 240, 160, 80, 180, 150]
        for col, w in zip(cols, widths):
            self.tree_db.heading(col, text=col)
            self.tree_db.column(col, width=w, minwidth=30)
        vsb2 = ttk.Scrollbar(parent, orient="vertical", command=self.tree_db.yview)
        hsb2 = ttk.Scrollbar(parent, orient="horizontal", command=self.tree_db.xview)
        self.tree_db.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)
        vsb2.pack(side="right", fill="y")
        hsb2.pack(side="bottom", fill="x")
        self.tree_db.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.tree_db.tag_configure("true", background="#1d3a2e", foreground="#3ecf8e")
        self.tree_db.tag_configure("false", background="#3a1d1d", foreground="#f7604f")
        self.tree_db.bind("<Double-1>", lambda e: self._ouvrir_recap_db())
        self._refresh_db_tab()

    # ── Tab 3 : Récapitulatif ─────────────────────────────────────────────────
    def _build_recap(self, parent: ttk.Frame) -> None:
        # Barre du haut
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", pady=(8, 4), padx=8)

        tk.Label(
            top,
            text="📊  Toutes les questions & réponses",
            bg=BG,
            fg=ACCENT2,
            font=FONT_B,
        ).pack(side="left")
        ttk.Button(top, text="🔄  Rafraîchir", command=self._refresh_recap).pack(
            side="left", padx=10
        )

        # Filtre type
        tk.Label(top, text="Filtrer :", bg=BG, fg=FG2, font=FONT_SM).pack(
            side="right", padx=(0, 4)
        )
        self.recap_filtre = ttk.Combobox(
            top, values=["Tous", "True", "False", "normale"], state="readonly", width=10
        )
        self.recap_filtre.current(0)
        self.recap_filtre.pack(side="right", padx=(0, 8))
        self.recap_filtre.bind("<<ComboboxSelected>>", lambda _: self._refresh_recap())

        # Statistiques
        self.frm_stats = tk.Frame(parent, bg=BG3)
        self.frm_stats.pack(fill="x", padx=8, pady=(0, 6))
        self.lbl_stat_total = tk.Label(
            self.frm_stats,
            text="Total : 0",
            bg=BG3,
            fg=FG,
            font=FONT_B,
            padx=16,
            pady=6,
        )
        self.lbl_stat_ok = tk.Label(
            self.frm_stats,
            text="✔ Conformes : 0",
            bg=BG3,
            fg=SUCCESS,
            font=FONT_B,
            padx=16,
            pady=6,
        )
        self.lbl_stat_nok = tk.Label(
            self.frm_stats,
            text="✘ Défauts : 0",
            bg=BG3,
            fg=DANGER,
            font=FONT_B,
            padx=16,
            pady=6,
        )
        self.lbl_stat_norm = tk.Label(
            self.frm_stats,
            text="— Normales : 0",
            bg=BG3,
            fg=FG2,
            font=FONT_B,
            padx=16,
            pady=6,
        )
        for lbl in (
            self.lbl_stat_total,
            self.lbl_stat_ok,
            self.lbl_stat_nok,
            self.lbl_stat_norm,
        ):
            lbl.pack(side="left")

        # Zone de contenu scrollable avec cartes
        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.recap_inner = tk.Frame(canvas, bg=BG)
        self._recap_win_id = canvas.create_window(
            (0, 0), window=self.recap_inner, anchor="nw"
        )

        def _on_resize(e):
            canvas.itemconfig(self._recap_win_id, width=e.width)

        canvas.bind("<Configure>", _on_resize)
        self.recap_inner.bind(
            "<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Scroll à la molette
        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _scroll)

        self._recap_canvas = canvas

    def _refresh_recap(self) -> None:
        """Reconstruit les cartes de l'onglet récapitulatif."""
        # Vider
        for w in self.recap_inner.winfo_children():
            w.destroy()

        filtre = self.recap_filtre.get() if hasattr(self, "recap_filtre") else "Tous"
        source = liste  # toujours depuis la liste en mémoire

        total = len(source)
        n_ok = sum(1 for r in source if str(r.get("type", "")).lower() == "true")
        n_nok = sum(1 for r in source if str(r.get("type", "")).lower() == "false")
        n_norm = total - n_ok - n_nok

        self.lbl_stat_total.config(text=f"Total : {total}")
        self.lbl_stat_ok.config(text=f"✔ Conformes : {n_ok}")
        self.lbl_stat_nok.config(text=f"✘ Défauts : {n_nok}")
        self.lbl_stat_norm.config(text=f"— Normales : {n_norm}")

        filtered = [
            r
            for r in source
            if filtre == "Tous" or str(r.get("type", "")).lower() == filtre.lower()
        ]

        if not filtered:
            tk.Label(
                self.recap_inner,
                text="Aucune entrée à afficher.\nChargez des données depuis l'onglet Questions.",
                bg=BG,
                fg=FG2,
                font=FONT_H,
                justify="center",
            ).pack(pady=60)
            return

        for i, row in enumerate(filtered):
            type_val = str(row.get("type", "normale")).lower()
            if type_val == "true":
                border_col = SUCCESS
                badge_col = SUCCESS
                badge_txt = "✔  CONFORME"
            elif type_val == "false":
                border_col = DANGER
                badge_col = DANGER
                badge_txt = "✘  DÉFAUT"
            else:
                border_col = BORDER
                badge_col = FG2
                badge_txt = "—  NORMALE"

            # Carte extérieure (bordure colorée gauche simulée)
            outer = tk.Frame(self.recap_inner, bg=border_col)
            outer.pack(fill="x", padx=10, pady=4)

            card = tk.Frame(outer, bg=BG2, padx=14, pady=10)
            card.pack(fill="x", padx=(3, 0))  # laisser 3px à gauche = bordure colorée

            # Ligne 1 : numéro + badge type + date
            row1 = tk.Frame(card, bg=BG2)
            row1.pack(fill="x")
            tk.Label(row1, text=f"#{i+1}", bg=BG2, fg=FG2, font=FONT_SM).pack(
                side="left", padx=(0, 8)
            )
            tk.Label(
                row1,
                text=badge_txt,
                bg=badge_col,
                fg="#fff",
                font=("Segoe UI", 8, "bold"),
                padx=6,
                pady=2,
            ).pack(side="left")
            date_val = row.get("date", "")
            if date_val:
                tk.Label(
                    row1, text=f"📅 {date_val}", bg=BG2, fg=FG2, font=FONT_SM
                ).pack(side="right")

            # Ligne 2 : Question
            row2 = tk.Frame(card, bg=BG2)
            row2.pack(fill="x", pady=(6, 2))
            tk.Label(
                row2, text="Q :", bg=BG2, fg=ACCENT2, font=FONT_B, width=3, anchor="w"
            ).pack(side="left")
            q_txt = row.get("question", "—")
            tk.Label(
                row2,
                text=q_txt,
                bg=BG2,
                fg=FG,
                font=FONT,
                anchor="w",
                wraplength=700,
                justify="left",
            ).pack(side="left", fill="x", expand=True)

            # Ligne 3 : Réponse
            rep_val = row.get("reponse", "None")
            row3 = tk.Frame(card, bg=BG2)
            row3.pack(fill="x", pady=2)
            tk.Label(
                row3, text="R :", bg=BG2, fg=SUCCESS, font=FONT_B, width=3, anchor="w"
            ).pack(side="left")
            tk.Label(
                row3,
                text=rep_val if rep_val not in ("None", "") else "—",
                bg=BG2,
                fg=FG if rep_val not in ("None", "") else FG2,
                font=FONT,
                anchor="w",
                wraplength=700,
                justify="left",
            ).pack(side="left", fill="x", expand=True)

            # Ligne 4 : Commentaire (seulement si présent)
            com_val = row.get("commentaire", "None")
            if com_val and com_val not in ("None", ""):
                row4 = tk.Frame(card, bg=BG2)
                row4.pack(fill="x", pady=(2, 0))
                tk.Label(
                    row4,
                    text="💬 :",
                    bg=BG2,
                    fg=WARNING,
                    font=FONT_B,
                    width=3,
                    anchor="w",
                ).pack(side="left")
                tk.Label(
                    row4,
                    text=com_val,
                    bg=BG2,
                    fg=WARNING,
                    font=FONT_SM,
                    anchor="w",
                    wraplength=700,
                    justify="left",
                ).pack(side="left", fill="x", expand=True)

    # ── Tab 4 : Export / Import ───────────────────────────────────────────────
    def _build_export(self, parent: ttk.Frame) -> None:
        frame = tk.Frame(parent, bg=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Export & Import", bg=BG, fg=ACCENT2, font=FONT_H).pack(
            pady=(0, 20)
        )

        cards = [
            ("💾  Exporter en TXT", WARNING, self._exp_txt),
            ("📦  Exporter en JSON", ACCENT, self._exp_json),
            ("📊  Exporter en CSV", SUCCESS, self._exp_csv),
            ("📂  Importer JSON", FG2, self._imp_json),
        ]
        for txt, col, cmd in cards:
            btn = tk.Button(
                frame,
                text=txt,
                bg=BG2,
                fg=col,
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                bd=0,
                pady=14,
                padx=30,
                activebackground=BG3,
                activeforeground=col,
                cursor="hand2",
                command=cmd,
            )
            btn.pack(fill="x", pady=5)

        tk.Frame(frame, bg=BG, height=20).pack()
        self.lbl_export_status = tk.Label(
            frame, text="", bg=BG, fg=SUCCESS, font=FONT_SM
        )
        self.lbl_export_status.pack()

    # ── Tab 5 : Aide ──────────────────────────────────────────────────────────
    def _build_aide(self, parent: ttk.Frame) -> None:
        """
        Onglet d'aide — affiche un fichier HTML hors ligne dans le navigateur
        par défaut du système (aucune dépendance externe requise).

        ► Placez votre fichier HTML à côté de ce script sous le nom  aide.html
          OU modifiez HTML_AIDE_PATH pour pointer vers votre fichier.
        """

        # ── Chemin vers votre fichier HTML d'aide ────────────────────────────
        HTML_AIDE_PATH = Path(__file__).parent / "aide.html"

        # ── Contenu HTML par défaut (utilisé si aide.html est absent) ────────
        # ╔══════════════════════════════════════════════════════════════════╗
        # ║                    MODIFIER HTML ICI                             ║
        # ╚══════════════════════════════════════════════════════════════════╝
        HTML_CONTENU_DEFAUT = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aide — Reconditionnement</title>
<style>

  /* ── Reset & base ───────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: "Segoe UI", Arial, sans-serif;
    background: #1a1d23;
    color: #e8eaf0;
    font-size: 16px;
    line-height: 1.7;
  }

  /* ── Mise en page ───────────────────────────────── */
  .page {
    display: flex;
    min-height: 100vh;
  }

  /* ── Sidebar (menu gauche) ──────────────────────── */
  .sidebar {
    width: 240px;
    min-width: 240px;
    background: #13151a;
    padding: 28px 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #2c3140;
  }

  .sidebar-logo {
    padding: 0 24px 24px;
    border-bottom: 1px solid #2c3140;
    margin-bottom: 16px;
  }

  .sidebar-logo h1 {
    font-size: 17px;
    color: #7fb3ff;
    font-weight: 700;
  }

  .sidebar-logo p {
    font-size: 12px;
    color: #5a6380;
    margin-top: 2px;
  }

  .nav-section {
    padding: 8px 24px 4px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #3a4060;
    font-weight: 700;
    margin-top: 8px;
  }

  .nav a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 24px;
    color: #9aa3b8;
    text-decoration: none;
    font-size: 14px;
    border-left: 3px solid transparent;
    transition: all 0.15s;
  }

  .nav a:hover,
  .nav a.active {
    color: #e8eaf0;
    background: #1e2230;
    border-left-color: #4f8ef7;
  }

  .nav a .icon { font-size: 16px; width: 20px; text-align: center; }

  /* ── Contenu principal ──────────────────────────── */
  .content {
    flex: 1;
    padding: 48px 56px;
    max-width: 860px;
  }

  /* ── En-tête de section ─────────────────────────── */
  .section {
    margin-bottom: 64px;
    scroll-margin-top: 32px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 2px solid #2c3140;
  }

  .section-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
  }

  .icon-blue   { background: #1a2a4a; }
  .icon-green  { background: #1a3a2a; }
  .icon-orange { background: #3a2a10; }
  .icon-purple { background: #2a1a3a; }
  .icon-red    { background: #3a1a1a; }

  .section-header h2 {
    font-size: 22px;
    font-weight: 700;
    color: #e8eaf0;
  }

  .section-header p {
    font-size: 13px;
    color: #5a6380;
    margin-top: 2px;
  }

  /* ── Texte courant ──────────────────────────────── */
  p { color: #9aa3b8; margin-bottom: 14px; }

  strong { color: #e8eaf0; }

  /* ── Étapes numérotées ──────────────────────────── */
  .steps { list-style: none; margin: 20px 0; }

  .steps li {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 14px;
  }

  .step-num {
    min-width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #4f8ef7;
    color: #fff;
    font-size: 13px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2px;
    flex-shrink: 0;
  }

  .step-text { color: #c8cad8; font-size: 15px; }
  .step-text strong { color: #e8eaf0; }

  /* ── Encadrés colorés ───────────────────────────── */
  .box {
    border-radius: 8px;
    padding: 16px 20px;
    margin: 18px 0;
    font-size: 14px;
  }

  .box-tip   { background: #1a2a4a; border-left: 4px solid #4f8ef7; color: #9ab8e8; }
  .box-ok    { background: #1a3020; border-left: 4px solid #3ecf8e; color: #7ec8a0; }
  .box-warn  { background: #2a2010; border-left: 4px solid #f7c04f; color: #c8a060; }

  .box strong { color: inherit; filter: brightness(1.3); }

  /* ── Badges de type ─────────────────────────────── */
  .badges { display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
  }

  .badge-ok    { background: #1a3020; color: #3ecf8e; border: 1px solid #2a5030; }
  .badge-nok   { background: #3a1a1a; color: #f7604f; border: 1px solid #5a2a2a; }
  .badge-norm  { background: #2c3140; color: #9aa3b8; border: 1px solid #3a4050; }

  /* ── Tableau des boutons ────────────────────────── */
  .btn-table { width: 100%; border-collapse: collapse; margin: 16px 0; }

  .btn-table th {
    text-align: left;
    padding: 10px 14px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #5a6380;
    border-bottom: 1px solid #2c3140;
  }

  .btn-table td {
    padding: 12px 14px;
    border-bottom: 1px solid #1e2230;
    font-size: 14px;
    color: #9aa3b8;
    vertical-align: top;
  }

  .btn-table td:first-child {
    color: #e8eaf0;
    font-weight: 600;
    white-space: nowrap;
    width: 200px;
  }

  /* ── Mini champ illustré ────────────────────────── */
  .field-demo {
    background: #13151a;
    border: 1px solid #2c3140;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 16px 0;
  }

  .field-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .field-row:last-child { margin-bottom: 0; }

  .field-label {
    width: 120px;
    font-size: 12px;
    color: #5a6380;
    flex-shrink: 0;
  }

  .field-val {
    background: #2c3140;
    border-radius: 5px;
    padding: 5px 12px;
    font-size: 13px;
    color: #c8cad8;
    flex: 1;
  }

  .field-req {
    font-size: 11px;
    color: #f7604f;
    margin-left: 6px;
  }

  /* ── Onglets illustration ───────────────────────── */
  .tabs-demo {
    display: flex;
    gap: 0;
    background: #13151a;
    border-radius: 8px 8px 0 0;
    border: 1px solid #2c3140;
    border-bottom: none;
    overflow: hidden;
    margin-top: 16px;
  }

  .tab-demo {
    padding: 10px 18px;
    font-size: 13px;
    color: #5a6380;
    border-right: 1px solid #2c3140;
  }

  .tab-demo.on {
    background: #1e2230;
    color: #7fb3ff;
    font-weight: 600;
  }

  .tabs-desc {
    background: #1e2230;
    border: 1px solid #2c3140;
    border-radius: 0 0 8px 8px;
    padding: 14px 20px;
    font-size: 13px;
    color: #7a8398;
    margin-bottom: 16px;
  }

  /* ── FAQ ────────────────────────────────────────── */
  .faq-item {
    border: 1px solid #2c3140;
    border-radius: 8px;
    margin-bottom: 10px;
    overflow: hidden;
  }

  .faq-q {
    padding: 14px 18px;
    font-size: 15px;
    font-weight: 600;
    color: #c8cad8;
    background: #1e2230;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
  }

  .faq-q:hover { background: #252a38; }

  .faq-q::after { content: "▾"; color: #4f8ef7; font-size: 18px; }

  .faq-a {
    padding: 14px 18px;
    font-size: 14px;
    color: #9aa3b8;
    background: #1a1d23;
    border-top: 1px solid #2c3140;
    display: none;
  }

  .faq-item.open .faq-a  { display: block; }
  .faq-item.open .faq-q::after { content: "▴"; }

  /* ── Mise en avant d'une info ───────────────────── */
  .highlight {
    background: #4f8ef720;
    border: 1px solid #4f8ef740;
    border-radius: 6px;
    padding: 4px 10px;
    color: #7fb3ff;
    font-size: 14px;
    display: inline;
  }

  /* ── Responsive ─────────────────────────────────── */
  @media (max-width: 700px) {
    .sidebar { display: none; }
    .content { padding: 24px 20px; }
  }

</style>
</head>
<body>

<div class="page">

  <!-- ═══════════════ SIDEBAR ═══════════════ -->
  <nav class="sidebar">
    <div class="sidebar-logo">
      <h1>⚙ Reconditionnement</h1>
      <p>Guide d'utilisation</p>
    </div>

    <div class="nav-section">Pour commencer</div>
    <div class="nav">
      <a href="#intro" class="active"><span class="icon">🏠</span> C'est quoi ce logiciel ?</a>
      <a href="#onglets"><span class="icon">📑</span> Les onglets</a>
    </div>

    <div class="nav-section">Les fonctions</div>
    <div class="nav">
      <a href="#questions"><span class="icon">📋</span> Ajouter une entrée</a>
      <a href="#types"><span class="icon">🏷️</span> Les types (OK / Défaut)</a>
      <a href="#recherche"><span class="icon">🔍</span> Rechercher</a>
      <a href="#bdd"><span class="icon">🗄️</span> Base de données</a>
      <a href="#recap"><span class="icon">📊</span> Récapitulatif</a>
      <a href="#export"><span class="icon">💾</span> Exporter</a>
    </div>

    <div class="nav-section">Aide</div>
    <div class="nav">
      <a href="#faq"><span class="icon">❓</span> Questions fréquentes</a>
    </div>
  </nav>

  <!-- ═══════════════ CONTENU ═══════════════ -->
  <main class="content">

    <!-- ── INTRO ── -->
    <section class="section" id="intro">
      <div class="section-header">
        <div class="section-icon icon-blue">🏠</div>
        <div>
          <h2>C'est quoi ce logiciel ?</h2>
          <p>Tout comprendre en 30 secondes</p>
        </div>
      </div>

      <p>Ce logiciel vous permet de <strong>noter et suivre des vérifications</strong> lors du reconditionnement de produits. Pour chaque contrôle effectué, vous enregistrez :</p>

      <div class="field-demo">
        <div class="field-row">
          <span class="field-label">La question</span>
          <span class="field-val">La batterie tient-elle la charge ?</span>
          <span class="field-req">obligatoire</span>
        </div>
        <div class="field-row">
          <span class="field-label">La réponse</span>
          <span class="field-val">Oui, autonomie 8h</span>
        </div>
        <div class="field-row">
          <span class="field-label">Le résultat</span>
          <span class="field-val">✔ Conforme &nbsp;/&nbsp; ✘ Défaut &nbsp;/&nbsp; — Normale</span>
        </div>
        <div class="field-row">
          <span class="field-label">Un commentaire</span>
          <span class="field-val">À surveiller dans 3 mois</span>
        </div>
      </div>

      <div class="box box-tip">
        💡 <strong>En résumé :</strong> c'est un carnet de contrôle qualité numérique. Chaque ligne = un contrôle réalisé sur un produit.
      </div>
    </section>

    <!-- ── ONGLETS ── -->
    <section class="section" id="onglets">
      <div class="section-header">
        <div class="section-icon icon-blue">📑</div>
        <div>
          <h2>Les onglets du logiciel</h2>
          <p>5 onglets, chacun avec un rôle précis</p>
        </div>
      </div>

      <p>En haut de la fenêtre, vous voyez 5 onglets. Cliquez dessus pour changer de section.</p>

      <div class="tabs-demo">
        <div class="tab-demo on">📋 Questions</div>
        <div class="tab-demo">🗄️ Base de données</div>
        <div class="tab-demo">📊 Récapitulatif</div>
        <div class="tab-demo">💾 Export / Import</div>
        <div class="tab-demo">❓ Aide</div>
      </div>
      <div class="tabs-desc">
        <strong style="color:#7fb3ff">📋 Questions</strong> — C'est ici que vous passez la plupart de votre temps. Vous ajoutez, modifiez et consultez vos contrôles.
      </div>

      <table class="btn-table">
        <tr>
          <th>Onglet</th>
          <th>À quoi ça sert ?</th>
        </tr>
        <tr>
          <td>📋 Questions</td>
          <td>Ajouter, modifier, supprimer des contrôles. C'est l'onglet principal.</td>
        </tr>
        <tr>
          <td>🗄️ Base de données</td>
          <td>Voir tout ce qui est enregistré de façon permanente sur votre ordinateur.</td>
        </tr>
        <tr>
          <td>📊 Récapitulatif</td>
          <td>Avoir une vue d'ensemble avec les statistiques (combien de conformes, de défauts…).</td>
        </tr>
        <tr>
          <td>💾 Export / Import</td>
          <td>Sauvegarder vos données dans un fichier (TXT, CSV, JSON) ou en recharger.</td>
        </tr>
        <tr>
          <td>❓ Aide</td>
          <td>Cette page d'aide.</td>
        </tr>
      </table>
    </section>

    <!-- ── QUESTIONS ── -->
    <section class="section" id="questions">
      <div class="section-header">
        <div class="section-icon icon-blue">📋</div>
        <div>
          <h2>Ajouter une nouvelle entrée</h2>
          <p>Onglet « 📋 Questions »</p>
        </div>
      </div>

      <p>Sur la <strong>gauche</strong> de l'onglet Questions, vous avez un formulaire avec 4 champs à remplir.</p>

      <ol class="steps">
        <li>
          <div class="step-num">1</div>
          <div class="step-text">
            <strong>Question</strong> — Écrivez le contrôle à effectuer.<br>
            <span style="color:#5a6380; font-size:13px;">Exemple : « L'écran est-il intact ? »</span><br>
            <span style="color:#f7604f; font-size:12px;">⚠ Ce champ est obligatoire. Sans question, l'entrée ne sera pas enregistrée.</span>
          </div>
        </li>
        <li>
          <div class="step-num">2</div>
          <div class="step-text">
            <strong>Réponse</strong> — Notez le résultat observé.<br>
            <span style="color:#5a6380; font-size:13px;">Exemple : « Oui, aucune fissure »</span>
          </div>
        </li>
        <li>
          <div class="step-num">3</div>
          <div class="step-text">
            <strong>Type</strong> — Choisissez dans la liste déroulante :<br>
            <span style="color:#3ecf8e">✔ True</span> = conforme &nbsp;|&nbsp; <span style="color:#f7604f">✘ False</span> = défaut &nbsp;|&nbsp; <span style="color:#9aa3b8">— normale</span> = neutre
          </div>
        </li>
        <li>
          <div class="step-num">4</div>
          <div class="step-text">
            <strong>Commentaire</strong> — Ajoutez une remarque si besoin (facultatif).<br>
            <span style="color:#5a6380; font-size:13px;">Exemple : « À revérifier après 48h »</span>
          </div>
        </li>
        <li>
          <div class="step-num">5</div>
          <div class="step-text">
            Cliquez sur le bouton <strong style="color:#4f8ef7">➕ Ajouter</strong>. L'entrée apparaît immédiatement dans le tableau à droite.
          </div>
        </li>
      </ol>

      <div class="box box-ok">
        ✔ <strong>Astuce :</strong> après avoir cliqué sur une ligne du tableau, ses informations se chargent automatiquement dans le formulaire. Vous pouvez alors les modifier et cliquer sur <strong>✏️ Modifier la sélection</strong>.
      </div>

      <h3 style="color:#c8cad8; margin: 24px 0 12px; font-size:16px;">Les boutons du panneau gauche</h3>

      <table class="btn-table">
        <tr>
          <th>Bouton</th>
          <th>Ce que ça fait</th>
        </tr>
        <tr>
          <td>➕ Ajouter</td>
          <td>Crée une nouvelle entrée avec ce que vous avez écrit dans le formulaire.</td>
        </tr>
        <tr>
          <td>✏️ Modifier la sélection</td>
          <td>Met à jour la ligne sélectionnée dans le tableau avec les nouvelles valeurs du formulaire.</td>
        </tr>
        <tr>
          <td>🗑️ Supprimer la sélection</td>
          <td>Supprime la ligne sélectionnée <em>de la liste visible</em> (pas de la base de données).</td>
        </tr>
        <tr>
          <td>🔄 Charger depuis la BDD</td>
          <td>Recharge toutes les entrées sauvegardées depuis la base de données.</td>
        </tr>
        <tr>
          <td>⬆️ Envoyer liste → BDD</td>
          <td>Sauvegarde toutes les entrées visibles dans la base de données de façon permanente.</td>
        </tr>
      </table>

      <div class="box box-warn">
        ⚠ <strong>Important :</strong> les données que vous ajoutez sont d'abord en <strong>mémoire temporaire</strong>. Si vous fermez le logiciel sans cliquer sur <strong>⬆️ Envoyer liste → BDD</strong>, elles seront perdues.
      </div>
    </section>

    <!-- ── TYPES ── -->
    <section class="section" id="types">
      <div class="section-header">
        <div class="section-icon icon-green">🏷️</div>
        <div>
          <h2>Les types : Conforme, Défaut, Normale</h2>
          <p>Comprendre les 3 couleurs du logiciel</p>
        </div>
      </div>

      <p>Chaque entrée a un <strong>type</strong> qui indique si le contrôle est passé ou non. Ce type colorie la ligne pour voir d'un coup d'œil l'état du produit.</p>

      <div class="badges">
        <div class="badge badge-ok">✔ True — Conforme</div>
        <div class="badge badge-nok">✘ False — Défaut</div>
        <div class="badge badge-norm">— normale — Neutre</div>
      </div>

      <table class="btn-table">
        <tr>
          <th>Type</th>
          <th>Quand l'utiliser ?</th>
        </tr>
        <tr>
          <td style="color:#3ecf8e">✔ True</td>
          <td>Le contrôle est passé avec succès. Le produit est conforme sur ce point.</td>
        </tr>
        <tr>
          <td style="color:#f7604f">✘ False</td>
          <td>Un problème a été trouvé. Ce point est à corriger ou signaler.</td>
        </tr>
        <tr>
          <td style="color:#9aa3b8">— normale</td>
          <td>Simple note d'information, pas encore évaluée ou sans incidence sur la conformité.</td>
        </tr>
      </table>

      <div class="box box-tip">
        💡 Les lignes en <strong style="color:#3ecf8e">vert</strong> = conformes &nbsp;|&nbsp; en <strong style="color:#f7604f">rouge</strong> = défauts &nbsp;|&nbsp; en gris = normales. Vous pouvez filtrer par type dans l'onglet Récapitulatif.
      </div>
    </section>

    <!-- ── RECHERCHE ── -->
    <section class="section" id="recherche">
      <div class="section-header">
        <div class="section-icon icon-blue">🔍</div>
        <div>
          <h2>Rechercher dans la liste</h2>
          <p>Onglet « 📋 Questions »</p>
        </div>
      </div>

      <p>En haut à droite de l'onglet Questions, il y a une barre de recherche avec une icône 🔍.</p>

      <ol class="steps">
        <li>
          <div class="step-num">1</div>
          <div class="step-text">Cliquez dans le champ à côté de 🔍.</div>
        </li>
        <li>
          <div class="step-num">2</div>
          <div class="step-text">Tapez un mot (ex : « batterie », « écran »).</div>
        </li>
        <li>
          <div class="step-num">3</div>
          <div class="step-text">Le tableau se met à jour <strong>en temps réel</strong> et n'affiche que les lignes qui correspondent.</div>
        </li>
      </ol>

      <div class="box box-tip">
        💡 La recherche fonctionne sur tous les champs : question, réponse, commentaire, date…
      </div>

      <p>Pour voir toutes les entrées de nouveau, effacez simplement ce que vous avez tapé.</p>
    </section>

    <!-- ── BASE DE DONNÉES ── -->
    <section class="section" id="bdd">
      <div class="section-header">
        <div class="section-icon icon-purple">🗄️</div>
        <div>
          <h2>La base de données</h2>
          <p>Onglet « 🗄️ Base de données »</p>
        </div>
      </div>

      <p>Cet onglet affiche <strong>tout ce qui est sauvegardé de façon permanente</strong> sur votre ordinateur dans un fichier appelé <span class="highlight">ma_base.db</span> (situé sur votre Bureau).</p>

      <div class="box box-tip">
        💡 Différence entre la liste et la base de données :<br><br>
        • <strong>La liste</strong> (onglet Questions) = ce que vous voyez à l'écran en ce moment. Elle est temporaire.<br>
        • <strong>La base de données</strong> = ce qui est enregistré sur le disque. Elle survit à la fermeture du logiciel.
      </div>

      <h3 style="color:#c8cad8; margin: 24px 0 12px; font-size:16px;">Supprimer une entrée de la base</h3>

      <ol class="steps">
        <li>
          <div class="step-num">1</div>
          <div class="step-text">Repérez le numéro <strong>ID</strong> de la ligne à supprimer (colonne tout à gauche du tableau).</div>
        </li>
        <li>
          <div class="step-num">2</div>
          <div class="step-text">Tapez ce numéro dans le champ <strong>« ID à supprimer »</strong> en haut à droite.</div>
        </li>
        <li>
          <div class="step-num">3</div>
          <div class="step-text">Cliquez sur <strong style="color:#f7604f">Supprimer</strong>. Une confirmation vous sera demandée.</div>
        </li>
      </ol>

      <div class="box box-warn">
        ⚠ La suppression dans la base de données est <strong>définitive</strong>. Il n'y a pas de bouton « annuler ».
      </div>

      <p>Vous pouvez aussi <strong>double-cliquer</strong> sur une ligne pour afficher le détail complet de cette entrée.</p>
    </section>

    <!-- ── RÉCAPITULATIF ── -->
    <section class="section" id="recap">
      <div class="section-header">
        <div class="section-icon icon-green">📊</div>
        <div>
          <h2>Le récapitulatif</h2>
          <p>Onglet « 📊 Récapitulatif »</p>
        </div>
      </div>

      <p>Cet onglet vous donne une <strong>vue d'ensemble</strong> de toutes vos entrées sous forme de cartes colorées, avec un compteur en haut.</p>

      <div class="field-demo" style="display:flex; gap:32px; padding:16px 24px; flex-wrap:wrap;">
        <div style="text-align:center;">
          <div style="font-size:22px; font-weight:700; color:#e8eaf0;">12</div>
          <div style="font-size:12px; color:#5a6380;">Total</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:22px; font-weight:700; color:#3ecf8e;">8</div>
          <div style="font-size:12px; color:#5a6380;">Conformes</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:22px; font-weight:700; color:#f7604f;">2</div>
          <div style="font-size:12px; color:#5a6380;">Défauts</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:22px; font-weight:700; color:#9aa3b8;">2</div>
          <div style="font-size:12px; color:#5a6380;">Normales</div>
        </div>
      </div>

      <h3 style="color:#c8cad8; margin: 24px 0 12px; font-size:16px;">Filtrer par type</h3>

      <p>En haut à droite de l'onglet, une liste déroulante <strong>Filtrer</strong> vous permet de n'afficher que les conformes, que les défauts, ou toutes les entrées.</p>

      <div class="box box-tip">
        💡 L'onglet se rafraîchit automatiquement chaque fois que vous cliquez dessus. Vous pouvez aussi cliquer sur <strong>🔄 Rafraîchir</strong>.
      </div>
    </section>

    <!-- ── EXPORT ── -->
    <section class="section" id="export">
      <div class="section-header">
        <div class="section-icon icon-orange">💾</div>
        <div>
          <h2>Exporter et importer des données</h2>
          <p>Onglet « 💾 Export / Import »</p>
        </div>
      </div>

      <p>Cet onglet vous permet de <strong>sauvegarder vos données dans un fichier</strong> ou d'en recharger depuis un fichier existant. Les fichiers sont créés automatiquement dans un dossier <span class="highlight">reconditionnement</span> sur votre Bureau.</p>

      <table class="btn-table">
        <tr>
          <th>Bouton</th>
          <th>Ce que ça crée</th>
          <th>Pour quoi faire ?</th>
        </tr>
        <tr>
          <td>💾 Exporter en TXT</td>
          <td>Un fichier texte simple (.txt)</td>
          <td>Facile à lire dans n'importe quel éditeur de texte.</td>
        </tr>
        <tr>
          <td>📦 Exporter en JSON</td>
          <td>Un fichier JSON (.json)</td>
          <td>Pour partager les données ou les réimporter plus tard.</td>
        </tr>
        <tr>
          <td>📊 Exporter en CSV</td>
          <td>Un tableau (.csv)</td>
          <td>Pour ouvrir dans Excel ou LibreOffice Calc.</td>
        </tr>
        <tr>
          <td>📂 Importer JSON</td>
          <td>—</td>
          <td>Recharge des données depuis un fichier JSON précédemment exporté.</td>
        </tr>
      </table>

      <ol class="steps">
        <li>
          <div class="step-num">1</div>
          <div class="step-text">Cliquez sur le format souhaité (ex : <strong>📊 Exporter en CSV</strong>).</div>
        </li>
        <li>
          <div class="step-num">2</div>
          <div class="step-text">Une fenêtre s'ouvre et vous demande un <strong>nom de fichier</strong>. Tapez le nom sans extension (ex : <em>controle_janvier</em>).</div>
        </li>
        <li>
          <div class="step-num">3</div>
          <div class="step-text">Le fichier est créé sur votre Bureau dans le dossier <strong>reconditionnement</strong>.</div>
        </li>
      </ol>

      <div class="box box-ok">
        ✔ Un message de confirmation en bas de l'écran vous indique que l'export a réussi.
      </div>
    </section>

    <!-- ── FAQ ── -->
    <section class="section" id="faq">
      <div class="section-header">
        <div class="section-icon icon-red">❓</div>
        <div>
          <h2>Questions fréquentes</h2>
          <p>Les problèmes les plus courants</p>
        </div>
      </div>

      <div class="faq-item">
        <div class="faq-q" onclick="toggle(this)">J'ai ajouté des entrées mais elles ont disparu après avoir relancé le logiciel.</div>
        <div class="faq-a">Vous avez oublié de sauvegarder. Dans l'onglet <strong>📋 Questions</strong>, cliquez sur <strong>⬆️ Envoyer liste → BDD</strong> avant de fermer le logiciel. Ensuite, à la prochaine ouverture, cliquez sur <strong>🔄 Charger depuis la BDD</strong>.</div>
      </div>

      <div class="faq-item">
        <div class="faq-q" onclick="toggle(this)">Le message « Cette question est déjà en base » apparaît.</div>
        <div class="faq-a">La question que vous essayez d'ajouter existe déjà dans la base de données. Chaque question doit être unique. Modifiez légèrement le texte si vous avez besoin d'une entrée similaire.</div>
      </div>

      <div class="faq-item">
        <div class="faq-q" onclick="toggle(this)">Je ne vois rien dans le tableau alors que j'ai des données.</div>
        <div class="faq-a">Vérifiez si vous n'avez pas du texte dans la barre de recherche 🔍. Effacez-la pour voir toutes les entrées. Si le tableau est toujours vide, cliquez sur <strong>🔄 Charger depuis la BDD</strong>.</div>
      </div>

      <div class="faq-item">
        <div class="faq-q" onclick="toggle(this)">Où est enregistré le fichier de base de données ?</div>
        <div class="faq-a">Le fichier s'appelle <strong>ma_base.db</strong> et il se trouve sur votre <strong>Bureau</strong> (ou dossier Desktop). Ne le supprimez pas, il contient toutes vos données.</div>
      </div>

      <div class="faq-item">
        <div class="faq-q" onclick="toggle(this)">Comment supprimer toutes les entrées d'un coup ?</div>
        <div class="faq-a">Il n'y a pas de bouton « tout effacer » pour éviter les suppressions accidentelles. Vous devez supprimer les entrées une par une depuis l'onglet <strong>🗄️ Base de données</strong> en utilisant leur ID.</div>
      </div>

      <div class="faq-item">
        <div class="faq-q" onclick="toggle(this)">Le double-clic sur une ligne, ça fait quoi ?</div>
        <div class="faq-a">Dans les onglets <strong>📋 Questions</strong> et <strong>🗄️ Base de données</strong>, double-cliquer sur une ligne ouvre une fenêtre de détail avec toutes les informations de cette entrée affichées clairement.</div>
      </div>

    </section>

  </main>
</div>

<script>
  // FAQ accordion
  function toggle(el) {
    el.parentElement.classList.toggle("open");
  }

  // Highlight nav on scroll
  const sections = document.querySelectorAll("section[id]");
  const links    = document.querySelectorAll(".nav a");

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 80) current = s.id;
    });
    links.forEach(a => {
      a.classList.toggle("active", a.getAttribute("href") === "#" + current);
    });
  });
</script>

</body>
</html>
"""

        # ─────────────────────────────────────────────────────────────────────

        # Barre du haut
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(
            top, text="❓  Aide & Documentation", bg=BG, fg=ACCENT2, font=FONT_B
        ).pack(side="left")
        self.lbl_aide_source = tk.Label(top, text="", bg=BG, fg=FG2, font=FONT_SM)
        self.lbl_aide_source.pack(side="right", padx=8)

        # Zone centrale
        center = tk.Frame(parent, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="📄", bg=BG, fg=ACCENT2, font=("Segoe UI", 48)).pack(
            pady=(0, 10)
        )
        tk.Label(
            center,
            text="Ouvrir la documentation dans votre navigateur",
            bg=BG,
            fg=FG,
            font=FONT_H,
        ).pack()
        tk.Label(
            center,
            text="Le fichier HTML s'ouvre hors ligne — aucune connexion requise.",
            bg=BG,
            fg=FG2,
            font=FONT_SM,
        ).pack(pady=(4, 24))

        self.lbl_aide_fichier = tk.Label(center, text="", bg=BG, fg=FG2, font=FONT_SM)
        self.lbl_aide_fichier.pack(pady=(0, 16))

        tk.Button(
            center,
            text="🌐  Ouvrir l'aide dans le navigateur",
            bg=ACCENT,
            fg="#fff",
            font=FONT_B,
            relief="flat",
            bd=0,
            pady=14,
            padx=30,
            activebackground=ACCENT2,
            activeforeground="#fff",
            cursor="hand2",
            command=lambda: self._ouvrir_aide(HTML_AIDE_PATH, HTML_CONTENU_DEFAUT),
        ).pack()

        tk.Frame(center, bg=BG, height=10).pack()
        tk.Label(
            center,
            text="💡  Placez votre fichier  aide.html  à côté de ce script.",
            bg=BG,
            fg=FG2,
            font=FONT_SM,
        ).pack()

        # Afficher le statut du fichier dès l'ouverture
        self._maj_statut_aide(HTML_AIDE_PATH)

    def _maj_statut_aide(self, html_path: Path) -> None:
        if html_path.exists():
            self.lbl_aide_fichier.config(
                text=f"✔  Fichier détecté : {html_path}", fg=SUCCESS
            )
        else:
            self.lbl_aide_fichier.config(
                text=f"⚠  aide.html introuvable — le contenu intégré sera utilisé.",
                fg=WARNING,
            )

    def _ouvrir_aide(self, html_path: Path, html_defaut: str) -> None:
        """Ouvre le fichier HTML dans le navigateur par défaut (hors ligne)."""
        import tempfile

        try:
            if html_path.exists():
                cible: Path = html_path
                log.info("Ouverture de l'aide depuis le fichier : %s", cible)
            else:
                # Écrit le contenu par défaut dans un fichier temporaire
                tmp = tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".html",
                    encoding="utf-8",
                    delete=False,
                    prefix="aide_reconditionnement_",
                )
                tmp.write(html_defaut)
                tmp.close()
                cible = Path(tmp.name)
                log.info("aide.html absent — contenu intégré écrit dans %s", cible)

            webbrowser.open(cible.as_uri())
        except OSError as exc:
            log.exception("Impossible d'ouvrir l'aide : %s", exc)
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'aide :\n{exc}", parent=self)

    # ─────────────────────────────────────────────────────────────────────────
    #  LOGIQUE
    # ─────────────────────────────────────────────────────────────────────────

    def _on_tab_change(self, _event: Optional[tk.Event] = None) -> None:
        """Rafraîchit le récap automatiquement à chaque visite de l'onglet."""
        try:
            idx: int = self.nb.index(self.nb.select())
            if idx == 2:  # onglet Récapitulatif
                self._refresh_recap()
        except Exception as exc:
            log.debug("_on_tab_change exception ignorée : %s", exc)

    def _now(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def refresh_table(self) -> None:
        q = self.search_var.get().lower() if hasattr(self, "search_var") else ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(liste, 1):
            vals = (
                i,
                row.get("question", ""),
                row.get("reponse", ""),
                row.get("type", ""),
                row.get("commentaire", ""),
                row.get("date", ""),
            )
            if q and not any(q in str(v).lower() for v in vals):
                continue
            tag = row.get("type", "normale").lower()
            if tag not in ("true", "false"):
                tag = "normale"
            self.tree.insert("", "end", iid=str(i - 1), values=vals, tags=(tag,))
        self.lbl_count.config(text=f"{len(liste)} entrée(s) en mémoire")

    def _on_select(self, _event: Optional[tk.Event] = None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        row = liste[idx]
        self.ent_question.delete(0, "end")
        self.ent_question.insert(0, row.get("question", ""))
        self.ent_reponse.delete(0, "end")
        self.ent_reponse.insert(0, row.get("reponse", ""))
        self.ent_comment.delete(0, "end")
        self.ent_comment.insert(0, row.get("commentaire", ""))
        t = row.get("type", "normale")
        self.cmb_type.set(t if t in ("normale", "True", "False") else "normale")

    def _ajouter(self) -> None:
        q: str = self.ent_question.get().strip()
        if not q:
            messagebox.showwarning(
                "Attention", "La question est obligatoire.", parent=self
            )
            return
        if question_existe(q):
            messagebox.showinfo("Info", "Cette question est déjà en base.", parent=self)
            return
        entry: dict[str, Any] = {
            "question": q,
            "reponse": self.ent_reponse.get().strip() or "None",
            "type": self.cmb_type.get(),
            "commentaire": self.ent_comment.get().strip() or "None",
            "date": self._now(),
        }
        liste.append(entry)
        log.info("Entrée ajoutée en mémoire : %s", q)
        ajouter_questions_db()
        self._clear_form()
        self.refresh_table()
        self._refresh_db_tab()

    def _modifier(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo(
                "Info", "Sélectionnez une ligne à modifier.", parent=self
            )
            return
        idx = int(sel[0])
        liste[idx]["question"] = (
            self.ent_question.get().strip() or liste[idx]["question"]
        )
        liste[idx]["reponse"] = self.ent_reponse.get().strip() or "None"
        liste[idx]["type"] = self.cmb_type.get()
        liste[idx]["commentaire"] = self.ent_comment.get().strip() or "None"
        self.refresh_table()

    def _supprimer_mem(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez une ligne.", parent=self)
            return
        idx = int(sel[0])
        q = liste[idx]["question"]
        if messagebox.askyesno(
            "Confirmer", f"Supprimer de la mémoire :\n« {q} »?", parent=self
        ):
            del liste[idx]
            self._clear_form()
            self.refresh_table()

    def _charger_db(self) -> None:
        charger_depuis_db()
        self.refresh_table()
        log.info("Chargement BDD depuis l'interface : %d entrée(s).", len(liste))
        messagebox.showinfo(
            "Chargé", f"{len(liste)} entrée(s) chargée(s) depuis la base.", parent=self
        )

    def _envoyer_db(self) -> None:
        if not liste:
            messagebox.showwarning("Vide", "La liste est vide.", parent=self)
            return
        ajouter_questions_db()
        self._refresh_db_tab()
        log.info("Envoi liste → BDD : %d entrée(s).", len(liste))
        messagebox.showinfo(
            "OK", f"{len(liste)} entrée(s) envoyée(s) en base.", parent=self
        )

    def _supprimer_db(self) -> None:
        val: str = self.ent_del_id.get().strip()
        if not val.isdigit():
            messagebox.showwarning("Erreur", "Entrez un ID valide.", parent=self)
            return
        if messagebox.askyesno(
            "Confirmer", f"Supprimer l'ID {val} de la base ?", parent=self
        ):
            log.info("Suppression demandée pour ID=%s depuis l'interface.", val)
            supprimer_question_db(int(val))
            self._refresh_db_tab()
            self.ent_del_id.delete(0, "end")

    def _refresh_db_tab(self) -> None:
        for item in self.tree_db.get_children():
            self.tree_db.delete(item)
        for row in get_all_db():
            tag = (row[3] or "normale").lower()
            if tag not in ("true", "false"):
                tag = "normale"
            self.tree_db.insert("", "end", values=row, tags=(tag,))

    def _clear_form(self) -> None:
        self.ent_question.delete(0, "end")
        self.ent_reponse.delete(0, "end")
        self.ent_comment.delete(0, "end")
        self.cmb_type.current(0)

    def _ouvrir_recap(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo(
                "Info",
                "Sélectionnez d'abord une ligne pour voir le récap.",
                parent=self,
            )
            return
        FenetreRecap(self, liste[int(sel[0])])

    def _ouvrir_recap_db(self) -> None:
        sel = self.tree_db.selection()
        if not sel:
            return
        vals = self.tree_db.item(sel[0], "values")
        if not vals:
            return
        FenetreRecap(
            self,
            {
                "id": vals[0],
                "question": vals[1],
                "reponse": vals[2],
                "type": vals[3],
                "commentaire": vals[4],
                "date": vals[5],
            },
        )

    # ── Exports ───────────────────────────────────────────────────────────────
    def _status(self, msg: str) -> None:
        self.lbl_export_status.config(text=msg)
        self.after(4000, lambda: self.lbl_export_status.config(text=""))

    def _exp_txt(self) -> None:
        nom: Optional[str] = simpledialog.askstring(
            "TXT", "Nom du fichier (sans extension) :", parent=self
        )
        if not nom:
            return

        try:
            f: Path = _get_dossier() / f"{nom}.txt"

            # Définir la largeur fixe de chaque colonne
            COL_NUM: int = 5
            COL_QUESTION: int = 35  # ← ajustez selon votre texte le plus long
            COL_REPONSE: int = 20
            COL_TYPE: int = 10
            COL_COMMENT: int = 25
            COL_DATE: int = 25
            # La date reste à la fin, pas besoin de largeur fixe

            # Ligne d'en-tête
            entete: str = (
                f"{'N°':<{COL_NUM}}"
                f"{'Question':<{COL_QUESTION}}"
                f"{'Réponse':<{COL_REPONSE}}"
                f"{'Type':<{COL_TYPE}}"
                f"{'Commentaire':<{COL_COMMENT}}"
                f"{'Date':<{COL_DATE}}"
            )
            separateur: str = "-" * (COL_NUM + COL_QUESTION + COL_REPONSE + COL_TYPE + COL_COMMENT + COL_DATE)

            txts: list[str] = [entete, separateur]

            for i, q in enumerate(liste, start=1):
                # Tronquer les textes trop longs avec "..."
                def tronq(texte: Any, largeur: int) -> str:
                    texte = str(texte) if texte else ""
                    return texte if len(texte) <= largeur else texte[:largeur - 3] + "..."

                ligne: str = (
                    f"{str(i):<{COL_NUM}}"
                    f"{tronq(q['question'], COL_QUESTION):<{COL_QUESTION}}"
                    f"{tronq(q['reponse'], COL_REPONSE):<{COL_REPONSE}}"
                    f"{tronq(q['type'], COL_TYPE):<{COL_TYPE}}"
                    f"{tronq(q['commentaire'], COL_COMMENT):<{COL_COMMENT}}"
                    f"{tronq(q['date'], COL_DATE):<{COL_DATE}}"

                )
                txts.append(ligne)

            f.write_text("\n".join(txts), encoding="utf-8")
            log.info("Export TXT réussi → %s", f)
            self._status(f"✔ TXT créé : {f}")

        except OSError as exc:
            log.exception("Erreur export TXT : %s", exc)
            messagebox.showerror("Erreur", str(exc), parent=self)

    def _exp_json(self) -> None:
        nom: Optional[str] = simpledialog.askstring(
            "JSON", "Nom du fichier (sans extension) :", parent=self
        )
        if not nom:
            return
        try:
            f: Path = _get_dossier() / f"{nom}.json"
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(liste, fp, indent=4, ensure_ascii=False)
            log.info("Export JSON réussi → %s", f)
            self._status(f"✔ JSON créé : {f}")
        except OSError as exc:
            log.exception("Erreur export JSON : %s", exc)
            messagebox.showerror("Erreur", str(exc), parent=self)

    def _exp_csv(self) -> None:
        nom: Optional[str] = simpledialog.askstring(
            "CSV", "Nom du fichier (sans extension) :", parent=self
        )
        if not nom:
            return
        try:
            cols: list[str] = ["id", "question", "reponse", "type", "commentaire", "date"]
            f: Path = _get_dossier() / f"{nom}.csv"
            with open(f, "w", newline="", encoding="utf-8-sig") as fp:
                w: csv.DictWriter[str] = csv.DictWriter(
                    fp, fieldnames=cols, extrasaction="ignore", delimiter=";"
                )
                w.writeheader()
                for row in liste:
                    w.writerow({c: row.get(c, "") for c in cols})
            log.info("Export CSV réussi → %s", f)
            self._status(f"✔ CSV créé : {f}")
        except OSError as exc:
            log.exception("Erreur export CSV : %s", exc)
            messagebox.showerror("Erreur", str(exc), parent=self)

    def _imp_json(self) -> None:
        global liste
        nom: Optional[str] = simpledialog.askstring(
            "Importer JSON", "Nom du fichier (sans .json) :", parent=self
        )
        if not nom:
            return
        try:
            f: Path = _get_dossier() / f"{nom}.json"
            if not f.exists():
                log.warning("Import JSON : fichier introuvable → %s", f)
                messagebox.showerror(
                    "Introuvable", f"Fichier non trouvé : {f}", parent=self
                )
                return
            with open(f, encoding="utf-8") as fp:
                liste = json.load(fp)
            log.info("Import JSON réussi depuis %s : %d entrée(s).", f, len(liste))
            self.refresh_table()
            self._status(f"✔ JSON chargé : {len(liste)} entrée(s)")
        except (OSError, json.JSONDecodeError) as exc:
            log.exception("Erreur import JSON : %s", exc)
            messagebox.showerror("Erreur", str(exc), parent=self)


if __name__ == "__main__":
    log.info("=== Lancement de reconditionnement_gui ===")
    try:
        app = App()
        app.mainloop()
    except Exception as exc:
        log.critical("Erreur fatale non gérée : %s", exc, exc_info=True)
        raise
