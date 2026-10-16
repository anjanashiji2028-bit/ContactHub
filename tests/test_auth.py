def test_registration_success(client):
    """Verify that a new user can register successfully."""
    response = client.post('/register', data={
        'full_name': 'Charlie Brown',
        'email': 'charlie@test.local',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

def test_registration_duplicate_email(client):
    """Verify that duplicate email registration is rejected."""
    response = client.post('/register', data={
        'full_name': 'Alice Copy',
        'email': 'alice@test.local',  # Pre-seeded in fixture
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"already exists" in response.data

def test_registration_password_mismatch(client):
    """Verify password and confirm_password must match."""
    response = client.post('/register', data={
        'full_name': 'Mismatch User',
        'email': 'mismatch@test.local',
        'password': 'Password@123',
        'confirm_password': 'Password@999'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_registration_short_password(client):
    """Verify password must be at least 6 characters."""
    response = client.post('/register', data={
        'full_name': 'Short PW User',
        'email': 'short@test.local',
        'password': '123',
        'confirm_password': '123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"at least 6 characters" in response.data

def test_login_success(client):
    """Verify login with correct credentials sets session and redirects to dashboard."""
    response = client.post('/login', data={
        'email': 'alice@test.local',
        'password': 'Secret@123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back, Alice Smith!" in response.data

def test_login_invalid_password(client):
    """Verify login rejection with incorrect password."""
    response = client.post('/login', data={
        'email': 'alice@test.local',
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_protected_route_requires_login(client):
    """Verify unauthenticated access to /dashboard redirects to login."""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_logout(auth_client):
    """Verify logout clears session and redirects."""
    response = auth_client.post('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out" in response.data

    # Attempting to access dashboard after logout should redirect
    dashboard_res = auth_client.get('/dashboard')
    assert dashboard_res.status_code == 302
