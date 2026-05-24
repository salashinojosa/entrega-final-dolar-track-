# ============================================================
# trm.py — Módulo de registro y análisis de TRM
# Proyecto: Reto 3 - Economía "Dolar-Track"
# ============================================================

import sqlite3
import statistics
from datetime import datetime


class RegistroTRM:
    """Gestiona el registro y análisis estadístico de la TRM diaria."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    # ── CRUD ──────────────────────────────────────────────────
    def registrar(self, fecha: str, moneda: str, trm: float) -> bool:
        """Inserta un nuevo registro de TRM. Retorna True si fue exitoso."""
        try:
            with self._conectar() as con:
                con.execute(
                    "INSERT INTO trm (fecha, moneda, trm) VALUES (?, ?, ?)",
                    (fecha, moneda.upper(), trm),
                )
            return True
        except sqlite3.IntegrityError:
            print(f"  ⚠  Ya existe un registro para {moneda.upper()} en {fecha}.")
            return False

    def obtener_todos(self, moneda: str = "USD") -> list[dict]:
        """Retorna todos los registros de una moneda, ordenados por fecha."""
        with self._conectar() as con:
            cur = con.execute(
                "SELECT id, fecha, moneda, trm FROM trm WHERE moneda=? ORDER BY fecha",
                (moneda.upper(),),
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def actualizar(self, id_trm: int, nuevo_valor: float) -> bool:
        with self._conectar() as con:
            cur = con.execute(
                "UPDATE trm SET trm=? WHERE id=?", (nuevo_valor, id_trm)
            )
        return cur.rowcount > 0

    def eliminar(self, id_trm: int) -> bool:
        with self._conectar() as con:
            cur = con.execute("DELETE FROM trm WHERE id=?", (id_trm,))
        return cur.rowcount > 0

    # ── Análisis ──────────────────────────────────────────────
    def calcular_estadisticas(self, moneda: str = "USD") -> dict:
        """Promedio, volatilidad (desv. estándar) y coef. de variación."""
        registros = self.obtener_todos(moneda)
        if not registros:
            return {}
        valores = [r["trm"] for r in registros]
        promedio = statistics.mean(valores)
        desv = statistics.stdev(valores) if len(valores) > 1 else 0.0
        cv = (desv / promedio * 100) if promedio else 0.0
        return {
            "moneda": moneda.upper(),
            "n": len(valores),
            "promedio": round(promedio, 2),
            "min": round(min(valores), 2),
            "max": round(max(valores), 2),
            "desv_std": round(desv, 2),
            "coef_variacion": round(cv, 4),
        }

    def generar_alerta(self, trm_actual: float, moneda: str = "USD") -> str:
        """Retorna 'VENDER', 'COMPRAR' o 'MANTENER' según umbral vs promedio."""
        from datos import UMBRAL_ALERTA_COMPRA, UMBRAL_ALERTA_VENTA
        stats = self.calcular_estadisticas(moneda)
        if not stats:
            return "SIN DATOS"
        promedio = stats["promedio"]
        if trm_actual > promedio * UMBRAL_ALERTA_VENTA:
            return "🔴 VENDER — TRM por encima del promedio histórico"
        if trm_actual < promedio * UMBRAL_ALERTA_COMPRA:
            return "🟢 COMPRAR — TRM por debajo del promedio histórico"
        return "🟡 MANTENER — TRM dentro del rango normal"
