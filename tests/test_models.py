"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
from service import app
from service.models import Inventory, DataValidationError, db

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
        """ It should always be true """
        print("hello")
        inventory_records = Inventory.all()
        self.assertEqual(inventory_records, [])

        record = Inventory(name="monitor", status=Inventory.Status.NEW, quantity=10, reorder_quantity=20, restock_level=2)
        self.assertTrue(record is not None)
        self.assertEqual(str(record), "<Inventory %r id=[%s]>" % ("monitor", "None"))
        self.assertEqual(record.product_id, None)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.status.name, Inventory.Status.NEW.name)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)
