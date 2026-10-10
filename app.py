import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, render_template, request

from ai.recommendation import recommend_hospitals


BASE_DIR = Path(__file__).resolve().parent


def resolve_database_path() -> Path:
    env_database = os.environ.get("HOSPITAL_FINDER_DATABASE")
    if env_database:
        return Path(env_database)

    project_database = BASE_DIR / "database" / "hospitals.db"
    if os.access(BASE_DIR, os.W_OK):
        return project_database

    cache_dir = Path("/tmp") / "hospital-finder"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "hospitals.db"


DATABASE = resolve_database_path()
CHANDIGARH_HOSPITALS = [
    ("Abhilasha Hospital", "Sector 35", "General care", 30.7279522, 76.7594992),
    ("Air Force Hospital", "Sector 31", "General care", 30.7033952, 76.7775151),
    ("Arya Hospital", "Manimajra", "General care", 30.7174644, 76.8329890),
    ("ARV Orthopaedic Hospital", "Sector 21", "Orthopedics", 30.7264061, 76.7732467),
    ("Ashwini Maternity Hospital", "Sector 34", "Maternity care", 30.7193760, 76.7578912),
    ("Babe Ke Hospital and IMT", "Sector 53", "General care", 30.7245070, 76.7324640),
    ("Bedi Hospital", "Sector 33", "General care", 30.7176996, 76.7693818),
    ("Cancer Hospital", "Sector 12", "Cancer care", 30.7633794, 76.7809938),
    ("Chaitanya Hospital", "Sector 44", "General care", 30.7107483, 76.7541911),
    ("CHD City Hospital", "Sector 8", "General care", 30.7417091, 76.7942557),
    ("Civil Hospital, Manimajra", "Manimajra", "General care", 30.7128525, 76.8424183),
    ("Civil Hospital, Sector 22", "Sector 22", "General care", 30.7324319, 76.7716616),
    ("Cloudnine Hospital", "Industrial Area Phase I", "Maternity and child care", 30.7001359, 76.7875764),
    ("Composite Hospital, ITBP", "Raipur Khurd", "General care", 30.6779880, 76.8072810),
    ("Dabur Dhanwantry Hospital", "Sector 46", "General care", 30.6999404, 76.7671408),
    ("Dharam Hospital", "Sector 15", "General care", 30.7491743, 76.7740258),
    ("Dr. Chandan Trikha Homeopathic Hospital", "Sector 32", "Homeopathy", 30.7127888, 76.7774089),
    ("Dr. Harvansh Singh Judge Institute of Dental Sciences and Hospital", "Sector 25", "Dental care", 30.7465298, 76.7545353),
    ("Deep Hospital", "Dhanas", "General care", 30.7635999, 76.7483211),
    ("Eden Hospital", "Industrial Area Phase II", "General care", 30.7091481, 76.8027108),
    ("ESIC Hospital, Ramdarbar", "Ramdarbar", "General care", 30.6967430, 76.7879640),
    ("Fortis Medcentre Hospital", "Sector 11", "General care", 30.7606212, 76.7820366),
    ("GMCH Sector 32", "Sector 32", "Multi-speciality", 30.7091585, 76.7813136),
    ("GMSH Sector 16", "Sector 16", "Multi-speciality", 30.7508839, 76.7809054),
    ("Grover Eye Laser and E.N.T. Hospital", "Sector 35", "Eye and ENT care", 30.7301782, 76.7603199),
    ("Guru Nanak Multispeciality Hospital", "Sector 35", "Multi-speciality", 30.7255395, 76.7622902),
    ("Kaushal Hospital", "Sector 42", "General care", 30.7229080, 76.7447786),
    ("Landmark Hospital", "Sector 33", "General care", 30.7122719, 76.7702748),
    ("Mangnum Hospital", "Sector 35", "General care", 30.7237708, 76.7604969),
    ("Mukat Hospital and Heart Institute", "Sector 34", "Cardiology and multi-speciality", 30.7228358, 76.7703393),
    ("Nehru Hospital, PGIMER", "Sector 12", "Multi-speciality", 30.7608977, 76.7765170),
    ("Neeraj Eye Hospital", "Sector 36", "Eye care", 30.7342210, 76.7525804),
    ("Nins Brain and Spine Hospital", "Sector 34", "Neurology and spine care", 30.7218259, 76.7669463),
    ("Omni Hospital", "Sector 34", "General care", 30.7216968, 76.7669718),
    ("Oxford Heart and Multispeciality Hospital", "Sector 19", "Cardiology and multi-speciality", 30.7287476, 76.7898551),
    ("Pandhi Hospital", "Sector 36", "General care", 30.7266382, 76.7523250),
    ("Police Hospital", "Sector 26", "General care", 30.7232383, 76.8122966),
    ("Postgraduate Institute of Medical Education and Research (PGIMER)", "Sector 12", "Multi-speciality", 30.7635373, 76.7747522),
    ("Rameshwara Hospital", "Sector 11", "General care", 30.7583074, 76.7843183),
    ("Santokh Hospital", "Sector 38", "General care", 30.7478631, 76.7489881),
    ("Virdi Eye Hospital (Virk Hospital)", "Sector 34", "Eye care", 30.7198176, 76.7686281),
]
ZIRAKPUR_HOSPITALS = [
    ("Life Line Hospital", "Dakshin Marg, Zirakpur", "General care", 30.6686656, 76.8134805),
    ("Vision Eye Hospital", "Ananapuri Colony, Zirakpur", "Eye care", 30.6660564, 76.8253081),
    ("Sethi Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6638500, 76.8289030),
    ("Arya Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6575377, 76.8222204),
    ("Saini Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6579782, 76.8166108),
    ("JP Hospital, Zirakpur", "Ananapuri Colony, Zirakpur", "General care", 30.6613553, 76.8184454),
    ("Matsya Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6629365, 76.8182021),
    ("Mata Jeevni Memorial Charitable Dental Hospital", "Zirakpur", "Dental care", 30.6567992, 76.8448195),
    ("Multispeciality Hospital", "VIP Road, Zirakpur", "Multi-speciality", 30.6382847, 76.8158255),
    ("Maxdent Tricity Dental Hospital and Hair Transplant Centre", "Ananapuri Colony, Zirakpur", "Dental care", 30.6431700, 76.8193010),
    ("Doctor Square Multispeciality Hospital", "VIP Road, Zirakpur", "Multi-speciality", 30.6392258, 76.8157820),
    ("Vishwas Hospital", "Defence Enclave, Zirakpur", "General care", 30.6482730, 76.8124699),
    ("Dr. R.C.P. Singh Memorial Charitable Hospital", "Sigma City Chowk, Zirakpur", "General care", 30.6435549, 76.8142945),
    ("Dhuper Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6521200, 76.8223652),
    ("Santosh Hospital", "Sigma City I, Zirakpur", "General care", 30.6521662, 76.8185704),
    ("Tara Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6545228, 76.8215102),
    ("Osmed Healthcare Multispeciality Hospital", "Defence Enclave, Zirakpur", "Multi-speciality", 30.6477784, 76.8129324),
    ("Blessings Hospital", "Zirakpur", "General care", 30.6552113, 76.8449387),
    ("Mom and Me Hospital", "Zirakpur", "Maternity and child care", 30.6535126, 76.8450721),
    ("Trinity Hospital and Medical Research Institute", "Sigma City I, Zirakpur", "Multi-speciality", 30.6472720, 76.8047550),
    ("Chaitanya Public Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6609356, 76.8290502),
    ("Ashirwad Hospital", "VIP Road, Zirakpur", "General care", 30.6366880, 76.8145320),
    ("Dr. Pragati's Multispeciality Dental Hospital", "Ananapuri Colony, Zirakpur", "Dental care", 30.6478955, 76.8235476),
    ("Odontos Dental Hospital", "Defence Enclave, Zirakpur", "Dental care", 30.6496020, 76.8214139),
    ("Advamed Hospital", "Zirakpur", "General care", 30.6454414, 76.8227729),
    ("S.S Hospital", "Ananapuri Colony, Zirakpur", "General care", 30.6516050, 76.8228040),
    ("Amcare Hospital", "VIP Road, Zirakpur", "General care", 30.6391360, 76.8169428),
    ("V Care Hospital", "VIP Road, Zirakpur", "General care", 30.6391081, 76.8160794),
    ("Dashmesh Hospital", "Sigma City I, Zirakpur", "General care", 30.6508669, 76.8132014),
]
DIRECTORY_CITIES = ("Chandigarh", "Zirakpur")
LEGACY_SAMPLE_NAMES = {
    "Sahyadri Super Speciality Hospital",
    "Deenanath Mangeshkar Hospital",
    "Ruby Hall Clinic",
    "Manipal Hospital",
    "Apollo Hospitals",
    "Kokilaben Dhirubhai Ambani Hospital",
}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(database_path: Path = DATABASE) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                rating REAL NOT NULL,
                specialties TEXT NOT NULL,
                emergency INTEGER NOT NULL DEFAULT 0,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                description TEXT NOT NULL
            )
            """
        )
        count = db.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
        existing_names = {
            row[0] for row in db.execute("SELECT name FROM hospitals").fetchall()
        }
        if count == 0 or existing_names == LEGACY_SAMPLE_NAMES:
            if count:
                db.execute("DELETE FROM hospitals")
            db.executemany(
                """
                INSERT INTO hospitals
                    (name, city, address, phone, rating, specialties, emergency,
                     latitude, longitude, description)
                VALUES (?, 'Chandigarh', ?, '', 0, ?, 0, ?, ?, ?)
                """,
                [
                    (
                        name,
                        f"{sector}, Chandigarh",
                        specialty,
                        latitude,
                        longitude,
                        "Directory location sourced from OpenStreetMap. Contact the hospital to confirm services, opening hours, and contact details.",
                    )
                    for name, sector, specialty, latitude, longitude in CHANDIGARH_HOSPITALS
                ],
            )
        db.executemany(
            """
            INSERT INTO hospitals
                (name, city, address, phone, rating, specialties, emergency,
                 latitude, longitude, description)
            SELECT ?, 'Zirakpur', ?, '', 0, ?, 0, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM hospitals WHERE name = ? AND city = 'Zirakpur'
            )
            """,
            [
                (
                    name,
                    f"{area}, Punjab",
                    specialty,
                    latitude,
                    longitude,
                    "Directory location sourced from OpenStreetMap. Contact the hospital to confirm services, opening hours, and contact details.",
                    name,
                )
                for name, area, specialty, latitude, longitude in ZIRAKPUR_HOSPITALS
            ],
        )


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("HOSPITAL_FINDER_DATABASE", str(DATABASE))
    init_db(Path(app.config["DATABASE"]))

    @app.before_request
    def connect_database() -> None:
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row

    @app.teardown_appcontext
    def close_database(_error: BaseException | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.get("/")
    def index():
        db = get_db()
        specialties = sorted(
            {
                specialty.strip()
                for row in db.execute("SELECT specialties FROM hospitals").fetchall()
                for specialty in row["specialties"].split(",")
            }
        )
        featured = db.execute(
            "SELECT * FROM hospitals WHERE city IN (?, ?) ORDER BY city, name",
            DIRECTORY_CITIES,
        ).fetchall()
        return render_template(
            "index.html",
            specialties=specialties,
            featured=featured,
        )

    @app.get("/search")
    def search():
        db = get_db()
        city = request.args.get("city", "").strip()
        if city not in DIRECTORY_CITIES:
            city = ""
        specialty = request.args.get("specialty", "").strip()
        query = request.args.get("q", "").strip()
        emergency_only = request.args.get("emergency") == "1"
        lat = _coordinate(request.args.get("lat"), -90, 90)
        lon = _coordinate(request.args.get("lon"), -180, 180)

        conditions = []
        params: list[object] = []
        if city:
            conditions.append("city = ?")
            params.append(city)
        else:
            conditions.append("city IN (?, ?)")
            params.extend(DIRECTORY_CITIES)
        if specialty:
            conditions.append("specialties LIKE ?")
            params.append(f"%{specialty}%")
        if query:
            conditions.append("(name LIKE ? OR address LIKE ? OR city LIKE ?)")
            params.extend([f"%{query}%"] * 3)
        if emergency_only:
            conditions.append("emergency = 1")

        sql = "SELECT * FROM hospitals"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        hospitals = [dict(row) for row in db.execute(sql, params).fetchall()]
        hospitals = recommend_hospitals(hospitals, lat=lat, lon=lon)
        return render_template(
            "results.html",
            hospitals=hospitals,
            city=city,
            specialty=specialty,
            query=query,
            emergency_only=emergency_only,
            user_lat=lat,
            user_lon=lon,
            result_count=len(hospitals),
        )

    @app.get("/hospital/<int:hospital_id>")
    def hospital_detail(hospital_id: int):
        hospital = get_db().execute(
            "SELECT * FROM hospitals WHERE id = ?", (hospital_id,)
        ).fetchone()
        if hospital is None:
            abort(404)
        return render_template("hospital.html", hospital=hospital)

    return app


def _coordinate(value: str | None, minimum: float, maximum: float) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        coordinate = float(value)
    except ValueError:
        return None
    return coordinate if minimum <= coordinate <= maximum else None


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
