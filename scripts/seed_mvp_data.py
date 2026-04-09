from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SESSIONS_DIR = BASE_DIR / "data" / "programming" / "sessions"
WEEKS_PATH = BASE_DIR / "data" / "programming" / "weeks.json"
MOVEMENTS_PATH = BASE_DIR / "data" / "library" / "movements.json"
GLOSSARY_PATH = BASE_DIR / "data" / "library" / "glossary.json"


def dump_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=True)
        file.write("\n")


def movement(name: str, **kwargs) -> dict[str, object]:
    item = {"name": name}
    item.update(kwargs)
    return item


def scaling(level: str, adjustment: str) -> dict[str, str]:
    return {"level": level, "adjustment": adjustment}


def coach_note(title: str, content: str) -> dict[str, str]:
    return {"title": title, "content": content}


def make_scaling(primary: str, intermediate: str, rx: str) -> list[dict[str, str]]:
    return [
        scaling("Principiante", primary),
        scaling("Intermedio", intermediate),
        scaling("RX", rx),
        scaling(
            "Competidor",
            "Mantener RX y agregar control de pacing, densidad o volumen extra solo si la tecnica sigue limpia.",
        ),
    ]


def make_part(
    title: str,
    part_type: str,
    duration: int,
    description: str,
    *,
    format: str | None = None,
    scheme: str | None = None,
    score_type: str | None = None,
    movements: list[dict[str, object]] | None = None,
    notes: str | None = None,
) -> dict[str, object]:
    item: dict[str, object] = {
        "title": title,
        "part_type": part_type,
        "duration_minutes": duration,
        "description": description,
    }
    if format:
        item["format"] = format
    if scheme:
        item["scheme"] = scheme
    if score_type:
        item["score_type"] = score_type
    if movements:
        item["movements"] = movements
    if notes:
        item["notes"] = notes
    return item


def iso_dates(week_start: str) -> list[str]:
    start = date.fromisoformat(week_start)
    return [(start + timedelta(days=offset)).isoformat() for offset in range(6)]


def session_day(
    session_date: str,
    title: str,
    *,
    goal: str,
    coach_summary: str,
    public_summary: str,
    family_type: str,
    dominant_stimulus: str,
    dominant_pattern: str,
    technical_level: str,
    fatigue_level: str,
    operational_color: str,
    equipment_alert: str,
    session_parts: list[dict[str, object]],
    scaling_options: list[dict[str, str]],
    coach_notes: list[dict[str, str]],
) -> dict[str, object]:
    return {
        "session_date": session_date,
        "title": title,
        "goal": goal,
        "coach_summary": coach_summary,
        "public_summary": public_summary,
        "family_type": family_type,
        "dominant_stimulus": dominant_stimulus,
        "dominant_pattern": dominant_pattern,
        "technical_level": technical_level,
        "fatigue_level": fatigue_level,
        "operational_color": operational_color,
        "equipment_alert": equipment_alert,
        "session_parts": session_parts,
        "scaling_options": scaling_options,
        "coach_notes": coach_notes,
    }


