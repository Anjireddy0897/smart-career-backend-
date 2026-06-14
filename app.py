from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request
import requests
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "career_backend.db")

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")
GENDER_OPTIONS = {"male", "female", "other", "prefer_not_to_say"}
OPTION_SCORES = {
    "very interested": 4,
    "interested": 3,
    "neutral": 2,
    "not interested": 1,
}

QUESTION_TO_SKILLS = {
    "q1": {"logic": 1},
    "q2": {"data": 1},
    "q3": {"ui": 1, "creativity": 1},
    "q4": {"management": 1, "leadership": 1},
    "q5": {"documentation": 1, "communication": 1},
    "q6": {"programming": 1, "technical": 1},
    "q7": {"business": 1},
    "q8": {"communication": 1},
    "q9": {"cybersecurity": 1, "security": 1},
    "q10": {"collaboration": 1, "creativity": 1},
}

CAREER_CATEGORY_PROFILES = {
    "IT & Technology": {"logic": 1, "data": 1, "programming": 1, "cybersecurity": 1, "ui": 1},
    "Business & Commerce": {"business": 1, "management": 1, "communication": 1},
    "Entrepreneurship": {"management": 1, "business": 1, "communication": 1, "creativity": 1},
    "Influencer & Content Creation": {"creativity": 1, "communication": 1, "collaboration": 1},
    "Arts & Creativity": {"creativity": 1, "ui": 1},
    "Anime & Animation": {"ui": 1, "creativity": 1, "logic": 1},
    "Gaming & Esports": {"logic": 1, "creativity": 1, "programming": 1},
    "Acting & Entertainment": {"communication": 1, "creativity": 1},
    "Music Careers": {"creativity": 1, "communication": 1},
    "Law Careers": {"communication": 1, "logic": 1, "business": 1},
    "Government & Railway": {"leadership": 1, "communication": 1, "logic": 1},
    "Healthcare": {"logic": 1, "data": 1, "communication": 1},
    "Agriculture": {"data": 1, "business": 1, "logic": 1},
}

CAREER_CATEGORY_CAREERS = {
    "IT & Technology": ["Software Engineer", "AI/ML Engineer", "Data Scientist", "Full Stack Developer", "DevOps Engineer", "Cybersecurity Analyst", "UI/UX Designer"],
    "Business & Commerce": ["Chartered Accountant", "MBA Graduate", "Investment Banker", "Financial Analyst", "Marketing Manager", "Business Consultant", "Company Secretary"],
    "Entrepreneurship": ["Startup Founder", "Tech Entrepreneur", "Small Business Owner", "E-commerce Owner", "Franchise Owner", "Consultant"],
    "Influencer & Content Creation": ["YouTuber", "Instagram Influencer", "Content Creator", "Social Media Manager", "Podcast Host", "Vlogger"],
    "Arts & Creativity": ["Graphic Designer", "Illustrator", "Digital Artist", "Fine Artist", "Art Director", "Tattoo Artist"],
    "Anime & Animation": ["Animator", "3D Artist", "Character Designer", "Storyboard Artist", "VFX Artist", "Animation Director"],
    "Gaming & Esports": ["Esports Player", "Game Streamer", "Gaming Coach", "Game Developer", "Gaming Content Creator", "Esports Commentator"],
    "Acting & Entertainment": ["Film Actor", "Theater Artist", "Voice Actor", "TV Serial Actor", "Stand-up Comedian"],
    "Music Careers": ["Playback Singer", "Music Producer", "Music Composer", "DJ / Music Artist", "Music Teacher", "Sound Engineer"],
    "Law Careers": ["Lawyer", "Corporate Lawyer", "Judge", "Legal Advisor", "Public Prosecutor", "Legal Analyst"],
    "Government & Railway": ["IAS Officer", "IPS Officer", "Railway Officer", "Bank PO", "SSC CGL", "Forest Officer", "Govt. Teacher"],
    "Healthcare": ["Doctor", "Nurse", "Physiotherapist", "Pharmacist", "Medical Lab Technician", "Radiologist", "Dentist"],
    "Agriculture": ["Agricultural Scientist", "Agri-Business Manager", "Horticulturist", "Food Technologist", "Agricultural Engineer", "Organic Farmer"],
}

CAREER_DOMAINS = {
    "IT & Technology": [
        "Software Engineer",
        "Data Scientist",
        "AI/ML Engineer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Cybersecurity Analyst",
        "UI/UX Designer",
    ],
    "Business & Commerce": [
        "Chartered Accountant (CA)",
        "MBA Graduate",
        "Investment Banker",
        "Financial Analyst",
        "Marketing Manager",
        "Business Consultant",
        "Company Secretary",
    ],
    "Entrepreneurship": [
        "Startup Founder",
        "Tech Entrepreneur",
        "Small Business Owner",
        "E-commerce Owner",
        "Franchise Owner",
        "Consultant",
    ],
    "Influencer & Content Creation": [
        "YouTuber",
        "Instagram Influencer",
        "Content Creator",
        "Social Media Manager",
        "Podcast Host",
        "Vlogger",
    ],
    "Arts & Creativity": [
        "Graphic Designer",
        "Illustrator",
        "Digital Artist",
        "Fine Artist",
        "Art Director",
        "Tattoo Artist",
    ],
    "Anime & Animation": [
        "Animator",
        "3D Artist",
        "Character Designer",
        "Storyboard Artist",
        "VFX Artist",
        "Animation Director",
    ],
    "Gaming & Esports": [
        "Esports Player",
        "Game Streamer",
        "Gaming Coach",
        "Game Developer",
        "Gaming Content Creator",
        "Esports Commentator",
    ],
    "Acting & Entertainment": ["Film Actor", "Theater Artist", "Voice Actor", "TV Serial Actor", "Stand-up Comedian"],
    "Music Careers": ["Playback Singer", "Music Producer", "Music Composer", "DJ / Music Artist", "Music Teacher", "Sound Engineer"],
    "Law Careers": ["Lawyer / Advocate", "Corporate Lawyer", "Judge", "Legal Advisor", "Public Prosecutor", "Legal Analyst"],
    "Government & Railway": ["IAS Officer", "IPS Officer", "Railway Officer", "Bank PO", "SSC CGL", "Forest Officer", "Govt. Teacher"],
    "Healthcare Careers": ["Doctor (MBBS)", "Nurse", "Physiotherapist", "Pharmacist", "Medical Lab Technician", "Radiologist", "Dentist"],
    "Agriculture Careers": ["Agricultural Scientist", "Agri-Business Manager", "Horticulturist", "Food Technologist", "Agricultural Engineer", "Organic Farmer"],
    "Fashion & Modeling": ["Fashion Designer", "Runway Model", "Fashion Stylist", "Costume Designer", "Fashion Photographer", "Textile Designer"],
    "Dance Careers": ["Professional Dancer", "Choreographer", "Dance Teacher", "Dance Content Creator", "Backup Dancer"],
    "Aviation Careers": ["Commercial Pilot", "Aircraft Engineer", "Air Traffic Controller", "Flight Attendant", "Airport Manager", "Aviation Safety Officer"],
}

