from flask import Flask, jsonify, request
import requests
import json
import os

app = Flask(__name__)

# Catalog server URL (will be set based on environment)
CATALOG_SERVER = os.getenv('CATALOG_REPLICAS', ['http://localhost:5001']).split(',')
last_catalog_server=0
FRONTEND_SERVER = os.getenv('FRONTEND_SERVER')

ORDER_LOG = 'order_log.txt'

def log_order(order_details):
    with open(ORDER_LOG, 'a') as f:
        f.write(json.dumps(order_details) + '\n')

@app.route('/purchase/<int:item_number>', methods=['POST'])
def purchase_book(item_number):
    # First check with catalog server if book is available
    global last_catalog_server
    last_catalog_server = (last_catalog_server+1) % len(CATALOG_SERVER)

    response = requests.get(f'{CATALOG_SERVER[last_catalog_server]}/info/{item_number}')
    
    if response.status_code != 200:
        return jsonify({"error": "Book not found"}), 404
    
    book_info = response.json()
    
    if book_info["quantity"] <= 0:
        return jsonify({"error": "Book out of stock"}), 400
    
    # Update the catalog to decrement quantity
    requests.post(f'{FRONTEND_SERVER}/invalidate/{item_number}')
    print(f'invalidated {item_number}')
    update_response = requests.post(f'{CATALOG_SERVER[last_catalog_server]}/update', json={
        "id": item_number,
        "quantity": -1
    })
    
    if update_response.status_code != 200:
        return jsonify({"error": "Failed to update catalog"}), 500
    
    # Log the order
    order_details = {
        "item_number": item_number,
        "title": book_info["title"],
        "price": book_info["price"]
    }
    log_order(order_details)
    
    return jsonify({
        "success": True,
        "message": f"Purchased '{book_info['title']}' for ${book_info['price']}"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

