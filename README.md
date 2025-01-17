<h1 align="center"> NYU DevOps /Inventory </h1>
<h4 align="center"> An Inventory Microservice </h4>
<p align=center>
<img src="Images/inventory.png" alt="isolated" />
</p>
<h4 align="center">


[![Build Status](https://github.com/CSCI-GA-2820-FA22-003/inventory/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-003/inventory/actions)
[![Integration Status](https://github.com/CSCI-GA-2820-FA22-003/inventory/actions/workflows/bdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-003/inventory/actions)
[![codecov](https://codecov.io/github/CSCI-GA-2820-FA22-003/inventory/branch/master/graph/badge.svg?token=Z7XPQY3G6T)](https://codecov.io/github/CSCI-GA-2820-FA22-003/inventory)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

<h4 align="center">
Inventory is a RESTFul microservice in the eCommerce application

## :star: About Us

The Inventory resource is an integral micro-service of the eCommerce application. This micro-service is used to efficiently organize and manage products in the inventory for the proper functioning of the eCommerce application.

## :mag: Overview

The project's `/service` folder contains `models.py` file for the model and `routes.py` file for the service. The `/tests` folder has `test_models.py` and `test_routes.py` to test `models.py` and `routes.py` separately. The `/tests` folder also contains `factories.py` which can be used to generate a random Inventory record.


## :computer: Setup

To run this project ensure you have [docker](https://docs.docker.com/engine/install/) installed and running in your local machine. Then clone this repository and navigate to the github repository while opening in Visual Studio Code. Then in the terminal type `flask run` and copy the HTTP URL into your web browser or use the Postman collection [here](https://drive.google.com/file/d/1wSYoq8DPg0hr0spHzS9AxRHpN-LQKhzt/view?usp=sharing) to test the application.

## :open_file_folder: Contents

The project contains the following:

```text
.gitignore          - this will ignore git files and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
├── test_routes.py  - test suite for service routes
└── factories.py    - used to generate infinite number of random inventory record
```

## :memo: Schema

Below are the attributes of the inventory table

```
- product_id: int: pk
- name: str
- condition: enum {"new", "refurbished", "return"}: pk (default: new)
- quantity: int (default: 0)
- reorder_quantity: int (default: 0)
- restock_level: int (default: 0)
- active: boolean (used to indicate soft deletes)
- created_at: datetime
- updated_at: datetime
```

## :golf: Endpoints

#### `POST /inventory`

Create an inventory record.

#### Request body
```
{
    "product_id": 2,
    "condition": "return",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
```
{
    "product_id": 2,
    "name": "laptop"
}
```
The fields `condition`, `quantity`, `reorder_quantity` and `restock_level` are optional. If not passed, they assume default values of `NEW`, `0`, `0` and `0` respectively.

#### Response
Created record
```
{
    "product_id": 2,
    "condition": "return",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
The created record is returned in the response.

#### `GET /inventory/{product_id}/{condition}`

#### Response
```
{
    "product_id": 2,
    "condition": "new",
    "name": "laptop",
    "quantity": 20,
    "reorder_quantity": 15,
    "restock_level": 3
}
```
The record that matches the keys `product_id` and `condition` is returned in the response.

#### `GET /inventory`

List all inventory records.

#### Response
```
[
    {
	"condition": "return",
	"name": "laptop",
	"product_id": 2,
	"quantity": 20,
	"reorder_quantity": 15,
	"restock_level": 3
    }
]
```
The list of inventory records is returned in the response.

#### `GET /inventory?name=<name>`

List all inventory records with name equal to the given name in the query string.

#### `GET /inventory?condition=<condition>`

List all inventory records with condition equal to the given condition in the query string.

#### `GET /inventory?active=<is_active>`

List all inventory records with active equal to the given value in the query string. Therefore if is_active is True then all inventory records which are available in the inventory will be returned. <br/> **Note**: is_active should be a boolean value.

#### `GET /inventory?quantity=<quantity>&operator=<operator>`

List all inventory records with quantity and operator in the query string. 
<br/> <br/> If you pass operator ```>``` then all inventory records having a quantity greater than quantity passed in the query string will be returned. <br/> <br/> **Note**: Possible operators are ```>```, ```<```,```>=```,```<=```,```=```. 
<br/> Any other operators will return a ```400_Bad_Request```

#### `GET /inventory?<multiple_parameters_in_query_string>`

List all inventory records that match the parameters passed in the query string.
<br/> Eg: ```GET /inventory?name="laptop"&active=NEW```. This would return all those inventory records with name as laptop and condition=NEW


#### `PUT /inventory/{product_id}`

Update an inventory record.

#### Request
```
{
    "product_id": 2,
    "condition": "new",
    "quantity": 2,
    "reorder_quantity": 1,
    "restock_level": 3
}
```
Find an inventory record by `product_id` and `condition`. The fields `quantity`, `reorder_quantity`, `restock_level` and `name` are updateable and optional.

#### Response
```
{
    "product_id": 2,
    "condition": "new",
    "name": "laptop",
    "quantity": 2,
    "reorder_quantity": 1,
    "restock_level": 3
}
```
Update the fields of existing record with the passed values. Return the updated record in the response.

#### `DELETE /inventory/{product_id}/{condition}`

Delete inventory record.

#### Response

The record that matches the keys `product_id` and `condition` returns `HTTP_204_NO_CONTENT`.
## :computer: User Interface

Our application is publicly available on http://159.122.186.89:31002.

We continue developing our application the developing application can be viewed at http://159.122.186.89:31001.

You should see the below API homepage open up.
<h4 align="center">
<p align=center>
<img src="Images/Flask-API.png" alt="isolated" />
</p>
<h4 align="center">

### Instructions on using the functionalities of the application

#### `Create an inventory Record`
1. Set the product id, condition, name, quantity as these are compulsory fields that are required.
2. Press on the Create button.
3. You should see a message Success on top of the page if the record was created and stored in the inventory.
4. To verify the data has been stored in the inventory you can place the product id and condition values in their respective fields and press the Read button. You should see all the properties of the record in their respective fields.

#### `List all records present in the inventory` 
1. Press the Clear button.
2. Press the Search button.
You should see all the records in the inventory in a tabular format at the bottom of the page.

#### `Search for a specific record whose product id and condition are known` 
1. Press the Clear button.
2. Set the product id and condition for the given record in their respective fields.
3. Press the Read button. You should see all the properties of the record in their respective fields.

#### `Search for records satisfying given properties`
1. Press the Clear button.
2. Set the values of fields on which you want to search for in the inventory.
3. Press the Search button. You should see all the records matching your search requirement in the bottom of the page.

#### `Updating a record`
1. Press the Clear button.
2. Set the value of product id and condition of the record you want to update.
3. Press the Read button to verify the properties of the record.
4. Press the Clear button.
5. Enter the product id and condition of the record you want to update. Set the values of the other fields you would like to update to.
6. Press the Update button.
7. Press the Clear button.
8. Enter the product id and condition. Press the Read button to verify the values of the fields have been updated.

#### `Checkout a record`
1. Press the Clear button.
2. Set the value of the product id and condition in their respective fields. 
3. Press the Read button.
4. Enter the quantity of the item that you would want to checkout and enter it in the Ordered Quantity field. 
5. Press the Checkout button.
6. Then you should see a message "Product has been checked out from the Inventory!" on the top of the page if the checkout was successful.
7. Press the Clear button.
8. Set the product id and condition in their respective fields.
9. Press the Read/Search button.
10. You should see the quantity field of the record updated. The quantity would be the remaining quantity of the record left in the inventory.

#### `Reorder a record`
1. Press the Clear button.
2. Set the value of the product id and condition in their respective fields. 
3. Press the Read button.
4. Enter the quantity of the item that you would want to checkout and enter it in the Ordered Quantity field. 
5. Press the Reorder button.
6. Then you should see a message "Product has been checked out from the Inventory!" on the top of the page if the checkout was successful.
7. Press the Clear button.
8. Set the product id and condition in their respective fields.
9. Press the Read/Search button.
10. You should see the quantity field of the record updated. The quantity would be the new quantity of the record present in the inventory.


## :wrench: Running Tests

Tests can be run using nosetests. Just type in `nosetests tests` in your terminal to check if all tests are being satisfied and to identify the code coverage.

## :sound: License

Licensed under the Apache License. See [LICENSE](LICENSE)

