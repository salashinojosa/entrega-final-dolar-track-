#!/usr/bin/env python3
# ============================================================
# main.py — Orquestador principal de DolarTrack
# Reto 3: Economía "Dolar-Track"
# Arquitectura: Esquema Estrella SQLite + Tkinter + Power BI
# ============================================================

import os
import sys
import sqlite3

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR  = os.path.join(BASE_DIR, "Backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")
DB_PATH      = os.path.join(BACKEND_DIR, "dolar_track.db")

sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, FRONTEND_DIR)

from datos import (DIM_MONEDAS, DIM_INVERSIONISTAS, FACT_TRM,
                   FACT_OPERACIONES, FACT_ALERTAS)


def crear_base_de_datos():
    primera_vez = not os.path.exists(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")

    con.executescript("""
        CREATE TABLE IF NOT EXISTS dim_monedas (
            id      INTEGER PRIMARY KEY,
            codigo  TEXT    NOT NULL UNIQUE,
            nombre  TEXT    NOT NULL,
            simbolo TEXT    NOT NULL,
            region  TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dim_inversionistas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT    NOT NULL,
            capital_cop REAL    NOT NULL,
            perfil      TEXT    NOT NULL,
            ciudad      TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fact_trm (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha         TEXT    NOT NULL,
            id_moneda     INTEGER NOT NULL REFERENCES dim_monedas(id),
            trm           REAL    NOT NULL,
            promedio_hist REAL    NOT NULL DEFAULT 0,
            volatilidad   REAL    NOT NULL DEFAULT 0,
            UNIQUE(fecha, id_moneda)
        );
        CREATE TABLE IF NOT EXISTS fact_operaciones (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            id_inversionista INTEGER NOT NULL REFERENCES dim_inversionistas(id),
            id_moneda        INTEGER NOT NULL REFERENCES dim_monedas(id),
            tipo             TEXT    NOT NULL CHECK(tipo IN ('COMPRA','VENTA')),
            monto_divisa     REAL    NOT NULL,
            trm              REAL    NOT NULL,
            monto_cop        REAL    NOT NULL,
            fecha            TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fact_alertas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            id_moneda   INTEGER NOT NULL REFERENCES dim_monedas(id),
            tipo_alerta TEXT    NOT NULL,
            trm         REAL    NOT NULL,
            promedio    REAL    NOT NULL,
            fecha       TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS trm (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha   TEXT    NOT NULL,
            moneda  TEXT    NOT NULL DEFAULT 'USD',
            trm     REAL    NOT NULL,
            UNIQUE(fecha, moneda)
        );
        CREATE TABLE IF NOT EXISTS inversionistas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            capital_cop REAL NOT NULL,
            perfil      TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS operaciones (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            id_inversionista INTEGER NOT NULL,
            moneda           TEXT    NOT NULL,
            tipo             TEXT    NOT NULL,
            monto_usd        REAL    NOT NULL,
            trm              REAL    NOT NULL,
            monto_cop        REAL    NOT NULL,
            fecha            TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alertas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            moneda      TEXT NOT NULL,
            tipo_alerta TEXT NOT NULL,
            trm         REAL NOT NULL,
            promedio    REAL NOT NULL,
            fecha       TEXT NOT NULL
        );
    """)
    con.commit()

    n = con.execute("SELECT COUNT(*) FROM dim_monedas").fetchone()[0]
    if primera_vez or n == 0:
        print("  Cargando datos iniciales...")

        for m in DIM_MONEDAS:
            try:
                con.execute(
                    "INSERT OR IGNORE INTO dim_monedas VALUES (?,?,?,?,?)",
                    (m["id"], m["codigo"], m["nombre"], m["simbolo"], m["region"]))
            except: pass

        for inv in DIM_INVERSIONISTAS:
            try:
                con.execute(
                    "INSERT OR IGNORE INTO dim_inversionistas VALUES (?,?,?,?,?)",
                    (inv["id"], inv["nombre"], inv["capital_cop"], inv["perfil"], inv["ciudad"]))
                con.execute(
                    "INSERT OR IGNORE INTO inversionistas (id,nombre,capital_cop,perfil) VALUES (?,?,?,?)",
                    (inv["id"], inv["nombre"], inv["capital_cop"], inv["perfil"]))
            except: pass

        for r in FACT_TRM:
            try:
                con.execute(
                    "INSERT OR IGNORE INTO fact_trm (fecha,id_moneda,trm,promedio_hist,volatilidad) VALUES (?,?,?,?,?)",
                    (r["fecha"], r["id_moneda"], r["trm"], r["promedio_hist"], r["volatilidad"]))
                moneda = "USD" if r["id_moneda"] == 1 else "EUR"
                con.execute(
                    "INSERT OR IGNORE INTO trm (fecha,moneda,trm) VALUES (?,?,?)",
                    (r["fecha"], moneda, r["trm"]))
            except: pass

        for op in FACT_OPERACIONES:
            try:
                monto_cop = op["monto_divisa"] * op["trm"]
                con.execute(
                    "INSERT INTO fact_operaciones (id_inversionista,id_moneda,tipo,monto_divisa,trm,monto_cop,fecha) VALUES (?,?,?,?,?,?,?)",
                    (op["id_inversionista"], op["id_moneda"], op["tipo"],
                     op["monto_divisa"], op["trm"], monto_cop, op["fecha"]))
                moneda = "USD" if op["id_moneda"] == 1 else "EUR"
                con.execute(
                    "INSERT INTO operaciones (id_inversionista,moneda,tipo,monto_usd,trm,monto_cop,fecha) VALUES (?,?,?,?,?,?,?)",
                    (op["id_inversionista"], moneda, op["tipo"],
                     op["monto_divisa"], op["trm"], monto_cop, op["fecha"]))
            except: pass

        for a in FACT_ALERTAS:
            try:
                con.execute(
                    "INSERT INTO fact_alertas (id_moneda,tipo_alerta,trm,promedio,fecha) VALUES (?,?,?,?,?)",
                    (a["id_moneda"], a["tipo_alerta"], a["trm"], a["promedio"], a["fecha"]))
                moneda = "USD" if a["id_moneda"] == 1 else "EUR"
                con.execute(
                    "INSERT INTO alertas (moneda,tipo_alerta,trm,promedio,fecha) VALUES (?,?,?,?,?)",
                    (moneda, a["tipo_alerta"], a["trm"], a["promedio"], a["fecha"]))
            except: pass

        con.commit()
        print("  Esquema Estrella:")
        print(f"    dim_monedas        : {len(DIM_MONEDAS)} registros")
        print(f"    dim_inversionistas : {len(DIM_INVERSIONISTAS)} registros")
        print(f"    fact_trm           : {len(FACT_TRM)} registros")
        print(f"    fact_operaciones   : {len(FACT_OPERACIONES)} registros")
        print(f"    fact_alertas       : {len(FACT_ALERTAS)} registros")

    con.close()


def main():
    print("""
  DOLAR-TRACK — Analitica Cambiaria
  Reto 3: Economia y Finanzas
  Esquema Estrella · Tkinter · Power BI
    """)
    print(f"  Base de datos: {DB_PATH}")
    crear_base_de_datos()
    print("  Iniciando interfaz grafica...")
    from interfaz import iniciar
    iniciar()


if __name__ == "__main__":
    main()
