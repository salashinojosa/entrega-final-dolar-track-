# ============================================================
# alertas.py — Módulo de alertas y reportes analíticos
# Proyecto: Reto 3 - Economía "Dolar-Track"
# ============================================================

import sqlite3
from datetime import datetime


class GestorAlertas:
    """Genera alertas automáticas y reportes de decisión."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    # ── CRUD ──────────────────────────────────────────────────
    def registrar_alerta(self, moneda: str, tipo_alerta: str, trm: float, promedio: float) -> int:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as con:
            cur = con.execute(
                "INSERT INTO alertas (moneda, tipo_alerta, trm, promedio, fecha) VALUES (?,?,?,?,?)",
                (moneda.upper(), tipo_alerta, trm, promedio, fecha),
            )
        return cur.lastrowid

    def obtener_alertas(self, moneda: str = None) -> list[dict]:
        query = "SELECT * FROM alertas"
        params = ()
        if moneda:
            query += " WHERE moneda=?"
            params = (moneda.upper(),)
        query += " ORDER BY fecha DESC"
        with self._conectar() as con:
            cur = con.execute(query, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def eliminar_alerta(self, id_alerta: int) -> bool:
        with self._conectar() as con:
            cur = con.execute("DELETE FROM alertas WHERE id=?", (id_alerta,))
        return cur.rowcount > 0

    # ── Reporte de decisión ───────────────────────────────────
    def reporte_decision(self, trm_actual: float, stats: dict, moneda: str = "USD") -> None:
        """Imprime un reporte visual de decisión de inversión."""
        print("\n" + "═" * 55)
        print(f"  📊  REPORTE DE DECISIÓN — {moneda}  |  {datetime.now():%Y-%m-%d}")
        print("═" * 55)
        print(f"  TRM actual    : $ {trm_actual:,.2f}")
        print(f"  Promedio hist.: $ {stats['promedio']:,.2f}")
        print(f"  Mín / Máx     : $ {stats['min']:,.2f}  /  $ {stats['max']:,.2f}")
        print(f"  Desv. estándar: $ {stats['desv_std']:,.2f}")
        print(f"  Coef. variación: {stats['coef_variacion']:.2f} %")

        from datos import UMBRAL_VOLATILIDAD_ALTA
        if stats["coef_variacion"] > UMBRAL_VOLATILIDAD_ALTA:
            print(f"\n  ⚡  ALTA VOLATILIDAD detectada (>{UMBRAL_VOLATILIDAD_ALTA}%)")
        else:
            print(f"\n  ✅  Volatilidad normal (<{UMBRAL_VOLATILIDAD_ALTA}%)")
        print("═" * 55 + "\n")
