import unittest

from shopzone import app


class TestShopzoneApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint_returns_healthy(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "healthy"})

    def test_products_endpoint_returns_catalog(self):
        response = self.client.get("/api/products")
        products = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(products)
        self.assertEqual(products[0]["id"], 1)

    def test_add_to_cart_accumulates_quantity_and_total(self):
        product = self.client.get("/api/products").get_json()[0]
        self.client.post("/api/cart/add", json={"id": 1, "quantity": 2})
        response = self.client.post(
            "/api/cart/add",
            json={"id": 1, "quantity": 1},
        )

        self.assertEqual(response.status_code, 200)
        cart = response.get_json()["cart"]
        self.assertEqual(cart["total_count"], 3)
        self.assertEqual(cart["total"], product["price"] * 3)
        self.assertEqual(cart["items"][0]["quantity"], 3)

    def test_add_to_cart_rejects_invalid_quantity(self):
        response = self.client.post(
            "/api/cart/add",
            json={"id": 1, "quantity": 0},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_add_to_cart_rejects_unknown_product(self):
        response = self.client.post(
            "/api/cart/add",
            json={"id": 999, "quantity": 1},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Product not found")

    def test_updating_quantity_to_zero_removes_cart_item(self):
        self.client.post("/api/cart/add", json={"id": 1})
        response = self.client.post(
            "/api/cart/update",
            json={"id": 1, "quantity": 0},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["items"], [])
        self.assertEqual(response.get_json()["total_count"], 0)

    def test_checkout_clears_cart(self):
        product = self.client.get("/api/products").get_json()[0]
        self.client.post("/api/cart/add", json={"id": 1})

        checkout_response = self.client.post("/api/checkout")
        cart_response = self.client.get("/api/cart")

        self.assertEqual(checkout_response.status_code, 200)
        self.assertEqual(checkout_response.get_json()["total"], product["price"])
        self.assertEqual(cart_response.get_json()["items"], [])

    def test_checkout_rejects_empty_cart(self):
        response = self.client.post("/api/checkout")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Your cart is empty")


if __name__ == "__main__":
    unittest.main()