CAREER_RECOMMENDATION_CAREERS = {
    "IT & Technology Careers": [
        {"career": "Software Engineer", "description": "Designs and develops software applications."},
        {"career": "Data Scientist", "description": "Analyzes data and builds predictive models."},
        {"career": "AI/ML Engineer", "description": "Develops artificial intelligence solutions."},
        {"career": "Full Stack Developer", "description": "Builds frontend and backend web applications."},
        {"career": "DevOps Engineer", "description": "Automates deployment and infrastructure."},
        {"career": "Cybersecurity Analyst", "description": "Protects systems from cyber threats."},
        {"career": "UI/UX Designer", "description": "Designs user-friendly digital experiences."},
    ],
    "Healthcare Careers": [
        {"career": "Doctor (MBBS)", "description": "Diagnoses and treats patients."},
        {"career": "Nurse", "description": "Provides patient care and support."},
        {"career": "Physiotherapist", "description": "Helps patients recover mobility."},
        {"career": "Pharmacist", "description": "Dispenses and manages medications."},
        {"career": "Medical Lab Technician", "description": "Conducts laboratory testing."},
        {"career": "Radiologist", "description": "Uses imaging technologies for diagnosis."},
        {"career": "Dentist", "description": "Treats oral and dental problems."},
    ],
    "Business & Commerce": [
        {"career": "Chartered Accountant (CA)", "description": "Handles auditing and financial accounting."},
        {"career": "MBA Graduate", "description": "Manages business operations and leadership."},
        {"career": "Investment Banker", "description": "Provides financial investment services."},
        {"career": "Financial Analyst", "description": "Analyzes financial performance."},
        {"career": "Marketing Manager", "description": "Leads marketing campaigns."},
        {"career": "Business Consultant", "description": "Advises companies on growth strategies."},
        {"career": "Company Secretary", "description": "Ensures legal compliance of organizations."},
    ],
    "Law Careers": [
        {"career": "Lawyer / Advocate", "description": "Represents clients in legal matters."},
        {"career": "Corporate Lawyer", "description": "Handles corporate legal affairs."},
        {"career": "Judge", "description": "Presides over court proceedings."},
        {"career": "Legal Advisor", "description": "Provides legal consultation."},
        {"career": "Public Prosecutor", "description": "Represents the state in criminal cases."},
        {"career": "Legal Analyst", "description": "Researches and interprets laws."},
    ],
    "Government & Railway": [
        {"career": "IAS Officer", "description": "Administrative leader serving the nation."},
        {"career": "IPS Officer", "description": "Leads police and law enforcement."},
        {"career": "Railway Officer", "description": "Manages railway operations."},
        {"career": "Bank PO", "description": "Officer in public sector banks."},
        {"career": "SSC CGL Officer", "description": "Works in central government departments."},
        {"career": "Forest Officer", "description": "Protects forest resources."},
        {"career": "Govt Teacher", "description": "Educates students in government schools."},
    ],
    "Aviation Careers": [
        {"career": "Commercial Pilot", "description": "Operates commercial aircraft."},
        {"career": "Aircraft Engineer", "description": "Maintains and repairs aircraft."},
        {"career": "Air Traffic Controller", "description": "Coordinates aircraft movement."},
        {"career": "Flight Attendant", "description": "Ensures passenger safety."},
        {"career": "Airport Manager", "description": "Oversees airport operations."},
        {"career": "Aviation Safety Officer", "description": "Maintains aviation safety standards."},
    ],
    "Acting & Entertainment": [
        {"career": "Film Actor", "description": "Performs leading and supporting roles in movies."},
        {"career": "Theater Artist", "description": "Performs in stage plays and live productions."},
        {"career": "Voice Actor", "description": "Provides voices for animation and games."},
        {"career": "TV Serial Actor", "description": "Acts in television serials."},
        {"career": "Stand-up Comedian", "description": "Performs comedy before live audiences."},
    ],
    "Fashion & Modeling": [
        {"career": "Fashion Designer", "description": "Designs clothing and fashion collections."},
        {"career": "Runway Model", "description": "Showcases fashion products."},
        {"career": "Fashion Stylist", "description": "Creates fashion looks."},
        {"career": "Costume Designer", "description": "Designs costumes for films and theatre."},
        {"career": "Fashion Photographer", "description": "Captures fashion campaigns."},
        {"career": "Textile Designer", "description": "Creates fabric patterns."},
    ],
    "Dance Careers": [
        {"career": "Professional Dancer", "description": "Performs dance professionally."},
        {"career": "Choreographer", "description": "Creates dance performances."},
        {"career": "Dance Teacher", "description": "Teaches dance styles."},
        {"career": "Dance Content Creator", "description": "Creates dance content online."},
        {"career": "Backup Dancer", "description": "Performs alongside artists."},
    ],
    "Entrepreneurship": [
        {"career": "Startup Founder", "description": "Builds and manages startup companies."},
        {"career": "Tech Entrepreneur", "description": "Creates technology businesses."},
        {"career": "Small Business Owner", "description": "Runs local businesses."},
        {"career": "E-commerce Owner", "description": "Operates online stores."},
        {"career": "Franchise Owner", "description": "Manages franchise businesses."},
        {"career": "Consultant", "description": "Provides expert business advice."},
    ],
    "Gaming & Esports": [
        {"career": "Esports Player", "description": "Competes in gaming tournaments."},
        {"career": "Game Streamer", "description": "Streams gameplay online."},
        {"career": "Gaming Coach", "description": "Trains esports players."},
        {"career": "Game Developer", "description": "Designs and develops video games."},
        {"career": "Gaming Content Creator", "description": "Creates gaming content."},
        {"career": "Esports Commentator", "description": "Provides esports commentary."},
    ],
    "Arts & Creativity": [
        {"career": "Graphic Designer", "description": "Creates visual designs."},
        {"career": "Illustrator", "description": "Creates drawings and illustrations."},
        {"career": "Digital Artist", "description": "Produces digital artwork."},
        {"career": "Fine Artist", "description": "Creates paintings and art."},
        {"career": "Art Director", "description": "Leads creative projects."},
        {"career": "Tattoo Artist", "description": "Creates artistic tattoos."},
    ],
    "Anime & Animation": [
        {"career": "Animator", "description": "Creates animated content."},
        {"career": "3D Artist", "description": "Designs 3D models."},
        {"career": "Character Designer", "description": "Creates animated characters."},
        {"career": "Storyboard Artist", "description": "Plans scenes visually."},
        {"career": "VFX Artist", "description": "Creates visual effects."},
        {"career": "Animation Director", "description": "Leads animation production."},
    ],
    "Influencer & Content Creation": [
        {"career": "YouTuber", "description": "Creates video content."},
        {"career": "Instagram Influencer", "description": "Builds audiences on social media."},
        {"career": "Content Creator", "description": "Produces digital content."},
        {"career": "Social Media Manager", "description": "Manages social media growth."},
        {"career": "Podcast Host", "description": "Hosts podcasts."},
        {"career": "Vlogger", "description": "Creates video blogs."},
    ],
    "Music Careers": [
        {"career": "Playback Singer", "description": "Records songs professionally."},
        {"career": "Music Producer", "description": "Produces music recordings."},
        {"career": "Music Composer", "description": "Creates original music."},
        {"career": "DJ / Music Artist", "description": "Performs and mixes music."},
        {"career": "Music Teacher", "description": "Teaches music."},
        {"career": "Sound Engineer", "description": "Handles audio production."},
    ],
    "Agriculture Careers": [
        {"career": "Agricultural Scientist", "description": "Researches farming innovations."},
        {"career": "Agri-Business Manager", "description": "Manages agricultural businesses."},
        {"career": "Horticulturist", "description": "Specializes in plants."},
        {"career": "Food Technologist", "description": "Develops food products."},
        {"career": "Agricultural Engineer", "description": "Applies engineering to farming."},
        {"career": "Organic Farmer", "description": "Practices sustainable farming."},
    ],
}

