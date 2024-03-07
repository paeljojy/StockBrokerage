import unittest
from Server import Response

class ResponseObject(unittest.TestCase):
    def test_response(self):
        response = Response(0, "test_string", None)
        self.assertEqual(0, response.get_status())
        self.assertEqual("test_string", response.get_message())








if __name__ == '__main__':
    unittest.main()