def build_engine_week(week_start: str, focus: str, variant: int) -> list[dict[str, object]]:
    days = iso_dates(week_start)
    monday_titles = ["Monday Base Builder", "Press and Pace Intervals", "Long Pull and Hinge", "Engine Reset Test 1"]
    tuesday_titles = ["Upper Pull Capacity", "Carry and Pull Flow", "Gymnastics Flow 2", "Pull Recovery Builder"]
    wednesday_titles = ["Midweek Engine Builder", "Tempo Front Rack Builder", "Wall Ball and Run Builder", "Front Squat Test"]
    thursday_titles = ["Gymnastics Density Day", "Aerobic Lunge Builder", "Press and Carry Builder", "Aerobic Test Builder"]
    friday_titles = ["Friday Threshold Grind", "Engine Checkpoint", "Friday Long Chipper", "Friday Mixed Test Piece"]
    saturday_titles = ["Saturday Team Engine", "Saturday Community Chipper", "Saturday Carry Relay", "Saturday Reset and Recover"]

    front_squat_scheme = ["5 x 3 @ 72% del 1RM", "4 x 4 @ 31X1", "5 x 2 @ 75% del 1RM", "Build to a heavy triple tecnico"][variant]
    front_squat_load = [("95 lb", "65 lb"), ("85 lb", "55 lb"), ("95 lb", "65 lb"), ("95 lb", "65 lb")][variant]
    run_distance = [400, 300, 400, 200][variant]
    run_alternative = [
        "500 m row o 24/20 cal bike si hace frio o esta lloviendo",
        "400 m row o 20/16 cal bike si el clima no deja correr",
        "500 m row o 22/18 cal bike si no se puede salir",
        "250 m row si el clima no permite correr alrededor del gimnasio",
    ][variant]
    friday_bike = [(10, 8), (12, 10), (0, 0), (8, 6)][variant]

    monday = session_day(
        days[0],
        monday_titles[variant],
        goal=f"Sostener el enfoque semanal: {focus}",
        coach_summary="Ordenar el piso temprano y pedir respiracion estable desde la primera pieza.",
        public_summary="Sesion para construir motor y fuerza util con progresion clara y escalable.",
        family_type="mixed_modal",
        dominant_stimulus="aerobic base" if variant < 2 else "aerobic power",
        dominant_pattern="hinge",
        technical_level="beginner-intermediate" if variant != 3 else "intermediate",
        fatigue_level="moderate" if variant != 3 else "high",
        operational_color="green" if variant < 3 else "yellow",
        equipment_alert="Uso compartido de rowers, barras y espacio exterior segun el clima.",
        session_parts=[
            make_part("Joint Prep", "joint_prep", 6, "Movilidad general de tobillo, cadera y espalda media para preparar bisagra y locomocion."),
            make_part("Warm-Up", "warm_up", 8, "Row o jog suave, hinge pattern y activacion de core.", format="2 rounds", scheme="150 m row, 10 PVC good mornings, 8 glute bridges, 20 s dead bug hold"),
            make_part("Deadlift Prep", "skill", 8, "Repasar brace y salida desde el piso con buena tension.", movements=[movement("Deadlift", sets=3, reps=4, suggested_load_general="Ligero a moderado para fijar posicion")]),
            make_part("Deadlift Strength", "strength", 10, "Volumen corto de bisagra para reforzar postura util para clase.", format="Working sets", scheme="5 x 5" if variant < 2 else "4 x 4", score_type="quality_load", movements=[movement("Deadlift", sets=5 if variant < 2 else 4, reps=5 if variant < 2 else 4, suggested_load_general="Carga moderada con tecnica constante")]),
            make_part("Engine Hinge WOD", "wod", 18, "Pieza principal para sostener ritmo sin perder calidad de bisagra.", format="AMRAP", scheme="12-18 minutes segun variante", score_type="rounds_and_reps", movements=[movement("Row", distance_meters=250), movement("Deadlift", reps=10 if variant < 2 else 12, suggested_load_male="135 lb", suggested_load_female="95 lb"), movement("Run", running_distance_meters=200 if variant != 2 else 400, weather_alternative="250 m row si no se puede salir")], notes="La barra debe permitir series continuas al menos en el primer tercio del WOD."),
            make_part("Cooldown", "cooldown", 6, "Respiracion, descarga de posterior y cierre breve."),
        ],
        scaling_options=make_scaling("Reducir metros, bajar carga o cambiar la carrera por row.", "Mantener el formato con barra moderada y transiciones ordenadas.", "Seguir el volumen y carga objetivo del dia."),
        coach_notes=[coach_note("Brace", "No sacrificar posicion lumbar por velocidad al despegar la barra."), coach_note("Flow", "Dejar carriles muy claros para que open gym no se mezcle con la clase.")],
    )

    tuesday = session_day(
        days[1],
        tuesday_titles[variant],
        goal=f"Construir densidad de tiron y trabajo de agarre dentro de {focus}.",
        coach_summary="Elegir la progresion de tiron correcta antes de perseguir velocidad o volumen.",
        public_summary="Trabajo de traccion superior y base respiratoria con opciones claras para todos.",
        family_type="gymnastics_bias",
        dominant_stimulus="muscular endurance" if variant != 3 else "recovery",
        dominant_pattern="pull",
        technical_level="intermediate" if variant != 3 else "beginner-intermediate",
        fatigue_level="moderate" if variant != 3 else "low-moderate",
        operational_color="green",
        equipment_alert="Se requiere barra de pull-up, anillas y espacio para carries.",
        session_parts=[
            make_part("Shoulder Prep", "joint_prep", 6, "Movilidad escapular, dorsal y grip prep."),
            make_part("General Warm-Up", "warm_up", 8, "Row suave, scap pulls y hollow work.", format="2 rounds", scheme="150 m row, 6 scap pulls, 20 s hollow hold"),
            make_part("Pull Skill", "skill", 10, "Practicar strict pull-up, ring row o rope progression segun la variante.", movements=[movement("Strict Pull-Up", reps=4), movement("Ring Row", reps=6), movement("Rope Climb Progression", reps=3, notes="Usar seated pull o stand drill si aplica")]),
            make_part("Pull Density WOD", "wod", 14 if variant == 3 else 16, "Pieza para repetir tiron, core y agarre sin romper tecnica.", format="AMRAP" if variant != 3 else "EMOM", scheme="14-16 minutes", score_type="rounds_and_reps" if variant != 3 else "quality_rounds", movements=[movement("Row", distance_meters=200 if variant != 3 else 125), movement("Ring Row", reps=12 if variant != 3 else 8), movement("Hanging Knee Raise", reps=10), movement("Farmer Carry", distance_meters=30, suggested_load_general="Moderado")], notes="Escalar temprano si la posicion de hombro deja de verse estable."),
            make_part("Accessory", "accessory", 6, "Trabajo breve de espalda alta y respiracion.", movements=[movement("Banded Face Pull", reps=15), movement("Dead Bug", reps=10)]),
            make_part("Cooldown", "cooldown", 6, "Soltar dorsales, antebrazos y hombros."),
        ],
        scaling_options=make_scaling("Usar ring rows, menos metros y carries mas cortos.", "Mantener el formato con la progresion correcta de tiron.", "Seguir la sesion completa con reps limpias y hombro activo."),
        coach_notes=[coach_note("Grip", "Controlar fatiga de agarre desde el warm-up."), coach_note("Quality", "No dejar que el kip o la cuerda rompan la posicion de hombro.")],
    )

    wednesday = session_day(
        days[2],
        wednesday_titles[variant],
        goal=f"Reforzar el patron de squat dentro del objetivo del bloque: {focus}.",
        coach_summary="La posicion manda la clase. Subir carga solo si el front rack y la profundidad siguen limpios.",
        public_summary="Sesion de sentadilla y motor con un WOD principal claro, exigente y escalable.",
        family_type="mixed_modal",
        dominant_stimulus="aerobic power" if variant != 3 else "strength",
        dominant_pattern="squat",
        technical_level="intermediate",
        fatigue_level="moderate" if variant < 3 else "moderate-high",
        operational_color="green" if variant < 3 else "yellow",
        equipment_alert="Uso moderado de racks, barras y una maquina por pareja.",
        session_parts=[
            make_part("Rack Mobility", "joint_prep", 6, "Movilidad de tobillo, cadera y front rack para preparar la sentadilla."),
            make_part("Warm-Up", "warm_up", 8, "Jog corto, air squats y tempo squats con PVC.", format="2 rounds", scheme="150 m jog, 10 air squats, 6 tempo front squats con PVC"),
            make_part("Front Squat Prep", "skill", 8, "Series tecnicas de squat y postura.", movements=[movement("Front Squat", sets=3, reps=3, suggested_load_general="Ligero para fijar postura")]),
            make_part("Front Squat Strength", "strength", 12 if variant != 3 else 14, "Bloque de fuerza del dia con porcentaje claro o build controlado.", format="Strength work", scheme=front_squat_scheme, score_type="quality_load", movements=[movement("Front Squat", sets=5 if variant == 0 else 4 if variant in {1, 2} else None, reps=3 if variant == 0 else 4 if variant == 1 else 2 if variant == 2 else 3, percentage_of_pr=front_squat_scheme if "%" in front_squat_scheme else None, suggested_load_general="Subir solo si la postura sigue limpia")], notes="Priorizar codos altos y recepcion estable en cada serie."),
            make_part("Midweek Squat WOD", "wod", 16 if variant != 3 else 10, "WOD principal para mezclar locomocion, squat y respiracion bajo fatiga.", format="For time" if variant in {0, 2, 3} else "Every 4:00", scheme="3-4 rounds segun variante", score_type="for_time" if variant in {0, 2, 3} else "time_per_set", movements=[movement("Run", running_distance_meters=run_distance, weather_alternative=run_alternative), movement("Front Squat", reps=12 if variant == 0 else 8 if variant == 1 else 15 if variant == 2 else 6, suggested_load_male=front_squat_load[0], suggested_load_female=front_squat_load[1]), movement("Burpee Over Bar", reps=10)]),
            make_part("Cooldown", "cooldown", 6 if variant != 3 else 8, "Respiracion, cuadriceps y release de front rack."),
        ],
        scaling_options=make_scaling("Reducir metros, usar goblet squat o bajar la carga de la barra.", "Mantener repeticiones con squat moderado y carrera controlada.", "Seguir el volumen y carga objetivo de la clase."),
        coach_notes=[coach_note("Front Rack", "Corregir codos bajos antes de subir carga."), coach_note("Pacing", "La carrera no puede romper la postura de la primera sentadilla.")],
    )

    thursday = session_day(
        days[3],
        thursday_titles[variant],
        goal=f"Dar continuidad al bloque con trabajo unilateral, gimnasia simple o soporte aerobico: {focus}.",
        coach_summary="Mantener una sesion clara, accesible y muy ordenada operativamente.",
        public_summary="Trabajo util de clase general con movimiento simple, core y respiracion.",
        family_type="mixed_modal",
        dominant_stimulus="density" if variant == 0 else "aerobic endurance" if variant != 3 else "aerobic base",
        dominant_pattern="squat" if variant == 0 else "single_leg" if variant == 1 else "press" if variant == 2 else "cyclical",
        technical_level="beginner-intermediate",
        fatigue_level="moderate",
        operational_color="green",
        equipment_alert="Espacio de piso, boxes y maquinas listos segun la variante del dia.",
        session_parts=[
            make_part("Joint Prep", "joint_prep", 6, "Activacion de hombro, cadera y linea media para movernos con control."),
            make_part("Warm-Up", "warm_up", 8, "Locomocion simple, core y activacion de piernas.", format="2 rounds", scheme="20 m walkouts o marches, 8 lunges, 20 s plank"),
            make_part("Skill Primer", "skill", 8 if variant != 3 else 6, "Practicar el patron principal del dia y fijar transiciones.", movements=[movement("Box Step-Up", reps=6), movement("Walking Lunge", reps=8), movement("Dumbbell Push Press", reps=6, suggested_load_general="Ligero")]),
            make_part("Thursday Builder", "wod", 16 if variant != 3 else 20, "Pieza principal para sostener densidad y calidad.", format="AMRAP" if variant != 3 else "For time", scheme="16-20 minutes", score_type="rounds_and_reps" if variant != 3 else "for_time", movements=[movement("Bike", machine_calories_male=12 if variant in {1, 3} else 8, machine_calories_female=10 if variant in {1, 3} else 6), movement("Box Step-Up", reps=12), movement("Walking Lunge", reps=16), movement("Run", running_distance_meters=200, weather_alternative="250 m row si el clima no permite salir")], notes="La postura del tronco debe verse igual del principio al final."),
            make_part("Accessory", "accessory", 6, "Trabajo breve de core y respiracion.", movements=[movement("Dead Bug", reps=10), movement("Couch Stretch", reps=1, notes="30 s por lado")]),
            make_part("Cooldown", "cooldown", 6, "Cierre de cadera, hombros y respiracion."),
        ],
        scaling_options=make_scaling("Bajar reps, calorias o usar versiones estacionarias del patron.", "Mantener el formato con carga ligera o reps recortadas.", "Seguir el volumen completo del dia con control tecnico."),
        coach_notes=[coach_note("Floor Flow", "Separar por carriles y niveles para evitar cruces."), coach_note("Core", "La calidad del tronco manda el ritmo del dia.")],
    )

    friday_main = [movement("Bike", machine_calories_male=friday_bike[0], machine_calories_female=friday_bike[1])] if friday_bike[0] else [movement("Row", distance_meters=250)]
    friday_main.append(movement("Thruster" if variant != 3 else "Power Clean", reps=12 if variant in {0, 1} else 21 if variant == 3 else 0, suggested_load_male="95 lb", suggested_load_female="65 lb"))
    friday_main.append(movement("Run", running_distance_meters=200 if variant in {0, 1} else 800 if variant == 2 else 0, weather_alternative="250 m row si el clima no permite correr"))
    friday = session_day(
        days[4],
        friday_titles[variant],
        goal=f"Cerrar la semana con una pieza fuerte y muy clara dentro de {focus}.",
        coach_summary="El error comun del viernes es salir demasiado rapido. Pacing primero, ego despues.",
        public_summary="Sesion exigente para practicar tolerancia al esfuerzo y control tecnico.",
        family_type="mixed_modal",
        dominant_stimulus="threshold" if variant != 2 else "aerobic endurance",
        dominant_pattern="squat" if variant == 0 else "mixed",
        technical_level="intermediate",
        fatigue_level="high",
        operational_color="yellow",
        equipment_alert="Asignar carriles por pareja y explicar muy bien el flujo antes de arrancar.",
        session_parts=[
            make_part("Joint Prep", "joint_prep", 6, "Movilidad de hombro, tobillo y tronco para soportar el WOD principal."),
            make_part("Warm-Up", "warm_up", 8, "Bike o row suave, barbell prep y activacion general.", format="2 rounds", scheme="5/4 cal bike, 6 squats o presses ligeros, 4 burpees"),
            make_part("Primer", "skill", 6, "Series progresivas o repaso rapido del patron del dia.", movements=[movement("Thruster" if variant != 3 else "Power Clean", sets=3, reps=3 if variant == 3 else 5, suggested_load_general="Ligero y tecnico")]),
            make_part("Friday Main WOD", "wod", 24 if variant in {0, 2} else 20 if variant == 1 else 14, "Pieza principal del dia para cerrar la semana con un esfuerzo util y medible.", format="For time" if variant != 1 else "Every 5:00", scheme="3-5 rounds segun variante", score_type="for_time" if variant != 1 else "time_per_set", movements=[item for item in friday_main if not (item["name"] == "Run" and item.get("running_distance_meters", 0) == 0) and not (item["name"] in {"Thruster", "Power Clean"} and item.get("reps", 0) == 0)], notes="Buscar un negative split o al menos una caida minima entre sets."),
            make_part("Competitor Extra", "competitor_extra", 5, "Flush corto para atletas con margen.", format="EMOM", scheme="5 minutes", movements=[movement("Toes-to-Bar", reps=6)]) if variant in {0, 3} else make_part("Accessory Reset", "accessory", 6, "Carry corto y respiracion de recuperacion."),
            make_part("Cooldown", "cooldown", 6, "Soltar hombros, cuadriceps y zona media."),
        ],
        scaling_options=make_scaling("Reducir metros, reps o carga del implemento principal.", "Mantener el formato con volumen intermedio y tecnica limpia.", "Completar el volumen tal como esta programado."),
        coach_notes=[coach_note("Pacing", "La primera salida debe ser la mas disciplinada del dia."), coach_note("Standards", "No regalar lockout, profundidad ni reps dudosas.")],
    )

    saturday = session_day(
        days[5],
        saturday_titles[variant],
        goal=f"Cerrar la semana con una sesion social y util conectada con {focus}.",
        coach_summary="El sabado debe sentirse comunitario, ordenado y con opciones simples para todos.",
        public_summary="Sesion en parejas o equipos con enfasis en motor, relevos claros y buena experiencia de clase.",
        family_type="partner_work",
        dominant_stimulus="aerobic endurance" if variant != 3 else "recovery",
        dominant_pattern="mixed" if variant != 0 else "pull",
        technical_level="beginner",
        fatigue_level="moderate" if variant != 3 else "low-moderate",
        operational_color="green",
        equipment_alert="Compartir una sola maquina por duo o equipo y dejar open gym operativo.",
        session_parts=[
            make_part("Joint Prep", "joint_prep", 6, "Activacion general y respiracion para una clase larga y social."),
            make_part("Warm-Up", "warm_up", 8, "Row o bike suave, medball prep y carry ligera.", format="2 rounds", scheme="100-150 m row, 8 medball squats, 20 m carry"),
            make_part("Partner Prep", "skill", 6, "Practicar relevos, conteo de reps y estandares del trabajo en equipo."),
            make_part("Saturday Team WOD", "wod", 22 if variant != 3 else 20, "Pieza principal del sabado para sostener flujo comunitario y buena energia.", format="AMRAP", scheme="20-24 minutes in pairs o teams of 3", score_type="rounds_and_reps", movements=[movement("Row", distance_meters=300 if variant == 0 else 250), movement("Wall Ball", reps=20 if variant == 0 else 16), movement("Run", running_distance_meters=200 if variant in {1, 2} else 0, weather_alternative="250 m row o 10/8 cal bike"), movement("Farmer Carry", distance_meters=30 if variant != 3 else 20, suggested_load_general="Ligero a moderado")], notes="Los relevos deben ser cortos y consistentes, no hero turns."),
            make_part("Cooldown", "cooldown", 6 if variant != 3 else 8, "Movilidad ligera, respiracion y charla de cierre."),
        ],
        scaling_options=make_scaling("Bajar metros, carga o reps para sostener buena experiencia de clase.", "Mantener la estructura con relevos mas cortos y volumen intermedio.", "Seguir el plan tal como esta con foco en flujo y consistencia."),
        coach_notes=[coach_note("Pairing", "Emparejar por ritmo y experiencia, no solo por amistad."), coach_note("Logistics", "Dejar carriles muy claros y una sola maquina por duo o equipo.")],
    )
    return [monday, tuesday, wednesday, thursday, friday, saturday]


