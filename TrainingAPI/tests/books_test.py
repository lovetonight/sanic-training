import sys

sys.path.append("../")
from main import app
import json
import unittest


class BooksTests(unittest.TestCase):
    """Unit testcases for REST APIs"""

    def test_get_all_books(self):
        request, response = app.test_client.get("/books")
        self.assertEqual(response.status, 200)  # Kiem tra =
        data = json.loads(response.text)
        self.assertGreaterEqual(data.get("n_books"), 0)  # Kiem tra >=
        self.assertIsInstance(
            data.get("books"), list
        )  # kiểm tra xem đối tượng có phải là một thể hiện của một lớp cụ thể hay không

    # TODO: unittest for another apis

    def test_register(self):
        user = {"username": "Trong Hoan 10", "password": "1"}
        request, response = app.test_client.post("auth/register", json=user)
        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        self.assertEqual(data["status"], "success")
        auth_token = data["token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        return headers

    def test_login(self):
        # TODO: unittest for login

        user = {"username": "Trong Hoan6", "password": "1"}
        request, response = app.test_client.post("/auth/login", json=user)
        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        self.assertEqual(data["status"], "success")
        auth_token = data["token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        return headers

    def test_create_books(self):
        # TODO: unittest for create_books
        headers = self.test_login()
        book = {
            "title": "Hoan",
            "authors": ["Hoan"],
            "description": "The test book.",
            "publisher": "2002",
        }
        request, response = app.test_client.post("/books", json=book, headers=headers)
        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        self.assertEqual(data["status"], "success")

        request, response = app.test_client.get("/books")
        data = json.loads(response.text)
        books = data["books"]
        self.assertTrue(any(b["title"] == "Hoan" for b in books))

    def test_delete_books(self):
        # TODO: unittest for delete_books
        headers = self.test_login()
        book_id = "59941373-6556-4c32-bf17-1e6883bed8da"
        request, response = app.test_client.delete(f"/books/{book_id}", headers=headers)

        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        self.assertEqual(data["status"], "success")

        request, response = app.test_client.get(f"/books/{book_id}")
        self.assertEqual(response.status, 500)

    def test_update_books(self):
        #     #TODO: unittest for update_books

        headers = self.test_login()
        update_title = "Trong Hoan"

        update_book = {"title": update_title}

        book_id = "292e0f72-d5d0-4216-95ce-bf196db17f4d"
        request, response = app.test_client.put(
            f"/books/{book_id}", json=update_book, headers=headers
        )
        self.assertEqual(response.status, 200)

        data = json.loads(response.text)
        self.assertEqual(data["status"], "success")

        request, response = app.test_client.get(f"/books/{book_id}")
        data = json.loads(response.text)
        self.assertEqual(data["title"], update_title)


if __name__ == "__main__":
    unittest.main()
