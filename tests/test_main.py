import os
from bs4 import BeautifulSoup
from app.DataManager import DataManager
import uuid
import pytest

EXPECTED_NUMBER_OF_ROWS = 72


def test_save_and_get_sets(client):
    db = DataManager()
    t_id = str(uuid.uuid4())
    ts_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    db.save_transaction(t_id, ts_id, user_id, "1000",
                        "2023-08-24 15:00:00", "Sample transaction", "complete")

    saved = db.get_transaction_sets_by_session(user_id=user_id)

    assert len(saved) == 1


def test_db_save_and_load(client):
    db = DataManager()
    t_id = str(uuid.uuid4())
    ts_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    db.save_transaction(t_id, ts_id, user_id, "1000",
                        "2023-08-24 15:00:00", "Sample transaction", "complete")

    t_id2 = str(uuid.uuid4())
    db.save_transaction(t_id2, ts_id, user_id, "1000",
                        "24/08/2023", "Sample transaction with weird date", "complete")

    t_id3 = str(uuid.uuid4())
    db.save_transaction(t_id=t_id3, ts_id=ts_id, user_id=user_id, amount=float('1000'),
                        date="24/08/2023", description="Sample transaction with named params", status='pending')

    res = db.get_transactions(user_id, ts_id, 0, 1000, False)

    assert len(res) == 3
    assert str(res[0][0]) == t_id
    assert str(res[0][1]) == ts_id
    assert str(res[0][2]) == user_id

    allSets = db.get_transaction_sets_by_session(user_id=user_id)
    assert len(allSets) == 1


def test_read_main(client):
    response = client.get("/tset/e75a078e-67b8-4b61-9a8b-8f17ac0816a3/upload")
    assert response.status_code == 200
    assert "Submit</button>" in response.text


@pytest.mark.skip()
def test_file_upload_and_save(client):
    response = client.get("/tset/e75a078e-67b8-4b61-9a8b-8f17ac0816a3/upload")

    path = os.path.join(os.getcwd(), 'tests/test_upload_1.csv')
    print(path)
    with open(path, 'rb') as test_file:
        # replace 'file_field_name' with the input name for your file field
        files = {'bank_csv': test_file}
        response = client.post(
            "/tset/e75a078e-67b8-4b61-9a8b-8f17ac0816a3/upload", files=files)

    assert response.status_code == 200

    savedTransactions = client.get(
        "/tset/e75a078e-67b8-4b61-9a8b-8f17ac0816a3")

    soup = BeautifulSoup(savedTransactions.text, 'html.parser')

    rows = soup.find('table').find_all('tr')

    # Here, you check that the number of rows (excluding the header) is as expected.
    # Adjust the number as necessary.
    assert len(rows) - 1 == EXPECTED_NUMBER_OF_ROWS

    assert "<table>" in response.text
