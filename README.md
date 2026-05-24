# 💵 DOLAR-TRACK — Analítica Cambiaria 

> **Reto 3 | Economía y Finanzas**  
> Sistema End-to-End de monitoreo de TRM, gestión de inversionistas y análisis de decisión cambiaria.

---

## 📋 Descripción del Proyecto

**DolarTrack** es un sistema de analítica cambiaria desarrollado en Python que permite registrar y analizar la Tasa Representativa del Mercado (TRM) del USD y EUR frente al COP, gestionar inversionistas con diferentes perfiles de riesgo, registrar operaciones de compra/venta de divisas y generar alertas automáticas de decisión de inversión.

El proyecto implementa una arquitectura **End-to-End** completa:

```
VS Code (Python) → SQLite (Base de Datos) → Tkinter (GUI) → Power BI (Análisis Visual)
```

---

## 🗂 Estructura del Proyecto

```
DolarTrack/
├── main.py                        # Orquestador principal
├── README.md                      # Este archivo
├── dashboard_dolartrack.html      # Dashboard web analítico
├── DolarTrack_PowerBI.xlsx        # Datos exportados para Power BI
├── DolarTrack_PowerBI.pbix        # Dashboard Power BI
│
├── Backend/                       # Lógica de negocio y base de datos
│   ├── datos.py                   # Datos iniciales y constantes
│   ├── trm.py                     # Registro y análisis de TRM
│   ├── inversionistas.py          # Gestión de inversionistas
│   ├── operaciones.py             # Operaciones de compra/venta
│   ├── alertas.py                 # Alertas y reportes analíticos
│   └── dolar_track.db             # Base de datos SQLite
│
└── Frontend/                      # Interfaz gráfica
    ├── interfaz.py                # GUI Tkinter completa
    └── imagenes/
        └── logo.png               # Logo generado con Pillow
```

---

## ⚙️ Requisitos

- Python **3.10+**
- Librerías necesarias:

```bash
pip install pillow
```

> Las demás librerías (`tkinter`, `sqlite3`, `statistics`) vienen incluidas con Python.

---

## 🚀 Instalación y Ejecución

**1. Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/dolar-track.git
cd dolar-track
```

**2. Instala dependencias:**
```bash
pip install pillow
```

**3. Ejecuta el sistema:**
```bash
python main.py
```

La base de datos se crea automáticamente con datos iniciales en el primer arranque.

---

## 🖥 Interfaz Gráfica (Tkinter + Pillow)

La GUI cuenta con **5 módulos** accesibles desde la barra de navegación:

### 📊 Dashboard
Vista general con KPIs en tiempo real:
- TRM actual USD y EUR
- Promedio histórico y volatilidad
- Señal automática de decisión (COMPRAR / VENDER / MANTENER)
- Tabla de historial reciente y últimas operaciones

### 📈 TRM
- Registro de TRM diaria (USD / EUR)
- Validación de formato de fecha y valores numéricos
- Señal automática al registrar cada valor
- Historial filtrable por moneda
- Actualización de registros existentes

### 👤 Inversionistas
- Registro con perfil de riesgo (Conservador / Moderado / Agresivo)
- Cálculo de exposición cambiaria según perfil
- Actualización de capital disponible

### 💼 Operaciones
- Registro de compras y ventas de divisas
- TRM manual o calculada automáticamente desde el promedio histórico
- Resumen de movimientos por inversionista en tiempo real

### 🔔 Alertas
- Análisis completo de señal de decisión
- Reporte de volatilidad y estadísticas
- Historial filtrable por moneda (USD / EUR)

---

## 🗄 Base de Datos (SQLite)

### Tablas

| Tabla | Descripción |
|---|---|
| `trm` | Registro histórico de TRM por fecha y moneda |
| `inversionistas` | Perfil y capital de cada inversionista |
| `operaciones` | Historial de compras y ventas de divisas |
| `alertas` | Señales automáticas generadas por el sistema |

### Diagrama de relaciones

```
inversionistas (id) ──→ operaciones (id_inversionista)
trm (fecha, moneda)  ──→ alertas (moneda, trm, promedio)
```

---

## 📊 Análisis y Señales Automáticas

El sistema genera señales de decisión comparando la TRM actual contra el promedio histórico:

| Condición | Señal |
|---|---|
| TRM > promedio × 1.02 | 🔴 **VENDER** — TRM por encima del promedio |
| TRM < promedio × 0.98 | 🟢 **COMPRAR** — TRM por debajo del promedio |
| En rango normal | 🟡 **MANTENER** — TRM dentro del rango |

### Perfiles de riesgo

| Perfil | % Capital expuesto |
|---|---|
| Conservador | 20% |
| Moderado | 40% |
| Agresivo | 70% |

### Umbral de volatilidad
- Coeficiente de variación **> 2%** → ⚡ Alta volatilidad detectada

---

## 📈 Power BI Dashboard

El archivo `DolarTrack_PowerBI.pbix` contiene **3 páginas** de análisis visual:

**Página 1 — Dashboard TRM**
- Evolución histórica TRM USD (gráfico de líneas)
- Evolución histórica TRM EUR (gráfico de líneas)
- Tarjetas KPI: TRM actual USD, TRM actual EUR, total inversionistas, total operaciones

**Página 2 — Operaciones**
- Compras vs Ventas por inversionista (barras agrupadas)
- Total COP movido por inversionista (barras)

**Página 3 — Alertas e Inversionistas**
- Capital por perfil de riesgo (gráfico circular)
- Frecuencia de alertas por tipo de señal (barras)
- Capital por inversionista (barras)

---

## 👥 Módulos del Backend

| Archivo | Clase | Responsabilidad |
|---|---|---|
| `trm.py` | `RegistroTRM` | CRUD de TRM, estadísticas, señales |
| `inversionistas.py` | `GestorInversionistas` | CRUD de inversionistas, exposición cambiaria |
| `operaciones.py` | `GestorOperaciones` | CRUD de operaciones, resúmenes |
| `alertas.py` | `GestorAlertas` | Registro de alertas, reportes de decisión |
| `datos.py` | — | Constantes, datos semilla, umbrales |

---

## 🔒 Seguridad y Validaciones

Todos los formularios implementan validación con `try-except` y `messagebox`:

- ✅ Campos obligatorios vacíos
- ✅ Formato de fecha `YYYY-MM-DD`
- ✅ Valores numéricos positivos
- ✅ Selección de perfil y moneda válidos
- ✅ Duplicados en registros de TRM por fecha y moneda

---

## 📌 Tecnologías Utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| SQLite3 | Base de datos relacional |
| Tkinter | Interfaz gráfica |
| Pillow | Procesamiento de imagen / logo |
| Power BI Desktop | Dashboard analítico visual |
| openpyxl | Exportación de datos a Excel |

---

## 👨‍💻 Autores 
JUAN SEBASTIAN SALAS 
LUKAS BLANCO 
ALAN ROSSOFF

**Reto 3 — Economía "Dolar-Track"**  
Curso: Fundamentos de Programación  
Arquitectura End-to-End: VS Code → SQLite → Tkinter → Power BI
