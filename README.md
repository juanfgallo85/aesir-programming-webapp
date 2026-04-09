# AESIR Programming WebApp

App web Flask para consultar la programacion de un box de CrossFit usando archivos JSON validados con Pydantic.

El MVP ya permite navegar por:

- hoy
- cualquier dia con sesion cargada
- semanas actuales e historicas
- bloques del ano
- calendario anual
- biblioteca de movimientos
- glosario
- exportacion limpia de dia y semana para impresion o PDF

## Stack

- Flask
- Jinja
- Bootstrap 5
- JSON como capa de datos
- Pydantic para validacion
- Gunicorn para despliegue

## Estructura general

```text
app/
  routes/        blueprints Flask
  services/      loaders, helpers de semanas, biblioteca y exportacion
  models/        modelos Pydantic
  templates/     vistas Jinja
  static/css/    estilos base, componentes y print
data/
  gym/           perfil del box y perfiles de atletas
  library/       movimientos y glosario
  programming/   ciclo, bloques, semanas, sesiones por fecha y reglas del generador
scripts/
  seed_full_year.py
  refresh_future_weeks.py
  validate_data.py
tests/
  test_routes_smoke.py
run.py
Procfile
requirements.txt
```

## Entorno local

Crear el entorno virtual local:

```powershell
py -3 -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## VS Code

El workspace ya incluye `.vscode/settings.json` para apuntar al entorno local del proyecto:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true
}
```

Si VS Code sigue mostrando otro interprete:

1. Abre la paleta con `Ctrl+Shift+P`
2. Ejecuta `Python: Select Interpreter`
3. Elige `.\.venv\Scripts\python.exe`

## Validar datos JSON

```powershell
python scripts\validate_data.py
```

## Sesiones y estados

La app ahora soporta sesiones manuales y sesiones auto generadas.

- Manual / legado: por compatibilidad se leen como `reviewed` si el JSON no declara estado.
- Auto generated: el generador las escribe con `status: draft`, `is_auto_generated: true`, `generated_by` y `generated_at`.

Estados soportados:

- `draft`: borrador regenerable
- `reviewed`: revisada y protegida contra regeneracion
- `final`: aprobada para operacion
- `locked`: bloqueada, no se toca automaticamente

Regla practica:

- `seed_full_year.py` no sobrescribe `reviewed`, `final` ni `locked`
- `refresh_future_weeks.py` solo toca `draft` si lo ejecutas con `--overwrite-draft yes`

## Correr la app localmente

En Windows corre la app local con Python:

```powershell
python run.py
```

`gunicorn` no es la opcion para desarrollo local en Windows dentro de este proyecto.

Abrir en el navegador:

```text
http://127.0.0.1:5000/
```

## Smoke tests

```powershell
python -m unittest tests\test_routes_smoke.py
```

## Poblar el ano por adelantado

Sembrar borradores para 2026 completo sin tocar sesiones protegidas:

```powershell
python scripts\seed_full_year.py --year 2026
```

Hacer una corrida de prueba sin escribir archivos:

```powershell
python scripts\seed_full_year.py --year 2026 --dry-run yes
```

Sembrar solo un rango:

```powershell
python scripts\seed_full_year.py --start-date 2026-06-01 --end-date 2026-08-31 --overwrite-draft no
```

## Refrescar semanas futuras

Renovar las siguientes 6 semanas desde una fecha base, regenerando solo drafts:

```powershell
python scripts\refresh_future_weeks.py --start-date 2026-05-01 --weeks-ahead 6 --overwrite-draft yes
```

Ver el impacto antes de escribir:

```powershell
python scripts\refresh_future_weeks.py --start-date 2026-05-01 --weeks-ahead 6 --overwrite-draft yes --dry-run yes
```

Si quieres crear faltantes pero conservar los drafts actuales:

```powershell
python scripts\refresh_future_weeks.py --start-date 2026-05-01 --weeks-ahead 6 --overwrite-draft no
```

## Rutas principales

- `/`
- `/today`
- `/day/<session_date>`
- `/week/current`
- `/week/<week_start>`
- `/block/current`
- `/block/<block_id>`
- `/calendar`
- `/library`
- `/library/movement/<slug>`
- `/glossary`
- `/export/day/<session_date>`
- `/export/week/<week_start>`

## Que cubre el MVP

- App Flask funcional y navegable sin base de datos
- Capa de datos en JSON validada con Pydantic
- 1 ciclo anual, 13 bloques y 52 semanas navegables
- 48 sesiones manuales protegidas como referencia y cientos de borradores `draft` para poblar el resto del ano
- Vista de dia, semana, bloque y calendario
- Biblioteca de movimientos y glosario util para operacion real
- Exportacion de dia y semana lista para impresion o PDF
- Generacion semiautomatica de borradores por bloque, familia de dia y rango de fechas
- Refresh mensual de semanas futuras sin tocar contenido revisado o aprobado
- Estilo mobile-first con Bootstrap 5 y CSS propio ligero
- Smoke tests practicos para rutas principales y validacion de datos

## Que se deja para V2

- comentarios entre coaches
- edicion de programacion por head coach
- autenticacion
- panel admin real
- base de datos
- flujos de aprobacion o versionado editorial

## Despliegue

Para produccion Linux o Koyeb, `Procfile` ya esta listo para usar Gunicorn:

```text
web: gunicorn run:app
```

Resumen practico:

- Local Windows: `python run.py`
- Produccion Linux/Koyeb: `gunicorn run:app`

Si el host instala dependencias desde `requirements.txt` y ejecuta el `Procfile`, la app queda lista para desplegar.
