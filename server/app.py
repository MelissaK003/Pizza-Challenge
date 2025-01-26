#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

#Fetch All Restaurants
@app.route("/restaurants")
def fetch_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = []

    for restaurant in restaurants:
        restaurant_list.append({
            'address':restaurant.address,
            'id':restaurant.id,
            'name':restaurant.name,
        })

    return (restaurant_list)

#Fetch Restaurants by id 
@app.route("/restaurants/<int:restaurant_id>", methods=["GET"])
def fetch_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)

    if restaurant is None:
        return {"error": "Restaurant not found"}, 404
    
    restaurant_list = {
            'address':restaurant.address,
            'id':restaurant.id,
            'name':restaurant.name,
            "restaurant_pizzas": [  
                {
                    "id": restaurant_pizza.id,
                    "pizza":{
                        "id": restaurant_pizza.pizza.id,
                        "ingredients": restaurant_pizza.pizza.ingredients,
                        "name": restaurant_pizza.pizza.name,
                    }
                } for restaurant_pizza in restaurant.restaurant_pizzas
            ]    
        }

    return (restaurant_list)

#Delete Restaurant
@app.route("/restaurants/<int:restaurant_id>", methods=["DELETE"])
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)

    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204 
    else:
        return {"error": "Restaurant not found"}, 404


#Fetch All Pizzas
@app.route("/pizzas")
def fetch_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = []

    for pizza in pizzas:
        pizza_list.append({
            'id':pizza.id,
            'ingredients':pizza.ingredients,
            'name':pizza.name,
        })

    return (pizza_list)

#Add Restaurant_pizza
@app.route("/restaurant_pizzas", methods=["POST"])
def add_restaurant_pizza():
    data = request.get_json()
    price = data.get('price')  
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not (1 <= price <= 30):
        return {"errors": ["validation errors"]}, 400

    check_pizza_id = Pizza.query.get(pizza_id)
    check_restaurant_id = Restaurant.query.get(restaurant_id)

    if not check_pizza_id or not check_restaurant_id:
        return {"error": "Restaurant or Pizza does not exist"}, 404

    new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(new_restaurant_pizza)
    db.session.commit()

    return {
        "id": new_restaurant_pizza.id,
        "price": new_restaurant_pizza.price,
        "pizza_id": new_restaurant_pizza.pizza_id,
        "restaurant_id": new_restaurant_pizza.restaurant_id,
        "pizza": {
            "id": new_restaurant_pizza.pizza.id,
            "name": new_restaurant_pizza.pizza.name,
            "ingredients": new_restaurant_pizza.pizza.ingredients
        },
        "restaurant": {
            "id": new_restaurant_pizza.restaurant.id,
            "name": new_restaurant_pizza.restaurant.name,
            "address": new_restaurant_pizza.restaurant.address
        }
    }, 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
