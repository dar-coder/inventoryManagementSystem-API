# inventoryManagementSystem-API
An inventory management system API that allows the user to buy and sell goods from/to partners by entering bills from vendors and issuing invoices to customers. The application keeps track of item information regarding item quantity and item prices (latest and average purchase and selling price). It is created using Python's Flask framework.

- Python version: 3.9.5

- Flask version: 2.0.3

- Werkzeug version: 2.0.3

The system allows creating, reading, updating and deleting data.

## 1. Usage

### 1. 1. Creating the database tables

**The database backup file for the project has already been created, and it is provided in the project folder**. However, if for some reason, the database file gets lost, simply run the "create_database.py" file in the project directory and a new (empty) database file will be created.

```bash
python create_database.py
```

### 1. 2. Starting the application
In order to be able to use the application, make sure that the dependencies provided in the "requirements.txt" file are installed on your machine.

You can start the application in one of the following 2 ways:

#### Way 1

1. Set the environment variable FLASK_APP to app.py
2. Run the application by using the "flask run" command

Examples:
- If you are using CMD
```bash
set FLASK_APP=app.py
flask run
```

- If you are using Powershell
```bash
$env:FLASK_APP = "app.py"
flask run
```

- If you are using BASH
```bash
export FLASK_APP=app.py
flask run
```

- If you are using Fish
```bash
set -x FLASK_APP app.py
flask run
```

#### Way 2

Alternatively, you can start the application by simply running the "app.py" file.

```bash
python app.py
```

### 1. 3. Endpoints
#### /
Displays the application name

#### /partners
Display list of all partners (if endpoint is accessed using a "GET" request), and inserts a new partner (if endpoint is accessed using a "POST" request).

If accessed using a "POST" request, his endpoint accepts the inputs provided through form-data that contains the following keys:

- partner_name
- partner_address
- partner_manager_first_name
- partner_manager_last_name

The partner_name and partner_address are required fields.

#### /partner/<int:partner_id>
Displays information about a partner (if endpoint is accessed by using a "GET" request);
Update information about a partner (if endpoint is accessed by using a "PUT" request);
Deletes a partner from database (if endpoint is accessed by using a "DELETE" request

The partner will not be deleted if the are bills or invoices linked to him.

#### /items
Displays a list of all items (if endpoint is accessed using a "GET" request), and inserts a new item into database (if endpoint is accessed using a "POST" request).

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the following keys:

- item_code
- item_description
- unit_id
- vat_rate_id

All of the abovementioned fields are required.

#### /item/<int:item_id>
Displays information about the desired partner (if endpoint is accessed by using a "GET" request), and deletes the item from database (if endpoint is accessed by using a "DELETE" request.

The item will not be deleted if the are bill records or invoice records linked to it.

#### /vat_rates
Displays a list of VAT rates (if endpoint is accessed by using a "GET" request), and inserts a VAT rate into database (if endpoint is accessed by using a "POST" request).

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the key "vat_rate", which is a required field.

#### /units_of_measure
Displays a list of all units of measure (if endpoint is accessed by using a "GET" request, and inserts a new unit of measure into the database (if endpoint is accessed by using a "POST" request).

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the following keys:

- unit_acronym
- unit_name

Both of the input fields are required.

#### /bills
Displays a list of all bills from partners (if endpoint is accessed by using a "GET" request), and inserts a new bill from parnter into database (if endpoint is accessed using a "POST" request

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the following keys:

- bill_number
- bill_date
- bill_due_date
- partner_id

All of the abovementioned fields are required.

The format in of the date and the due date must be dd.mm.yyyy

#### /bill_records
Displays a list of all bill_records (if endpoint is accessed by using a "GET" request, and inserts a new bill record into the database (if endpoint is accessed by using a "POST" request).

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the following keys:

- item_id
- quantity
- price
- bill_id

All of the abovementioned fields are required.

#### /invoices
Displays a list of all issued invoices (if endpoint is accessed by using a "GET" request, and inserts a new invoice into the database (if endpoint is accessed by using a "POST" request).

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the following keys:

- invoice_date
- invoice_due_date
- partner_id

All of the abovementioned fields are required.

The invoices are numbered automatically, starting with Invoice No. 00001.

The format in of the date and the due date must be dd.mm.yyyy

#### /invoice_records
Displays a list of all invoice records (if endpoint is accessed by using a "GET" request, and inserts a new invoice record in the database (if endpoint is accessed by using a "POST" request.

If accessed using a "POST" request, this endpoint accepts the inputs provided through form-data that contains the following keys:

- item_id
- quantity
- selling_price
- vat_included
- invoice_id

All of the abovementioned fields, except the "vat_included" field are required.

If the VAT is included in the selling price, the "vat_included" field must be set to 1. Otherwise, it should be set to 0 or not provided at all.
