
from flask import Flask, render_template, jsonify, request, session

APP_VERSION = "1.0.5"

app = Flask(__name__, template_folder="templates")

# Development secret key. Change this before production deployment.
app.secret_key = "change-this-to-a-long-random-secret-key"

# Product catalogue
products = [
    {
        "id": 1,
        "name": "Premium Laptop",
        "category": "Electronics",
        "price": 3000.00,
        "description": "High-performance laptop for work and entertainment.",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=700",
        "rating": 4.8
    },
    {
        "id": 2,
        "name": "Smartphone",
        "category": "Electronics",
        "price": 450.00,
        "description": "Modern smartphone with an excellent display.",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=700",
        "rating": 4.6
    },
    {
        "id": 3,
        "name": "Wireless Headphones",
        "category": "Accessories",
        "price": 80.00,
        "description": "Comfortable wireless headphones with clear sound.",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=700",
        "rating": 4.7
    },
    {
        "id": 4,
        "name": "Smart Watch",
        "category": "Accessories",
        "price": 120.00,
        "description": "Track your daily activity and notifications.",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=700",
        "rating": 4.5
    },
    {
        "id": 5,
        "name": "Digital Camera",
        "category": "Electronics",
        "price": 550.00,
        "description": "Capture high-quality photographs and videos.",
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=700",
        "rating": 4.9
    },
    {
        "id": 6,
        "name": "Running Shoes",
        "category": "Fashion",
        "price": 95.00,
        "description": "Lightweight shoes designed for everyday comfort.",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=700",
        "rating": 4.6
    },
    {
        "id": 7,
        "name": "Travel Backpack",
        "category": "Fashion",
        "price": 65.00,
        "description": "Spacious backpack for travel and everyday use.",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=700",
        "rating": 4.4
    },
    {
        "id": 8,
        "name": "Gaming Keyboard",
        "category": "Accessories",
        "price": 110.00,
        "description": "Responsive keyboard for gaming and productivity.",
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=700",
        "rating": 4.7
    }
]


# Helper function: Find product by ID
def find_product(product_id):
    return next(
        (p for p in products if p["id"] == product_id),
        None
    )


# Helper function: Prepare shopping cart data
def get_cart_data():
    cart = session.get("cart", {})
    items = []
    total = 0
    total_count = 0

    for product_id, quantity in cart.items():
        product = find_product(int(product_id))

        if product:
            item_total = product["price"] * quantity

            items.append({
                **product,
                "quantity": quantity,
                "item_total": round(item_total, 2)
            })

            total += item_total
            total_count += quantity

    return {
        "items": items,
        "total": round(total, 2),
        "total_count": total_count
    }


# Homepage
@app.route("/")
def home():
    return render_template("Shopzone.html", products=products)


# Product API
@app.route("/api/products")
def get_products():
    return jsonify(products)


# Health check
@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


# Application version
@app.route("/api/version")
def get_version():
    return jsonify({
        "application": "Modern Shop",
        "version": APP_VERSION
    })


# Get shopping cart
@app.route("/api/cart")
def get_cart():
    return jsonify(get_cart_data())


# Add product to cart
@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    data = request.get_json(silent=True) or {}

    try:
        product_id = int(data.get("id", 0))
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid product or quantity"}), 400

    product = find_product(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    if quantity < 1 or quantity > 99:
        return jsonify({"error": "Quantity must be between 1 and 99"}), 400

    cart = session.get("cart", {})
    key = str(product_id)

    new_quantity = cart.get(key, 0) + quantity

    if new_quantity > 99:
        return jsonify({"error": "Maximum quantity is 99"}), 400

    cart[key] = new_quantity
    session["cart"] = cart

    return jsonify({
        "message": "Product added successfully",
        "cart": get_cart_data()
    })


# Update product quantity
@app.route("/api/cart/update", methods=["POST"])
def update_cart():
    data = request.get_json(silent=True) or {}

    try:
        product_id = int(data.get("id", 0))
        quantity = int(data.get("quantity", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input"}), 400

    cart = session.get("cart", {})
    key = str(product_id)

    if not find_product(product_id):
        return jsonify({"error": "Product not found"}), 404

    if quantity < 0 or quantity > 99:
        return jsonify({"error": "Invalid quantity"}), 400

    if quantity == 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    session["cart"] = cart

    return jsonify(get_cart_data())


# Remove product from cart
@app.route("/api/cart/remove", methods=["POST"])
def remove_from_cart():
    data = request.get_json(silent=True) or {}

    try:
        product_id = int(data.get("id", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid product ID"}), 400

    cart = session.get("cart", {})
    cart.pop(str(product_id), None)

    session["cart"] = cart

    return jsonify(get_cart_data())


# Demo checkout
@app.route("/api/checkout", methods=["POST"])
def checkout():
    cart_data = get_cart_data()

    if not cart_data["items"]:
        return jsonify({"error": "Your cart is empty"}), 400

    # Demonstration only: no real payment is collected.
    order = {
        "message": "Your demo order was placed successfully!",
        "total": cart_data["total"],
        "items": cart_data["items"]
    }

    session["cart"] = {}

    return jsonify(order)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
