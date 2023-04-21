import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
app.app_context().push()
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()

    # Imidiately return if drink list empty.
    if len(drinks) == 0:
        abort(404)

    # Get drink short info
    drinks = [drink.short() for drink in drinks]

    return jsonify({
        "success": True, 
        "drinks": drinks
    })

'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.order_by(Drink.id).all()

    # Imidiately return if drink list empty.
    if len(drinks) == 0:
        abort(404)

    # Get drink detail info
    drinks = [drink.long() for drink in drinks]
    
    return jsonify({
        "success": True, 
        "drinks": drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_new_drink(jwt):
    body = request.get_json()

    # Prepare data for the new drink
    drinkTitle = body.get("title", None)
    drinkRecipe = body.get("recipe", None)

    try:
        new_drink = Drink (title = drinkTitle, 
                           recipe = json.dumps(drinkRecipe))

        # Insert new drink to database
        new_drink.insert()

        return jsonify({
            "success": True, 
            "drinks": new_drink.long()
        })

    except:
        db.session.rollback()
        abort(422) # Un Processable


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def modify_drink(jwt, id):
    body = request.get_json()

    # Get update info from UI
    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    # Imidiately return if new drink input invalid.
    if (new_title is None) and (new_recipe is None):
        abort(400) # bad request

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404) # Drink not found

        # Update drink info
        drink.title = new_title
        drink.recipe = json.dumps(new_recipe)

        return jsonify({
            "success": True, 
            "drinks": drink.long()
        })

    except:
        db.session.rollback()
        abort(422) # Un Processable

'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def remove_drink(jwt, id):
    try:
        # Get drink that has drink id = id
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404) # Drink not found

        # Delete the selected drink 
        drink.delete()

        return jsonify({
            "success": True, 
            "delete": id
        })

    except:
        db.session.rollback()
        abort(422) # Un Processable

# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, 
        "message": "bad request"
        }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False, 
        "error": 500, 
        "message": "internal server error"
    }), 500

@app.errorhandler(AuthError)
def authorization_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