def build_summer_week(week_start: str, focus: str, variant: int) -> list[dict[str, object]]:
    days = iso_dates(week_start)
    titles = [
        ["Summer Base Run", "Row and Carry Builder", "Bike Tempo Builder", "Run and Core Ladder", "Carry Threshold Friday", "Holiday Partner Engine"],
        ["Summer Mixed Engine 2", "Carry and Core Builder 2", "Bike and Wall Ball Builder", "Run Ladder Summer", "Friday Long Summer WOD", "Saturday Summer Team Flow"],
    ][variant]
    family_types = ["mixed_modal", "mixed_modal", "mixed_modal", "mixed_modal", "mixed_modal", "partner_work"]
    stimuli = ["aerobic base", "aerobic endurance", "threshold", "aerobic endurance", "threshold" if variant == 0 else "aerobic endurance", "aerobic base"]
    patterns = ["cyclical", "carry", "cyclical", "core", "carry" if variant == 0 else "mixed", "mixed"]
    technicals = ["beginner-intermediate", "beginner", "beginner-intermediate", "beginner", "intermediate", "beginner"]
    fatigues = ["moderate", "moderate", "moderate-high", "moderate", "high", "moderate"]
    colors = ["green", "green", "yellow", "green", "yellow", "green"]
    skill_moves = [
        movement("Run", running_distance_meters=200, weather_alternative="250 m row o 12/10 cal bike"),
        movement("Sandbag Carry", distance_meters=20, suggested_load_general="Ligero a moderado"),
        movement("Bike", machine_calories_male=6, machine_calories_female=5),
        movement("Run", running_distance_meters=200, weather_alternative="250 m row"),
        movement("Sandbag Carry" if variant == 0 else "Front Squat", distance_meters=20 if variant == 0 else None, reps=None if variant == 0 else 5, suggested_load_general="Moderado" if variant == 0 else "Ligero"),
        movement("Farmer Carry", distance_meters=20, suggested_load_general="Ligero"),
    ]
    main_moves = [
        [movement("Run", running_distance_meters=400, weather_alternative="500 m row o 24/20 cal bike"), movement("Farmer Carry", distance_meters=40, suggested_load_general="Moderado"), movement("Sit-Up", reps=16)],
        [movement("Row", distance_meters=300), movement("Sandbag Carry", distance_meters=40, suggested_load_general="Moderado"), movement("Box Step-Up", reps=14)],
        [movement("Bike", machine_calories_male=12 if variant == 0 else 10, machine_calories_female=10 if variant == 0 else 8), movement("Wall Ball", reps=12)],
        [movement("Run", running_distance_meters=200, weather_alternative="250 m row por tramo"), movement("Sit-Up", reps=12)],
        [movement("Bike", machine_calories_male=14 if variant == 0 else 12, machine_calories_female=12 if variant == 0 else 10), movement("Sandbag Carry", distance_meters=60 if variant == 0 else 40, suggested_load_general="Moderado"), movement("Run", running_distance_meters=400 if variant == 1 else 0, weather_alternative="500 m row o 22/18 cal bike"), movement("Wall Ball", reps=15 if variant == 1 else 0)],
        [movement("Row", distance_meters=250), movement("Run", running_distance_meters=200, weather_alternative="250 m row o 10/8 cal bike"), movement("Farmer Carry", distance_meters=30, suggested_load_general="Ligero a moderado"), movement("Sit-Up", reps=15)],
    ]

    sessions = []
    for index, session_date in enumerate(days):
        sessions.append(
            session_day(
                session_date,
                titles[index],
                goal=f"Dar continuidad al bloque de verano: {focus}",
                coach_summary="Usar el clima y la operacion del box para decidir rapido la mejor alternativa sin perder el objetivo del dia.",
                public_summary="Sesion de verano para construir motor, ritmo y trabajo general fitness con buena continuidad.",
                family_type=family_types[index],
                dominant_stimulus=stimuli[index],
                dominant_pattern=patterns[index],
                technical_level=technicals[index],
                fatigue_level=fatigues[index],
                operational_color=colors[index],
                equipment_alert="Exterior, rowers, bikes y cargas simples coordinadas para la misma clase en todos los horarios.",
                session_parts=[
                    make_part("Joint Prep", "joint_prep", 6, "Movilidad de tobillo, cadera y hombro antes del trabajo principal."),
                    make_part("Warm-Up", "warm_up", 8, "Carrera, row o bike progresiva y activacion general.", format="2 rounds", scheme="100-150 m cyclical work, 8 squats o lunges, 20 s plank"),
                    make_part("Skill Prep", "skill", 8 if index not in {2, 3} else 6, "Practicar la pieza tecnica o la transicion principal del dia.", movements=[skill_moves[index]]),
                    make_part("Main WOD", "wod", 18 if index not in {4, 5} else 20 if index == 4 else 22, "Pieza principal del dia para sostener el objetivo del bloque con ritmo util y escalable.", format="AMRAP" if index in {0, 1, 5} else "Intervals" if index in {2, 3} else "For time" if variant == 1 else "Every 5:00", scheme="Bloque de verano", score_type="rounds_and_reps" if index in {0, 1, 5} else "time_per_piece", movements=[item for item in main_moves[index] if not (item["name"] == "Run" and item.get("running_distance_meters", 0) == 0) and not (item["name"] == "Wall Ball" and item.get("reps", 0) == 0)], notes="Priorizar pacing y transiciones limpias antes que hero efforts."),
                    make_part("Accessory", "accessory", 6, "Trabajo breve de core, pie o respiracion para cerrar util.", movements=[movement("Dead Bug", reps=10), movement("Couch Stretch", reps=1, notes="30 s por lado")]) if index in {0, 2} else make_part("Cooldown", "cooldown", 6, "Respiracion, cadera y cierre ligero."),
                    make_part("Cooldown", "cooldown", 6, "Respiracion y descarga de cadera, pantorrilla y hombros.") if index in {0, 1, 2, 4, 5} else make_part("Accessory Reset", "accessory", 6, "Trabajo ligero de recovery y respiracion."),
                ],
                scaling_options=make_scaling("Bajar metros, calorias, carga o usar la alternativa por clima desde el inicio.", "Mantener el formato con volumen intermedio y ritmo estable.", "Seguir la sesion completa del dia con buen control de pacing."),
                coach_notes=[coach_note("Weather", "Tomar la decision exterior/interior antes de arrancar la clase."), coach_note("Summer Pacing", "En calor fuerte, cuidar hidratacion y evitar salidas demasiado agresivas.")],
            )
        )
    return sessions