RECOMMENDATION_DOMAIN_PRIORITY = [
    "IT & Technology Careers",
    "Gaming & Esports",
    "Entrepreneurship",
    "Acting & Entertainment",
    "Arts & Creativity",
    "Anime & Animation",
    "Influencer & Content Creation",
    "Music Careers",
    "Business & Commerce",
    "Fashion & Modeling",
    "Dance Careers",
    "Healthcare Careers",
    "Law Careers",
    "Government & Railway",
    "Aviation Careers",
    "Agriculture Careers",
]

CAREER_DETAILS = {
    "Software Engineer": {"skillsRequired": ["Python", "JavaScript", "DSA", "Git"], "roadmap": ["Learn programming basics", "Practice data structures", "Build projects", "Contribute to GitHub"], "salaryRange": "4-20 LPA", "demandLevel": "High"},
    "AI/ML Engineer": {"skillsRequired": ["Python", "Machine Learning", "Deep Learning", "TensorFlow"], "roadmap": ["Learn Python", "Learn statistics", "Study ML fundamentals", "Build AI projects"], "salaryRange": "8-25 LPA", "demandLevel": "High"},
    "Data Scientist": {"skillsRequired": ["Python", "Statistics", "SQL", "Data Visualization"], "roadmap": ["Learn statistics", "Practice SQL", "Master Python for data", "Work on datasets"], "salaryRange": "6-22 LPA", "demandLevel": "High"},
    "Full Stack Developer": {"skillsRequired": ["HTML", "CSS", "JavaScript", "Backend Development"], "roadmap": ["Learn frontend basics", "Learn backend basics", "Build full stack apps", "Deploy projects"], "salaryRange": "5-22 LPA", "demandLevel": "High"},
    "Cybersecurity Analyst": {"skillsRequired": ["Networking", "Security Tools", "Linux", "Threat Analysis"], "roadmap": ["Learn networking", "Study security fundamentals", "Practice labs", "Earn security certifications"], "salaryRange": "5-20 LPA", "demandLevel": "High"},
    "UI/UX Designer": {"skillsRequired": ["Figma", "Wireframing", "User Research", "Prototyping"], "roadmap": ["Learn design basics", "Study user research", "Create wireframes", "Build a portfolio"], "salaryRange": "4-18 LPA", "demandLevel": "High"},
}

DEFAULT_CAREER_DETAILS = {
    "skillsRequired": ["Communication", "Problem Solving", "Domain Knowledge"],
    "roadmap": ["Understand the career path", "Learn core skills", "Practice through projects", "Apply for internships"],
    "salaryRange": "Varies",
    "demandLevel": "Medium",
}


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def ensure_database() -> None:
    os.makedirs(BASE_DIR, exist_ok=True)
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS personal_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                date_of_birth TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                city TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS career_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                skill_scores_json TEXT NOT NULL,
                category_scores_json TEXT NOT NULL,
                recommendations_json TEXT NOT NULL,
                top_category TEXT NOT NULL,
                top_score INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS career_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                recommendations_json TEXT NOT NULL,
                top_domain TEXT NOT NULL,
                top_score INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS education_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                current_education_level TEXT NOT NULL,
                stream TEXT,
                school_college_name TEXT NOT NULL,
                average_percentage_gpa TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def json_error(message: str, status_code: int, errors: Optional[Dict[str, Any]] = None):
    payload: Dict[str, Any] = {"success": False, "message": message}
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status_code


def normalize_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip().lower()


def get_request_data() -> Dict[str, Any]:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def validate_email(value: Optional[str]) -> bool:
    return bool(value and EMAIL_REGEX.match(value))


