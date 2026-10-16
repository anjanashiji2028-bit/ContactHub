def test_create_contact_success(auth_client):
    """Verify that a contact is successfully created."""
    response = auth_client.post('/contacts/new', data={
        'full_name': 'Dr. Alan Turing',
        'phone': '+44 1625 123456',
        'secondary_phone': '+44 1625 999999',
        'email': 'alan.turing@manchester.ac.uk',
        'company': 'University of Manchester',
        'job_title': 'Reader in Mathematics',
        'address': 'Wilmslow',
        'city': 'Manchester',
        'category': 'Work',
        'notes': 'Father of modern computing',
        'is_favorite': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dr. Alan Turing" in response.data
    assert b"added successfully!" in response.data

def test_create_contact_validation_failure(auth_client):
    """Verify validation when required phone number is missing."""
    response = auth_client.post('/contacts/new', data={
        'full_name': 'No Phone Person',
        'phone': '',  # Missing required phone
        'category': 'Other'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Primary phone number is required" in response.data

def test_edit_contact(auth_client):
    """Verify updating existing contact fields."""
    # First, create a contact
    auth_client.post('/contacts/new', data={
        'full_name': 'Original Name',
        'phone': '1111111111',
        'category': 'Personal'
    }, follow_redirects=True)

    # Edit contact id 1
    response = auth_client.post('/contacts/1/edit', data={
        'full_name': 'Updated Name',
        'phone': '2222222222',
        'category': 'Work',
        'city': 'New City'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Updated Name" in response.data
    assert b"2222222222" in response.data

def test_delete_contact(auth_client):
    """Verify deleting a contact permanently."""
    # Create contact
    auth_client.post('/contacts/new', data={
        'full_name': 'To Be Deleted',
        'phone': '9998887776',
        'category': 'Other'
    }, follow_redirects=True)

    # Delete contact
    response = auth_client.post('/contacts/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b"permanently deleted" in response.data

    # Query contacts list again: now the flash is cleared and contact is gone
    subsequent_res = auth_client.get('/contacts')
    assert b"To Be Deleted" not in subsequent_res.data

def test_toggle_favorite(auth_client):
    """Verify toggling favorite status."""
    auth_client.post('/contacts/new', data={
        'full_name': 'Star Contact',
        'phone': '5555555555',
        'category': 'Friends'
    }, follow_redirects=True)

    # Toggle to favorite
    response = auth_client.post('/contacts/1/toggle-favorite', headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['is_favorite'] == 1

def test_search_and_filter(auth_client):
    """Verify search query and category filtering."""
    # Add two contacts in different categories (following redirect so flash is consumed)
    auth_client.post('/contacts/new', data={'full_name': 'DevOps Specialist', 'phone': '101', 'category': 'Work'}, follow_redirects=True)
    auth_client.post('/contacts/new', data={'full_name': 'Cousin John', 'phone': '102', 'category': 'Family'}, follow_redirects=True)

    # Search for DevOps
    res_search = auth_client.get('/contacts?q=DevOps')
    assert b"DevOps Specialist" in res_search.data
    assert b"Cousin John" not in res_search.data

    # Filter by Family
    res_cat = auth_client.get('/contacts?category=Family')
    assert b"Cousin John" in res_cat.data
    assert b"DevOps Specialist" not in res_cat.data

def test_strict_user_isolation(client):
    """Verify that User 2 (Bob) cannot view, edit, or delete User 1's (Alice's) contact."""
    # Alice (user_id=1) creates a secret contact and follows redirect
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = "Alice Smith"
        sess['user_email'] = "alice@test.local"

    client.post('/contacts/new', data={
        'full_name': 'Alice Confidential Contact',
        'phone': '+1 800 000 0001',
        'category': 'Work'
    }, follow_redirects=True)

    # Now Alice logs out / Bob logs in with clean session
    with client.session_transaction() as sess:
        sess.clear()
        sess['user_id'] = 2
        sess['user_name'] = "Bob Jones"
        sess['user_email'] = "bob@test.local"

    # Bob lists contacts: must not see Alice's contact
    res_list = client.get('/contacts')
    assert b"Alice Confidential Contact" not in res_list.data

    # Bob attempts direct access to Alice's contact id 1
    res_detail = client.get('/contacts/1', follow_redirects=True)
    assert b"access denied" in res_detail.data.lower() or b"not found" in res_detail.data.lower()
    assert b"Alice Confidential Contact" not in res_detail.data

    # Bob attempts to edit Alice's contact id 1
    res_edit = client.post('/contacts/1/edit', data={
        'full_name': 'Hacked By Bob',
        'phone': '0000000000',
        'category': 'Work'
    }, follow_redirects=True)
    assert b"access denied" in res_edit.data.lower() or b"not found" in res_edit.data.lower()

    # Bob attempts to delete Alice's contact id 1
    res_del = client.post('/contacts/1/delete', follow_redirects=True)
    assert b"access denied" in res_del.data.lower() or b"not found" in res_del.data.lower()
