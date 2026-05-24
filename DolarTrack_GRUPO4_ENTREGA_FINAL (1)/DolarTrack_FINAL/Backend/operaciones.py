# ============================================================
# operaciones.py — Módulo de operaciones de compra/venta
# Proyecto: Reto 3 - Economía "Dolar-Track"
# ============================================================

import sqlite3
from datetime import datetime


TIPOS_VALIDOS = ("COMPRA", "VENTA")


class GestorOperaciones:
    """Registra y consulta operaciones de compra/venta de divisas."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    # ── CRUD ──────────────────────────────────────────────────
    def registrar(
        self,
        id_inversionista: int,
        moneda: str,
        tipo: str,
        monto_usd: float,
        trm: float,
    ) -> int:
        """Registra una operación y retorna su ID."""
        tipo = tipo.upper()
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Use: {TIPOS_VALIDOS}")
        monto_cop = monto_usd * trm
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as con:
            cur = con.execute(
                """INSERT INTO operaciones
                   (id_inversionista, moneda, tipo, monto_usd, trm, monto_cop, fecha)
                   VALUES (?,?,?,?,?,?,?)""",
                (id_inversionista, moneda.upper(), tipo, monto_usd, trm, monto_cop, fecha),
            )
        return cur.lastrowid

    def obtener_todas(self) -> list[dict]:
        with self._conectar() as con:
            cur = con.execute(
                """SELECT o.id, i.nombre, o.moneda, o.tipo,
                          o.monto_usd, o.trm, o.monto_cop, o.fecha
                   FROM operaciones o
                   JOIN inversionistas i ON o.id_inversionista = i.id
                   ORDER BY o.fecha DESC"""
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def eliminar(self, id_op: int) -> bool:
        with self._conectar() as con:
            cur = con.execute("DELETE FROM operaciones WHERE id=?", (id_op,))
        return cur.rowcount > 0

    # ── Análisis ──────────────────────────────────────────────
    def resumen_por_inversionista(self) -> list[dict]:
        """Total comprado y vendido en USD por inversionista."""
        with self._conectar() as con:
            cur = con.execute(
                """SELECT i.nombre, o.tipo, SUM(o.monto_usd) as total_usd
                   FROM operaciones o
                   JOIN inversionistas i ON o.id_inversionista = i.id
                   GROUP BY i.nombre, o.tipo
                   ORDER BY i.nombre"""
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
