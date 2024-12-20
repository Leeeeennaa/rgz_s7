from flask import Flask, render_template, make_response
from flask_caching import Cache
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config["CACHE_TYPE"] = "SimpleCache"
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600  
cache = Cache(app)

limiter = Limiter(
    app = app,
    key_func=get_remote_address,
    storage_uri="memory://"
)

with open("weather_data.json", "r", encoding="utf-8") as f:
    weather_data = json.load(f)
    cities = [city["city"] for city in weather_data["cities"]]

@app.errorhandler(429)
def rate_limit_exceeded(e):
    print('triggered')
    return make_response({'next_response': limiter.current_limit.reset_at}, 429)


@app.route("/")
def index():
    return render_template("index.html", cities=cities)


@app.route("/weather/<city>", methods=['GET'])
@cache.cached(query_string=True)
@limiter.limit('10/hour')
def weather(city):
    found = False
    for elem in weather_data['cities']:
        if city == elem['city']:
            response = make_response({'city': city, 'temperature': elem['temperature']}, 200)
            found = True
    if not found:
        response = make_response({'error': "Город не найден"}, 404)
    return response

if __name__ == "__main__":
    app.run()