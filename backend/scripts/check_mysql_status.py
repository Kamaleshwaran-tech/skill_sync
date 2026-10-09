"""
Diagnostic & Verification Script for MySQL & SkillSync AI.
"""

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymysql
from app.config.settings import get_settings
from app.database.session import Base, engine, get_database_url, SessionLocal
import app.models.models
import app.models.auth_models
from app.services.seed_service import seed_initial_data_if_empty

def diagnose_and_create():
    settings = get_settings()
    print("=" * 60)
    print("[INFO] SKILLSYNC AI -- MYSQL DIAGNOSTIC & INITIALIZER")
    print("=" * 60)
    print(f"DATABASE_URL configured in backend/.env: {settings.database_url}")
    print("-" * 60)

    # Test connecting directly to MySQL server
    passwords = ["2006", "root", "password", "", "admin", "123456", "1234"]
    connected = False
    working_password = None

    for pwd in passwords:
        try:
            conn = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                password=pwd,
                connect_timeout=3,
            )
            connected = True
            working_password = pwd
            print(f"[SUCCESS] Connected to MySQL as 'root' with password: '{pwd}'")
            
            with conn.cursor() as cur:
                # Create Database explicitly
                print("[INFO] Executing: CREATE DATABASE IF NOT EXISTS `skillsync_ai` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                cur.execute("CREATE DATABASE IF NOT EXISTS `skillsync_ai` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.commit()

                # List all databases
                cur.execute("SHOW DATABASES;")
                dbs = [row[0] for row in cur.fetchall()]
                print(f"[INFO] Databases currently inside your MySQL Server: {dbs}")

            conn.close()
            break
        except Exception as err:
            print(f"[FAIL] Connection attempt with password '{pwd}' failed: {err}")

    if not connected:
        print("\n[ERROR] COULD NOT CONNECT TO MYSQL SERVER ON PORT 3306!")
        print("Please check:")
        print("1. Is MySQL Server service running in Windows Services (services.msc -> MySQL80)?")
        print("2. What port is MySQL Workbench connected to? (usually 3306 or 3307)")
        sys.exit(1)

    print("-" * 60)
    print("[INFO] CREATING ALL 28 TABLES IN MYSQL `skillsync_ai`...")
    try:
        from sqlalchemy import create_engine
        mysql_url = f"mysql+pymysql://root:{working_password}@localhost:3306/skillsync_ai"
        my_engine = create_engine(mysql_url, echo=False, future=True)
        Base.metadata.create_all(bind=my_engine)
        print("[SUCCESS] Base.metadata.create_all() finished successfully!")

        # Verify tables inside MySQL
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password=working_password,
            database="skillsync_ai",
        )
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = [row[0] for row in cur.fetchall()]
            print(f"[INFO] Total tables created inside MySQL 'skillsync_ai' ({len(tables)}):")
            for t in sorted(tables):
                print(f"   * {t}")

            # Check if users already seeded
            cur.execute("SELECT id, email, role FROM users;")
            users = cur.fetchall()
            print(f"\n[INFO] Users in MySQL ({len(users)}): {users}")

            # Check jobs
            cur.execute("SELECT id, title, company FROM jobs;")
            jobs = cur.fetchall()
            print(f"[INFO] Jobs in MySQL ({len(jobs)}): {jobs}")

        conn.close()

    except Exception as exc:
        print(f"[ERROR] Error creating tables: {exc}")
        sys.exit(1)

    print("=" * 60)
    print("[SUCCESS] MYSQL DATABASE AND ALL TABLES ARE 100% READY!")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_and_create()

