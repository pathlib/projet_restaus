from pathlib import Path
from datetime import datetime
import json
import csv
import os
import platform
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
liste = []

home = Path.home()
if   (home / "Desktop").exists(): DB_PATH = home / "Desktop" / "ma_base.db"
elif (home / "Bureau").exists():  DB_PATH = home / "Bureau"  / "ma_base.db"
else:                              DB_PATH = home / "ma_base.db"


# ─── BASE DE DONNÉES ──────────────────────────────────────────────────────────
def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        question    TEXT    NOT NULL,
        reponse     TEXT    DEFAULT 'None',
        type        TEXT    DEFAULT 'normale',
        commentaire TEXT    DEFAULT 'None',
        date        TEXT    DEFAULT ''
    )''')
    conn.commit(); conn.close()

def question_existe(question):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM utilisateurs WHERE question = ?', (question,))
    result = c.fetchone(); conn.close()
    return result is not None

def ajouter_questions_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for u in liste:
        if 'question' in u and not question_existe(u['question']):
            c.execute('INSERT INTO utilisateurs (question) VALUES (?)', (u['question'],))
    conn.commit(); conn.close()

def supprimer_question_db(id_q):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor(); c.execute('DELETE FROM utilisateurs WHERE id = ?', (id_q,))
    conn.commit(); conn.close()

def charger_depuis_db():
    global liste
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, question, reponse, type, commentaire, date FROM utilisateurs')
    rows = c.fetchall(); conn.close()
    liste = [{'id': r[0], 'question': r[1], 'reponse': r[2] or 'None',
              'type': r[3] or 'normale', 'commentaire': r[4] or 'None', 'date': r[5] or ''}
             for r in rows]
    return liste

def get_all_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, question, reponse, type, commentaire, date FROM utilisateurs')
    rows = c.fetchall(); conn.close()
    return rows

def _get_dossier():
    if   (home / "Desktop").exists(): bureau = home / "Desktop"
    elif (home / "Bureau").exists():  bureau = home / "Bureau"
    else:                              bureau = home
    dossier = bureau / "reconditionnement"
    dossier.mkdir(exist_ok=True)
    return dossier


# ─── COULEURS & STYLE ─────────────────────────────────────────────────────────
BG       = "#1a1d23"
BG2      = "#22262f"
BG3      = "#2c3140"
ACCENT   = "#4f8ef7"
ACCENT2  = "#7fb3ff"
SUCCESS  = "#3ecf8e"
DANGER   = "#f7604f"
WARNING  = "#f7c04f"
FG       = "#e8eaf0"
FG2      = "#9aa3b8"
BORDER   = "#3a3f50"
FONT     = ("Segoe UI", 10)
FONT_B   = ("Segoe UI", 10, "bold")
FONT_H   = ("Segoe UI", 14, "bold")
FONT_SM  = ("Segoe UI", 9)


# ─── FENÊTRE RÉCAP DÉTAIL ─────────────────────────────────────────────────────
class FenetreRecap(tk.Toplevel):
    def __init__(self, master, row: dict):
        super().__init__(master)
        self.title("📄  Récapitulatif")
        self.geometry("600x480")
        self.minsize(480, 360)
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build(row)
        self.transient(master)
        self.grab_set()
        x = master.winfo_rootx() + (master.winfo_width()  - 600) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 480) // 2
        self.geometry(f"+{x}+{y}")

    def _section(self, parent, label, value, fg_val=FG):
        tk.Label(parent, text=label, bg=BG2, fg=FG2,
                 font=FONT_SM, anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        frame_val = tk.Frame(parent, bg=BG3, padx=10, pady=8)
        frame_val.pack(fill="x", padx=14)
        txt = tk.Text(frame_val, bg=BG3, fg=fg_val, font=FONT,
                      relief="flat", bd=0, wrap="word", height=3, state="normal")
        txt.insert("1.0", value if value and value not in ("None", "") else "—")
        txt.configure(state="disabled")
        txt.pack(fill="x")

    def _build(self, row: dict):
        hdr = tk.Frame(self, bg=BG2, pady=12, padx=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📄  Récapitulatif de l'entrée",
                 bg=BG2, fg=ACCENT2, font=FONT_H).pack(side="left")
        type_val = row.get("type", "normale")
        badge_color = SUCCESS if type_val.lower() == "true" else (DANGER if type_val.lower() == "false" else FG2)
        tk.Label(hdr, text=f"  {type_val.upper()}  ",
                 bg=badge_color, fg="#fff", font=FONT_B, padx=8, pady=4).pack(side="right", padx=6)

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG2)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e): canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))

        self._section(inner, "❓  Question",    row.get("question", ""),    fg_val=ACCENT2)
        self._section(inner, "✅  Réponse",     row.get("reponse", ""),     fg_val=SUCCESS)
        self._section(inner, "💬  Commentaire", row.get("commentaire", ""), fg_val=WARNING)

        meta = tk.Frame(inner, bg=BG2)
        meta.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(meta, text=f"🆔 ID : {row.get('id','—')}",     bg=BG2, fg=FG2, font=FONT_SM).pack(side="left", padx=(0,20))
        tk.Label(meta, text=f"📅 Date : {row.get('date','—')}", bg=BG2, fg=FG2, font=FONT_SM).pack(side="left")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=14, pady=8)
        ttk.Button(inner, text="✖  Fermer", style="Danger.TButton", command=self.destroy).pack(pady=(0, 14))


# ─── APPLICATION ─────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        create_db()
        self.title("Reconditionnement")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self._style()
        self._build()
        self.refresh_table()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=FG, font=FONT,
                     troughcolor=BG2, bordercolor=BORDER, relief="flat")
        s.configure("TFrame",      background=BG)
        s.configure("Card.TFrame", background=BG2)
        s.configure("TLabel",      background=BG,  foreground=FG, font=FONT)
        s.configure("Title.TLabel",background=BG,  foreground=ACCENT2, font=FONT_H)
        s.configure("Sub.TLabel",  background=BG2, foreground=FG2, font=FONT_SM)
        s.configure("TButton",     background=BG3, foreground=FG, font=FONT,
                     borderwidth=0, focusthickness=0, padding=(10, 6))
        s.map("TButton",
              background=[("active", ACCENT), ("pressed", "#3a6fcf")],
              foreground=[("active", "#fff")])
        s.configure("Accent.TButton",   background=ACCENT,  foreground="#fff", font=FONT_B)
        s.map("Accent.TButton",   background=[("active", ACCENT2)])
        s.configure("Danger.TButton",   background=DANGER,  foreground="#fff", font=FONT_B)
        s.map("Danger.TButton",   background=[("active", "#c94535")])
        s.configure("Success.TButton",  background=SUCCESS, foreground="#fff", font=FONT_B)
        s.map("Success.TButton",  background=[("active", "#2da06a")])
        s.configure("TEntry", fieldbackground=BG3, foreground=FG,
                     bordercolor=BORDER, insertcolor=FG, font=FONT, padding=6)
        s.configure("TCombobox", fieldbackground=BG3, foreground=FG, font=FONT)
        s.configure("Treeview", background=BG2, foreground=FG,
                     fieldbackground=BG2, rowheight=30, font=FONT)
        s.configure("Treeview.Heading", background=BG3, foreground=ACCENT2,
                     font=FONT_B, relief="flat")
        s.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#fff")])
        s.configure("TNotebook", background=BG, tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab", background=BG3, foreground=FG2, font=FONT, padding=[14, 8])
        s.map("TNotebook.Tab",
              background=[("selected", BG2)],
              foreground=[("selected", ACCENT2)])
        s.configure("TSeparator", background=BORDER)
        s.configure("TScrollbar", background=BG3, troughcolor=BG2,
                     arrowcolor=FG2, bordercolor=BORDER)

    def _build(self):
        hdr = tk.Frame(self, bg=BG2, pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  Reconditionnement", bg=BG2,
                 fg=ACCENT2, font=("Segoe UI", 16, "bold")).pack(side="left")
        self.lbl_count = tk.Label(hdr, text="", bg=BG2, fg=FG2, font=FONT_SM)
        self.lbl_count.pack(side="right", padx=10)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=8)

        self.tab_main   = ttk.Frame(self.nb)
        self.tab_db     = ttk.Frame(self.nb)
        self.tab_recap  = ttk.Frame(self.nb)
        self.tab_export = ttk.Frame(self.nb)
        self.nb.add(self.tab_main,   text="  📋  Questions  ")
        self.nb.add(self.tab_db,     text="  🗄️  Base de données  ")
        self.nb.add(self.tab_recap,  text="  📊  Récapitulatif  ")
        self.nb.add(self.tab_export, text="  💾  Export / Import  ")

        self._build_main(self.tab_main)
        self._build_db(self.tab_db)
        self._build_recap(self.tab_recap)
        self._build_export(self.tab_export)

        # Rafraîchit le récap automatiquement à chaque fois qu'on ouvre l'onglet
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    # ── Tab 1 : Questions ─────────────────────────────────────────────────────
    def _build_main(self, parent):
        left = tk.Frame(parent, bg=BG2, width=310)
        left.pack(side="left", fill="y", padx=(0, 6), pady=6)
        left.pack_propagate(False)

        tk.Label(left, text="Nouvelle entrée", bg=BG2, fg=ACCENT2,
                 font=FONT_B).pack(anchor="w", padx=14, pady=(14, 6))
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)

        def lbl(txt):
            tk.Label(left, text=txt, bg=BG2, fg=FG2, font=FONT_SM).pack(anchor="w", padx=14, pady=(10,2))

        lbl("Question *")
        self.ent_question = ttk.Entry(left, width=32)
        self.ent_question.pack(padx=14, fill="x")

        lbl("Réponse")
        self.ent_reponse = ttk.Entry(left, width=32)
        self.ent_reponse.pack(padx=14, fill="x")

        lbl("Type")
        self.cmb_type = ttk.Combobox(left, values=["normale", "True", "False"], state="readonly", width=30)
        self.cmb_type.current(0)
        self.cmb_type.pack(padx=14, fill="x")

        lbl("Commentaire")
        self.ent_comment = ttk.Entry(left, width=32)
        self.ent_comment.pack(padx=14, fill="x")

        tk.Frame(left, bg=BG2, height=12).pack()
        ttk.Button(left, text="➕  Ajouter", style="Accent.TButton",
                   command=self._ajouter).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=6).pack()
        ttk.Button(left, text="✏️  Modifier la sélection",
                   command=self._modifier).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=6).pack()
        ttk.Button(left, text="🗑️  Supprimer la sélection", style="Danger.TButton",
                   command=self._supprimer_mem).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=16).pack()
        ttk.Button(left, text="🔄  Charger depuis la BDD", style="Success.TButton",
                   command=self._charger_db).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=6).pack()
        ttk.Button(left, text="⬆️  Envoyer liste → BDD",
                   command=self._envoyer_db).pack(padx=14, fill="x")
        tk.Frame(left, bg=BG2, height=16).pack()
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)
        tk.Frame(left, bg=BG2, height=8).pack()
        tk.Button(left, text="🔎  Voir le récap", bg=ACCENT, fg="#fff",
                  font=FONT_B, relief="flat", bd=0, pady=8,
                  activebackground=ACCENT2, activeforeground="#fff",
                  cursor="hand2", command=self._ouvrir_recap).pack(padx=14, fill="x")

        # Right panel
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, pady=6, padx=(0,6))

        sf = tk.Frame(right, bg=BG)
        sf.pack(fill="x", pady=(0, 6))
        tk.Label(sf, text="🔍", bg=BG, fg=FG2, font=FONT).pack(side="left", padx=(0,4))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.refresh_table())
        ttk.Entry(sf, textvariable=self.search_var, width=30).pack(side="left")
        tk.Button(sf, text="🔎 Récap", bg=ACCENT, fg="#fff",
                  font=FONT_B, relief="flat", bd=0, padx=10,
                  activebackground=ACCENT2, activeforeground="#fff",
                  cursor="hand2", command=self._ouvrir_recap).pack(side="right", padx=6)

        cols = ("N°", "Question", "Réponse", "Type", "Commentaire", "Date")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="browse")
        widths = [40, 230, 160, 80, 180, 150]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=30)

        vsb = ttk.Scrollbar(right, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(right, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._ouvrir_recap())

        self.tree.tag_configure("true",    background="#1d3a2e", foreground="#3ecf8e")
        self.tree.tag_configure("false",   background="#3a1d1d", foreground="#f7604f")
        self.tree.tag_configure("normale", background=BG2)

    # ── Tab 2 : Base de données ───────────────────────────────────────────────
    def _build_db(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", pady=(8,4), padx=8)
        tk.Label(top, text="Contenu de la base SQLite", bg=BG, fg=ACCENT2, font=FONT_B).pack(side="left")
        ttk.Button(top, text="🔄  Rafraîchir", command=self._refresh_db_tab).pack(side="left", padx=10)

        right_top = tk.Frame(top, bg=BG)
        right_top.pack(side="right")
        tk.Label(right_top, text="ID à supprimer :", bg=BG, fg=FG2, font=FONT_SM).pack(side="left")
        self.ent_del_id = ttk.Entry(right_top, width=8)
        self.ent_del_id.pack(side="left", padx=4)
        ttk.Button(right_top, text="Supprimer", style="Danger.TButton",
                   command=self._supprimer_db).pack(side="left")

        cols = ("ID", "Question", "Réponse", "Type", "Commentaire", "Date")
        self.tree_db = ttk.Treeview(parent, columns=cols, show="headings")
        widths = [45, 240, 160, 80, 180, 150]
        for col, w in zip(cols, widths):
            self.tree_db.heading(col, text=col)
            self.tree_db.column(col, width=w, minwidth=30)
        vsb2 = ttk.Scrollbar(parent, orient="vertical",   command=self.tree_db.yview)
        hsb2 = ttk.Scrollbar(parent, orient="horizontal", command=self.tree_db.xview)
        self.tree_db.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)
        vsb2.pack(side="right", fill="y")
        hsb2.pack(side="bottom", fill="x")
        self.tree_db.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.tree_db.tag_configure("true",  background="#1d3a2e", foreground="#3ecf8e")
        self.tree_db.tag_configure("false", background="#3a1d1d", foreground="#f7604f")
        self.tree_db.bind("<Double-1>", lambda e: self._ouvrir_recap_db())
        self._refresh_db_tab()

    # ── Tab 3 : Récapitulatif ─────────────────────────────────────────────────
    def _build_recap(self, parent):
        # Barre du haut
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", pady=(8,4), padx=8)

        tk.Label(top, text="📊  Toutes les questions & réponses",
                 bg=BG, fg=ACCENT2, font=FONT_B).pack(side="left")
        ttk.Button(top, text="🔄  Rafraîchir", command=self._refresh_recap).pack(side="left", padx=10)

        # Filtre type
        tk.Label(top, text="Filtrer :", bg=BG, fg=FG2, font=FONT_SM).pack(side="right", padx=(0,4))
        self.recap_filtre = ttk.Combobox(top, values=["Tous", "True", "False", "normale"],
                                          state="readonly", width=10)
        self.recap_filtre.current(0)
        self.recap_filtre.pack(side="right", padx=(0,8))
        self.recap_filtre.bind("<<ComboboxSelected>>", lambda _: self._refresh_recap())

        # Statistiques
        self.frm_stats = tk.Frame(parent, bg=BG3)
        self.frm_stats.pack(fill="x", padx=8, pady=(0,6))
        self.lbl_stat_total  = tk.Label(self.frm_stats, text="Total : 0",  bg=BG3, fg=FG,      font=FONT_B, padx=16, pady=6)
        self.lbl_stat_ok     = tk.Label(self.frm_stats, text="✔ Conformes : 0", bg=BG3, fg=SUCCESS, font=FONT_B, padx=16, pady=6)
        self.lbl_stat_nok    = tk.Label(self.frm_stats, text="✘ Défauts : 0",   bg=BG3, fg=DANGER,  font=FONT_B, padx=16, pady=6)
        self.lbl_stat_norm   = tk.Label(self.frm_stats, text="— Normales : 0",  bg=BG3, fg=FG2,     font=FONT_B, padx=16, pady=6)
        for lbl in (self.lbl_stat_total, self.lbl_stat_ok, self.lbl_stat_nok, self.lbl_stat_norm):
            lbl.pack(side="left")

        # Zone de contenu scrollable avec cartes
        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, padx=8, pady=(0,8))

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.recap_inner = tk.Frame(canvas, bg=BG)
        self._recap_win_id = canvas.create_window((0, 0), window=self.recap_inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(self._recap_win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        self.recap_inner.bind("<Configure>",
                              lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Scroll à la molette
        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        self._recap_canvas = canvas

    def _refresh_recap(self):
        """Reconstruit les cartes de l'onglet récapitulatif."""
        # Vider
        for w in self.recap_inner.winfo_children():
            w.destroy()

        filtre = self.recap_filtre.get() if hasattr(self, "recap_filtre") else "Tous"
        source = liste  # toujours depuis la liste en mémoire

        total  = len(source)
        n_ok   = sum(1 for r in source if str(r.get("type","")).lower() == "true")
        n_nok  = sum(1 for r in source if str(r.get("type","")).lower() == "false")
        n_norm = total - n_ok - n_nok

        self.lbl_stat_total.config(text=f"Total : {total}")
        self.lbl_stat_ok.config(   text=f"✔ Conformes : {n_ok}")
        self.lbl_stat_nok.config(  text=f"✘ Défauts : {n_nok}")
        self.lbl_stat_norm.config( text=f"— Normales : {n_norm}")

        filtered = [r for r in source
                    if filtre == "Tous" or str(r.get("type","")).lower() == filtre.lower()]

        if not filtered:
            tk.Label(self.recap_inner, text="Aucune entrée à afficher.\nChargez des données depuis l'onglet Questions.",
                     bg=BG, fg=FG2, font=FONT_H, justify="center").pack(pady=60)
            return

        for i, row in enumerate(filtered):
            type_val = str(row.get("type", "normale")).lower()
            if   type_val == "true":  border_col = SUCCESS; badge_col = SUCCESS; badge_txt = "✔  CONFORME"
            elif type_val == "false": border_col = DANGER;  badge_col = DANGER;  badge_txt = "✘  DÉFAUT"
            else:                     border_col = BORDER;  badge_col = FG2;     badge_txt = "—  NORMALE"

            # Carte extérieure (bordure colorée gauche simulée)
            outer = tk.Frame(self.recap_inner, bg=border_col)
            outer.pack(fill="x", padx=10, pady=4)

            card = tk.Frame(outer, bg=BG2, padx=14, pady=10)
            card.pack(fill="x", padx=(3, 0))  # laisser 3px à gauche = bordure colorée

            # Ligne 1 : numéro + badge type + date
            row1 = tk.Frame(card, bg=BG2)
            row1.pack(fill="x")
            tk.Label(row1, text=f"#{i+1}", bg=BG2, fg=FG2, font=FONT_SM).pack(side="left", padx=(0,8))
            tk.Label(row1, text=badge_txt, bg=badge_col, fg="#fff",
                     font=("Segoe UI", 8, "bold"), padx=6, pady=2).pack(side="left")
            date_val = row.get("date", "")
            if date_val:
                tk.Label(row1, text=f"📅 {date_val}", bg=BG2, fg=FG2, font=FONT_SM).pack(side="right")

            # Ligne 2 : Question
            row2 = tk.Frame(card, bg=BG2)
            row2.pack(fill="x", pady=(6,2))
            tk.Label(row2, text="Q :", bg=BG2, fg=ACCENT2, font=FONT_B, width=3, anchor="w").pack(side="left")
            q_txt = row.get("question", "—")
            tk.Label(row2, text=q_txt, bg=BG2, fg=FG, font=FONT, anchor="w", wraplength=700, justify="left").pack(side="left", fill="x", expand=True)

            # Ligne 3 : Réponse
            rep_val = row.get("reponse", "None")
            row3 = tk.Frame(card, bg=BG2)
            row3.pack(fill="x", pady=2)
            tk.Label(row3, text="R :", bg=BG2, fg=SUCCESS, font=FONT_B, width=3, anchor="w").pack(side="left")
            tk.Label(row3, text=rep_val if rep_val not in ("None","") else "—",
                     bg=BG2, fg=FG if rep_val not in ("None","") else FG2,
                     font=FONT, anchor="w", wraplength=700, justify="left").pack(side="left", fill="x", expand=True)

            # Ligne 4 : Commentaire (seulement si présent)
            com_val = row.get("commentaire", "None")
            if com_val and com_val not in ("None", ""):
                row4 = tk.Frame(card, bg=BG2)
                row4.pack(fill="x", pady=(2,0))
                tk.Label(row4, text="💬 :", bg=BG2, fg=WARNING, font=FONT_B, width=3, anchor="w").pack(side="left")
                tk.Label(row4, text=com_val, bg=BG2, fg=WARNING, font=FONT_SM,
                         anchor="w", wraplength=700, justify="left").pack(side="left", fill="x", expand=True)

    # ── Tab 4 : Export / Import ───────────────────────────────────────────────
    def _build_export(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Export & Import", bg=BG, fg=ACCENT2, font=FONT_H).pack(pady=(0,20))

        cards = [
            ("💾  Exporter en TXT",  WARNING,  self._exp_txt),
            ("📦  Exporter en JSON", ACCENT,   self._exp_json),
            ("📊  Exporter en CSV",  SUCCESS,  self._exp_csv),
            ("📂  Importer JSON",    FG2,      self._imp_json),
        ]
        for txt, col, cmd in cards:
            btn = tk.Button(frame, text=txt, bg=BG2, fg=col,
                            font=("Segoe UI", 11, "bold"),
                            relief="flat", bd=0, pady=14, padx=30,
                            activebackground=BG3, activeforeground=col,
                            cursor="hand2", command=cmd)
            btn.pack(fill="x", pady=5)

        tk.Frame(frame, bg=BG, height=20).pack()
        self.lbl_export_status = tk.Label(frame, text="", bg=BG, fg=SUCCESS, font=FONT_SM)
        self.lbl_export_status.pack()

    # ─────────────────────────────────────────────────────────────────────────
    #  LOGIQUE
    # ─────────────────────────────────────────────────────────────────────────

    def _on_tab_change(self, _event=None):
        """Rafraîchit le récap automatiquement à chaque visite de l'onglet."""
        try:
            idx = self.nb.index(self.nb.select())
            if idx == 2:  # onglet Récapitulatif
                self._refresh_recap()
        except Exception:
            pass

    def _now(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def refresh_table(self):
        q = self.search_var.get().lower() if hasattr(self, "search_var") else ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(liste, 1):
            vals = (i, row.get("question",""), row.get("reponse",""),
                    row.get("type",""), row.get("commentaire",""), row.get("date",""))
            if q and not any(q in str(v).lower() for v in vals):
                continue
            tag = row.get("type","normale").lower()
            if tag not in ("true","false"): tag = "normale"
            self.tree.insert("", "end", iid=str(i-1), values=vals, tags=(tag,))
        self.lbl_count.config(text=f"{len(liste)} entrée(s) en mémoire")

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])
        row = liste[idx]
        self.ent_question.delete(0, "end"); self.ent_question.insert(0, row.get("question",""))
        self.ent_reponse.delete(0,  "end"); self.ent_reponse.insert(0,  row.get("reponse",""))
        self.ent_comment.delete(0,  "end"); self.ent_comment.insert(0,  row.get("commentaire",""))
        t = row.get("type","normale")
        self.cmb_type.set(t if t in ("normale","True","False") else "normale")

    def _ajouter(self):
        q = self.ent_question.get().strip()
        if not q:
            messagebox.showwarning("Attention", "La question est obligatoire.", parent=self); return
        if question_existe(q):
            messagebox.showinfo("Info", "Cette question est déjà en base.", parent=self); return
        entry = {"question": q, "reponse": self.ent_reponse.get().strip() or "None",
                 "type": self.cmb_type.get(), "commentaire": self.ent_comment.get().strip() or "None",
                 "date": self._now()}
        liste.append(entry)
        ajouter_questions_db()
        self._clear_form()
        self.refresh_table()
        self._refresh_db_tab()

    def _modifier(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez une ligne à modifier.", parent=self); return
        idx = int(sel[0])
        liste[idx]["question"]    = self.ent_question.get().strip() or liste[idx]["question"]
        liste[idx]["reponse"]     = self.ent_reponse.get().strip()  or "None"
        liste[idx]["type"]        = self.cmb_type.get()
        liste[idx]["commentaire"] = self.ent_comment.get().strip()  or "None"
        self.refresh_table()

    def _supprimer_mem(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez une ligne.", parent=self); return
        idx = int(sel[0])
        q = liste[idx]["question"]
        if messagebox.askyesno("Confirmer", f"Supprimer de la mémoire :\n« {q} »?", parent=self):
            del liste[idx]
            self._clear_form()
            self.refresh_table()

    def _charger_db(self):
        charger_depuis_db()
        self.refresh_table()
        messagebox.showinfo("Chargé", f"{len(liste)} entrée(s) chargée(s) depuis la base.", parent=self)

    def _envoyer_db(self):
        if not liste:
            messagebox.showwarning("Vide", "La liste est vide.", parent=self); return
        ajouter_questions_db()
        self._refresh_db_tab()
        messagebox.showinfo("OK", f"{len(liste)} entrée(s) envoyée(s) en base.", parent=self)

    def _supprimer_db(self):
        val = self.ent_del_id.get().strip()
        if not val.isdigit():
            messagebox.showwarning("Erreur", "Entrez un ID valide.", parent=self); return
        if messagebox.askyesno("Confirmer", f"Supprimer l'ID {val} de la base ?", parent=self):
            supprimer_question_db(int(val))
            self._refresh_db_tab()
            self.ent_del_id.delete(0,"end")

    def _refresh_db_tab(self):
        for item in self.tree_db.get_children():
            self.tree_db.delete(item)
        for row in get_all_db():
            tag = (row[3] or "normale").lower()
            if tag not in ("true","false"): tag = "normale"
            self.tree_db.insert("", "end", values=row, tags=(tag,))

    def _clear_form(self):
        self.ent_question.delete(0,"end")
        self.ent_reponse.delete(0,"end")
        self.ent_comment.delete(0,"end")
        self.cmb_type.current(0)

    def _ouvrir_recap(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez d'abord une ligne pour voir le récap.", parent=self); return
        FenetreRecap(self, liste[int(sel[0])])

    def _ouvrir_recap_db(self):
        sel = self.tree_db.selection()
        if not sel: return
        vals = self.tree_db.item(sel[0], "values")
        if not vals: return
        FenetreRecap(self, {"id": vals[0], "question": vals[1], "reponse": vals[2],
                             "type": vals[3], "commentaire": vals[4], "date": vals[5]})

    # ── Exports ───────────────────────────────────────────────────────────────
    def _status(self, msg):
        self.lbl_export_status.config(text=msg)
        self.after(4000, lambda: self.lbl_export_status.config(text=""))

    def _exp_txt(self):
        nom = simpledialog.askstring("TXT", "Nom du fichier (sans extension) :", parent=self)
        if not nom: return
        try:
            f = _get_dossier() / f"{nom}.txt"
            f.write_text("\n".join(map(str, liste)), encoding="utf-8")
            self._status(f"✔ TXT créé : {f}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)

    def _exp_json(self):
        nom = simpledialog.askstring("JSON", "Nom du fichier (sans extension) :", parent=self)
        if not nom: return
        try:
            f = _get_dossier() / f"{nom}.json"
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(liste, fp, indent=4, ensure_ascii=False)
            self._status(f"✔ JSON créé : {f}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)

    def _exp_csv(self):
        nom = simpledialog.askstring("CSV", "Nom du fichier (sans extension) :", parent=self)
        if not nom: return
        try:
            cols = ["id","question","reponse","type","commentaire","date"]
            f = _get_dossier() / f"{nom}.csv"
            with open(f, "w", newline="", encoding="utf-8-sig") as fp:
                w = csv.DictWriter(fp, fieldnames=cols, extrasaction="ignore", delimiter=";")
                w.writeheader()
                for row in liste:
                    w.writerow({c: row.get(c,"") for c in cols})
            self._status(f"✔ CSV créé : {f}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)

    def _imp_json(self):
        global liste
        nom = simpledialog.askstring("Importer JSON", "Nom du fichier (sans .json) :", parent=self)
        if not nom: return
        try:
            f = _get_dossier() / f"{nom}.json"
            if not f.exists():
                messagebox.showerror("Introuvable", f"Fichier non trouvé : {f}", parent=self); return
            with open(f, encoding="utf-8") as fp:
                liste = json.load(fp)
            self.refresh_table()
            self._status(f"✔ JSON chargé : {len(liste)} entrée(s)")
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