def build_skill_week(week_start: str, focus: str, variant: int) -> list[dict[str, object]]:
    days = iso_dates(week_start)
    titles = [
        ["Handstand Line Builder", "Rope and Pull Builder", "Tempo Press Density", "Double-Under and Core", "Skill Density Friday", "Saturday Skill Team Flow"],
        ["Strict Pull Density", "Overhead Support Builder", "Gymnastics Repeatability", "Tempo Squat Support", "Friday Skill Sprint", "Saturday Skill Mixer"],
    ][variant]
    family_types = ["gymnastics_bias", "gymnastics_bias", "mixed_modal", "gymnastics_bias", "mixed_modal", "partner_work"]
    stimuli = ["skill density", "muscular endurance", "skill density", "coordination", "threshold" if variant == 0 else "power output", "aerobic base"]
    patterns = ["press", "pull", "press", "cyclical", "mixed", "mixed"]
    technicals = ["intermediate", "intermediate", "intermediate", "beginner-intermediate", "intermediate", "beginner-intermediate"]
    fatigues = ["moderate", "moderate", "moderate", "moderate", "high", "moderate"]
    colors = ["green", "green", "yellow", "green", "yellow", "green"]
    skill_moves = [
        movement("Handstand Hold", reps=1, notes="20-30 s por set"),
        movement("Rope Climb Progression", reps=4, notes="Elegir progresion util para el perfil"),
        movement("Push Press", reps=4, percentage_of_pr="70% del 1RM", suggested_load_general="Moderado y limpio"),
        movement("Double-Under Progression", reps=30),
        movement("Wall Walk", reps=4 if variant == 0 else 0),
        movement("Double-Under Progression", reps=30),
    ]
    main_moves = [
        [movement("Hand-Release Push-Up", reps=10), movement("Box Step-Up", reps=12), movement("Bike", machine_calories_male=8, machine_calories_female=6)],
        [movement("Row", distance_meters=200), movement("Ring Row", reps=12), movement("Hanging Knee Raise", reps=10), movement("Farmer Carry", distance_meters=30, suggested_load_general="Moderado")],
        [movement("Dumbbell Push Press", reps=12, suggested_load_general="Moderado"), movement("Sit-Up", reps=16), movement("Run", running_distance_meters=200, weather_alternative="250 m row")],
        [movement("Double-Under Progression", reps=40), movement("V-Up", reps=12), movement("Row", distance_meters=150)],
        [movement("Bike", machine_calories_male=10 if variant == 0 else 8, machine_calories_female=8 if variant == 0 else 6), movement("Wall Walk", reps=4 if variant == 0 else 0), movement("Dumbbell Push Press", reps=12 if variant == 0 else 10, suggested_load_general="Moderado"), movement("Handstand Hold", reps=1, notes="10-15 s o alternativa equivalente") if variant == 1 else movement("Toes-to-Bar", reps=6)],
        [movement("Row", distance_meters=250), movement("Double-Under Progression", reps=40 if variant == 0 else 30), movement("Farmer Carry", distance_meters=30, suggested_load_general="Ligero a moderado"), movement("Sit-Up", reps=15)],
    ]

    sessions = []
    for index, session_date in enumerate(days):
        sessions.append(
            session_day(
                session_date,
                titles[index],
                goal=f"Desarrollar densidad tecnica y control de skill dentro del bloque: {focus}",
                coach_summary="El objetivo del dia es calidad tecnica repetida, no solo cansarse rapido.",
                public_summary="Sesion tecnica de CrossFit general fitness con progresiones claras y un WOD util.",
                family_type=family_types[index],
                dominant_stimulus=stimuli[index],
                dominant_pattern=patterns[index],
                technical_level=technicals[index],
                fatigue_level=fatigues[index],
                operational_color=colors[index],
                equipment_alert="Wall space, barras, anillas, cuerdas y maquinas organizadas por carriles para no saturar la clase.",
                session_parts=[
                    make_part("Joint Prep", "joint_prep", 6, "Movilidad de muñeca, hombro, cadera y pie segun la skill del dia."),
                    make_part("Warm-Up", "warm_up", 8, "Activacion progresiva del patron principal y linea media.", format="2 rounds", scheme="Trabajo general + activacion especifica"),
                    make_part("Skill Block", "skill", 10 if index not in {0, 1, 3} else 12, "Bloque tecnico principal con opciones reales para todos los perfiles.", movements=[skill_moves[index]]),
                    make_part("Strength / Support", "strength", 10 if index in {0, 2} else 0, "Trabajo de soporte de fuerza para fijar posiciones utiles.", format="Working sets", scheme="5 x 5 o 4 x 4", score_type="quality_load", movements=[movement("Strict Press" if index == 0 else "Push Press", sets=5 if index == 0 else 4, reps=5 if index == 0 else 4, suggested_load_general="Moderado y limpio")]) if index in {0, 2} else make_part("Support Primer", "skill", 6, "Recordar estandares y transiciones antes del WOD."),
                    make_part("Main WOD", "wod", 12 if index in {0, 3} else 14 if index in {1, 2, 4} else 22, "Pieza principal para repetir la skill o un soporte cercano bajo fatiga controlada.", format="AMRAP" if index in {0, 1, 2, 3, 5} else "For time", scheme="12-24 minutes segun el dia", score_type="rounds_and_reps" if index in {0, 1, 2, 3, 5} else "for_time", movements=[item for item in main_moves[index] if not (item["name"] == "Wall Walk" and item.get("reps", 0) == 0)], notes="La tecnica del skill de la semana sigue importando dentro del WOD."),
                    make_part("Competitor Extra", "competitor_extra", 5, "Flush corto para atletas con margen.", format="EMOM", scheme="5 minutes", movements=[movement("Toes-to-Bar", reps=8)]) if index == 4 else make_part("Cooldown", "cooldown", 6, "Respiracion, hombro y descarga general."),
                    make_part("Cooldown", "cooldown", 6, "Soltar muñeca, hombro, pantorrilla y cadera.") if index == 4 else make_part("Accessory", "accessory", 6, "Trabajo breve de recovery y linea media.", movements=[movement("Dead Bug", reps=10), movement("Couch Stretch", reps=1, notes="30 s por lado")]),
                ],
                scaling_options=make_scaling("Elegir la progresion tecnica mas simple que mantenga el objetivo del dia.", "Mantener el formato con volumen moderado y tecnica repetible.", "Seguir el plan completo del dia con el skill correspondiente."),
                coach_notes=[coach_note("Skill First", "No dejar que el reloj se coma la calidad de la progresion tecnica."), coach_note("Stations", "Separar por nivel y por tipo de skill para evitar cuellos de botella.")],
            )
        )
    return sessions


