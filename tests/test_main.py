import os
from bs4 import BeautifulSoup
from app.DataManager import DataManager
from app.open_ai_client import OpenAIClient

import uuid
import pytest

EXPECTED_NUMBER_OF_ROWS = 72

user_id = 'bd65600d-8669-4903-8a14-af88203add38'


def test_save_and_get_sets(client):
    db = DataManager()
    t_id = str(uuid.uuid4())
    ts_id = str(uuid.uuid4())

    beforeSets = len(db.get_transaction_sets_by_session(user_id=user_id))

    db.save_transaction(t_id, ts_id, user_id, "1000",
                        "2023-08-24 15:00:00", "Sample transaction", "complete")

    saved = db.get_transaction_sets_by_session(user_id=user_id)

    assert len(saved) - beforeSets == 1


def test_db_save_and_load(client):
    db = DataManager()
    t_id = str(uuid.uuid4())
    ts_id = str(uuid.uuid4())
    # user_id = str(uuid.uuid4())

    beforeSetCount = len(db.get_transaction_sets_by_session(user_id=user_id))

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

    afterSetCount = len(db.get_transaction_sets_by_session(user_id=user_id))
    assert (afterSetCount - beforeSetCount) == 1

    db.delete_transaction_set(ts_id)


def test_open_ai(client):
    db = DataManager()
    t_id = str(uuid.uuid4())
    ts_id = str(uuid.uuid4())
   # user_id = str(uuid.uuid4())

    save = db.save_transaction(t_id, ts_id, user_id, "1000",
                               "2023-08-24 15:00:00", "Grocery Shop at Countdown", "pending")

    assert save.rowcount == 1

    # transToProcess = db.get_transactions_to_process(
    # user_id=user_id, ts_id=ts_id, page=0, limit=2)
    # assert len(transToProcess) == 1

    res = client.post(
        f"/tset/{ts_id}/categorize")
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, 'html.parser')

    rows = soup.find('table').find_all('tr')

    # Here, you check that the number of rows (excluding the header) is as expected.
    # Adjust the number as necessary.
    assert len(rows) - 1 == 1

   # client.categorizeTransactions(transToProcess, overrideCategories=[])

    trans = db.get_transactions(user_id, ts_id, 0, 1000, False)

    assert len(trans) == 1
    assert trans[0][trans[0]._key_to_index['category']] == 'Groceries'


def test_read_main(client):
    response = client.get("/tset/e75a078e-67b8-4b61-9a8b-8f17ac0816a3/upload")
    assert response.status_code == 200
    assert "Submit</button>" in response.text


def test_header_save_and_get(client):
    db = DataManager()

    record = {
        "ts_id": str(uuid.uuid4()),
        "amount_head": 'Amount',
        'user_id': user_id,
        "date_head": 'Date',
        "description_head": ["Description", "OtherDescription"],
        'custom_rules': "custom_rules",
        'custom_categories': ["custom_categories", "custom_categories2", "custom_categories3"]
    }
    saveRes = db.save_header(record)

    assert saveRes == 1

    savedHeader = db.get_header(
        ts_id=record['ts_id'], user_id=record['user_id'])

    if savedHeader:
        assert str(savedHeader.ts_id) == record['ts_id']
        assert savedHeader.amount_head == 'Amount'
        assert savedHeader.date_head == 'Date'
        assert savedHeader.description_head == record["description_head"]
        assert savedHeader.custom_rules == 'custom_rules'
        assert savedHeader.custom_categories == record["custom_categories"]

    else:
        raise "Should save header"


def test_file_upload_and_save(client):
    ts_id = str(uuid.uuid4())

    response = client.get(f"/tset/{ts_id}/upload")

    path = os.path.join(os.getcwd(), 'tests/test_upload_1.csv')
    print(path)
    with open(path, 'rb') as test_file:
        # replace 'file_field_name' with the input name for your file field
        files = {'bank_csv': test_file}
        response = client.post(
            f"/tset/{ts_id}/upload", files=files)

    assert response.status_code == 200

    savedTransactions = client.get(
        f"/tset/{ts_id}")

    soup = BeautifulSoup(savedTransactions.text, 'html.parser')

    rows = soup.find('table').find_all('tr')

    # Here, you check that the number of rows (excluding the header) is as expected.
    # Adjust the number as necessary.
    assert len(rows) - 1 == EXPECTED_NUMBER_OF_ROWS

    assert "<table>" in response.text

    db = DataManager()
    db.delete_transaction_set(ts_id)