def validate_phone(value: Optional[str]) -> bool:
    return bool(value and PHONE_REGEX.match(value))


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_db() as connection:
        cursor = connection.execute(
            "SELECT id, full_name, email, password_hash, created_at, updated_at FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as connection:
        cursor = connection.execute(
            "SELECT id, full_name, email, password_hash, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def serialize_user(user_row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user_row["id"],
        "full_name": user_row["full_name"],
        "email": user_row["email"],
        "created_at": user_row["created_at"],
        "updated_at": user_row["updated_at"],
    }


def resolve_user_id(data: Dict[str, Any]) -> Optional[int]:
    user_id = data.get("user_id")
    if user_id is not None:
        try:
            return int(user_id)
        except (TypeError, ValueError):
            return None

    email = normalize_email(data.get("email"))
    if email and validate_email(email):
        user = get_user_by_email(email)
        if user:
            return int(user["id"])
    return None


def normalize_answer(value: Any) -> Optional[str]:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    return normalized if normalized in OPTION_SCORES else None


def json_dumps(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


def json_loads(value: str) -> Any:
    import json

    return json.loads(value)


def normalize_numeric_answer(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if value is None:
        return 0

    normalized_value = str(value).strip()
    if normalized_value.isdigit():
        return int(normalized_value)

    legacy_label = normalize_answer(normalized_value)
    return OPTION_SCORES.get(legacy_label or "", 0)


def coerce_recommendation_score(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if value is None:
        return 0

    normalized_value = str(value).strip()
    if normalized_value.isdigit():
        return int(normalized_value)

    legacy_label = normalize_answer(normalized_value)
    return OPTION_SCORES.get(legacy_label or "", 0)


def calculate_top_domains(answers: Dict[str, Any]) -> list[str]:
    q1 = coerce_recommendation_score(answers.get("q1"))
    q2 = coerce_recommendation_score(answers.get("q2"))
    q3 = coerce_recommendation_score(answers.get("q3"))
    q4 = coerce_recommendation_score(answers.get("q4"))
    q5 = coerce_recommendation_score(answers.get("q5"))
    q6 = coerce_recommendation_score(answers.get("q6"))
    q7 = coerce_recommendation_score(answers.get("q7"))
    q8 = coerce_recommendation_score(answers.get("q8"))
    q9 = coerce_recommendation_score(answers.get("q9"))
    q10 = coerce_recommendation_score(answers.get("q10"))

    domain_scores = {
        "IT & Technology Careers": q1 + q8,
        "Healthcare Careers": q2,
        "Business & Commerce": q3 + q4,
        "Law Careers": q4,
        "Government & Railway": q3 + q4 + q2,
        "Aviation Careers": q9,
        "Acting & Entertainment": q6 + q7,
        "Fashion & Modeling": q5,
        "Dance Careers": q7,
        "Entrepreneurship": q3 + q10 + q1,
        "Gaming & Esports": q1 + q8 + q6,
        "Arts & Creativity": q5 + q6,
        "Anime & Animation": q5 + q6 + q8,
        "Influencer & Content Creation": q6 + q7 + q10,
        "Music Careers": q7 + q6,
        "Agriculture Careers": q9 + q2,
    }

    priority_lookup = {domain: index for index, domain in enumerate(RECOMMENDATION_DOMAIN_PRIORITY)}
    sorted_domains = sorted(
        domain_scores.items(),
        key=lambda item: (-item[1], priority_lookup.get(item[0], len(priority_lookup))),
    )
    return [domain for domain, _ in sorted_domains[:3]]


def build_student_profile(top_domains: list[str]) -> str:
    profile_parts: list[str] = []
    for domain in top_domains:
        cleaned = domain.replace(" Careers", "")
        if cleaned == "IT & Technology":
            profile_parts.append("Technology")
        elif cleaned == "Gaming & Esports":
            profile_parts.append("Gaming")
        elif cleaned == "Influencer & Content Creation":
            profile_parts.append("Content Creation")
        else:
            profile_parts.append(cleaned)
    return " + ".join(profile_parts)


def calculate_result(answers: Dict[str, Any]) -> list[Dict[str, Any]]:
    top_domains = calculate_top_domains(answers)

    recommendations: list[Dict[str, Any]] = []
    for domain in top_domains:
        recommendations.extend(CAREER_RECOMMENDATION_CAREERS.get(domain, []))

    return recommendations[:10]


def calculate_skill_scores(answers: Dict[str, Any]) -> Dict[str, int]:
    skill_scores = {
        "logic": 0,
        "data": 0,
        "ui": 0,
        "management": 0,
        "documentation": 0,
        "programming": 0,
        "business": 0,
        "communication": 0,
        "cybersecurity": 0,
        "collaboration": 0,
        "creativity": 0,
        "leadership": 0,
        "technical": 0,
        "security": 0,
    }

    for question_key, skill_weights in QUESTION_TO_SKILLS.items():
        score = OPTION_SCORES.get(normalize_answer(answers.get(question_key)) or "", 0)
        for skill_name, weight in skill_weights.items():
            skill_scores[skill_name] = skill_scores.get(skill_name, 0) + (score * weight)

    return skill_scores


def recommend_careers(answers: Dict[str, Any]) -> Dict[str, Any]:
    skill_scores = calculate_skill_scores(answers)

    category_scores = {}
    for category_name, profile in CAREER_CATEGORY_PROFILES.items():
        category_scores[category_name] = sum(skill_scores.get(skill, 0) * weight for skill, weight in profile.items())

    ranked_categories = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    top_category = ranked_categories[0][0] if ranked_categories else "IT & Technology"
    top_score = ranked_categories[0][1] if ranked_categories else 0

    recommended_careers = []
    for career_name in CAREER_CATEGORY_CAREERS.get(top_category, []):
        details = CAREER_DETAILS.get(career_name, DEFAULT_CAREER_DETAILS)
        recommended_careers.append(
            {
                "career": career_name,
                "score": top_score,
                "skillsRequired": details["skillsRequired"],
                "roadmap": details["roadmap"],
                "salaryRange": details["salaryRange"],
                "demandLevel": details["demandLevel"],
            }
        )

    return {
        "skillScores": skill_scores,
        "categoryScores": ranked_categories,
        "primaryCareerPath": top_category,
        "topScore": top_score,
        "recommendedCareers": recommended_careers[:5],
    }


def store_career_assessment(user_id: int, answers: Dict[str, Any], recommendations: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = now_iso()
    payload_answers = {key: answers.get(key) for key in [f"q{i}" for i in range(1, 11)]}

    with get_db() as connection:
        row = connection.execute(
            "SELECT id FROM career_assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()

        if row:
            assessment_id = int(row["id"])
            connection.execute(
                """
                UPDATE career_assessments
                SET answers_json = ?, skill_scores_json = ?, category_scores_json = ?, recommendations_json = ?,
                    top_category = ?, top_score = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    json_dumps(payload_answers),
                    json_dumps(recommendations["skillScores"]),
                    json_dumps(recommendations["categoryScores"]),
                    json_dumps(recommendations["recommendedCareers"]),
                    recommendations["primaryCareerPath"],
                    int(recommendations["topScore"]),
                    timestamp,
                    assessment_id,
                ),
            )
            action = "updated"
        else:
            cursor = connection.execute(
                """
                INSERT INTO career_assessments (
                    user_id, answers_json, skill_scores_json, category_scores_json,
                    recommendations_json, top_category, top_score, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    json_dumps(payload_answers),
                    json_dumps(recommendations["skillScores"]),
                    json_dumps(recommendations["categoryScores"]),
                    json_dumps(recommendations["recommendedCareers"]),
                    recommendations["primaryCareerPath"],
                    int(recommendations["topScore"]),
                    timestamp,
                    timestamp,
                ),
            )
            assessment_id = int(cursor.lastrowid)
            action = "created"

    return {"assessment_id": assessment_id, "action": action, "stored_at": timestamp}


def store_career_recommendation(user_id: int, answers: Dict[str, Any], recommendations: Any) -> Dict[str, Any]:
    timestamp = now_iso()
    top_recommendation = recommendations[0] if recommendations else {"career": "", "description": ""}

    top_domain = ""
    if recommendations:
        first_career = recommendations[0].get("career", "")
        for domain_name, careers in CAREER_RECOMMENDATION_CAREERS.items():
            if any(career_item.get("career") == first_career for career_item in careers):
                top_domain = domain_name
                break

    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO career_recommendations (
                user_id, answers_json, recommendations_json, top_domain, top_score, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                json_dumps(answers),
                json_dumps(recommendations),
                top_domain,
                len(recommendations),
                timestamp,
                timestamp,
            ),
        )

    return {
        "recommendation_id": int(cursor.lastrowid),
        "user_id": user_id,
        "top_domain": top_domain,
        "top_score": len(recommendations),
        "stored_at": timestamp,
    }


def fetch_latest_career_recommendation(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT id, user_id, answers_json, recommendations_json, top_domain, top_score, created_at, updated_at
            FROM career_recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return None

    recommendation = dict(row)
    recommendation["answers"] = json_loads(recommendation.pop("answers_json"))
    recommendation["recommendations"] = json_loads(recommendation.pop("recommendations_json"))
    return recommendation


def fetch_latest_assessment(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT id, user_id, answers_json, skill_scores_json, category_scores_json,
                   recommendations_json, top_category, top_score, created_at, updated_at
            FROM career_assessments
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return None

    assessment = dict(row)
    assessment["answers"] = json_loads(assessment.pop("answers_json"))
    assessment["skill_scores"] = json_loads(assessment.pop("skill_scores_json"))
    assessment["category_scores"] = json_loads(assessment.pop("category_scores_json"))
    assessment["recommended_careers"] = json_loads(assessment.pop("recommendations_json"))
    return assessment


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "success": True,
            "message": "Smart Career backend is running.",
            "database": {
                "type": "sqlite",
                "path": DB_PATH,
            },
            "endpoints": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "profile_update": "/api/profile/update",
                "personal_details": "/api/personal-details",
                "education_details": "/api/education-details",
                "profile": "/api/profile/<email>",
                "self_test": "/api/debug/self-test",
            },
        }
    )


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"success": True, "status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify(
            {
                "success": False,
                "error": "message is required",
            }
        ), 400

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:4b",
                "system": (
                    "You are a concise career assistant. Reply in 1-2 short sentences, "
                    "keep answers direct, and avoid long explanations unless the user asks."
                ),
                "prompt": user_message,
                "stream": False,
                "keep_alive": "5m",
                "options": {
                    "num_predict": 80,
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        payload = response.json()
        ai_reply = (payload.get("response") or "").strip()

        if not ai_reply:
            return jsonify(
                {
                    "success": False,
                    "error": "Ollama returned no response text",
                }
            ), 502

        return jsonify(
            {
                "success": True,
                "reply": ai_reply,
                "model": payload.get("model", "gemma3:4b"),
            }
        )

    except Exception as e:
        return jsonify(
            {
                "success": False,
                "error": str(e),
            }
        ), 500


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = get_request_data()
    full_name = (data.get("full_name") or "").strip()
    email = normalize_email(data.get("email"))
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    errors: Dict[str, str] = {}
    if not full_name:
        errors["full_name"] = "Full name is required."
    if not validate_email(email):
        errors["email"] = "A valid email is required."
    if len(password) < 6:
        errors["password"] = "Password must be at least 6 characters long."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    if errors:
        return json_error("Validation failed.", 400, errors)

    if get_user_by_email(email):
        return json_error("An account with this email already exists.", 409)

    timestamp = now_iso()
    password_hash = generate_password_hash(password)

    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (full_name, email, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, password_hash, timestamp, timestamp),
        )
        user_id = cursor.lastrowid

    return jsonify(
        {
            "success": True,
            "message": "Account created successfully.",
            "user": {
                "id": user_id,
                "full_name": full_name,
                "email": email,
            },
        }
    ), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = get_request_data()
    email = normalize_email(data.get("email"))
    password = data.get("password") or ""

    errors: Dict[str, str] = {}
    if not validate_email(email):
        errors["email"] = "A valid email is required."
    if not password:
        errors["password"] = "Password is required."
    if errors:
        return json_error("Validation failed.", 400, errors)

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return json_error("Invalid email or password.", 401)

    return jsonify(
        {
            "success": True,
            "message": "Login successful.",
            "user": serialize_user(user),
        }
    )


@app.route("/api/profile/update", methods=["POST", "PUT", "PATCH"])
def update_profile():
    data = get_request_data()
    user_id = resolve_user_id(data)
    full_name = (data.get("full_name") or "").strip()
    email = normalize_email(data.get("email"))
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    errors: Dict[str, str] = {}
    if not user_id or not get_user_by_id(user_id):
        errors["user"] = "Valid user_id or email is required."
    if not full_name:
        errors["full_name"] = "Full name is required."
    if email and not validate_email(email):
        errors["email"] = "A valid email is required."
    if password or confirm_password:
        if len(password) < 6:
            errors["password"] = "Password must be at least 6 characters long."
        if password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."

    if errors:
        return json_error("Validation failed.", 400, errors)

    current_user = get_user_by_id(user_id)
    assert current_user is not None

    if email and email != current_user["email"]:
        existing_user = get_user_by_email(email)
        if existing_user and int(existing_user["id"]) != int(user_id):
            return json_error("An account with this email already exists.", 409)

    timestamp = now_iso()
    update_fields = ["full_name = ?", "updated_at = ?"]
    update_values = [full_name, timestamp]

    if email:
        update_fields.insert(1, "email = ?")
        update_values.insert(1, email)

    if password:
        update_fields.append("password_hash = ?")
        update_values.append(generate_password_hash(password))

    update_values.append(user_id)

    with get_db() as connection:
        connection.execute(
            f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?",
            update_values,
        )

    updated_user = get_user_by_id(user_id)
    return jsonify(
        {
            "success": True,
            "message": "Profile updated successfully.",
            "user": serialize_user(updated_user) if updated_user else None,
        }
    )


@app.route("/api/personal-details", methods=["POST", "PUT", "PATCH"])
def save_personal_details():
    data = get_request_data()
    user_id = resolve_user_id(data)
    date_of_birth = (data.get("date_of_birth") or "").strip()
    gender = (data.get("gender") or "").strip().lower()
    phone_number = (data.get("phone_number") or "").strip()
    city = (data.get("city") or "").strip()

    errors: Dict[str, str] = {}
    if not user_id or not get_user_by_id(user_id):
        errors["user"] = "Valid user_id or email is required."
    if not date_of_birth:
        errors["date_of_birth"] = "Date of birth is required."
    if gender not in GENDER_OPTIONS:
        errors["gender"] = "Gender must be one of: male, female, other, prefer_not_to_say."
    if not validate_phone(phone_number):
        errors["phone_number"] = "Phone number must contain 7 to 15 digits and may start with +."
    if not city:
        errors["city"] = "City is required."

    if errors:
        return json_error("Validation failed.", 400, errors)

    timestamp = now_iso()
    with get_db() as connection:
        cursor = connection.execute(
            "SELECT id FROM personal_details WHERE user_id = ?",
            (user_id,),
        )
        existing = cursor.fetchone()
        if existing:
            connection.execute(
                """
                UPDATE personal_details
                SET date_of_birth = ?, gender = ?, phone_number = ?, city = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (date_of_birth, gender, phone_number, city, timestamp, user_id),
            )
            action = "updated"
        else:
            connection.execute(
                """
                INSERT INTO personal_details (
                    user_id, date_of_birth, gender, phone_number, city, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, date_of_birth, gender, phone_number, city, timestamp, timestamp),
            )
            action = "created"

    return jsonify(
        {
            "success": True,
            "message": f"Personal details {action} successfully.",
            "personal_details": {
                "user_id": user_id,
                "date_of_birth": date_of_birth,
                "gender": gender,
                "phone_number": phone_number,
                "city": city,
            },
        }
    )


@app.route("/api/education-details", methods=["POST", "PUT", "PATCH"])
def save_education_details():
    data = get_request_data()
    user_id = resolve_user_id(data)
    current_education_level = (data.get("current_education_level") or "").strip()
    stream = (data.get("stream") or "").strip()
    school_college_name = (data.get("school_college_name") or "").strip()
    average_percentage_gpa = (data.get("average_percentage_gpa") or "").strip()

    errors: Dict[str, str] = {}
    if not user_id or not get_user_by_id(user_id):
        errors["user"] = "Valid user_id or email is required."
    if not current_education_level:
        errors["current_education_level"] = "Current education level is required."
    if not school_college_name:
        errors["school_college_name"] = "School/college name is required."
    if not average_percentage_gpa:
        errors["average_percentage_gpa"] = "Average percentage/GPA is required."

    if errors:
        return json_error("Validation failed.", 400, errors)

    timestamp = now_iso()
    with get_db() as connection:
        cursor = connection.execute(
            "SELECT id FROM education_details WHERE user_id = ?",
            (user_id,),
        )
        existing = cursor.fetchone()
        if existing:
            connection.execute(
                """
                UPDATE education_details
                SET current_education_level = ?, stream = ?, school_college_name = ?, average_percentage_gpa = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (
                    current_education_level,
                    stream,
                    school_college_name,
                    average_percentage_gpa,
                    timestamp,
                    user_id,
                ),
            )
            action = "updated"
        else:
            connection.execute(
                """
                INSERT INTO education_details (
                    user_id, current_education_level, stream, school_college_name,
                    average_percentage_gpa, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    current_education_level,
                    stream,
                    school_college_name,
                    average_percentage_gpa,
                    timestamp,
                    timestamp,
                ),
            )
            action = "created"

    return jsonify(
        {
            "success": True,
            "message": f"Education details {action} successfully.",
            "education_details": {
                "user_id": user_id,
                "current_education_level": current_education_level,
                "stream": stream,
                "school_college_name": school_college_name,
                "average_percentage_gpa": average_percentage_gpa,
            },
        }
    )


@app.route("/api/profile/<email>", methods=["GET"])
def get_profile(email: str):
    normalized_email = normalize_email(email)
    if not validate_email(normalized_email):
        return json_error("A valid email is required.", 400)

    user = get_user_by_email(normalized_email)
    if not user:
        return json_error("User not found.", 404)

    user_id = int(user["id"])
    with get_db() as connection:
        cursor = connection.execute(
            "SELECT date_of_birth, gender, phone_number, city, created_at, updated_at FROM personal_details WHERE user_id = ?",
            (user_id,),
        )
        personal_details = cursor.fetchone()
        cursor = connection.execute(
            "SELECT current_education_level, stream, school_college_name, average_percentage_gpa, created_at, updated_at FROM education_details WHERE user_id = ?",
            (user_id,),
        )
        education_details = cursor.fetchone()

    return jsonify(
        {
            "success": True,
            "user": serialize_user(user),
            "personal_details": dict(personal_details) if personal_details else None,
            "education_details": dict(education_details) if education_details else None,
        }
    )


@app.route("/api/career-assessment", methods=["POST"])
def submit_career_assessment():
    data = get_request_data()
    user_id = resolve_user_id(data)
    if not user_id or not get_user_by_id(user_id):
        return json_error("Valid user_id or email is required.", 400)

    answers: Dict[str, Any] = {}
    validation_errors: Dict[str, str] = {}
    for index in range(1, 11):
        key = f"q{index}"
        normalized = normalize_answer(data.get(key))
        if not normalized:
            validation_errors[key] = "Choose one of: Very Interested, Interested, Neutral, Not Interested."
        else:
            answers[key] = normalized

    if validation_errors:
        return json_error("Validation failed.", 400, validation_errors)

    recommendations = recommend_careers(answers)
    storage = store_career_assessment(user_id, answers, recommendations)

    return jsonify(
        {
            "success": True,
            "message": "Career assessment saved successfully.",
            "assessment": {
                "assessment_id": storage["assessment_id"],
                "user_id": user_id,
                "answers": answers,
                "primaryCareerPath": recommendations["primaryCareerPath"],
                "topScore": recommendations["topScore"],
                "recommendedCareers": recommendations["recommendedCareers"],
            },
        }
    ), 201


@app.route("/api/career-recommendation", methods=["POST"])
def submit_career_recommendation():
    data = get_request_data()
    user_id = resolve_user_id(data)
    if not user_id or not get_user_by_id(user_id):
        return json_error("Valid user_id or email is required.", 400)

    answers: Dict[str, Any] = {}
    validation_errors: Dict[str, str] = {}
    for index in range(1, 11):
        key = f"q{index}"
        raw_value = data.get(key)
        score = normalize_numeric_answer(raw_value)
        if score < 1 or score > 5:
            validation_errors[key] = "Choose a value from 1 to 5."
        else:
            answers[key] = score

    if validation_errors:
        return json_error("Validation failed.", 400, validation_errors)

    top_domains = calculate_top_domains(answers)
    recommendations = calculate_result(answers)
    storage = store_career_recommendation(user_id, answers, recommendations)
    saved_recommendation = fetch_latest_career_recommendation(user_id)

    api_output = {
        "success": True,
        "recommendedCareers": recommendations,
    }

    return jsonify(
        {
            "success": True,
            "answers": answers,
            "topDomains": top_domains,
            "studentProfile": build_student_profile(top_domains),
            "recommendedCareers": recommendations,
            "recommendations": recommendations,
            "saved": storage,
            "savedRecord": saved_recommendation,
            "apiOutput": api_output,
        }
    ), 201


@app.route("/api/career-recommendation/<int:user_id>", methods=["GET"])
def get_career_recommendation(user_id: int):
    if not get_user_by_id(user_id):
        return json_error("User not found.", 404)

    recommendation = fetch_latest_career_recommendation(user_id)
    if not recommendation:
        return json_error("Career recommendation not found.", 404)

    return jsonify({"success": True, "recommendation": recommendation})


@app.route("/api/career-assessment/<int:user_id>", methods=["GET"])
def get_career_assessment(user_id: int):
    if not get_user_by_id(user_id):
        return json_error("User not found.", 404)

    assessment = fetch_latest_assessment(user_id)
    if not assessment:
        return json_error("Career assessment not found.", 404)

    return jsonify({"success": True, "assessment": assessment})


@app.route("/api/debug/storage", methods=["GET"])
def debug_storage():
    email = normalize_email(request.args.get("email"))
    user_id_value = request.args.get("user_id")
    user_id: Optional[int] = None

    if user_id_value:
        try:
            user_id = int(user_id_value)
        except (TypeError, ValueError):
            return json_error("user_id must be an integer.", 400)
    elif email:
        user = get_user_by_email(email)
        if user:
            user_id = int(user["id"])
    else:
        return json_error("Provide either email or user_id.", 400)

    if not user_id:
        return json_error("User not found.", 404)

    with get_db() as connection:
        user_row = connection.execute(
            "SELECT id, full_name, email, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        personal_row = connection.execute(
            "SELECT * FROM personal_details WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        education_row = connection.execute(
            "SELECT * FROM education_details WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    return jsonify(
        {
            "success": True,
            "database": "sqlite",
            "user": dict(user_row) if user_row else None,
            "personal_details": dict(personal_row) if personal_row else None,
            "education_details": dict(education_row) if education_row else None,
            "stored": {
                "user": bool(user_row),
                "personal_details": bool(personal_row),
                "education_details": bool(education_row),
            },
        }
    )


@app.route("/api/debug/career-assessment-storage", methods=["GET"])
def debug_career_assessment_storage():
    email = normalize_email(request.args.get("email"))
    user_id_value = request.args.get("user_id")
    user_id: Optional[int] = None

    if user_id_value:
        try:
            user_id = int(user_id_value)
        except (TypeError, ValueError):
            return json_error("user_id must be an integer.", 400)
    elif email:
        user = get_user_by_email(email)
        if user:
            user_id = int(user["id"])
    else:
        return json_error("Provide either email or user_id.", 400)

    if not user_id:
        return json_error("User not found.", 404)

    assessment = fetch_latest_assessment(user_id)
    return jsonify(
        {
            "success": True,
            "database": "sqlite",
            "assessment": assessment,
            "stored": bool(assessment),
        }
    )


@app.route("/view-data", methods=["GET"])
def view_data_page():
        return """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Stored Data Viewer</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #f5f7fb;
            --card: #ffffff;
            --text: #172033;
            --muted: #667085;
            --border: #d9e0ea;
            --accent: #2563eb;
            --accent-2: #7c3aed;
            --success: #127a3d;
            --error: #b42318;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: linear-gradient(180deg, #eef2ff 0%, var(--bg) 40%, #eef7ff 100%);
            color: var(--text);
            min-height: 100vh;
        }
        .wrap {
            max-width: 1100px;
            margin: 0 auto;
            padding: 32px 16px 48px;
        }
        .hero {
            display: grid;
            gap: 12px;
            margin-bottom: 24px;
        }
        .hero h1 {
            margin: 0;
            font-size: clamp(28px, 4vw, 44px);
            letter-spacing: -0.04em;
        }
        .hero p {
            margin: 0;
            color: var(--muted);
            max-width: 720px;
            line-height: 1.5;
        }
        .panel {
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(217,224,234,0.9);
            border-radius: 20px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
            padding: 20px;
            backdrop-filter: blur(12px);
        }
        .controls {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            margin-bottom: 18px;
        }
        .controls input {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px 16px;
            font-size: 16px;
            outline: none;
            background: #fff;
        }
        .controls input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(37,99,235,0.12);
        }
        .controls button {
            border: 0;
            border-radius: 14px;
            padding: 14px 18px;
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            cursor: pointer;
            min-width: 140px;
        }
        .note {
            color: var(--muted);
            font-size: 14px;
            margin-bottom: 16px;
        }
        .status {
            margin: 0 0 16px;
            font-weight: 700;
        }
        .status.ok { color: var(--success); }
        .status.err { color: var(--error); }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
        }
        .card {
            border: 1px solid var(--border);
            border-radius: 16px;
            background: #fff;
            padding: 16px;
        }
        .card h2 {
            margin: 0 0 12px;
            font-size: 18px;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 13px;
            line-height: 1.5;
            color: #1f2937;
        }
        .pill {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: #eef2ff;
            color: #3730a3;
            font-size: 12px;
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        @media (max-width: 720px) {
            .controls { grid-template-columns: 1fr; }
            .controls button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="wrap">
        <div class="hero">
            <h1>Stored Data Viewer</h1>
            <p>Enter a real saved email or user id to inspect what is stored in SQLite for account, personal details, and education details.</p>
        </div>

        <div class="panel">
            <div class="controls">
                <input id="lookupValue" type="text" placeholder="Enter email or user id" value="">
                <button id="lookupButton" type="button">Load Data</button>
            </div>
            <div class="note">Example: <span class="pill">email: user@example.com</span><span class="pill">user id: 1</span></div>
            <p id="status" class="status"></p>
            <div class="cards">
                <div class="card">
                    <h2>User</h2>
                    <pre id="userBox">No data loaded yet.</pre>
                </div>
                <div class="card">
                    <h2>Personal Details</h2>
                    <pre id="personalBox">No data loaded yet.</pre>
                </div>
                <div class="card">
                    <h2>Education Details</h2>
                    <pre id="educationBox">No data loaded yet.</pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        const lookupValue = document.getElementById('lookupValue');
        const lookupButton = document.getElementById('lookupButton');
        const statusEl = document.getElementById('status');
        const userBox = document.getElementById('userBox');
        const personalBox = document.getElementById('personalBox');
        const educationBox = document.getElementById('educationBox');

        function pretty(value) {
            return value ? JSON.stringify(value, null, 2) : 'Not found';
        }

        function setStatus(message, ok) {
            statusEl.textContent = message;
            statusEl.className = ok ? 'status ok' : 'status err';
        }

        async function loadData() {
            const value = lookupValue.value.trim();
            if (!value) {
                setStatus('Enter an email or user id first.', false);
                return;
            }

            const isId = /^\\d+$/.test(value);
            const url = isId
                ? `/api/debug/storage?user_id=${encodeURIComponent(value)}`
                : `/api/debug/storage?email=${encodeURIComponent(value)}`;

            setStatus('Loading data...', true);
            userBox.textContent = 'Loading...';
            personalBox.textContent = 'Loading...';
            educationBox.textContent = 'Loading...';

            try {
                const response = await fetch(url);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || 'Failed to load stored data.');
                }

                userBox.textContent = pretty(data.user);
                personalBox.textContent = pretty(data.personal_details);
                educationBox.textContent = pretty(data.education_details);
                setStatus(
                    `Loaded successfully. Stored flags: user=${data.stored.user}, personal_details=${data.stored.personal_details}, education_details=${data.stored.education_details}`,
                    true
                );
            } catch (error) {
                setStatus(error.message, false);
                userBox.textContent = 'No data loaded.';
                personalBox.textContent = 'No data loaded.';
                educationBox.textContent = 'No data loaded.';
            }
        }

        lookupButton.addEventListener('click', loadData);
        lookupValue.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                loadData();
            }
        });
    </script>
</body>
</html>
        """


@app.route("/api/debug/self-test", methods=["POST"])
def self_test():
    payload = get_request_data()
    unique_suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    full_name = payload.get("full_name", f"Test User {unique_suffix}")
    email = normalize_email(payload.get("email", f"test{unique_suffix}@example.com"))
    password = payload.get("password", "Test@12345")

    results: Dict[str, Any] = {}

    with app.test_client() as client:
        register_response = client.post(
            "/api/auth/register",
            json={
                "full_name": full_name,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )
        results["register"] = {
            "status_code": register_response.status_code,
            "body": register_response.get_json(),
        }

        if register_response.status_code not in (200, 201):
            return jsonify({"success": False, "message": "Registration test failed.", "results": results}), 500

        user_data = register_response.get_json().get("user", {})
        user_id = user_data.get("id")

        personal_response = client.post(
            "/api/personal-details",
            json={
                "user_id": user_id,
                "date_of_birth": "2000-01-01",
                "gender": "male",
                "phone_number": "+919876543210",
                "city": "Mumbai",
            },
        )
        results["personal_details"] = {
            "status_code": personal_response.status_code,
            "body": personal_response.get_json(),
        }

        education_response = client.post(
            "/api/education-details",
            json={
                "user_id": user_id,
                "current_education_level": "Graduate",
                "stream": "Computer Science",
                "school_college_name": "ABC College",
                "average_percentage_gpa": "8.5",
            },
        )
        results["education_details"] = {
            "status_code": education_response.status_code,
            "body": education_response.get_json(),
        }

        profile_response = client.get(f"/api/profile/{email}")
        profile_json = profile_response.get_json() or {}
        results["profile"] = {
            "status_code": profile_response.status_code,
            "body": profile_json,
        }

        assessment_response = client.post(
            "/api/career-assessment",
            json={
                "user_id": user_id,
                "q1": "Very Interested",
                "q2": "Very Interested",
                "q3": "Interested",
                "q4": "Neutral",
                "q5": "Neutral",
                "q6": "Very Interested",
                "q7": "Interested",
                "q8": "Interested",
                "q9": "Very Interested",
                "q10": "Interested",
            },
        )
        results["career_assessment"] = {
            "status_code": assessment_response.status_code,
            "body": assessment_response.get_json(),
        }

        assessment_lookup_response = client.get(f"/api/career-assessment/{user_id}")
        results["career_assessment_lookup"] = {
            "status_code": assessment_lookup_response.status_code,
            "body": assessment_lookup_response.get_json(),
        }

    profile_body = results["profile"]["body"]
    personal_saved = bool(profile_body.get("personal_details"))
    education_saved = bool(profile_body.get("education_details"))
    career_assessment_saved = bool(results.get("career_assessment", {}).get("body", {}).get("success"))
    career_assessment_loaded = bool(results.get("career_assessment_lookup", {}).get("body", {}).get("assessment"))

    if not personal_saved or not education_saved or not career_assessment_saved or not career_assessment_loaded:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Data was not fully persisted.",
                    "results": results,
                }
            ),
            500,
        )

    return jsonify(
        {
            "success": True,
            "message": "Database save test passed.",
            "results": results,
        }
    )


@app.errorhandler(404)
def not_found(_error):
    return json_error("Route not found.", 404)


@app.errorhandler(500)
def server_error(_error):
    return json_error("Internal server error.", 500)


if __name__ == "__main__":
    ensure_database()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
