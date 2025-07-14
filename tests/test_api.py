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
        response = self.client.post('/analyze/', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'parsed_data': [
                {
                    'paragraphIndex': 0,
                    'sentenceIndex': 0,
                    'text': 'People always act like everything is either good or bad.',
                    'charStart': 0,
                    'charEnd': 55
                },
                {
                    'paragraphIndex': 0,
                    'sentenceIndex': 1,
                    'text': 'That’s just not true.',
                    'charStart': 57,
                    'charEnd': 77
                },
                {
                    'paragraphIndex': 0,
                    'sentenceIndex': 2,
                    'text': 'We must be prepared, or we will face terrible consequences.',
                    'charStart': 79,
                    'charEnd': 137
                },
                {
                    'paragraphIndex': 0,
                    'sentenceIndex': 3,
                    'text': 'Are you ready to lose everything?',
                    'charStart': 139,
                    'charEnd': 171
                },
                {
                    'paragraphIndex': 1,
                    'sentenceIndex': 0,
                    'text': 'Some experts suggest waiting.',
                    'charStart': 174,
                    'charEnd': 202
                },
                {
                    'paragraphIndex': 1,
                    'sentenceIndex': 1,
                    'text': 'Others believe action is needed now.',
                    'charStart': 204,
                    'charEnd': 239
                },
                {
                    'paragraphIndex': 1,
                    'sentenceIndex': 2,
                    'text': 'Either you’re with us, or against us.',
                    'charStart': 241,
                    'charEnd': 277
                }
            ]
        })

    def test_analyze_validation_error(self):
        response = self.client.post('/analyze/', json={})
        self.assertEqual(response.status_code, 422)
        self.assertIn('detail', response.json())


if __name__ == '__main__':
    unittest.main()
