from flask import Flask, jsonify, request
import requests
import os
import time

app = Flask(__name__)

# Server URLs (will be set based on environment)
CATALOG_SERVER = os.getenv('CATALOG_REPLICAS', ['http://localhost:5001']).split(',')
last_catalog_server=0
ORDER_REPLICAS = os.getenv('ORDER_REPLICAS',['http://localhost:5002']).split(',')
last_order_server=0

CACHE = {}
ID_TO_KEYS = {}

CACHE_EXPIRY_SECONDS = 60  # optional: entries expire after 60 seconds

def get_from_cache(key):
    print(f'Get {key} from cache')
    entry = CACHE.get(key)
    if entry:
        if time.time() - entry["timestamp"] < CACHE_EXPIRY_SECONDS:
            return entry["value"]
        else:
            del CACHE[key]  # expired
    return None

def add_to_cache(key, value, book_ids):
    print(f'Add {key} to cache')
    CACHE[key] = {"value": value, "timestamp": time.time()}
    for book_id in book_ids:
        if book_id not in ID_TO_KEYS:
            ID_TO_KEYS[book_id] = set()
        ID_TO_KEYS[book_id].add(key)

def invalidate_cache_for_id(book_id):
    print(f'Invlidated cache for{book_id}')
    keys = ID_TO_KEYS.pop(book_id, set())
    for key in keys:
        if key in CACHE:
            del CACHE[key]
@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    cache_key = f"search:{topic}"
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return jsonify(cached_result)
    global last_catalog_server
    last_catalog_server = (last_catalog_server+1) % len(CATALOG_SERVER)
    response = requests.get(f'{CATALOG_SERVER[last_catalog_server]}/search/{topic}')
    if response.status_code == 200:
        books = response.json()
        book_ids = [book["id"] for book in books]
        add_to_cache(cache_key, books, book_ids)
        return jsonify(books)
    return jsonify({"error": "Failed to search"}), 500

@app.route('/info/<int:item_number>', methods=['GET'])
def info(item_number):
    cache_key = f"info:{item_number}"
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return jsonify(cached_result)
    
    global last_catalog_server
    last_catalog_server = (last_catalog_server+1) % len(CATALOG_SERVER)
    response = requests.get(f'{CATALOG_SERVER[last_catalog_server]}/info/{item_number}')
    if response.status_code == 200:
        book = response.json()
        add_to_cache(cache_key, book, [item_number])
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route('/purchase/<int:item_number>', methods=['POST'])
def purchase(item_number):
    global last_order_server
    last_order_server = (last_order_server + 1) % len(ORDER_REPLICAS)
    response = requests.post(f'{ORDER_REPLICAS[last_order_server]}/purchase/{item_number}')
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({"error": "Purchase failed"}), 400

@app.route('/invalidate/<int:item_number>', methods=['POST'])
def invalidate(item_number):
    invalidate_cache_for_id(item_number)
    return jsonify({"status": f"Cache invalidated for book ID {item_number}."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
