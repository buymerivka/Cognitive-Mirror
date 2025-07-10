import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_analyze_success(self):
        payload = {'input_data': 'Some input text'}
        response = self.client.post('/analyze/', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'details': 'Data received successfully.'})

    def test_analyze_validation_error(self):
        response = self.client.post('/analyze/', json={})
        self.assertEqual(response.status_code, 422)
        self.assertIn('detail', response.json())


if __name__ == '__main__':
    unittest.main()
