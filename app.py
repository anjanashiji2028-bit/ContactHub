import os
import csv
import io
import re
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g, jsonify, Response, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config, TestConfig
from database.init_db import get_db_connection, init_db

def create_app(test_config=None):
    """Application factory for ContactHub."""
    app = Flask(__name__)
    
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_object(Config)

    # Ensure database directory and file exist
    with app.app_context():
        init_db(app.config['DATABASE_PATH'])

    # Database Context Management
    def get_db():
        if 'db' not in g:
            g.db = get_db_connection(app.config['DATABASE_PATH'])
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # CSRF Protection Helpers
    def generate_csrf_token():
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(24)
        return session['_csrf_token']

    @app.context_processor
    def inject_helpers():
        return {
            'csrf_token': generate_csrf_token,
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'email': session.get('user_email')
            } if 'user_id' in session else None,
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'app_name': app.config.get('APP_NAME', 'ContactHub')
        }

    @app.before_request
    def verify_csrf():
        if request.method in ('POST', 'PUT', 'DELETE'):
            if app.config.get('TESTING') and not app.config.get('WTF_CSRF_ENABLED', False):
                return  # Skip CSRF in test mode when disabled
            token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            expected_token = session.get('_csrf_token')
            if not token or not expected_token or token != expected_token:
                abort(400, description="Invalid or missing CSRF token. Please refresh and try again.")

    # Authorization Decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('login', next=request.path))
            return f(*args, **kwargs)
        return decorated_function

    # Template filter for initials avatar
    @app.template_filter('initials')
    def initials_filter(name):
        if not name:
            return "CH"
        parts = name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return name[:2].upper()

    # Color generator based on name string
    @app.template_filter('avatar_color')
    def avatar_color_filter(name):
        colors = [
            '#0d9488', '#0284c7', '#2563eb', '#7c3aed',
            '#db2777', '#ea580c', '#059669', '#4f46e5'
        ]
        if not name:
            return colors[0]
        val = sum(ord(c) for c in name)
        return colors[val % len(colors)]

    # Newline to HTML line break filter
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if not s:
            return ""
        from markupsafe import Markup, escape
        return Markup(escape(s).replace('\n', '<br>\n'))

    # ==========================================
    # ROUTES: HOME & AUTHENTICATION
    # ==========================================

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            errors = []
            if not full_name:
                errors.append("Full Name is required.")
            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("A valid email address is required.")
            if len(password) < 6:
                errors.append("Password must be at least 6 characters long.")
            if password != confirm_password:
                errors.append("Passwords do not match.")

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('register.html', full_name=full_name, email=email)

            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                flash("An account with this email address already exists.", "danger")
                return render_template('register.html', full_name=full_name, email=email)

            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, password_hash)
            )
            db.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            next_url = request.args.get('next')

            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template('login.html', email=email)

            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                generate_csrf_token()

                flash(f"Welcome back, {user['full_name']}!", "success")
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))

            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html', email=email)

        return render_template('login.html')

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        session.clear()
        flash("You have been successfully logged out.", "info")
        return redirect(url_for('login'))

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update_info':
                new_name = request.form.get('full_name', '').strip()
                if not new_name:
                    flash("Full name cannot be empty.", "danger")
                else:
                    cursor.execute("UPDATE users SET full_name = ? WHERE id = ?", (new_name, user_id))
                    db.commit()
                    session['user_name'] = new_name
                    flash("Profile name updated successfully.", "success")
            elif action == 'change_password':
                current_pw = request.form.get('current_password', '')
                new_pw = request.form.get('new_password', '')
                confirm_pw = request.form.get('confirm_password', '')

                cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()

                if not check_password_hash(user_row['password_hash'], current_pw):
                    flash("Current password is incorrect.", "danger")
                elif len(new_pw) < 6:
                    flash("New password must be at least 6 characters long.", "danger")
                elif new_pw != confirm_pw:
                    flash("New passwords do not match.", "danger")
                else:
                    new_hash = generate_password_hash(new_pw)
                    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
                    db.commit()
                    flash("Password changed successfully.", "success")

            return redirect(url_for('profile'))

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) AS total FROM contacts WHERE user_id = ?", (user_id,))
        total_contacts = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS favs FROM contacts WHERE user_id = ? AND is_favorite = 1", (user_id,))
        fav_contacts = cursor.fetchone()['favs']

        return render_template('profile.html', user=user, total_contacts=total_contacts, fav_contacts=fav_contacts)

    # ==========================================
    # ROUTES: DASHBOARD
    # ==========================================

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Overall summary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN category = 'Personal' THEN 1 ELSE 0 END) AS personal,
                SUM(CASE WHEN category = 'Work' THEN 1 ELSE 0 END) AS work,
                SUM(CASE WHEN category = 'Family' THEN 1 ELSE 0 END) AS family,
                SUM(CASE WHEN category = 'Friends' THEN 1 ELSE 0 END) AS friends,
                SUM(CASE WHEN category = 'Other' THEN 1 ELSE 0 END) AS other,
                SUM(CASE WHEN is_favorite = 1 THEN 1 ELSE 0 END) AS favorites
            FROM contacts
            WHERE user_id = ?
        """, (user_id,))
        stats = cursor.fetchone()

        # Recent 5 contacts
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (user_id,))
        recent_contacts = cursor.fetchall()

        # Favorite contacts (quick cards)
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE user_id = ? AND is_favorite = 1 
            ORDER BY full_name ASC 
            LIMIT 6
        """, (user_id,))
        favorite_contacts = cursor.fetchall()

        # Category breakdown for display
        categories = [
            {'name': 'Personal', 'count': stats['personal'] or 0, 'color': 'primary', 'icon': 'bi-person'},
            {'name': 'Work', 'count': stats['work'] or 0, 'color': 'info', 'icon': 'bi-briefcase'},
            {'name': 'Family', 'count': stats['family'] or 0, 'color': 'success', 'icon': 'bi-house-heart'},
            {'name': 'Friends', 'count': stats['friends'] or 0, 'color': 'warning', 'icon': 'bi-people'},
            {'name': 'Other', 'count': stats['other'] or 0, 'color': 'secondary', 'icon': 'bi-tag'}
        ]

        return render_template(
            'dashboard.html',
            stats=stats,
            recent_contacts=recent_contacts,
            favorite_contacts=favorite_contacts,
            categories=categories
        )

    # ==========================================
    # ROUTES: CONTACT CRUD & MANAGEMENT
    # ==========================================

    @app.route('/contacts')
    @login_required
    def contacts():
        user_id = session['user_id']
        search_query = request.args.get('q', '').strip()
        category_filter = request.args.get('category', '').strip()
        favorite_filter = request.args.get('favorite', '').strip()
        sort_by = request.args.get('sort', 'name_asc').strip()
        page = request.args.get('page', 1, type=int)
        per_page = app.config.get('ITEMS_PER_PAGE', 8)

        db = get_db()
        cursor = db.cursor()

        # Base filter condition strictly constrained to authenticated user
        conditions = ["user_id = ?"]
        params = [user_id]

        if search_query:
            conditions.append(
                "(full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR company LIKE ? OR city LIKE ?)"
            )
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard, wildcard, wildcard])

        if category_filter and category_filter in ['Personal', 'Family', 'Friends', 'Work', 'Other']:
            conditions.append("category = ?")
            params.append(category_filter)

        if favorite_filter == '1':
            conditions.append("is_favorite = 1")

        where_clause = " AND ".join(conditions)

        # Sorting logic
        sort_clauses = {
            'name_asc': 'full_name ASC',
            'name_desc': 'full_name DESC',
            'date_desc': 'created_at DESC',
            'date_asc': 'created_at ASC'
        }
        order_clause = sort_clauses.get(sort_by, 'full_name ASC')

        # Total count for pagination
        count_query = f"SELECT COUNT(*) AS total FROM contacts WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()['total']
        total_pages = max(1, (total_items + per_page - 1) // per_page)
        page = min(max(1, page), total_pages)
        offset = (page - 1) * per_page

        # Fetch records
        query = f"""
            SELECT * FROM contacts 
            WHERE {where_clause} 
            ORDER BY {order_clause} 
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [per_page, offset])
        contact_list = cursor.fetchall()

        # Fetch category counts for tabs
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM contacts 
            WHERE user_id = ? 
            GROUP BY category
        """, (user_id,))
        cat_counts = {row['category']: row['count'] for row in cursor.fetchall()}

        return render_template(
            'contacts.html',
            contacts=contact_list,
            search_query=search_query,
            category_filter=category_filter,
            favorite_filter=favorite_filter,
            sort_by=sort_by,
            page=page,
            total_pages=total_pages,
            total_items=total_items,
            cat_counts=cat_counts
        )

    @app.route('/contacts/new', methods=['GET', 'POST'])
    @login_required
    def add_contact():
        user_id = session['user_id']

        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            secondary_phone = request.form.get('secondary_phone', '').strip() or None
            email = request.form.get('email', '').strip() or None
            company = request.form.get('company', '').strip() or None
            job_title = request.form.get('job_title', '').strip() or None
            address = request.form.get('address', '').strip() or None
            city = request.form.get('city', '').strip() or None
            category = request.form.get('category', 'Other').strip()
            notes = request.form.get('notes', '').strip() or None
            is_favorite = 1 if request.form.get('is_favorite') else 0

            # Validations
            errors = []
            if not full_name:
                errors.append("Contact full name is required.")
            if not phone:
                errors.append("Primary phone number is required.")
            if category not in ['Personal', 'Family', 'Friends', 'Work', 'Other']:
                category = 'Other'

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('contact_form.html', action='add', contact=request.form)

            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO contacts 
                (user_id, full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite))
            db.commit()

            new_id = cursor.lastrowid
            flash(f"Contact '{full_name}' added successfully!", "success")
            return redirect(url_for('contact_detail', contact_id=new_id))

        return render_template('contact_form.html', action='add', contact={})

    @app.route('/contacts/<int:contact_id>')
    @login_required
    def contact_detail(contact_id):
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Strict user_id ownership check prevents IDOR
        cursor.execute("SELECT * FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        contact = cursor.fetchone()

        if not contact:
            flash("Contact not found or you do not have permission to view it.", "danger")
            return redirect(url_for('contacts'))

        return render_template('contact_detail.html', contact=contact)

    @app.route('/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_contact(contact_id):
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        contact = cursor.fetchone()

        if not contact:
            flash("Contact not found or access denied.", "danger")
            return redirect(url_for('contacts'))

        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            secondary_phone = request.form.get('secondary_phone', '').strip() or None
            email = request.form.get('email', '').strip() or None
            company = request.form.get('company', '').strip() or None
            job_title = request.form.get('job_title', '').strip() or None
            address = request.form.get('address', '').strip() or None
            city = request.form.get('city', '').strip() or None
            category = request.form.get('category', 'Other').strip()
            notes = request.form.get('notes', '').strip() or None
            is_favorite = 1 if request.form.get('is_favorite') else 0

            errors = []
            if not full_name:
                errors.append("Contact full name is required.")
            if not phone:
                errors.append("Primary phone number is required.")
            if category not in ['Personal', 'Family', 'Friends', 'Work', 'Other']:
                category = 'Other'

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('contact_form.html', action='edit', contact=request.form, contact_id=contact_id)

            cursor.execute("""
                UPDATE contacts SET
                    full_name = ?, phone = ?, secondary_phone = ?, email = ?,
                    company = ?, job_title = ?, address = ?, city = ?,
                    category = ?, notes = ?, is_favorite = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite, contact_id, user_id))
            db.commit()

            flash(f"Contact '{full_name}' updated successfully!", "success")
            return redirect(url_for('contact_detail', contact_id=contact_id))

        return render_template('contact_form.html', action='edit', contact=contact, contact_id=contact_id)

    @app.route('/contacts/<int:contact_id>/delete', methods=['POST'])
    @login_required
    def delete_contact(contact_id):
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT full_name FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        contact = cursor.fetchone()

        if not contact:
            flash("Contact not found or access denied.", "danger")
            return redirect(url_for('contacts'))

        contact_name = contact['full_name']
        cursor.execute("DELETE FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        db.commit()

        flash(f"Contact '{contact_name}' was permanently deleted.", "info")
        return redirect(url_for('contacts'))

    @app.route('/contacts/<int:contact_id>/toggle-favorite', methods=['POST'])
    @login_required
    def toggle_favorite(contact_id):
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT is_favorite, full_name FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        contact = cursor.fetchone()

        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404

        new_status = 0 if contact['is_favorite'] == 1 else 1
        cursor.execute("UPDATE contacts SET is_favorite = ? WHERE id = ? AND user_id = ?", (new_status, contact_id, user_id))
        db.commit()

        # If AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': True, 'is_favorite': new_status})

        msg = f"Marked '{contact['full_name']}' as favorite." if new_status else f"Removed '{contact['full_name']}' from favorites."
        flash(msg, "success")
        return redirect(request.referrer or url_for('contacts'))

    # ==========================================
    # ROUTES: IMPORT & EXPORT (CSV)
    # ==========================================

    @app.route('/export')
    @login_required
    def export_contacts():
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM contacts WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()['total']
        return render_template('export_contacts.html', total_contacts=total)

    @app.route('/export/download', methods=['POST'])
    @login_required
    def download_csv():
        user_id = session['user_id']
        category = request.form.get('category', 'all')
        
        db = get_db()
        cursor = db.cursor()

        if category and category != 'all':
            cursor.execute("""
                SELECT full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite, created_at
                FROM contacts 
                WHERE user_id = ? AND category = ?
                ORDER BY full_name ASC
            """, (user_id, category))
        else:
            cursor.execute("""
                SELECT full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite, created_at
                FROM contacts 
                WHERE user_id = ?
                ORDER BY full_name ASC
            """, (user_id,))

        contacts_to_export = cursor.fetchall()

        # Create in-memory CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Full Name', 'Primary Phone', 'Secondary Phone', 'Email',
            'Company', 'Job Title', 'Address', 'City', 'Category',
            'Notes', 'Is Favorite', 'Created Date'
        ])

        for row in contacts_to_export:
            writer.writerow([
                row['full_name'],
                row['phone'],
                row['secondary_phone'] or '',
                row['email'] or '',
                row['company'] or '',
                row['job_title'] or '',
                row['address'] or '',
                row['city'] or '',
                row['category'],
                row['notes'] or '',
                'Yes' if row['is_favorite'] == 1 else 'No',
                row['created_at']
            ])

        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"contacthub_export_{timestamp}.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    @app.route('/import', methods=['GET', 'POST'])
    @login_required
    def import_contacts():
        user_id = session['user_id']
        
        if request.method == 'POST':
            if 'csv_file' not in request.files:
                flash("No file was uploaded.", "danger")
                return redirect(url_for('import_contacts'))

            file = request.files['csv_file']
            if not file or file.filename == '':
                flash("Please select a valid CSV file to upload.", "danger")
                return redirect(url_for('import_contacts'))

            if not file.filename.lower().endswith('.csv'):
                flash("Only files with .csv extension are supported.", "danger")
                return redirect(url_for('import_contacts'))

            # Duplicate handling policy: 'skip', 'update', or 'allow_duplicates'
            duplicate_policy = request.form.get('duplicate_policy', 'skip')

            try:
                # Read stream with encoding detection (try utf-8, fallback to latin-1)
                content = file.stream.read()
                try:
                    decoded = content.decode('utf-8-sig')
                except UnicodeDecodeError:
                    decoded = content.decode('latin-1')

                stream = io.StringIO(decoded, newline=None)
                reader = csv.DictReader(stream)

                if not reader.fieldnames:
                    flash("Uploaded CSV file appears to be empty.", "danger")
                    return redirect(url_for('import_contacts'))

                # Normalize headers: lower case, strip whitespace
                header_map = {}
                for field in reader.fieldnames:
                    clean = field.strip().lower().replace(' ', '_')
                    header_map[clean] = field

                # Match possible header variations
                name_col = header_map.get('full_name') or header_map.get('name')
                phone_col = header_map.get('primary_phone') or header_map.get('phone') or header_map.get('mobile')

                if not name_col or not phone_col:
                    flash("CSV must contain at least 'Full Name' (or 'Name') and 'Primary Phone' (or 'Phone') columns.", "danger")
                    return redirect(url_for('import_contacts'))

                sec_phone_col = header_map.get('secondary_phone') or header_map.get('secondary')
                email_col = header_map.get('email') or header_map.get('email_address')
                company_col = header_map.get('company') or header_map.get('organization')
                job_col = header_map.get('job_title') or header_map.get('designation') or header_map.get('job')
                address_col = header_map.get('address')
                city_col = header_map.get('city')
                category_col = header_map.get('category')
                notes_col = header_map.get('notes')
                fav_col = header_map.get('is_favorite') or header_map.get('favorite')

                db = get_db()
                cursor = db.cursor()

                inserted = 0
                updated = 0
                skipped = 0

                valid_categories = {'Personal', 'Family', 'Friends', 'Work', 'Other'}

                for row in reader:
                    full_name = (row.get(name_col) or '').strip()
                    phone = (row.get(phone_col) or '').strip()
                    if not full_name or not phone:
                        skipped += 1
                        continue

                    sec_phone = (row.get(sec_phone_col) or '').strip() or None if sec_phone_col else None
                    email = (row.get(email_col) or '').strip() or None if email_col else None
                    company = (row.get(company_col) or '').strip() or None if company_col else None
                    job_title = (row.get(job_col) or '').strip() or None if job_col else None
                    address = (row.get(address_col) or '').strip() or None if address_col else None
                    city = (row.get(city_col) or '').strip() or None if city_col else None
                    
                    cat_val = (row.get(category_col) or 'Other').strip().capitalize() if category_col else 'Other'
                    category = cat_val if cat_val in valid_categories else 'Other'
                    notes = (row.get(notes_col) or '').strip() or None if notes_col else None
                    
                    fav_raw = (row.get(fav_col) or '0').strip().lower() if fav_col else '0'
                    is_fav = 1 if fav_raw in ('1', 'true', 'yes', 'y') else 0

                    # Duplicate check: check if contact with same phone or same email already exists for this user
                    cursor.execute("""
                        SELECT id FROM contacts 
                        WHERE user_id = ? AND (phone = ? OR (email IS NOT NULL AND email = ?))
                    """, (user_id, phone, email if email else ''))
                    existing = cursor.fetchone()

                    if existing:
                        if duplicate_policy == 'skip':
                            skipped += 1
                            continue
                        elif duplicate_policy == 'update':
                            cursor.execute("""
                                UPDATE contacts SET 
                                    full_name = ?, secondary_phone = ?, company = ?,
                                    job_title = ?, address = ?, city = ?, category = ?,
                                    notes = ?, is_favorite = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE id = ? AND user_id = ?
                            """, (full_name, sec_phone, company, job_title, address, city, category, notes, is_fav, existing['id'], user_id))
                            updated += 1
                            continue
                        # If allow_duplicates, proceed to insert

                    cursor.execute("""
                        INSERT INTO contacts 
                        (user_id, full_name, phone, secondary_phone, email, company, job_title, address, city, category, notes, is_favorite)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, full_name, phone, sec_phone, email, company, job_title, address, city, category, notes, is_fav))
                    inserted += 1

                db.commit()
                flash(f"Import completed successfully! Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}.", "success")
                return redirect(url_for('contacts'))

            except Exception as e:
                flash(f"Error processing CSV file: {str(e)}", "danger")
                return redirect(url_for('import_contacts'))

        return render_template('import_contacts.html')

    @app.route('/import/template')
    @login_required
    def download_template():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Full Name', 'Primary Phone', 'Secondary Phone', 'Email',
            'Company', 'Job Title', 'Address', 'City', 'Category',
            'Notes', 'Is Favorite'
        ])
        writer.writerow([
            'John Doe', '+1 555 123 4567', '+1 555 987 6543', 'john.doe@example.com',
            'Acme Global', 'Cloud Engineer', '100 Tech Blvd', 'Austin', 'Work',
            'Contact from Tech Summit', 'Yes'
        ])
        writer.writerow([
            'Jane Smith', '+44 20 7946 0991', '', 'jane.smith@example.org',
            'Design Studio', 'Art Director', '12 Abbey Road', 'London', 'Friends',
            'College batchmate', 'No'
        ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=contacthub_sample_template.csv"}
        )

    # ==========================================
    # HEALTH CHECK & SYSTEM ENDPOINTS
    # ==========================================

    @app.route('/health')
    def health():
        """Health check endpoint used by Docker, Kubernetes, and monitoring tools."""
        db_status = "disconnected"
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            if cursor.fetchone():
                db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        status_code = 200 if db_status == "connected" else 503
        return jsonify({
            'service': app.config.get('APP_NAME', 'ContactHub'),
            'version': app.config.get('APP_VERSION', '1.0.0'),
            'status': 'healthy' if db_status == "connected" else 'unhealthy',
            'database': db_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), status_code

    # ==========================================
    # ERROR HANDLERS
    # ==========================================

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('404.html', error_title="400 - Bad Request", error_message=getattr(error, 'description', 'Invalid request.')), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html', error_title="404 - Page Not Found", error_message="The page or contact you are looking for does not exist or has been moved."), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('500.html', error_title="500 - Internal Server Error", error_message="An unexpected server error occurred. Please try again later."), 500

    return app

# WSGI Application instance
app = create_app()

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
