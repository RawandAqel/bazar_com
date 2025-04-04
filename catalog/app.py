from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Initialize catalog data
CATALOG_FILE = 'catalog_data.json'

def load_catalog():
    if not os.path.exists(CATALOG_FILE):
        # Initial catalog data
        catalog = {
            "books": [
                {
                    "id": 1,
                    "title": "How to get a good grade in DOS in 40 minutes a day",
                    "topic": "distributed systems",
                    "quantity": 10,
                    "price": 40
                },
                {
                    "id": 2,
                    "title": "RPCs for Noobs",
                    "topic": "distributed systems",
                    "quantity": 5,
                    "price": 50
                },
                {
                    "id": 3,
                    "title": "Xen and the Art of Surviving Undergraduate School",
                    "topic": "undergraduate school",
                    "quantity": 8,
                    "price": 30
                },
                {
                    "id": 4,
                    "title": "Cooking for the Impatient Undergrad",
                    "topic": "undergraduate school",
                    "quantity": 3,
                    "price": 25
                }
            ]
        }
        with open(CATALOG_FILE, 'w') as f:
            json.dump(catalog, f)
    else:
        with open(CATALOG_FILE, 'r') as f:
            catalog = json.load(f)
    return catalog

def save_catalog(catalog):
    with open(CATALOG_FILE, 'w') as f:
        json.dump(catalog, f)

@app.route('/search/<topic>', methods=['GET'])
def search_by_topic(topic):
    catalog = load_catalog()
    books = [{"id": book["id"], "title": book["title"]} 
             for book in catalog["books"] if book["topic"] == topic]
    return jsonify(books)

@app.route('/info/<int:item_number>', methods=['GET'])
def get_book_info(item_number):
    catalog = load_catalog()
    book = next((book for book in catalog["books"] if book["id"] == item_number), None)
    if book:
        return jsonify({
            "title": book["title"],
            "quantity": book["quantity"],
            "price": book["price"]
        })
    return jsonify({"error": "Book not found"}), 404

@app.route('/update', methods=['POST'])
def update_book():
    data = request.get_json()
    catalog = load_catalog()
    
    for book in catalog["books"]:
        if book["id"] == data["id"]:
            if "price" in data:
                book["price"] = data["price"]
            if "quantity" in data:
                book["quantity"] += data["quantity"]  # Can be positive or negative
            save_catalog(catalog)
            return jsonify({"success": True})
    
    return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)