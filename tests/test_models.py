"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
from service import app
from service.models import Inventory, DataValidationError, db
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Inventory   M O D E L   T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_instantiate_inventory_record(self):
        inventory_records = Inventory.all()
        self.assertEqual(inventory_records, [])

        record = Inventory(product_id=1, name="monitor", condition=Inventory.Condition.NEW, quantity=10, reorder_quantity=20, restock_level=2)
        self.assertTrue(record is not None)
        self.assertEqual(str(record), "<Inventory %r product_id=[%d] condition=[%s]>" % ("monitor", 1, Inventory.Condition.NEW.value))
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)

    def test_inventory_serialize(self):
        record = Inventory(product_id=1, name="monitor", condition=Inventory.Condition.NEW, quantity=10, reorder_quantity=20, restock_level=2)
        actual_output = record.serialize()
        expected_output = {
            "product_id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        self.assertEqual(actual_output, expected_output)

    def test_inventory_deserialize(self):
        data = {
            "product_id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)

    def test_invalid_inventory_deserialize(self):
        data = {}
        record = Inventory()
        self.assertRaises(DataValidationError, record.deserialize, data)


    def test_read_a_record(self):
        """It should Read a Record"""
        record = InventoryFactory()
        logging.debug(record)
        record.create()
        self.assertIsNotNone(record.product_id)
        # Fetch it back
        found_record = record.find((record.product_id,record.condition))
        self.assertEqual(found_record.product_id, record.product_id)
        self.assertEqual(found_record.condition, record.condition)
    
    def test_delete_a_record(self):
        """Test to check if record is deleted"""
        inventory_record = InventoryFactory()
        inventory_record.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory_record and make sure it isn't in the database
        inventory_record.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_update_a_record(self):
        """It should Update a Record"""
        record = InventoryFactory()
        logging.debug(record)
        record.create()
        self.assertIsNotNone(record.product_id)
        # Change it an save it
        record.reorder_quantity = 15
        record.quantity = 10
        record.restock_level = 2
        original_id = record.product_id
        record.update()
        self.assertEqual(record.product_id, original_id)
        self.assertEqual(record.reorder_quantity, 15)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.restock_level, 2)
        records = Inventory.all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].product_id, original_id)
        self.assertEqual(records[0].reorder_quantity, 15)
        self.assertEqual(records[0].quantity, 10)
        self.assertEqual(records[0].restock_level, 2)
