# ============================================================
# datos.py — Datos iniciales para DolarTrack
# Proyecto: Reto 3 - Economía "Dolar-Track"
# ============================================================

# ── Dimensión: Monedas ──────────────────────────────────────
DIM_MONEDAS = [
    {"id": 1, "codigo": "USD", "nombre": "Dólar Americano",  "simbolo": "$",  "region": "América del Norte"},
    {"id": 2, "codigo": "EUR", "nombre": "Euro",             "simbolo": "€",  "region": "Europa"},
    {"id": 3, "codigo": "GBP", "nombre": "Libra Esterlina",  "simbolo": "£",  "region": "Reino Unido"},
    {"id": 4, "codigo": "JPY", "nombre": "Yen Japonés",      "simbolo": "¥",  "region": "Asia"},
    {"id": 5, "codigo": "CHF", "nombre": "Franco Suizo",     "simbolo": "Fr", "region": "Europa Central"},
]

# ── Dimensión: Inversionistas ───────────────────────────────
DIM_INVERSIONISTAS = [
    {"id": 1, "nombre": "Carlos Mendez",   "capital_cop": 10_000_000, "perfil": "Conservador", "ciudad": "Bogotá"},
    {"id": 2, "nombre": "Laura Jimenez",   "capital_cop": 25_000_000, "perfil": "Moderado",    "ciudad": "Medellín"},
    {"id": 3, "nombre": "Andres Rios",     "capital_cop": 50_000_000, "perfil": "Agresivo",    "ciudad": "Cali"},
    {"id": 4, "nombre": "Maria Fernandez", "capital_cop": 15_000_000, "perfil": "Moderado",    "ciudad": "Barranquilla"},
    {"id": 5, "nombre": "Jorge Salazar",   "capital_cop": 30_000_000, "perfil": "Agresivo",    "ciudad": "Bucaramanga"},
]

# ── Tabla de Hechos: TRM (Fact) ─────────────────────────────
FACT_TRM = [
    {"fecha": "2025-04-01", "id_moneda": 1, "trm": 4050.50, "promedio_hist": 4050.50, "volatilidad": 0.0},
    {"fecha": "2025-04-02", "id_moneda": 1, "trm": 4075.25, "promedio_hist": 4062.87, "volatilidad": 0.4},
    {"fecha": "2025-04-03", "id_moneda": 1, "trm": 4102.00, "promedio_hist": 4075.91, "volatilidad": 0.8},
    {"fecha": "2025-04-04", "id_moneda": 1, "trm": 4088.75, "promedio_hist": 4079.12, "volatilidad": 0.6},
    {"fecha": "2025-04-07", "id_moneda": 1, "trm": 4120.30, "promedio_hist": 4087.36, "volatilidad": 0.9},
    {"fecha": "2025-04-01", "id_moneda": 2, "trm": 4420.10, "promedio_hist": 4420.10, "volatilidad": 0.0},
    {"fecha": "2025-04-02", "id_moneda": 2, "trm": 4445.30, "promedio_hist": 4432.70, "volatilidad": 0.4},
    {"fecha": "2025-04-03", "id_moneda": 2, "trm": 4462.75, "promedio_hist": 4442.71, "volatilidad": 0.6},
    {"fecha": "2025-04-04", "id_moneda": 2, "trm": 4438.20, "promedio_hist": 4441.58, "volatilidad": 0.5},
    {"fecha": "2025-04-07", "id_moneda": 2, "trm": 4478.50, "promedio_hist": 4448.97, "volatilidad": 0.7},
]

# ── Tabla de Hechos: Operaciones ────────────────────────────
FACT_OPERACIONES = [
    {"id_inversionista": 1, "id_moneda": 1, "tipo": "COMPRA", "monto_divisa": 500.0,  "trm": 4050.50, "fecha": "2025-04-01"},
    {"id_inversionista": 2, "id_moneda": 1, "tipo": "COMPRA", "monto_divisa": 1000.0, "trm": 4075.25, "fecha": "2025-04-02"},
    {"id_inversionista": 3, "id_moneda": 2, "tipo": "COMPRA", "monto_divisa": 800.0,  "trm": 4420.10, "fecha": "2025-04-01"},
    {"id_inversionista": 1, "id_moneda": 1, "tipo": "VENTA",  "monto_divisa": 300.0,  "trm": 4120.30, "fecha": "2025-04-07"},
    {"id_inversionista": 4, "id_moneda": 2, "tipo": "COMPRA", "monto_divisa": 600.0,  "trm": 4445.30, "fecha": "2025-04-02"},
    {"id_inversionista": 5, "id_moneda": 1, "tipo": "COMPRA", "monto_divisa": 2000.0, "trm": 4088.75, "fecha": "2025-04-04"},
]

# ── Alertas ─────────────────────────────────────────────────
FACT_ALERTAS = [
    {"id_moneda": 1, "tipo_alerta": "MANTENER", "trm": 4050.50, "promedio": 4062.87, "fecha": "2025-04-01 08:00:00"},
    {"id_moneda": 1, "tipo_alerta": "COMPRAR",  "trm": 4075.25, "promedio": 4087.36, "fecha": "2025-04-02 08:00:00"},
    {"id_moneda": 2, "tipo_alerta": "MANTENER", "trm": 4420.10, "promedio": 4432.70, "fecha": "2025-04-01 08:00:00"},
    {"id_moneda": 2, "tipo_alerta": "VENDER",   "trm": 4478.50, "promedio": 4441.58, "fecha": "2025-04-07 08:00:00"},
    {"id_moneda": 1, "tipo_alerta": "VENDER",   "trm": 4120.30, "promedio": 4087.36, "fecha": "2025-04-07 08:00:00"},
]

# ── Umbrales ────────────────────────────────────────────────
UMBRAL_VOLATILIDAD_ALTA = 2.0
UMBRAL_ALERTA_VENTA     = 1.02
UMBRAL_ALERTA_COMPRA    = 0.98
PERFILES                = ["Conservador", "Moderado", "Agresivo"]
