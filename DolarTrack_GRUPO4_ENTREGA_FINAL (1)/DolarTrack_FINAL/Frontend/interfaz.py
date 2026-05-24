#!/usr/bin/env python3
# ============================================================
# interfaz.py — Interfaz gráfica DolarTrack
# Frontend: Tkinter + Pillow  |  Reto 3: Economía "Dolar-Track"
# ============================================================

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk

# ── Rutas ─────────────────────────────────────────────────
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR     = os.path.dirname(FRONTEND_DIR)
BACKEND_DIR  = os.path.join(BASE_DIR, "Backend")
DB_PATH      = os.path.join(BACKEND_DIR, "dolar_track.db")
LOGO_PATH    = os.path.join(FRONTEND_DIR, "imagenes", "logo.png")

PBIX_PATH    = os.path.join(BASE_DIR, "DolarTrack_PowerBI_Final.pbix")

sys.path.insert(0, BACKEND_DIR)

from trm           import RegistroTRM
from inversionistas import GestorInversionistas, PERFILES
from operaciones   import GestorOperaciones
from alertas       import GestorAlertas
from datos         import UMBRAL_VOLATILIDAD_ALTA, UMBRAL_ALERTA_COMPRA, UMBRAL_ALERTA_VENTA

# ══════════════════════════════════════════════════════════
#  DESIGN TOKENS — Inspired by the existing HTML dashboard
# ══════════════════════════════════════════════════════════
C = {
    "bg":       "#0f1117",
    "bg2":      "#161820",
    "bg3":      "#1e2130",
    "bg4":      "#252840",
    "border":   "#1f2235",
    "text":     "#e8eaf0",
    "text2":    "#8b90a0",
    "text3":    "#555a6e",
    "accent":   "#4f7cff",
    "accent2":  "#7b5ea7",
    "green":    "#2ecc8f",
    "red":      "#ff4d6a",
    "amber":    "#f0a500",
    "teal":     "#1ac9b2",
    "white":    "#ffffff",
}

FF = "Segoe UI"          # body
FM = "Consolas"          # monospace / numbers
FB = ("Segoe UI", 9, "bold")
FT = ("Segoe UI", 13, "bold")
FH = ("Segoe UI", 10, "bold")
FN = ("Consolas", 10)
FS = ("Segoe UI", 9)


# ══════════════════════════════════════════════════════════
#  WIDGET HELPERS
# ══════════════════════════════════════════════════════════
def lbl(parent, text, fg=None, font=None, bg=None, anchor="w", **kw):
    return tk.Label(
        parent, text=text,
        fg=fg or C["text"], font=font or FS,
        bg=bg or C["bg3"], anchor=anchor, **kw
    )

