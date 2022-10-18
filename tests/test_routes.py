"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
from cgi import test
import os
import logging
import random
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app, routes
from service.models import Inventory, db, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory-records"
######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventory(TestCase):
    """ Test Cases for Inventory Routes """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        #set up the connection with the database
        init_db(app)
        

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def _create_inventory_records(self, count):
        """Factory method to create inventory records in bulk"""
        records = []
        for _ in range(count):
            test_record = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_record.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            records.append(test_record)
        return records

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_inventory_records(self):
        """ Test Create Products """
        test_record = InventoryFactory()
        logging.debug("Test Inventory Records: %s", test_record.serialize())
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_record = response.get_json()
        self.assertEqual(new_record["product_id"], test_record.product_id)
        self.assertEqual(new_record["name"], test_record.name)
        self.assertEqual(new_record["condition"], test_record.condition.value)
        self.assertEqual(new_record["quantity"], test_record.quantity)
        self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        self.assertEqual(new_record["restock_level"], test_record.restock_level)

        #uncomment this once list all products works
        #Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_record = response.get_json()
        #self.assertEqual(new_record["id"], test_record.id)
        # self.assertEqual(new_record["name"], test_record.name)
        # self.assertEqual(new_record["condition"], test_record.condition.value)
        # self.assertEqual(new_record["quantity"], test_record.quantity)
        # self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        # self.assertEqual(new_record["restock_level"], test_record.restock_level)

    def test_create_alreadyexists_record(self):
        """Test if a record already exists"""
        
        test_record = InventoryFactory()
        logging.debug("New Inventory Record: %s", test_record.serialize())
        
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

       # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_record = response.get_json()
        self.assertEqual(new_record["product_id"], test_record.product_id)
        self.assertEqual(new_record["name"], test_record.name)
        self.assertEqual(new_record["condition"], test_record.condition.value)
        self.assertEqual(new_record["quantity"], test_record.quantity)
        self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        self.assertEqual(new_record["restock_level"], test_record.restock_level)

        # Create a new record with the same data values as just inserted into the database, this should return a 409 conflict
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_record_invalid_content_type(self):
        """Test if the user input is of invalid content type"""
        
        input_data = {
            "id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
            }
        
        logging.debug("New Inventory Record: %s", input_data)
        
        #this will test when a json is passed by cannot be parsed
        response = self.client.post(BASE_URL, data=input_data)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        #this will test when a string is passed which has invalid request headers
        response = self.client.post(BASE_URL, data="1")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_delete_inventory_record_success(self):
        """Test to check if it deletes an inventory record"""
        test_inventory_record = self._create_inventory_records(1)[0]

        response = self.client.get(f"{BASE_URL}/{test_inventory_record.product_id}", json=test_inventory_record.serialize())
        # check if record was created successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f"{BASE_URL}/{test_inventory_record.product_id}", json=test_inventory_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_inventory_record.product_id}", json=test_inventory_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_inventory_record_exception(self):
        """Test to check if code handles non-existent record"""
        SAMPLE_PRODUCT_ID = -999
        test_inventory_record = InventoryFactory()
        test_inventory_record.product_id = SAMPLE_PRODUCT_ID

        response = self.client.delete(f"{BASE_URL}/{SAMPLE_PRODUCT_ID}", json=test_inventory_record.serialize())
        # specified product shouldnt exist already
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_list_inventory_records(self):
        expected_records = self._create_inventory_records(5)
        expected_response = [record.serialize() for record in expected_records]
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
        self.assertCountEqual(expected_response, data)

    # Test to update non-existent inventory records
    def test_update_non_existent_inventory_records(self):
        test_record = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))
        data = response.get_json()
        # increment product_id so that query searches for a different product_id
        data['product_id'] += 1
        response = self.client.put("{}/{}/{}".format(BASE_URL, data['product_id'], data['condition']), json=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # Test to update existing inventory records with random valid values
    def test_update_inventory_records(self):
        # Create a test record
        test_record = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))

        # Get record as JSON
        data = response.get_json()
        logging.debug(data)
        fields = ['quantity', 'restock_level', 'reorder_quantity']
        quantities = [10, 15, 20]
        restock_levels = [1, 2, 3]

        """ Randomly select any 2 fields and update them """
        # Select 1st field
        field1 = random.choice(fields)
        logging.debug('Field selected for update: %s', field1)
        if field1 == 'quantity' or field1 == 'reorder_quantity':
            logging.debug('Old value = %d', data[field1])
            qset = set(quantities)
            qset.remove(data[field1])
            data[field1] = random.choice(list(qset))
            logging.debug('New value = %d', data[field1])
        elif field1 == 'restock_level':
            logging.debug('Old value = %d', data[field1])
            rlset = set(restock_levels)
            rlset.remove(data[field1])
            data[field1] = random.choice(list(set(rlset)))
            logging.debug('New value = %d', data[field1])
        elif field1 == 'active':
            logging.debug('Old value = %r', data[field1])
            data[field1] = not data[field1]
            logging.debug('New value = %r', data[field1])

        # Remove selected field
        fset = set(fields)
        fset.remove(field1)
        fields = list(fset)

        # Select another field
        field2 = random.choice(fields)
        if field2 == 'quantity' or field2 == 'reorder_quantity':
            logging.debug('Old value = %d', data[field2])
            qset = set(quantities)
            qset.remove(data[field2])
            data[field2] = random.choice(list(qset))
            logging.debug('New value = %d', data[field2])
        elif field2 == 'restock_level':
            logging.debug('Old value = %d', data[field2])
            qset = set(quantities)
            rlset = set(restock_levels)
            rlset.remove(data[field2])
            data[field2] = random.choice(list(rlset))
            logging.debug('New value = %d', data[field2])
        elif field2 == 'active':
            logging.debug('Old value = %r', data[field2])
            data[field2] = not data[field2]
            logging.debug('New value = %r', data[field2])

        # Make call to update record
        response = self.client.put("{}/{}/{}".format(BASE_URL, data['product_id'], data['condition']), json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_record = response.get_json()
        self.assertEqual(updated_record[field1], data[field1])
        self.assertEqual(updated_record[field2], data[field2])

    # Test to attempt update with invalid values
    def test_attempt_incorrect_value_update(self):
        """Test to check if a record gets updated with an invalid value for a particular field"""
        test_record = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))

        # Get record as JSON
        data = response.get_json()
        logging.debug(data)
        data['quantity'] = '100'
        response = self.client.put("{}/{}/{}".format(BASE_URL, data['product_id'], data['condition']), json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json(), {"Result": "Invalid request"})
        data['quantity'] = 20
        data['reorder_quantity'] = '200'
        response = self.client.put("{}/{}/{}".format(BASE_URL, data['product_id'], data['condition']), json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json(), {"Result": "Invalid request"})
        data['reorder_quantity'] = 10
        data['restock_level'] = '3'
        response = self.client.put("{}/{}/{}".format(BASE_URL, data['product_id'], data['condition']), json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json(), {"Result": "Invalid request"})

        

           
    def test_read_records(self):
        record = self._create_inventory_records(1)[0]
        record.name = None
        record.quantity  = None
        record.reorder_quantity = None
        record.restock_level = None
        logging.debug("Test Read Records: %s", record.serialize())
        response = self.client.get(f"{BASE_URL}/{record.product_id}", json= record.serialize())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_id"], record.product_id)
        self.assertEqual(data["condition"], record.condition.value)

    def test_read_non_existent_records(self):
        record = self._create_inventory_records(1)[0]
        record.product_id = record.product_id + 1
        record.name = None
        record.quantity  = None
        record.reorder_quantity = None
        record.restock_level = None
        logging.debug("Test Read Records: %s", record.serialize())
        response = self.client.get(f"{BASE_URL}/{record.product_id}", json= record.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
