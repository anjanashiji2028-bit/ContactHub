import io

def test_export_csv(auth_client):
    """Verify that export generates CSV containing user's contacts."""
    # Seed a contact
    auth_client.post('/contacts/new', data={
        'full_name': 'Exportable Contact',
        'phone': '9876543210',
        'email': 'exportable@test.local',
        'category': 'Work'
    })

    response = auth_client.post('/export/download', data={'category': 'all'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert 'attachment;' in response.headers['Content-Disposition']
    
    csv_text = response.data.decode('utf-8')
    assert "Exportable Contact" in csv_text
    assert "9876543210" in csv_text
    assert "Full Name" in csv_text

def test_export_isolation(client):
    """Verify CSV export contains ONLY the authenticated user's contacts."""
    # Alice adds contact
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = "Alice Smith"
    client.post('/contacts/new', data={'full_name': 'Alice Private Info', 'phone': '111111'})

    # Bob logs in and exports
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['user_name'] = "Bob Jones"
    response = client.post('/export/download', data={'category': 'all'})
    assert response.status_code == 200
    csv_text = response.data.decode('utf-8')
    assert "Alice Private Info" not in csv_text

def test_import_template_download(auth_client):
    """Verify template CSV download endpoint."""
    response = auth_client.get('/import/template')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert b"Full Name,Primary Phone" in response.data

def test_import_csv_valid_data(auth_client):
    """Verify importing contacts from a well-formed CSV file."""
    csv_content = (
        "Full Name,Primary Phone,Email,Category,City\n"
        "Grace Hopper,+1 555 4321,grace@navy.mil,Work,Arlington\n"
        "Ada Lovelace,+44 20 7946 0123,ada@math.org,Personal,London\n"
    )
    data = {
        'csv_file': (io.BytesIO(csv_content.encode('utf-8')), 'test_contacts.csv'),
        'duplicate_policy': 'skip'
    }
    response = auth_client.post('/import', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"Import completed successfully" in response.data
    assert b"Grace Hopper" in response.data
    assert b"Ada Lovelace" in response.data

def test_import_csv_duplicate_skip(auth_client):
    """Verify that duplicates are skipped when policy is 'skip'."""
    # First import
    csv_content = "Full Name,Primary Phone\nDuplicate Guy,9999999999\n"
    auth_client.post('/import', data={
        'csv_file': (io.BytesIO(csv_content.encode('utf-8')), 'first.csv'),
        'duplicate_policy': 'skip'
    }, content_type='multipart/form-data')

    # Second import with same phone
    res2 = auth_client.post('/import', data={
        'csv_file': (io.BytesIO(csv_content.encode('utf-8')), 'second.csv'),
        'duplicate_policy': 'skip'
    }, content_type='multipart/form-data', follow_redirects=True)
    assert res2.status_code == 200
    assert b"Skipped: 1" in res2.data

def test_import_csv_missing_required_columns(auth_client):
    """Verify error when CSV lacks required Full Name or Phone columns."""
    bad_csv = "RandomCol1,RandomCol2\nFoo,Bar\n"
    response = auth_client.post('/import', data={
        'csv_file': (io.BytesIO(bad_csv.encode('utf-8')), 'bad.csv'),
        'duplicate_policy': 'skip'
    }, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"must contain at least" in response.data
