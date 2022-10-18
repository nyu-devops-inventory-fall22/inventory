"""
My Service

Describe what your service does here
"""

from logging import raiseExceptions
from flask import Flask, jsonify, request, url_for, make_response, abort
from .common import status  # HTTP Status Codes
from service.models import Inventory
from datetime import datetime


# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Inventory.init_db(app)

@app.route("/inventory-records/<product_id>", methods=["GET"])
def get_inventory_records(product_id):
    """
    Retrieve a single record
    This endpoint will return a record based on it's product id and condition
    """
    #fetch the condition from the payload of the data
    app.logger.info("Reading the given record")
    check_content_type("application/json")
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    product = inventory.find((inventory.product_id,inventory.condition))

    if not product : 
         abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()),status.HTTP_200_OK

@app.route("/inventory-records", methods=["POST"])
def create_inventory_records():
    """
    Creates inventory record
    This end point will create an inventory record and store it in the database based on user input in the body
    """
    app.logger.info("Request to create a record")
    check_content_type("application/json")
    inventory = Inventory()
    inventory.deserialize(request.get_json())

    product=inventory.find((inventory.product_id,inventory.condition))
    if product:
        abort(status.HTTP_409_CONFLICT, f"Product with id '{inventory.product_id}' and condition '{inventory.condition} 'already exists.")

    inventory.create()
    location_url = url_for("get_inventory_records", product_id=inventory.product_id, _external=True)

    app.logger.info(f"Inventory product with ID {inventory.product_id} and condition: {inventory.condition} created.")
    #return jsonify(inventory.serialize()), status.HTTP_201_CREATED
    return jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}
    

@app.route("/inventory-records", methods=["GET"])
def list_inventory_records():
    """Returns all of the Inventory records"""
    app.logger.info("Request list of inventory records")
    records = Inventory.all()
    results = [record.serialize() for record in records]
    app.logger.info("Returning %d inventory records", len(results))
    return jsonify(results), status.HTTP_200_OK

@app.route("/inventory-records/<product_id>", methods=["DELETE"])
def delete_inventory_record(product_id):
    """Deletes inventory record

    @param: product_id is the id of the record that is to be deleted
    """
    app.logger.info("Request to delete inventory record with id: %s", product_id)
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory_record = inventory.find((inventory.product_id, inventory.condition))
    app.logger.info(f"For the provided id, Inventory Record returned is: {inventory_record}")

    if inventory_record:
        inventory_record.delete()
    else:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    
    app.logger.info(f"Inventory record with ID {product_id} delete complete.")
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