DETAILED_WEEKS = [
    ("2026-04-06", "block-2026-04-engine-reset", "Reset de ritmo, sentadilla frontal y trabajo mixto controlado.", build_engine_week),
    ("2026-04-13", "block-2026-04-engine-reset", "Subir densidad aerobica sin perder calidad de recepcion y postura.", build_engine_week),
    ("2026-04-20", "block-2026-04-engine-reset", "Combinar trabajo mixto mas largo con control de transiciones.", build_engine_week),
    ("2026-04-27", "block-2026-04-engine-reset", "Semana de referencia de pacing para cerrar el bloque con criterio claro.", build_engine_week),
    ("2026-06-29", "block-2026-06-summer-aerobic-mix", "Reforzar ritmo continuo con carrera y maquinas en esfuerzos largos.", build_summer_week),
    ("2026-07-06", "block-2026-06-summer-aerobic-mix", "Aumentar volumen de trabajo aerobico mixto con transiciones simples.", build_summer_week),
    ("2026-09-21", "block-2026-09-skill-density", "Instalar ventanas tecnicas cortas con alta calidad de ejecucion.", build_skill_week),
    ("2026-09-28", "block-2026-09-skill-density", "Aumentar densidad de practica manteniendo descansos utiles.", build_skill_week),
]


def seed_sessions_and_weeks() -> tuple[int, int]:
    all_sessions: list[dict[str, object]] = []
    detailed_week_starts: set[str] = set()

    for index, (week_start, block_id, focus, builder) in enumerate(DETAILED_WEEKS):
        detailed_week_starts.add(week_start)
        variant = sum(1 for item in DETAILED_WEEKS[:index] if item[1] == block_id)
        all_sessions.extend(builder(week_start, focus, variant))

    for session in all_sessions:
        dump_json(SESSIONS_DIR / f"{session['session_date']}.json", session)

    weeks = json.loads(WEEKS_PATH.read_text(encoding="utf-8"))
    for week in weeks:
        if week["start_date"] in detailed_week_starts:
            week["session_dates"] = iso_dates(week["start_date"])
        elif week.get("session_dates"):
            week["session_dates"] = []
    dump_json(WEEKS_PATH, weeks)

    return len(all_sessions), len(detailed_week_starts)


def main() -> None:
    session_count, week_count = seed_sessions_and_weeks()
    print(f"OK seeded sessions: {session_count}")
    print(f"OK detailed weeks: {week_count}")


if __name__ == "__main__":
    main()
