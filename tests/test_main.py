import os


def test_read_main(client):
    response = client.get("/tset/e75a078e-67b8-4b61-9a8b-8f17ac0816a3/upload")
    assert response.status_code == 200
    assert "Submit</button>" in response.text


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