def entry(parent, var, width=22, fg=None):
    e = tk.Entry(
        parent, textvariable=var, width=width,
        font=FN, bg=C["bg4"], fg=fg or C["text"],
        insertbackground=C["accent"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["accent"],
    )
    return e

def btn(parent, text, cmd, color=None, fg=None, width=None, pady=7):
    kw = dict(
        text=text, command=cmd,
        font=FH, bg=color or C["accent"],
        fg=fg or C["bg"], relief="flat", bd=0,
        activebackground=C["accent2"],
        activeforeground=C["white"],
        cursor="hand2", pady=pady,
    )
    if width:
        kw["width"] = width
    return tk.Button(parent, **kw)

def sep(parent, color=None, height=1):
    return tk.Frame(parent, bg=color or C["border"], height=height)

def section_title(parent, text, color=None):
    f = tk.Frame(parent, bg=C["bg3"])
    tk.Label(f, text=text, font=FT, fg=color or C["accent"],
             bg=C["bg3"], anchor="w").pack(side="left")
    return f

def card(parent, **kw):
    defaults = dict(bg=C["bg3"], bd=0, relief="flat",
                    highlightthickness=1,
                    highlightbackground=C["border"])
    defaults.update(kw)
    return tk.Frame(parent, **defaults)

def make_tree(parent, columns, widths, height=14):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("DT.Treeview",
        background=C["bg2"], foreground=C["text"],
        rowheight=26, fieldbackground=C["bg2"],
        font=("Consolas", 9), borderwidth=0)
    style.configure("DT.Treeview.Heading",
        background=C["bg3"], foreground=C["accent"],
        font=("Segoe UI", 9, "bold"), relief="flat")
    style.map("DT.Treeview",
        background=[("selected", C["accent"])],
        foreground=[("selected", C["bg"])])
    style.layout("DT.Treeview", [('DT.Treeview.treearea', {'sticky': 'nswe'})])

    wrap = tk.Frame(parent, bg=C["bg"])
    sb = tk.Scrollbar(wrap, orient="vertical", bg=C["bg2"], troughcolor=C["bg3"])
    tree = ttk.Treeview(wrap, columns=columns, show="headings",
                        style="DT.Treeview", yscrollcommand=sb.set, height=height)
    sb.config(command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, minwidth=40, anchor="center")
    tree.tag_configure("green",  foreground=C["green"])
    tree.tag_configure("red",    foreground=C["red"])
    tree.tag_configure("amber",  foreground=C["amber"])
    tree.tag_configure("accent", foreground=C["accent"])
    tree.tag_configure("teal",   foreground=C["teal"])
    return wrap, tree

def combo(parent, var, values, width=18):
    style = ttk.Style()
    style.configure("DT.TCombobox",
        fieldbackground=C["bg4"], background=C["bg4"],
        foreground=C["text"], selectbackground=C["accent"])
    c = ttk.Combobox(parent, textvariable=var, values=values,
                     state="readonly", font=FN, width=width,
                     style="DT.TCombobox")
    return c

def stat_card(parent, label, value, color=None, sub=None):
    """Small KPI card."""
    f = card(parent)
    f.pack_propagate(False)
    tk.Label(f, text=label, font=("Segoe UI", 8), fg=C["text2"],
             bg=C["bg3"], anchor="w").pack(anchor="w", padx=10, pady=(8, 0))
    tk.Label(f, text=value, font=("Consolas", 15, "bold"),
             fg=color or C["accent"], bg=C["bg3"], anchor="w").pack(anchor="w", padx=10)
    if sub:
        tk.Label(f, text=sub, font=("Segoe UI", 8), fg=C["text3"],
                 bg=C["bg3"], anchor="w").pack(anchor="w", padx=10, pady=(0, 8))
    else:
        tk.Label(f, text="", bg=C["bg3"]).pack(pady=(0, 6))
    return f


# ══════════════════════════════════════════════════════════
#  APP ROOT
# ══════════════════════════════════════════════════════════
class DolarTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DolarTrack — Analítica Cambiaria")
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(bg=C["bg"])

        self.rt  = RegistroTRM(DB_PATH)
        self.ri  = GestorInversionistas(DB_PATH)
        self.ro  = GestorOperaciones(DB_PATH)
        self.ra  = GestorAlertas(DB_PATH)

        self._kpi_refs = {}   # keep stat_card label refs for live updates
        self._build()
        self.show_tab("dashboard")

    # ── Construcción de UI ────────────────────────────────
    def _build(self):
        self._build_header()
        self._build_nav()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        h = tk.Frame(self, bg=C["bg2"], height=62)
        h.pack(fill="x")
        h.pack_propagate(False)

        sep(h, C["border"]).pack(side="bottom", fill="x")

        # Logo
        try:
            img = Image.open(LOGO_PATH)
            img = img.resize((312, 60), Image.LANCZOS)
            self._logo = ImageTk.PhotoImage(img)
            tk.Label(h, image=self._logo, bg=C["bg2"]).pack(side="left", padx=14, pady=2)
        except Exception:
            tk.Label(h, text="💵  DOLAR-TRACK", font=("Segoe UI", 18, "bold"),
                     fg=C["accent"], bg=C["bg2"]).pack(side="left", padx=16)

        # Right: live badge + clock
        right = tk.Frame(h, bg=C["bg2"])
        right.pack(side="right", padx=18)
        self._time_var = tk.StringVar()
        tk.Label(right, textvariable=self._time_var, font=(FM, 10),
                 fg=C["text3"], bg=C["bg2"]).pack(side="right")
        tk.Label(right, text="  ●  LIVE  ", font=("Segoe UI", 9, "bold"),
                 fg=C["green"], bg=C["bg2"]).pack(side="right")
        self._tick_clock()

    def _tick_clock(self):
        self._time_var.set(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _build_nav(self):
        nav = tk.Frame(self, bg=C["bg2"])
        nav.pack(fill="x")
        sep(nav, C["border"]).pack(side="bottom", fill="x")

        self._nav_btns = {}
        tabs = [
            ("dashboard",    "⬛  Dashboard"),
            ("trm",          "📈  TRM"),
            ("inversores",   "👤  Inversionistas"),
            ("operaciones",  "💼  Operaciones"),
            ("alertas",      "🔔  Alertas"),
        ]
        for key, label in tabs:
            b = tk.Button(nav, text=label, font=("Segoe UI", 9, "bold"),
                bg=C["bg2"], fg=C["text2"], relief="flat", bd=0,
                padx=20, pady=10, cursor="hand2",
                activebackground=C["bg3"], activeforeground=C["accent"],
                command=lambda k=key: self.show_tab(k))
            b.pack(side="left")
            self._nav_btns[key] = b

        # Botón Power BI — alineado a la derecha
        pbi_btn = tk.Button(
            nav, text="📊  Abrir Power BI",
            font=("Segoe UI", 9, "bold"),
            bg="#f0a500", fg=C["bg"],
            relief="flat", bd=0,
            padx=20, pady=10, cursor="hand2",
            activebackground="#d4900a", activeforeground=C["bg"],
            command=self._abrir_power_bi
        )
        pbi_btn.pack(side="right", padx=8)

    def _build_body(self):
        self._body = tk.Frame(self, bg=C["bg"])
        self._body.pack(fill="both", expand=True, padx=12, pady=8)

        self._tabs = {
            "dashboard":   TabDashboard(self._body, self),
            "trm":         TabTRM(self._body, self),
            "inversores":  TabInversores(self._body, self),
            "operaciones": TabOperaciones(self._body, self),
            "alertas":     TabAlertas(self._body, self),
        }

    def _build_statusbar(self):
        sb = tk.Frame(self, bg=C["bg2"], height=26)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        sep(sb, C["border"], 1).pack(side="top", fill="x")
        self._status_var = tk.StringVar(value=f"📂  {DB_PATH}")
        tk.Label(sb, textvariable=self._status_var, font=(FM, 8),
                 fg=C["text3"], bg=C["bg2"], anchor="w").pack(side="left", padx=12)

    # ── Navegación ────────────────────────────────────────
    def show_tab(self, key: str):
        for k, f in self._tabs.items():
            f.pack_forget()
        self._tabs[key].pack(fill="both", expand=True)
        self._tabs[key].refresh()
        for k, b in self._nav_btns.items():
            if k == key:
                b.configure(fg=C["accent"], bg=C["bg3"])
            else:
                b.configure(fg=C["text2"], bg=C["bg2"])

    def set_status(self, msg: str):
        self._status_var.set(f"  {msg}")

    def _abrir_power_bi(self):
        """Abre el archivo .pbix de Power BI automáticamente."""
        try:
            if not os.path.exists(PBIX_PATH):
                messagebox.showerror(
                    "Archivo no encontrado",
                    f"No se encontró el archivo Power BI en:\n{PBIX_PATH}\n\n"
                    "Verifique que el archivo .pbix esté en la carpeta raíz del proyecto."
                )
                return
            if sys.platform == "win32":
                os.startfile(PBIX_PATH)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", PBIX_PATH])
            else:
                subprocess.Popen(["xdg-open", PBIX_PATH])
            self.set_status("📊 Power BI abierto exitosamente")
            messagebox.showinfo("✅ Power BI", "Abriendo dashboard de Power BI...")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Power BI:\n{str(e)}")


# ══════════════════════════════════════════════════════════
#  TAB: DASHBOARD
# ══════════════════════════════════════════════════════════
class TabDashboard(tk.Frame):
    def __init__(self, parent, app: DolarTrackApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _eliminar_ultimo(self):
        """Elimina el último registro de TRM — demo CRUD para sustentación."""
        registros = self.app.rt.obtener_todos("USD")
        if not registros:
            messagebox.showerror("Error", "No hay registros de TRM para eliminar.")
            return
        ultimo = registros[-1]
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Desea eliminar el registro ID {ultimo['id']}?\n"
            f"Fecha: {ultimo['fecha']} | TRM: $ {ultimo['trm']:,.2f}"
        )
        if confirmar:
            if self.app.rt.eliminar(ultimo["id"]):
                messagebox.showinfo("✅ Eliminado",
                    f"Registro ID {ultimo['id']} eliminado correctamente.")
                self.refresh()
                self.app.set_status(f"🗑 TRM ID {ultimo['id']} eliminada")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el registro.")

    def _build(self):
        rt = self.app.rt
        ri = self.app.ri
        ro = self.app.ro
        ra = self.app.ra

        stats_usd = rt.calcular_estadisticas("USD")
        stats_eur = rt.calcular_estadisticas("EUR")
        trm_usd_list = rt.obtener_todos("USD")
        trm_eur_list = rt.obtener_todos("EUR")
        all_ops = ro.obtener_todas()
        all_inv = ri.obtener_todos()
        all_alrt = ra.obtener_alertas()

        last_usd = trm_usd_list[-1]["trm"] if trm_usd_list else 0
        last_eur = trm_eur_list[-1]["trm"] if trm_eur_list else 0

        # ── KPI row ──────────────────────────────────────
        kpi_row = tk.Frame(self, bg=C["bg"])
        kpi_row.pack(fill="x", pady=(0, 8))

        kpis = [
            ("TRM USD Actual", f"$ {last_usd:,.2f}" if last_usd else "—", C["accent"], "COP por 1 USD"),
            ("TRM EUR Actual", f"$ {last_eur:,.2f}" if last_eur else "—", C["accent2"], "COP por 1 EUR"),
            ("Prom. USD hist.", f"$ {stats_usd.get('promedio',0):,.2f}" if stats_usd else "—", C["teal"], f"n={stats_usd.get('n','—')} registros"),
            ("Volatilidad USD", f"{stats_usd.get('coef_variacion',0):.2f}%" if stats_usd else "—",
                C["amber"] if stats_usd and stats_usd.get("coef_variacion",0) > UMBRAL_VOLATILIDAD_ALTA else C["green"],
                "Alta" if stats_usd and stats_usd.get("coef_variacion",0) > UMBRAL_VOLATILIDAD_ALTA else "Normal"),
            ("Inversionistas", str(len(all_inv)), C["teal"], "registrados"),
            ("Operaciones", str(len(all_ops)), C["amber"], "compras + ventas"),
            ("Alertas activas", str(len(all_alrt)), C["red"] if all_alrt else C["green"], "en historial"),
        ]

        for label, value, color, sub in kpis:
            c = stat_card(kpi_row, label, value, color, sub)
            c.configure(width=138, height=80)
            c.pack(side="left", padx=(0, 6), fill="y")

        # ── Señal de decisión ──────────────────────────
        if last_usd and stats_usd:
            signal = rt.generar_alerta(last_usd, "USD")
            sig_color = C["green"] if "COMPRAR" in signal else C["red"] if "VENDER" in signal else C["amber"]
            sig_frame = card(self)
            sig_frame.pack(fill="x", pady=(0, 8))
            tk.Label(sig_frame, text="💡  Señal automática USD",
                     font=("Segoe UI", 9), fg=C["text2"], bg=C["bg3"],
                     anchor="w").pack(anchor="w", padx=12, pady=(8, 2))
            tk.Label(sig_frame, text=signal,
                     font=("Segoe UI", 12, "bold"), fg=sig_color,
                     bg=C["bg3"], anchor="w").pack(anchor="w", padx=12, pady=(0, 8))

        # ── Botones CRUD rápidos ──────────────────────────
        crud_row = tk.Frame(self, bg=C["bg"])
        crud_row.pack(fill="x", pady=(0, 8))

        tk.Label(crud_row, text="Acciones rápidas:",
                 font=("Segoe UI", 9, "bold"), fg=C["text2"],
                 bg=C["bg"]).pack(side="left", padx=(0, 10))

        crud_btns = [
            ("➕  Registrar TRM",     lambda: self.app.show_tab("trm"),         C["accent"]),
            ("✏️  Actualizar TRM",    lambda: self.app.show_tab("trm"),         C["teal"]),
            ("🗑  Eliminar Registro", lambda: self._eliminar_ultimo(),           C["red"]),
            ("📋  Ver Tabla",         lambda: self.app.show_tab("trm"),         C["amber"]),
        ]
        for text, cmd, color in crud_btns:
            tk.Button(crud_row, text=text, command=cmd,
                      font=("Segoe UI", 9, "bold"),
                      bg=color, fg=C["bg"], relief="flat", bd=0,
                      padx=12, pady=6, cursor="hand2",
                      activebackground=C["accent2"],
                      activeforeground=C["white"]).pack(side="left", padx=4)

        # ── Two columns: TRM history + ops ──────────────
        mid = tk.Frame(self, bg=C["bg"])
        mid.pack(fill="both", expand=True)

        # Left: TRM USD history
        left = card(mid)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(left, text="Historial TRM — USD", font=FH, fg=C["accent"],
                 bg=C["bg3"], anchor="w").pack(anchor="w", padx=10, pady=(8, 4))
        sep(left, C["border"]).pack(fill="x", padx=6)

        cols = ["Fecha", "TRM $", "vs Prom."]
        widths = [110, 110, 90]
        tw, tree = make_tree(left, cols, widths, height=10)
        tw.pack(fill="both", expand=True, padx=6, pady=6)
        prom_usd = stats_usd.get("promedio", 0) if stats_usd else 0
        for r in reversed(trm_usd_list[-12:]):
            diff = r["trm"] - prom_usd
            tag = "green" if diff < 0 else "red"
            tree.insert("", "end", values=(
                r["fecha"], f"$ {r['trm']:,.2f}",
                f"{'+'if diff>=0 else ''}{diff:,.2f}"
            ), tags=(tag,))

        # Right: recent operations
        right = card(mid)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Últimas Operaciones", font=FH, fg=C["amber"],
                 bg=C["bg3"], anchor="w").pack(anchor="w", padx=10, pady=(8, 4))
        sep(right, C["border"]).pack(fill="x", padx=6)

        cols2 = ["Inversionista", "Mon.", "Tipo", "USD", "COP $"]
        widths2 = [130, 50, 65, 80, 110]
        tw2, tree2 = make_tree(right, cols2, widths2, height=10)
        tw2.pack(fill="both", expand=True, padx=6, pady=6)
        for op in all_ops[:12]:
            tag = "green" if op["tipo"] == "COMPRA" else "red"
            tree2.insert("", "end", values=(
                op["nombre"][:16], op["moneda"], op["tipo"],
                f"{op['monto_usd']:,.2f}", f"$ {op['monto_cop']:,.0f}"
            ), tags=(tag,))


# ══════════════════════════════════════════════════════════
#  TAB: TRM
# ══════════════════════════════════════════════════════════
class TabTRM(tk.Frame):
    def __init__(self, parent, app: DolarTrackApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._moneda_var = tk.StringVar(value="USD")
        self._build()

    def _build(self):
        # ── Left panel: form ──────────────────────────
        left = card(self)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.configure(width=278)
        left.pack_propagate(False)

        section_title(left, "Registrar TRM", C["accent"]).pack(
            anchor="w", padx=12, pady=(12, 4))
        sep(left, C["accent"], 2).pack(fill="x", padx=12, pady=(0, 8))

        form = tk.Frame(left, bg=C["bg3"])
        form.pack(padx=12, fill="x")

        lbl(form, "Fecha (YYYY-MM-DD)", bg=C["bg3"]).pack(anchor="w", pady=(6, 1))
        self.v_fecha = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        entry(form, self.v_fecha).pack(fill="x")

        lbl(form, "Moneda", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        combo(form, self._moneda_var, ["USD", "EUR"]).pack(fill="x")

        lbl(form, "TRM (COP)", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        self.v_trm = tk.StringVar()
        entry(form, self.v_trm, fg=C["green"]).pack(fill="x")

        tk.Frame(left, bg=C["bg3"], height=10).pack()
        bf = tk.Frame(left, bg=C["bg3"])
        bf.pack(padx=12, fill="x")
        btn(bf, "✅  Registrar TRM", self._registrar).pack(fill="x", pady=(0, 6))
        btn(bf, "🗑  Limpiar campos", self._limpiar,
            color=C["bg4"], fg=C["text2"]).pack(fill="x")

        sep(left, C["border"]).pack(fill="x", padx=12, pady=14)
        section_title(left, "Estadísticas", C["teal"]).pack(anchor="w", padx=12, pady=(0, 6))

        self._stats_frame = tk.Frame(left, bg=C["bg3"])
        self._stats_frame.pack(padx=12, fill="x")

        # moneda filter buttons at top of stats
        mf = tk.Frame(left, bg=C["bg3"])
        mf.pack(padx=12, pady=(4, 0), fill="x")
        btn(mf, "USD", lambda: self._show_stats("USD"),
            color=C["bg4"], fg=C["accent"]).pack(side="left", padx=(0, 4))
        btn(mf, "EUR", lambda: self._show_stats("EUR"),
            color=C["bg4"], fg=C["accent2"]).pack(side="left")

        self._show_stats("USD")

        # ── Right panel: table + filter ───────────────
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        top = tk.Frame(right, bg=C["bg"])
        top.pack(fill="x", pady=(0, 6))
        lbl(top, "Historial de TRM", font=FT, fg=C["accent"], bg=C["bg"]).pack(side="left")

        filt = tk.Frame(right, bg=C["bg"])
        filt.pack(fill="x", pady=(0, 4))
        lbl(filt, "Filtrar:", bg=C["bg"], fg=C["text2"]).pack(side="left")
        self._filt_mon = tk.StringVar(value="USD")
        combo(filt, self._filt_mon, ["USD", "EUR"], width=8).pack(side="left", padx=6)
        btn(filt, "Aplicar", self.refresh, color=C["bg3"], fg=C["accent"]).pack(side="left")

        cols = ["ID", "Fecha", "Moneda", "TRM (COP)", "Señal"]
        widths = [40, 110, 70, 120, 220]
        tw, self.tree = make_tree(right, cols, widths, height=18)
        tw.pack(fill="both", expand=True)

        bot = tk.Frame(right, bg=C["bg"])
        bot.pack(fill="x", pady=6)
        lbl(bot, "Actualizar ID:", bg=C["bg"], fg=C["text2"]).pack(side="left")
        self.v_upd_id = tk.StringVar()
        entry(bot, self.v_upd_id, width=6).pack(side="left", padx=4)
        lbl(bot, "Nuevo valor:", bg=C["bg"], fg=C["text2"]).pack(side="left")
        self.v_upd_val = tk.StringVar()
        entry(bot, self.v_upd_val, width=10).pack(side="left", padx=4)
        btn(bot, "💰 Actualizar", self._actualizar,
            color=C["amber"], fg=C["bg"]).pack(side="left", padx=4)

    def _show_stats(self, moneda):
        for w in self._stats_frame.winfo_children():
            w.destroy()
        stats = self.app.rt.calcular_estadisticas(moneda)
        if not stats:
            lbl(self._stats_frame, "Sin datos", fg=C["text3"],
                bg=C["bg3"]).pack()
            return
        rows = [
            ("Promedio",    f"$ {stats['promedio']:,.2f}",  C["teal"]),
            ("Mínimo",      f"$ {stats['min']:,.2f}",       C["green"]),
            ("Máximo",      f"$ {stats['max']:,.2f}",       C["red"]),
            ("Desv. std.",  f"$ {stats['desv_std']:,.2f}",  C["text"]),
            ("Coef. var.",  f"{stats['coef_variacion']:.4f}%",
                C["amber"] if stats["coef_variacion"] > UMBRAL_VOLATILIDAD_ALTA else C["green"]),
            ("Registros",   str(stats["n"]),                 C["text2"]),
        ]
        for name, val, color in rows:
            row = tk.Frame(self._stats_frame, bg=C["bg3"])
            row.pack(fill="x", pady=1)
            lbl(row, name, fg=C["text2"], bg=C["bg3"]).pack(side="left")
            lbl(row, val, fg=color, bg=C["bg3"], font=FN).pack(side="right")

    def _registrar(self):
        fecha = self.v_fecha.get().strip()
        moneda = self._moneda_var.get()
        trm_str = self.v_trm.get().strip()

        # Validaciones con try-except
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de validación",
                "Formato de fecha incorrecto.\nUse YYYY-MM-DD  (ej: 2025-05-01)")
            return
        if not moneda:
            messagebox.showerror("Error de validación", "Seleccione una moneda.")
            return
        try:
            trm_val = float(trm_str.replace(",", "."))
            if trm_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de validación",
                "La TRM debe ser un número positivo.\nEjemplo: 4150.50")
            return

        try:
            ok = self.app.rt.registrar(fecha, moneda, trm_val)
            if not ok:
                messagebox.showwarning("Registro duplicado",
                    f"Ya existe una TRM para {moneda} en {fecha}.")
                return
            stats = self.app.rt.calcular_estadisticas(moneda)
            signal = self.app.rt.generar_alerta(trm_val, moneda)
            self.app.ra.registrar_alerta(moneda, signal, trm_val, stats.get("promedio", 0))

            sig_color_word = "🟢 COMPRAR" if "COMPRAR" in signal else \
                             "🔴 VENDER"  if "VENDER"  in signal else "🟡 MANTENER"
            messagebox.showinfo("✅ TRM Registrada",
                f"TRM {moneda} del {fecha}: $ {trm_val:,.2f}\n\n"
                f"Señal automática: {signal}\n\n"
                f"Promedio histórico: $ {stats.get('promedio',0):,.2f}")
            self._limpiar()
            self.refresh()
            self.app.set_status(
                f"✅ TRM {moneda} registrada: $ {trm_val:,.2f}  |  Señal: {sig_color_word}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def _limpiar(self):
        self.v_trm.set("")
        self.v_fecha.set(datetime.now().strftime("%Y-%m-%d"))

    def _actualizar(self):
        try:
            id_trm = int(self.v_upd_id.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número entero.")
            return
        try:
            nuevo = float(self.v_upd_val.get().strip().replace(",", "."))
            if nuevo <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El valor debe ser un número positivo.")
            return
        try:
            if self.app.rt.actualizar(id_trm, nuevo):
                messagebox.showinfo("✅ Actualizado", f"TRM ID {id_trm} actualizada.")
                self.v_upd_id.set(""); self.v_upd_val.set("")
                self.refresh()
                self.app.set_status(f"💰 TRM ID {id_trm} → $ {nuevo:,.2f}")
            else:
                messagebox.showerror("Error", f"No se encontró TRM con ID {id_trm}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        moneda = self._filt_mon.get() or "USD"
        stats = self.app.rt.calcular_estadisticas(moneda)
        prom = stats.get("promedio", 0) if stats else 0

        for r in reversed(self.app.rt.obtener_todos(moneda)):
            signal = self.app.rt.generar_alerta(r["trm"], moneda)
            if "COMPRAR" in signal: tag = "green"
            elif "VENDER" in signal: tag = "red"
            else: tag = "amber"
            self.tree.insert("", "end", values=(
                r["id"], r["fecha"], r["moneda"],
                f"$ {r['trm']:,.2f}", signal
            ), tags=(tag,))
        self._show_stats(moneda)


# ══════════════════════════════════════════════════════════
#  TAB: INVERSIONISTAS
# ══════════════════════════════════════════════════════════
class TabInversores(tk.Frame):
    def __init__(self, parent, app: DolarTrackApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._perfil_var = tk.StringVar()
        self._build()

    def _build(self):
        # Left
        left = card(self)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.configure(width=278)
        left.pack_propagate(False)

        section_title(left, "Registrar Inversionista", C["accent"]).pack(
            anchor="w", padx=12, pady=(12, 4))
        sep(left, C["accent"], 2).pack(fill="x", padx=12, pady=(0, 8))

        form = tk.Frame(left, bg=C["bg3"])
        form.pack(padx=12, fill="x")

        lbl(form, "Nombre completo", bg=C["bg3"]).pack(anchor="w", pady=(6, 1))
        self.v_nombre = tk.StringVar()
        entry(form, self.v_nombre).pack(fill="x")

        lbl(form, "Capital disponible (COP)", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        self.v_capital = tk.StringVar()
        entry(form, self.v_capital, fg=C["green"]).pack(fill="x")

        lbl(form, "Perfil de riesgo", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        combo(form, self._perfil_var, PERFILES).pack(fill="x")

        bf = tk.Frame(left, bg=C["bg3"])
        bf.pack(padx=12, pady=10, fill="x")
        btn(bf, "✅  Registrar", self._registrar).pack(fill="x", pady=(0, 6))
        btn(bf, "🗑  Limpiar", self._limpiar,
            color=C["bg4"], fg=C["text2"]).pack(fill="x")

        sep(left, C["border"]).pack(fill="x", padx=12, pady=10)

        # Exposición cambiaria
        section_title(left, "Exposición Cambiaria", C["teal"]).pack(
            anchor="w", padx=12, pady=(0, 4))
        ef = tk.Frame(left, bg=C["bg3"])
        ef.pack(padx=12, fill="x")
        lbl(ef, "ID Inversionista", bg=C["bg3"]).pack(anchor="w", pady=(4, 1))
        self.v_exp_id = tk.StringVar()
        entry(ef, self.v_exp_id, width=8).pack(anchor="w")
        lbl(ef, "Moneda", bg=C["bg3"]).pack(anchor="w", pady=(6, 1))
        self.v_exp_mon = tk.StringVar(value="USD")
        combo(ef, self.v_exp_mon, ["USD", "EUR"], width=10).pack(anchor="w")
        btn(ef, "📊  Calcular Exposición", self._calcular_exp,
            color=C["teal"], fg=C["bg"]).pack(fill="x", pady=8)

        # Right
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        lbl(right, "Listado de Inversionistas", font=FT, fg=C["accent"],
            bg=C["bg"]).pack(anchor="w", pady=(0, 6))

        cols = ["ID", "Nombre", "Capital COP", "Perfil", "Exposición USD (TRM prom.)"]
        widths = [40, 160, 130, 100, 200]
        tw, self.tree = make_tree(right, cols, widths, height=16)
        tw.pack(fill="both", expand=True)

        bot = tk.Frame(right, bg=C["bg"])
        bot.pack(fill="x", pady=6)
        lbl(bot, "Act. capital ID:", bg=C["bg"], fg=C["text2"]).pack(side="left")
        self.v_ac_id = tk.StringVar()
        entry(bot, self.v_ac_id, width=6).pack(side="left", padx=4)
        lbl(bot, "Nuevo capital:", bg=C["bg"], fg=C["text2"]).pack(side="left")
        self.v_ac_val = tk.StringVar()
        entry(bot, self.v_ac_val, width=14).pack(side="left", padx=4)
        btn(bot, "💰 Actualizar", self._actualizar_capital,
            color=C["amber"], fg=C["bg"]).pack(side="left", padx=4)

    def _registrar(self):
        nombre  = self.v_nombre.get().strip()
        cap_str = self.v_capital.get().strip()
        perfil  = self._perfil_var.get()

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        try:
            capital = float(cap_str.replace(",", ".").replace(" ", ""))
            if capital <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de validación",
                "El capital debe ser un número positivo.\nEjemplo: 10000000")
            return
        if not perfil:
            messagebox.showerror("Error", "Seleccione un perfil de riesgo.")
            return

        pct = {"Conservador": 20, "Moderado": 40, "Agresivo": 70}.get(perfil, 0)
        try:
            new_id = self.app.ri.registrar(nombre, capital, perfil)
            messagebox.showinfo("✅ Inversionista Registrado",
                f"'{nombre}' registrado con ID {new_id}.\n"
                f"Capital: $ {capital:,.0f} COP\n"
                f"Perfil {perfil}: expone el {pct}% de su capital.")
            self._limpiar()
            self.refresh()
            self.app.set_status(f"✅ Inversionista '{nombre}' — ID {new_id}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _limpiar(self):
        self.v_nombre.set(""); self.v_capital.set("")
        self._perfil_var.set("")

    def _calcular_exp(self):
        try:
            id_inv = int(self.v_exp_id.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número entero.")
            return
        moneda = self.v_exp_mon.get()
        stats = self.app.rt.calcular_estadisticas(moneda)
        trm = stats.get("promedio", 4100) if stats else 4100
        exp = self.app.ri.calcular_exposicion(id_inv, trm)
        if not exp:
            messagebox.showerror("No encontrado",
                f"No se encontró inversionista con ID {id_inv}.")
            return
        messagebox.showinfo("📊 Exposición Cambiaria",
            f"👤  {exp['nombre']}  |  Perfil: {exp['perfil']}\n\n"
            f"Capital total       : $ {exp['capital_total_cop']:>12,.0f} COP\n"
            f"Exposición ({exp['pct_exposicion']:.0f}%)    : $ {exp['capital_expuesto_cop']:>12,.0f} COP\n"
            f"TRM usada ({moneda})  : $ {exp['trm_usada']:>12,.2f}\n"
            f"─────────────────────────────────────\n"
            f"Divisas posibles    :  {exp['usd_posibles']:>12,.2f} {moneda}")

    def _actualizar_capital(self):
        try:
            id_inv = int(self.v_ac_id.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser entero.")
            return
        try:
            nuevo = float(self.v_ac_val.get().strip().replace(",", "."))
            if nuevo <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El capital debe ser número positivo.")
            return
        try:
            if self.app.ri.actualizar_capital(id_inv, nuevo):
                messagebox.showinfo("✅ Actualizado",
                    f"Capital de ID {id_inv} actualizado a $ {nuevo:,.0f} COP.")
                self.v_ac_id.set(""); self.v_ac_val.set("")
                self.refresh()
            else:
                messagebox.showerror("Error", f"ID {id_inv} no encontrado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        stats_usd = self.app.rt.calcular_estadisticas("USD")
        trm_prom = stats_usd.get("promedio", 4100) if stats_usd else 4100
        for inv in self.app.ri.obtener_todos():
            exp = self.app.ri.calcular_exposicion(inv["id"], trm_prom)
            usd_p = f"{exp['usd_posibles']:,.2f} USD" if exp else "—"
            tag = {"Conservador": "teal", "Moderado": "amber",
                   "Agresivo": "red"}.get(inv["perfil"], "")
            self.tree.insert("", "end", values=(
                inv["id"], inv["nombre"],
                f"$ {inv['capital_cop']:,.0f}",
                inv["perfil"], usd_p
            ), tags=(tag,))


# ══════════════════════════════════════════════════════════
#  TAB: OPERACIONES
# ══════════════════════════════════════════════════════════
class TabOperaciones(tk.Frame):
    def __init__(self, parent, app: DolarTrackApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._mon_var  = tk.StringVar(value="USD")
        self._tipo_var = tk.StringVar(value="COMPRA")
        self._build()

    def _build(self):
        # Left
        left = card(self)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.configure(width=278)
        left.pack_propagate(False)

        section_title(left, "Nueva Operación", C["accent"]).pack(
            anchor="w", padx=12, pady=(12, 4))
        sep(left, C["accent"], 2).pack(fill="x", padx=12, pady=(0, 8))

        form = tk.Frame(left, bg=C["bg3"])
        form.pack(padx=12, fill="x")

        lbl(form, "ID Inversionista", bg=C["bg3"]).pack(anchor="w", pady=(6, 1))
        self.v_id_inv = tk.StringVar()
        entry(form, self.v_id_inv, width=10).pack(anchor="w")

        lbl(form, "Moneda", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        combo(form, self._mon_var, ["USD", "EUR"]).pack(fill="x")

        lbl(form, "Tipo de operación", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        tipo_frame = tk.Frame(form, bg=C["bg3"])
        tipo_frame.pack(fill="x")
        for t, col in [("COMPRA", C["green"]), ("VENTA", C["red"])]:
            tk.Radiobutton(tipo_frame, text=t, variable=self._tipo_var, value=t,
                font=FH, fg=col, bg=C["bg3"], selectcolor=C["bg4"],
                activebackground=C["bg3"], activeforeground=col).pack(side="left", padx=4)

        lbl(form, "Monto (USD / EUR)", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        self.v_monto = tk.StringVar()
        entry(form, self.v_monto, fg=C["amber"]).pack(fill="x")

        lbl(form, "TRM a usar (dejar vacío → usa promedio hist.)",
            bg=C["bg3"], fg=C["text3"], font=("Segoe UI", 8)).pack(anchor="w", pady=(6, 1))
        self.v_trm_op = tk.StringVar()
        entry(form, self.v_trm_op, width=14).pack(anchor="w")

        bf = tk.Frame(left, bg=C["bg3"])
        bf.pack(padx=12, pady=10, fill="x")
        btn(bf, "✅  Registrar Operación", self._registrar,
            color=C["green"], fg=C["bg"]).pack(fill="x", pady=(0, 6))
        btn(bf, "🗑  Limpiar", self._limpiar,
            color=C["bg4"], fg=C["text2"]).pack(fill="x")

        sep(left, C["border"]).pack(fill="x", padx=12, pady=10)

        # Resumen mini
        section_title(left, "Resumen por inversor", C["teal"]).pack(
            anchor="w", padx=12, pady=(0, 4))
        self._resumen_frame = tk.Frame(left, bg=C["bg3"])
        self._resumen_frame.pack(padx=12, fill="x")

        # Right
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)
        lbl(right, "Historial de Operaciones", font=FT, fg=C["accent"],
            bg=C["bg"]).pack(anchor="w", pady=(0, 6))

        cols = ["ID", "Inversionista", "Mon.", "Tipo", "Monto USD", "TRM", "Monto COP", "Fecha"]
        widths = [35, 130, 45, 65, 90, 85, 110, 135]
        tw, self.tree = make_tree(right, cols, widths, height=18)
        tw.pack(fill="both", expand=True)

    def _registrar(self):
        try:
            id_inv = int(self.v_id_inv.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El ID del inversionista debe ser entero.")
            return
        moneda = self._mon_var.get()
        tipo   = self._tipo_var.get()
        try:
            monto = float(self.v_monto.get().strip().replace(",", "."))
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de validación",
                "El monto debe ser un número positivo.\nEjemplo: 500.00")
            return

        trm_str = self.v_trm_op.get().strip()
        if trm_str:
            try:
                trm_val = float(trm_str.replace(",", "."))
                if trm_val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "La TRM debe ser número positivo.")
                return
        else:
            stats = self.app.rt.calcular_estadisticas(moneda)
            trm_val = stats.get("promedio", 4100) if stats else 4100

        try:
            new_id = self.app.ro.registrar(id_inv, moneda, tipo, monto, trm_val)
            monto_cop = monto * trm_val
            messagebox.showinfo("✅ Operación Registrada",
                f"Operación #{new_id} registrada exitosamente.\n\n"
                f"Tipo    : {tipo}  {moneda}\n"
                f"Monto   : {monto:,.2f} {moneda}\n"
                f"TRM     : $ {trm_val:,.2f}\n"
                f"Valor   : $ {monto_cop:,.0f} COP")
            self._limpiar()
            self.refresh()
            self.app.set_status(
                f"✅ {tipo} {monto:,.2f} {moneda} — $ {monto_cop:,.0f} COP  [ID {new_id}]")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _limpiar(self):
        self.v_id_inv.set(""); self.v_monto.set("")
        self.v_trm_op.set(""); self._tipo_var.set("COMPRA")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for op in self.app.ro.obtener_todas():
            tag = "green" if op["tipo"] == "COMPRA" else "red"
            self.tree.insert("", "end", values=(
                op["id"], op["nombre"][:14], op["moneda"], op["tipo"],
                f"{op['monto_usd']:,.2f}", f"$ {op['trm']:,.2f}",
                f"$ {op['monto_cop']:,.0f}", op["fecha"][:16]
            ), tags=(tag,))

        # Refresh resumen
        for w in self._resumen_frame.winfo_children():
            w.destroy()
        for r in self.app.ro.resumen_por_inversionista():
            row = tk.Frame(self._resumen_frame, bg=C["bg3"])
            row.pack(fill="x", pady=1)
            tag_col = C["green"] if r["tipo"] == "COMPRA" else C["red"]
            lbl(row, f"{r['nombre'][:14]} · {r['tipo']}",
                fg=C["text2"], bg=C["bg3"], font=FS).pack(side="left")
            lbl(row, f"{r['total_usd']:,.2f}", fg=tag_col,
                bg=C["bg3"], font=FN).pack(side="right")


# ══════════════════════════════════════════════════════════
#  TAB: ALERTAS
# ══════════════════════════════════════════════════════════
class TabAlertas(tk.Frame):
    def __init__(self, parent, app: DolarTrackApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._filt_var = tk.StringVar(value="TODAS")
        self._build()

    def _build(self):
        # Left
        left = card(self)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.configure(width=278)
        left.pack_propagate(False)

        section_title(left, "Generar Alerta Manual", C["red"]).pack(
            anchor="w", padx=12, pady=(12, 4))
        sep(left, C["red"], 2).pack(fill="x", padx=12, pady=(0, 8))

        form = tk.Frame(left, bg=C["bg3"])
        form.pack(padx=12, fill="x")

        lbl(form, "Moneda", bg=C["bg3"]).pack(anchor="w", pady=(6, 1))
        self.v_mon = tk.StringVar(value="USD")
        combo(form, self.v_mon, ["USD", "EUR"]).pack(fill="x")

        lbl(form, "TRM actual (COP)", bg=C["bg3"]).pack(anchor="w", pady=(8, 1))
        self.v_trm_hoy = tk.StringVar()
        entry(form, self.v_trm_hoy, fg=C["amber"]).pack(fill="x")

        btn(form, "🔍  Analizar y Registrar Alerta",
            self._analizar, color=C["red"], fg=C["white"]).pack(fill="x", pady=(10, 0))

        sep(left, C["border"]).pack(fill="x", padx=12, pady=12)

        # Info
        section_title(left, "Umbrales del sistema", C["text2"]).pack(
            anchor="w", padx=12, pady=(0, 6))
        info = tk.Frame(left, bg=C["bg3"])
        info.pack(padx=12, fill="x")
        for label, val, col in [
            ("Vender si TRM >", f"{(UMBRAL_ALERTA_VENTA-1)*100:.0f}% sobre prom.", C["red"]),
            ("Comprar si TRM <", f"{(1-UMBRAL_ALERTA_COMPRA)*100:.0f}% bajo prom.", C["green"]),
            ("Alta volatilidad >", f"{UMBRAL_VOLATILIDAD_ALTA}% coef. var.", C["amber"]),
        ]:
            r = tk.Frame(info, bg=C["bg3"]); r.pack(fill="x", pady=2)
            lbl(r, label, fg=C["text2"], bg=C["bg3"], font=FS).pack(side="left")
            lbl(r, val, fg=col, bg=C["bg3"], font=FS).pack(side="right")

        # Right
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        top = tk.Frame(right, bg=C["bg"])
        top.pack(fill="x", pady=(0, 6))
        lbl(top, "Historial de Alertas", font=FT, fg=C["red"],
            bg=C["bg"]).pack(side="left")

        filt_f = tk.Frame(right, bg=C["bg"])
        filt_f.pack(fill="x", pady=(0, 4))
        lbl(filt_f, "Filtrar:", fg=C["text2"], bg=C["bg"]).pack(side="left")
        combo(filt_f, self._filt_var, ["TODAS", "USD", "EUR"], width=8).pack(side="left", padx=6)
        btn(filt_f, "Aplicar", self.refresh, color=C["bg3"], fg=C["accent"]).pack(side="left")

        cols = ["ID", "Moneda", "TRM", "Promedio", "Señal", "Fecha"]
        widths = [40, 60, 100, 100, 260, 145]
        tw, self.tree = make_tree(right, cols, widths, height=18)
        tw.pack(fill="both", expand=True)

    def _analizar(self):
        moneda = self.v_mon.get()
        trm_str = self.v_trm_hoy.get().strip()
        try:
            trm_val = float(trm_str.replace(",", "."))
            if trm_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de validación",
                "Ingrese un valor de TRM positivo.\nEjemplo: 4200.50")
            return

        stats = self.app.rt.calcular_estadisticas(moneda)
        if not stats:
            messagebox.showerror("Sin datos",
                f"No hay datos históricos de TRM para {moneda}.")
            return

        signal = self.app.rt.generar_alerta(trm_val, moneda)
        self.app.ra.registrar_alerta(moneda, signal, trm_val, stats["promedio"])

        cv = stats["coef_variacion"]
        volatilidad = f"⚡ ALTA ({cv:.2f}%)" if cv > UMBRAL_VOLATILIDAD_ALTA \
                      else f"✅ Normal ({cv:.2f}%)"
        sig_color = "verde" if "COMPRAR" in signal else "roja" if "VENDER" in signal else "amarilla"

        messagebox.showinfo("📊 Análisis de Decisión",
            f"Moneda: {moneda}  |  TRM analizada: $ {trm_val:,.2f}\n\n"
            f"Promedio histórico : $ {stats['promedio']:,.2f}\n"
            f"Mín / Máx          : $ {stats['min']:,.2f}  /  $ {stats['max']:,.2f}\n"
            f"Desv. estándar     : $ {stats['desv_std']:,.2f}\n"
            f"Volatilidad        : {volatilidad}\n\n"
            f"{'═'*40}\n"
            f"➤  Señal: {signal}\n"
            f"{'═'*40}\n\n"
            "Alerta registrada en el historial.")
        self.v_trm_hoy.set("")
        self.refresh()
        self.app.set_status(f"🔔 Alerta {moneda}: {signal[:30]}…")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        filt = self._filt_var.get()
        moneda_filt = None if filt == "TODAS" else filt
        for a in self.app.ra.obtener_alertas(moneda_filt):
            sig = a["tipo_alerta"]
            if "COMPRAR" in sig: tag = "green"
            elif "VENDER" in sig: tag = "red"
            else: tag = "amber"
            self.tree.insert("", "end", values=(
                a["id"], a["moneda"],
                f"$ {a['trm']:,.2f}", f"$ {a['promedio']:,.2f}",
                sig[:50], a["fecha"]
            ), tags=(tag,))


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════
def iniciar():
    app = DolarTrackApp()
    app.mainloop()

if __name__ == "__main__":
    iniciar()
