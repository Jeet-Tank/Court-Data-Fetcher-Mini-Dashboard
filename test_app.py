import pytest
from driver import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # disable CSRF for testing
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Case Type" in response.data
    assert b"Case Number" in response.data

def test_invalid_form_submission(client):
    # Submit with missing data (empty form)
    response = client.post('/get_case', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error in Case Type" in response.data

def test_valid_form_submission(monkeypatch, client):
    # Patch fetch_case_data to return dummy data
    def fake_fetch_case_data(case_type, case_number, case_year, flash=None):
        return (
            {
                "number": "123456",
                "status": "PENDING",
                "petitioner": "John Doe",
                "respondent": "Jane Smith",
                "next_date": "01/01/2025",
                "last_date": "01/02/2025",
                "order_documents": ["order1.pdf"],
                "order_dates": ["2025-01-01"]
            },
            "<html></html>"  # mock HTML
        )
    monkeypatch.setattr("scraper.fetch_case_data", fake_fetch_case_data)

    data = {
        "case_type": "W.P.(C)",
        "case_number": 1234,
        "year": "2023",
        "submit": True
    }
    response = client.post('/get_case', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Petitioner" in response.data
    assert b"Download Order" in response.data

def test_download_route_missing_file(client):
    response = client.get('/download')
    assert response.status_code == 400
    assert b"No file URL provided" in response.data
