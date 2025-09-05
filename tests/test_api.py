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
        payload = {
            'input_data': 'People always act like everything is either good or bad. That’s just not true.\n'
                          'We must be prepared, or we will face terrible consequences. Are you ready to lose '
                          'everything?\n\nSome experts suggest waiting. Others believe action is needed now.\n'
                          'Either you’re with us, or against us.'}
        response = self.client.post('/analyze_manipulations/', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_analyze_validation_error(self):
        response = self.client.post('/analyze_manipulations/', json={})
        self.assertEqual(response.status_code, 422)
        self.assertIn('detail', response.json())


if __name__ == '__main__':
    unittest.main()
