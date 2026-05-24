# ============================================================
# inversionistas.py — Módulo de gestión de inversionistas
# Proyecto: Reto 3 - Economía "Dolar-Track"
# ============================================================

import sqlite3


PERFILES = ["Conservador", "Moderado", "Agresivo"]


class GestorInversionistas:
    """CRUD de inversionistas y cálculo de exposición cambiaria."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    # ── CRUD ──────────────────────────────────────────────────
    def registrar(self, nombre: str, capital_cop: float, perfil: str) -> int:
        """Inserta inversionista y retorna su ID."""
        if perfil not in PERFILES:
            raise ValueError(f"Perfil inválido. Opciones: {PERFILES}")
        with self._conectar() as con:
            cur = con.execute(
                "INSERT INTO inversionistas (nombre, capital_cop, perfil) VALUES (?,?,?)",
                (nombre.strip().title(), capital_cop, perfil),
            )
        return cur.lastrowid

    def obtener_todos(self) -> list[dict]:
        with self._conectar() as con:
            cur = con.execute(
                "SELECT id, nombre, capital_cop, perfil FROM inversionistas ORDER BY nombre"
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def actualizar_capital(self, id_inv: int, nuevo_capital: float) -> bool:
        with self._conectar() as con:
            cur = con.execute(
                "UPDATE inversionistas SET capital_cop=? WHERE id=?",
                (nuevo_capital, id_inv),
            )
        return cur.rowcount > 0

    def eliminar(self, id_inv: int) -> bool:
        with self._conectar() as con:
            cur = con.execute("DELETE FROM inversionistas WHERE id=?", (id_inv,))
        return cur.rowcount > 0

    # ── Análisis ──────────────────────────────────────────────
    def calcular_exposicion(self, id_inv: int, trm: float) -> dict:
        """Cuántos USD/EUR puede comprar con su capital disponible."""
        with self._conectar() as con:
            row = con.execute(
                "SELECT nombre, capital_cop, perfil FROM inversionistas WHERE id=?",
                (id_inv,),
            ).fetchone()
        if not row:
            return {}
        nombre, capital, perfil = row
        # Porcentaje del capital a exponer según perfil
        porcentajes = {"Conservador": 0.20, "Moderado": 0.40, "Agresivo": 0.70}
        pct = porcentajes.get(perfil, 0.30)
        capital_expuesto = capital * pct
        usd_posibles = capital_expuesto / trm if trm else 0
        return {
            "nombre": nombre,
            "perfil": perfil,
            "capital_total_cop": capital,
            "pct_exposicion": pct * 100,
            "capital_expuesto_cop": round(capital_expuesto, 2),
            "usd_posibles": round(usd_posibles, 2),
            "trm_usada": trm,
        }
