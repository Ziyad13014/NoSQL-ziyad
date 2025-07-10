from flask import Flask, jsonify
import redis
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)

# Initialisation de Flask
app = Flask(__name__)

# Configuration de Redis
try:
    cache = redis.Redis(host='localhost', port=6379, password='motdepasse', decode_responses=True)
    cache.ping()
    logging.info("Connexion à Redis réussie.")
except redis.RedisError as e:
    logging.error("Erreur de connexion à Redis.", exc_info=e)
    cache = None

def get_from_cache(key):
    if not cache:
        return None
    try:
        return cache.get(key)
    except redis.RedisError as e:
        logging.error("Erreur lors de la lecture du cache.", exc_info=e)
        return None

def set_to_cache(key, value, ttl=60):
    if not cache:
        return
    try:
        cache.setex(key, ttl, value)
    except redis.RedisError as e:
        logging.error("Erreur lors de l'écriture dans le cache.", exc_info=e)

def simulate_slow_database(key):
    time.sleep(2)  # Simulation d'une base de données lente
    fake_data = {
        "foo": "valeur_de_foo",
        "bar": "valeur_de_bar"
    }
    return fake_data.get(key, f"data_pour_{key}")

@app.route('/data/<key>')
def get_data(key):
    start_time = time.time()

    value = get_from_cache(key)
    if value:
        elapsed = time.time() - start_time
        logging.info(f"Cache hit pour la clé: {key}")
        return jsonify(source="cache", data=value, response_time=elapsed)
    else:
        logging.info(f"Cache miss pour la clé: {key}. Simulation lente en cours...")
        value = simulate_slow_database(key)
        set_to_cache(key, value)
        elapsed = time.time() - start_time
        return jsonify(source="slow", data=value, response_time=elapsed)

if __name__ == '__main__':
    app.run(debug=True)
