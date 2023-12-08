
import unittest
from unittest.mock import Mock
from your_module import HTTPResponseError, DataFormatError, get_field_from_json_response

class TestGetFieldFromJsonResponse(unittest.TestCase):
    def test_successful_response(self):
        # Mock a successful HTTP response
        response = Mock()
        response.ok = True
        response.json.return_value = {"field_name": "expected_data"}

        # Call the function and assert the result
        result = get_field_from_json_response(response, "field_name")
        self.assertEqual(result, "expected_data")

    def test_http_response_error(self):
        # Mock an HTTP response with an error
        response = Mock()
        response.ok = False
        response.status_code = 404
        response.text = "Not Found"

        # Call the function and assert that it raises HTTPResponseError
        with self.assertRaises(HTTPResponseError) as context:
            get_field_from_json_response(response, "field_name")

        # Assert the error message
        self.assertEqual(
            str(context.exception),
            'can not get jobs status:\n Status code: 404\nBody: Not Found'
        )

    def test_json_decode_error(self):
        # Mock an HTTP response with invalid JSON
        response = Mock()
        response.ok = True
        response.json.side_effect = JSONDecodeError("JSONDecodeError", "", 0)

        # Call the function and assert that it raises DataFormatError
        with self.assertRaises(DataFormatError) as context:
            get_field_from_json_response(response, "field_name")

        # Assert the error message
        self.assertEqual(
            str(context.exception),
            f'Can not convert to json response: {response.text}'
        )

    def test_key_error(self):
        # Mock an HTTP response with missing field_name key
        response = Mock()
        response.ok = True
        response.json.return_value = {"other_field": "value"}

        # Call the function and assert that it raises DataFormatError
        with self.assertRaises(DataFormatError) as context:
            get_field_from_json_response(response, "field_name")

        # Assert the error message
        self.assertEqual(
            str(context.exception),
            f'Required key (field_name) cannot be found: {response.text}'
        )

if __name__ == '__main__':
    unittest.main()
