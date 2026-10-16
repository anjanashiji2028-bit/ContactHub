import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_db_connection, init_db
from config import Config

def seed_database(db_path=None):
    """Populates the database with realistic fictional data for demonstration."""
    if db_path is None:
        db_path = Config.DATABASE_PATH
        
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    print("[*] Seeding demo users...")
    demo_password_hash = generate_password_hash("Demo@12345")
    test_password_hash = generate_password_hash("Test@12345")
    
    # Insert Demo User 1
    cursor.execute("""
        INSERT OR IGNORE INTO users (full_name, email, password_hash)
        VALUES (?, ?, ?)
    """, ("Alex Morgan", "demo@contacthub.local", demo_password_hash))
    
    # Insert Demo User 2 (for user isolation verification)
    cursor.execute("""
        INSERT OR IGNORE INTO users (full_name, email, password_hash)
        VALUES (?, ?, ?)
    """, ("Samantha Reed", "testuser@contacthub.local", test_password_hash))
    
    conn.commit()
    
    # Get user id for Alex Morgan
    cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@contacthub.local",))
    alex_id = cursor.fetchone()['id']
    
    # Get user id for Samantha Reed
    cursor.execute("SELECT id FROM users WHERE email = ?", ("testuser@contacthub.local",))
    samantha_id = cursor.fetchone()['id']
    
    print(f"[*] Seeding contacts for user id {alex_id} (Alex Morgan)...")
    
    sample_contacts_alex = [
        ("Aarav Sharma", "+91 98765 43210", "+91 98765 43219", "aarav.sharma@example.com", "Infosys Technologies", "Senior Software Engineer", "123 Brigade Road", "Bengaluru", "Work", "Colleague from Cloud Platforms team. Key contact for Docker microservices.", 1),
        ("Priya Nair", "+91 98123 45678", None, "priya.nair@example.com", "Wipro Digital", "DevOps Consultant", "45 MG Road", "Kochi", "Work", "Met at Kubernetes Community Days 2026.", 1),
        ("Dr. Rajesh Kumar", "+91 94470 11223", "+91 484 2554433", "dr.rajesh.k@example.com", "Aster Medcity", "Consultant Physician", "Cheranalloor", "Kochi", "Personal", "Family doctor. Available Monday-Friday.", 0),
        ("Ananya Patel", "+91 99887 65432", None, "ananya.patel@example.com", "Google Cloud Partner", "Solutions Architect", "Sector 29", "Gurugram", "Work", "Discussed AWS Lambda serverless migration.", 1),
        ("Rohan Verma", "+91 97112 33445", None, "rohan.verma@example.com", "Self-employed", "Freelance UI/UX Designer", "Koramangala 5th Block", "Bengaluru", "Friends", "College classmate from BCA 2024 batch.", 0),
        ("Sneha Menon", "+91 94951 88990", "+91 94951 88991", "sneha.menon@example.com", "Tata Consultancy Services", "System Analyst", "Infopark Phase 2", "Kochi", "Family", "Cousin sister. Living in Kakkanad.", 1),
        ("Vikram Singh", "+91 98200 12345", None, "vikram.singh@example.com", "Reliance Jio", "Network Architect", "Bandra Kurla Complex", "Mumbai", "Work", "Contact for 5G edge computing virtualization queries.", 0),
        ("Kavita Iyer", "+91 93456 78901", None, "kavita.iyer@example.com", "HCL Tech", "QA Automation Lead", "OMR IT Corridor", "Chennai", "Friends", "Study group lead for Python automation.", 0),
        ("Uncle Thomas", "+91 94471 22334", None, "thomas.mathew@example.com", "Retired", "Plantation Manager", "Kanjirappally", "Kottayam", "Family", "Call on Sunday evenings.", 1),
        ("City Ambulance Helpline", "108", "102", "emergency@health.gov.in", "National Health Mission", "Emergency Service", "Civil Station", "Kochi", "Other", "Official emergency medical response hotline.", 0),
        ("David Miller", "+1 415 555 0199", None, "david.miller@example.com", "Cloud Native Foundation", "Open Source Mentor", "Market Street", "San Francisco", "Work", "Kubernetes upstream project mentor.", 0),
        ("Maya Pillai", "+91 96543 21098", None, "maya.pillai@example.com", "Deloitte India", "Cybersecurity Analyst", "Cyber City", "Hyderabad", "Friends", "BCA project partner. Working on cloud security.", 1),
    ]
    
    for c in sample_contacts_alex:
        cursor.execute("""
            INSERT OR IGNORE INTO contacts 
            (user_id, full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (alex_id, c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10]))
    
    # Seed isolated contact for Samantha Reed
    cursor.execute("""
        INSERT OR IGNORE INTO contacts 
        (user_id, full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (samantha_id, "Secret Contact of Samantha", "+91 90000 00001", None, "secret@example.com", "Confidential Corp", "Manager", "Top Secret", "Delhi", "Personal", "This contact must NEVER be visible to Alex Morgan.", 0))
    
    # Seed tags for Alex
    tags = ["VIP", "College", "College-Project", "Tech-Lead"]
    for tag in tags:
        cursor.execute("INSERT OR IGNORE INTO tags (user_id, tag_name) VALUES (?, ?)", (alex_id, tag))
        
    conn.commit()
    conn.close()
    print("[+] Database successfully seeded with demo accounts and fictional contacts.")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    seed_database(target)
