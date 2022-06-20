from flask import Flask, request, jsonify
from helpers import validate_form_fields
import sqlite3

app = Flask(__name__)

def db_connection():
    """Connect application to database"""
    
    conn = None
    try:
        conn = sqlite3.connect("database.sqlite3")
    except sqlite3.error as e:
        print(e)
    return conn


@app.route("/")
def index():
    """Display application name"""

    return jsonify({"application name": "Inventory Management System"})


@app.route("/partners", methods=["GET", "POST"])
def partners():
    """Display list of all partners (if endpoint is accessed using a "GET" request),
    and inserts a new partner (if endpoint is accessed using a "POST" request)"""

    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all patners from database and add them to a list that gets returned
    if request.method == "GET":
        partners = []
        data = db.execute("SELECT * FROM partners").fetchall()
        
        # If there are no partners in database, return False
        if data is None or len(data) == 0:
            return(jsonify({"success": False, "message": "There are no partners in database"}))

        # Each partner is a dictionary that gets added to the list
        for row in data:
            partner = {}
            partner["id"] = row[0]
            partner["partner_name"] = row[1]
            partner["partner_address"] = row[2]
            partner["partner_manager_first_name"] = row[3]
            partner["partner_manager_last_name"] = row[4]

            partners.append(partner)
        
        return jsonify({"success": True, "partners": partners})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new partner into the database
    if request.method == "POST":
        # Check if all necessary keys are in the request form
        form_fields = ["partner_name", "partner_address", "partner_manager_first_name", "partner_manager_last_name"]
        valid_form_data = validate_form_fields(form_fields, request.form)
        if valid_form_data == True:
            pass
        else:
            return jsonify({"success": False, "message": f"form-data must contain {valid_form_data[1]}"})

        partner_name = request.form["partner_name"]
        partner_address = request.form["partner_address"]
        partner_manager_first_name = request.form["partner_manager_first_name"]
        partner_manager_last_name = request.form["partner_manager_last_name"]

        # If a required input is not provided, return False
        if not partner_name or not partner_address:
            return jsonify({"success": False, "message": "'partner_name' and 'partner_address' are required fields"})

        # Check if partner already exists, If not, insert the new partner in the database
        data = db.execute("SELECT * FROM partners WHERE partner_name = :partner_name", {
            "partner_name": partner_name
        }).fetchone()

        if data is None or len(data) == 0:        
            db.execute(""" INSERT INTO partners (
                partner_name,
                partner_address,
                partner_manager_first_name,
                partner_manager_last_name
                ) VALUES (
                    :partner_name,
                    :partner_address,
                    :partner_manager_first_name,
                    :partner_manager_last_name
                    ) """, {
                        "partner_name": partner_name,
                        "partner_address": partner_address,
                        "partner_manager_first_name": partner_manager_first_name,
                        "partner_manager_last_name": partner_manager_last_name
                    })
            conn.commit()

            return jsonify({"success": True, "message": f"{partner_name} successfully added in database"})
        else:
            return jsonify({"success": False, "message": f"{partner_name} already exists in database"})


@app.route("/partner/<int:partner_id>", methods=["GET", "PUT", "DELETE"])
def partner(partner_id):
    """Display information about a partner (if endpoint is accessed by using a "GET" request);
    update information about a partner (if endpoint is accessed by using a "PUT" request);
    delete a partner from database (if endpoint is accessed by using a "DELETE" request"""
    
    #Connect to database
    conn = db_connection()
    db = conn.cursor()

    # Check the database for the partner with the provided id. If there is no such partner, return False
    data = db.execute("SELECT * FROM partners WHERE partner_id = :partner_id", {"partner_id": partner_id}).fetchone()
    
    if data is None or len(data) == 0:
        return jsonify({"success": False, "message": f"There is no partner with id {partner_id} in database"})
    
    partner_name = data[1]

    # If endpoint is accessed using a "GET" request, fetch all the information about the partner from database and add it to a list that gets returned
    if request.method == "GET":
        partner = {}
        partner["partner_id"] = data[0]
        partner["partner_name"] = data[1]
        partner["partner_address"] = data[2]
        partner["partner_manager_first_name"] = data[3]
        partner["partner_manager_last_name"] = data[4]

        return(jsonify({"success": True, "partner": partner}))

    # If endpoint is accessed using a "PUT" request, update the information about the partner
    if request.method == "PUT":
        # Check if all necessary keys are in the request form
        form_fields = ["partner_name", "partner_address", "partner_manager_first_name", "partner_manager_last_name"]
        valid_form_data = validate_form_fields(form_fields, request.form)
        if valid_form_data == True:
            pass
        else:
            return jsonify({"success": False, "message": f"form-data must contain {valid_form_data[1]}"})

        partner_name = request.form["partner_name"]
        partner_address = request.form["partner_address"]
        partner_manager_first_name = request.form["partner_manager_first_name"]
        partner_manager_last_name = request.form["partner_manager_last_name"]

        # Check if all necessary data is provided
        if not partner_name or not partner_address:
            return jsonify({"success": False, "message": "'partner_name' and 'partner_address' are required fields"})

        db.execute(""" UPDATE partners SET
        partner_name = :partner_name,
        partner_address = :partner_address,
        partner_manager_first_name = :partner_manager_first_name,
        partner_manager_last_name = :partner_manager_last_name
        WHERE
        partner_id = :partner_id""", {
            "partner_name": partner_name,
            "partner_address": partner_address,
            "partner_manager_first_name": partner_manager_first_name,
            "partner_manager_last_name": partner_manager_last_name,
            "partner_id": partner_id
        })

        conn.commit()

        return jsonify({"success": True, "message": f"Information about {partner_name} successfully updated"})

    if request.method == "DELETE":
        # Check if there are any bills from the partner or any invoices issued to the partner. If True, DO NOT delete the partner
        bills = db.execute("SELECT * FROM bills WHERE partner_id = :partner_id", {"partner_id": partner_id}).fetchone()
        invoices = db.execute("SELECT * FROM invoices WHERE partner_id = :partner_id", {"partner_id": partner_id}).fetchone()

        if bills is not None or invoices is not None:
            return jsonify({"success": False, "message": "Cannot delete partner. There are bills/invoices from/to this partner"})

        db.execute("DELETE FROM partners WHERE partner_id = :partner_id", {"partner_id": partner_id})
        conn.commit()
        
        return jsonify({"success": True, "message": f"{partner_name} successfully deleted from database"})


@app.route("/items", methods=["GET", "POST"])
def items():
    """Display list of all items (if endpoint is accessed using a "GET" request),
    and inserts a new item into database (if endpoint is accessed using a "POST" request)"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all items from database and add them to a list that gets returned
    if request.method == "GET":
        data = db.execute("SELECT * FROM items").fetchall()
        
        # if there are no items in database, return False
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": "There are no items in database"})
        
        items = []

        # Each item is a dictionary that gets added to the list
        for row in data:
            item = {}
            item["item_id"] = row[0]
            item["item_code"] = row[1]
            item["item_description"] = row[2]
            item["unit_id"] = row[3]
            item["vat_rate_id"] = row[4]
            item["item_quantity"] = row[5]
            item["latest_purchase_price"] = row[6]
            item["average_purchase_price"] = row[7]
            item["latest_selling_price"] = row[8]

            items.append(item)
        
        return jsonify({"success": True, "items": items})

    if request.method == "POST":
        # Check if the request form contains all necessary keys
        form_fields = ["item_code", "item_description", "unit_id", "vat_rate_id"]
        valid_form_data = validate_form_fields(form_fields, request.form)
        if valid_form_data:
            pass
        else:
            return jsonify({"success": False, "message": f"{valid_form_data[1]}"})

        item_code = request.form["item_code"]
        item_description = request.form["item_description"]
        try:
            unit_id = int(request.form["unit_id"])
        except:
            return jsonify({"success": False, "message": "'unit_id' must be integer"})

        try:
            vat_rate_id = int(request.form["vat_rate_id"])
        except:
            return jsonify({"success": False, "message": "'vat_rate_id' must be integer"})

        # If a required input is not provided, return False
        if not item_code or not item_description or not unit_id or not vat_rate_id:
            return jsonify({"success": False, "message": "You must provide all reqiured data"})

        check_unit_id = db.execute("SELECT * FROM units_of_measure WHERE unit_id = :unit_id", {"unit_id": unit_id}).fetchone()
        if check_unit_id is None or len(check_unit_id) == 0:
            return jsonify({"success": False, "message": f"{unit_id} is not valid (not in database)"})

        check_vat_rate_id = db.execute("SELECT * FROM vat_rates WHERE vat_rate_id = :vat_rate_id", {"vat_rate_id": vat_rate_id}).fetchone()
        if check_vat_rate_id is None or len(check_vat_rate_id) == 0:
            return jsonify({"success": False, "message": f"{vat_rate_id} is not valid (not in database)"})

        check_item_code = db.execute("SELECT * FROM items WHERE item_code = :item_code", {"item_code": item_code}).fetchone()
        check_item_description = db.execute("SELECT * FROM items WHERE item_description = :item_description", {"item_description": item_description}).fetchone()

        if (check_item_code is None or len(check_item_code) == 0) and (check_item_description is None or len(check_item_description) == 0):
            db.execute("""INSERT INTO items (
                item_code,
                item_description,
                unit_id,
                vat_rate_id
                ) VALUES (
                    :item_code,
                    :item_description,
                    :unit_id,
                    :vat_rate_id
                    )""", {
                        "item_code": item_code,
                        "item_description": item_description,
                        "unit_id": unit_id,
                        "vat_rate_id": vat_rate_id
                    })
            conn.commit()

            return jsonify({"success": True, "message": f"{item_description} successfully added to database"})
        else:
            return jsonify({"success": False, "message": f"Item with code {item_code} or item with description {item_description} already exists in database"})


@app.route("/item/<int:item_id>", methods=["GET", "DELETE"])
def item(item_id):
    """Display information about the desired item (if endpoint is accessed using a "GET" request,
    and delete desired item from database (if endpoint is accessed using a "DELETE" request)"""
    
    #Connect to database
    conn = db_connection()
    db = conn.cursor()

    # Check if item is in database
    data = db.execute("SELECT * FROM items WHERE item_id = :item_id", {"item_id": item_id}).fetchone()
    if data is None or len(data) == 0:
        return jsonify({"success": False, "message": f"There is no item with id {item_id} in database"})

    if request.method == "GET":
        item ={}
        item["item_id"] = data[0]
        item["item_code"] = data[1]
        item["item_description"] = data[2]
        item["unit_id"] = data[3]
        item["vat_rate_id"] = data[4]
        item["item_quantity"] = data[5]
        item["latest_purchase_price"] = data[6]
        item["average_purchase_price"] = data[7]
        item["latest_selling_price"] = data[8]

        return jsonify({"success": True, "item": item})

    if request.method == "DELETE":
        # Check if there are any bill records or invoice records with the item. If true, DO NOT delete the item.
        bill_records = db.execute("SELECT * FROM bill_records WHERE item_id = :item_id", {"item_id": item_id}).fetchone()
        invoice_records = db.execute("SELECT * FROM invoice_records WHERE item_id = :item_id", {"item_id": item_id}).fetchone()

        if bill_records is not None or invoice_records is not None:
            return jsonify({"success": False, "message": "Cannot delete item from database. There are bill records and/or invoice records with this item."})
        
        db.execute("DELETE FROM items WHERE item_id = :item_id", {"item_id": item_id})
        conn.commit()

        return jsonify({"success": True, "message": f"{data[2]} successfully deleted from database"})


@app.route("/vat_rates", methods=["GET", "POST"])
def vat_rates():
    """Display list of VAT rates (if endpoint is accessed by using a "GET" request),
    and insert a VAT rate into database (if endpoint is accessed by using a "POST" request)"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all VAT rates from database and add them to a list that gets returned
    if request.method == "GET":
        data = db.execute("SELECT * FROM vat_rates").fetchall()
        
        # If there are no VAT rates in database, return False
        if data is None or len(data) == 0:
            return(jsonify({"success": False, "message": "There are no VAT rates in database"}))
        
        vat_rates = []

        # Each VAT rate is a dictionary that gets added to the list
        for row in data:
            vat_rate = {}
            vat_rate["vat_rate_id"] = row[0]
            vat_rate["vat_rate"] = row[1]

            vat_rates.append(vat_rate)

        return jsonify({"success": True, "vat_rates": vat_rates})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new VAT rate into the database
    if request.method == "POST":
        # Check if all necessary keys are in the request form
        form_fields = ["vat_rate"]
        valid_form_data = validate_form_fields(form_fields, request.form)
        if valid_form_data:
            pass
        else:
            return jsonify({"success": False, "message": valid_form_data[1]})

        vat_rate = request.form["vat_rate"]
        
        # If a VAT rate is not provided, return False
        if not vat_rate:
            return jsonify({"success": False, "message": "'vat_rate' is a required field"})

        # Check if VAT rate already exists in database
        data = db.execute("SELECT * FROM vat_rates WHERE vat_rate = :vat_rate", {"vat_rate": vat_rate}).fetchone()
        if data is None or len(data) == 0:
            db.execute("INSERT INTO vat_rates (vat_rate) VALUES (:vat_rate)", {"vat_rate": vat_rate})
            conn.commit()
            return jsonify({"success": True, "message": f"VAT rate of {vat_rate}% successfully added to database"})
        else:
            return jsonify({"success": False, "message": f"VAT rate of {vat_rate}% already exists in database"})


@app.route("/units_of_measure", methods=["GET", "POST"])
def units_of_measure():
    """Display a list of all units of measure (if endpoint is accessed by using a "GET" request,
    and insert a new unit of measure into the database (if endpoint is accessed by using a "POST" request)"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all units of measure from database and add them to a list that gets returned
    if request.method == "GET":
        # If there are no units of measure in database, return False
        data = db.execute("SELECT * FROM units_of_measure").fetchall()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": "There no units of measure in database"})

        units_of_measure = []

        # Each unit of measure is a dictionary that gets added to the list
        for row in data:
            unit_of_measure = {}
            unit_of_measure["unit_id"] = row[0]
            unit_of_measure["unit_acronym"] = row[1]
            unit_of_measure["unit_name"] = row[2]

            units_of_measure.append(unit_of_measure)

        return jsonify({"success": True, "units of measure": units_of_measure})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new unit of measure into the database
    if request.method == "POST":
        # Check if all necessary keys are in the request form
        form_fields = ["unit_acronym", "unit_name"]
        valid_form_fields = validate_form_fields(form_fields, request.form)

        if valid_form_fields:
            pass
        else:
            return jsonify({"success": False, "message": valid_form_fields[1]})

        unit_acronym = request.form["unit_acronym"]
        unit_name = request.form["unit_name"]

        # If a required input is not provided, return False
        if not unit_acronym or not unit_name:
            return jsonify({"success": False, "message": "You must provide all necessary data"})

        # Check if the unit of measure already exists in the database
        data = db.execute("""SELECT * FROM units_of_measure WHERE
        unit_acronym = :unit_acronym OR
        unit_name = :unit_name""", {
            "unit_acronym": unit_acronym.upper(),
            "unit_name": unit_name.capitalize()
        }).fetchone()

        if data is None or len(data) == 0:
            db.execute("""INSERT INTO units_of_measure (
                unit_acronym, unit_name) VALUES (
                    :unit_acronym,
                    :unit_name)""", {
                        "unit_acronym": unit_acronym.upper(),
                        "unit_name": unit_name.capitalize()
                    })

            conn.commit()

            return jsonify({"success": True, "message": f"{unit_name.capitalize()} ({unit_acronym.upper()}) successfully added to database"})
        else:
            return jsonify({"success": False, "message": f"{unit_name.capitalize()} ({unit_acronym.upper()}) already exists in database"})


@app.route("/bills", methods=["GET", "POST"])
def bills():
    """Display list of all bills from partners (if endpoint is accessed by using a "GET" request),
    and insert a new bill from parnter into database (if endpoint is accessed using a "POST" request"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all bills from database and add them to a list that gets returned
    if request.method == "GET":
        # If there are no bills in the database, return False
        data = db.execute("SELECT * FROM bills ORDER BY bill_date").fetchall()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": "There are no bills in database"})

        bills = []

        # Each bill is a dictionary that gets added to the list
        for row in data:
            bill = {}
            bill["bill_id"] = row[0]
            bill["bill_number"] = row[1]
            bill["bill_date"] = row[2]
            bill["bill_due_date"] = row[3]
            bill["bill_amount"] = row[4]
            bill["partner_id"] = row[5]

            bills.append(bill)
        
        return jsonify({"success": True, "bills": bills})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new bill into the database
    if request.method == "POST":
        # Check if the form data contains the necessary keys (input fields)
        form_fields = ["bill_number", "bill_date", "bill_due_date", "bill_amount", "partner_id"]
        for form_field in form_fields:
            if form_field not in request.form:
                return jsonify({"success": False, "message": f"Form-data must contain a field called \'{form_field}\'"})

        bill_number = request.form["bill_number"]
        bill_date = request.form["bill_date"]
        bill_due_date = request.form["bill_due_date"]
        try:
            partner_id = int(request.form["partner_id"])
        except:
            return jsonify({"success": False, "message": "partner_id must be integer"})
        
        try:
            bill_amount = int(request.form["bill_amount"])
        except:
            return jsonify({"success": False, "message": "Bill amount must be integer"})

        # Check if all required inputs are provided
        if not bill_number or not bill_date or not bill_due_date or not bill_amount or not partner_id:
            return jsonify({"success": False, "message": "You need to provide all required data"})

        # Check if the partner that had sent the bill is in the database
        data = db.execute("SELECT * FROM partners WHERE partner_id = :partner_id", {"partner_id": partner_id}).fetchone()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": f"There is no partner with id {partner_id} in database"})

        # Validate the bill date
        # The format in which the user provides the date must be dd.mm.yyyy
        # The format in which the date is stored in the database is yyyy-mm-dd (this way, we can later compare and order dates)
        if len(bill_date) != 10:
            return jsonify({"success": False, "message": "The format of bill date must be: dd.mm.yyyy"})

        if bill_date[2] != "." or bill_date[5] != ".":
            return jsonify({"success": False, "message": "The format of bill date must be: dd.mm.yyyy"})

        try:
            day = int(bill_date[0:2])
        except:
            return jsonify({"success": False, "message": "The format of bill date must be: dd.mm.yyyy"})

        if day < 1 or day > 31:
            return jsonify({"success": False, "message": "Day must be between 01 and 31"})

        try:
            month = int(bill_date[3:5])
        except:
            return jsonify({"success": False, "message": "The format of bill date must be: dd.mm.yyyy"})

        if month < 1 or month > 12:
            return jsonify({"success": False, "message": "Month must be between 01 and 12"})

        if (month == 2 and day > 28) or ((month == 4 or month == 6 or month == 9 or month == 11) and day > 30):
            return jsonify({"success": False, "message": "Invalid date"})
        
        try:
            year = int(bill_date[6:])
        except:
            return jsonify({"success": False, "message": "The format of bill date must be: dd.mm.yyyy"})

        if year < 1950 and year > 2500:
            return jsonify({"success": False, "message": "Year must be between 1950 and 2500"})

        day = bill_date[0:2]
        month = bill_date[3:5]
        year = bill_date[6:]

        bill_date = f"{year}-{month}-{day}"

        # Validate the bill due date
        # The format in which the user provides the due date must be dd.mm.yyyy
        # The format in which the due date is stored in the database is yyyy-mm-dd (this way, we can later compare and order dates)
        if len(bill_due_date) != 10:
            return jsonify({"success": False, "message": "The format of bill due date must be: dd.mm.yyyy"})

        if bill_due_date[2] != "." or bill_due_date[5] != ".":
            return jsonify({"success": False, "message": "The format of bill due date must be: dd.mm.yyyy"})

        try:
            day = int(bill_due_date[0:2])
        except:
            return jsonify({"success": False, "message": "The format of bill due date must be: dd.mm.yyyy"})

        if day < 1 or day > 31:
            return jsonify({"success": False, "message": "Day must be between 01 and 31"})

        try:
            month = int(bill_due_date[3:5])
        except:
            return jsonify({"success": False, "message": "The format of bill due date must be: dd.mm.yyyy"})

        if month < 1 or month > 12:
            return jsonify({"success": False, "message": "Month must be between 01 and 12"})

        if (month == 2 and day > 28) or ((month == 4 or month == 6 or month == 9 or month == 11) and day > 30):
            return jsonify({"success": False, "message": "Invalid due date"})
        
        try:
            year = int(bill_due_date[6:])
        except:
            return jsonify({"success": False, "message": "The format of bill due date must be: dd.mm.yyyy"})

        if year < 1950 and year > 2500:
            return jsonify({"success": False, "message": "Year must be between 1950 and 2500"})

        day = bill_due_date[0:2]
        month = bill_due_date[3:5]
        year = bill_due_date[6:]

        bill_due_date = f"{year}-{month}-{day}"

        if bill_due_date < bill_date:
            return jsonify({"success": False, "message": "Due date can't be before the date"})

        # Check if the bill already exists in the database
        data = db.execute("""SELECT * FROM bills WHERE
        bill_number = :bill_number AND
        bill_date = :bill_date AND
        bill_due_date = :bill_due_date AND
        bill_amount = :bill_amount AND
        partner_id = :partner_id""", {
            "bill_number": bill_number,
            "bill_date": bill_date,
            "bill_due_date": bill_due_date,
            "bill_amount": bill_amount,
            "partner_id": partner_id
        }).fetchone()

        if data is None or len(data) == 0:
            db.execute("""INSERT INTO bills (
                bill_number,
                bill_date,
                bill_due_date,
                bill_amount,
                partner_id
            ) VALUES (
                :bill_number,
                :bill_date,
                :bill_due_date,
                :bill_amount,
                :partner_id
            )""", {
                "bill_number": bill_number,
                "bill_date": bill_date,
                "bill_due_date": bill_due_date,
                "bill_amount": bill_amount,
                "partner_id": partner_id
            })
            conn.commit()

            return jsonify({"success": True, "message": f"Bill no. {bill_number} successfully added to database"})
        else:
            return jsonify({"success": False, "message": "This bill already exists"})
        

@app.route("/bill_records", methods=["GET", "POST"])
def bill_records():
    """Display a list of all bill_records (if endpoint is accessed by using a "GET" request,
    and insert a new bill record into the database (if endpoint is accessed by using a "POST" request)"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all bill records from database and add them to a list that gets returned
    if request.method == "GET":
        # If there are no bill records in database, return False
        data = db.execute("SELECT * FROM bill_records").fetchall()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": "There are no bill records in database"})

        bill_records = []

        # Each bill record is a dictionary that gets added to the list
        for row in data:
            bill_record = {}
            bill_record["bill_record_id"] = row[0]
            bill_record["item_id"] = row[1]
            bill_record["quantity"] = row[2]
            bill_record["price"] = row[3]
            bill_record["bill_record_amount_net"] = row[4]
            bill_record["bill_record_vat"] = row[5]
            bill_record["bill_record_amount_total"] = row[6]
            bill_record["bill_id"] = row[7]

            bill_records.append(bill_record)

        return jsonify({"success": True, "bill_records": bill_records})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new bill record into the database
    if request.method == "POST":
        # Check if all necessary keys are in the request form
        form_fields = ["item_id", "quantity", "price", "bill_id"]
        for form_field in form_fields:
            if form_field not in request.form:
                return jsonify({"success": False, "message": f"form-data must contain {form_field}"})

        try:
            item_id = int(request.form["item_id"])
            quantity = float(request.form["quantity"])
            price = float(request.form["price"])
            bill_id = int(request.form["bill_id"])
        except:
            item_id = None
            quantity = None
            price = None
            bill_id = None

        # If a required input is not provided, return False
        if not item_id or not quantity or not price or not bill_id:
            return jsonify({"success": False, "message": "You must provide all necessary data"})

        # Check if the item that had been billed by the partner exists in the database
        check_item = db.execute("SELECT * FROM items WHERE item_id = :item_id", {"item_id": item_id}).fetchone()
        if check_item is None or len(check_item) == 0:
            return jsonify({"success": False, "message": f"There is no item with id {item_id} in database"})

        # Check if the bill that contains the item exists in the database
        check_bill = db.execute("SELECT * FROM bills WHERE bill_id = :bill_id", {"bill_id": bill_id}).fetchone()
        if check_bill is None or len(check_bill) == 0:
            return jsonify({"success": False, "message": f"There is no bill with id {bill_id} in database"})

        vat_rate = db.execute("""SELECT vat_rate FROM vat_rates WHERE vat_rate_id = 
        (SELECT vat_rate_id FROM items WHERE item_id = :item_id)""", {"item_id": item_id}).fetchone()

        vat_rate = int(vat_rate[0])

        bill_record_amount_net = quantity * price
        bill_record_vat = bill_record_amount_net * (vat_rate / 100)
        bill_record_amount_total = bill_record_amount_net + bill_record_vat

        db.execute("""INSERT INTO bill_records (
            item_id,
            quantity,
            price,
            bill_record_amount_net,
            bill_record_vat,
            bill_record_amount_total,
            bill_id
            ) VALUES (
            :item_id,
            :quantity,
            :price,
            :bill_record_amount_net,
            :bill_record_vat,
            :bill_record_amount_total,
            :bill_id
            )""", {
                "item_id": item_id,
                "quantity": quantity,
                "price": price,
                "bill_record_amount_net": bill_record_amount_net,
                "bill_record_vat": bill_record_vat,
                "bill_record_amount_total": bill_record_amount_total,
                "bill_id": bill_id
            })
        conn.commit()

        # Update item information regarding quantity and prices
        item_quantity = quantity + check_item[5]

        item_total_purchase = db.execute("""SELECT SUM(bill_record_amount_net), SUM(quantity)
        FROM bill_records
        WHERE item_id = :item_id""", {
            "item_id": item_id
        }).fetchone()

        item_total_purchase_value = item_total_purchase[0]
        item_total_purchase_quantity = item_total_purchase[1]
        average_purchase_price = item_total_purchase_value / item_total_purchase_quantity

        db.execute("""UPDATE items SET
        item_quantity = :item_quantity,
        latest_purchase_price = :price,
        average_purchase_price = :average_purchase_price
        WHERE
        item_id = :item_id""", {
            "item_quantity": item_quantity,
            "price": price,
            "average_purchase_price": average_purchase_price,
            "item_id": item_id
        })
        conn.commit()

        return jsonify({"success": True, "message": "Bill record successfully added to database"})


@app.route("/invoices", methods=["GET", "POST"])
def invoices():
    """Display list of all issued invoices (if endpoint is accessed by using a "GET" request,
    and insert a new invoice into the database (if endpoint is accessed by using a "POST" request)"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all issued invoices from database and add them to a list that gets returned
    if request.method == "GET":
        # If there are no issued invoices in database, return False
        data = db.execute("SELECT * FROM invoices ORDER BY invoice_number").fetchall()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": "There are no invoices in database"})

        invoices = []

        # Each issued invoice is a dictionary that gets added to the list
        for row in data:
            invoice = {}
            invoice["invoice_id"] = row[0]
            invoice["invoice_number"] = row[1]
            invoice["invoice_date"] = row[2]
            invoice["invoice_due_date"] = row[3]
            invoice["invoice_amount_net"] = row[4]
            invoice["invoice_vat"] = row[5]
            invoice["invoice_amount_total"] = row[6]
            invoice["partner_id"] = row[7]

            invoices.append(invoice)
        
        return jsonify({"success": True, "invoices": invoices})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new issued invoice into the database
    if request.method == "POST":
        data = db.execute("SELECT * FROM invoices ORDER BY invoice_number DESC").fetchall()
        # The invoices are numbered automatically, starting with 00001
        if data is None or len(data) == 0:
            invoice_number = "00001"
        else:
            latest_invoice_number = data[0][1]
            invoice_number = int(latest_invoice_number) + 1
            invoice_number = (5 - len(str(invoice_number))) * "0" + str(invoice_number)

        # Check if all necessary keys are in the request form
        form_fields = ["invoice_date", "invoice_due_date", "partner_id"]
        for form_field in form_fields:
            if form_field not in request.form:
                return jsonify({"success": False, "message": f"Form-data must contain a field called \'{form_field}\'"})

        invoice_date = request.form["invoice_date"]
        invoice_due_date = request.form["invoice_due_date"]
        try:
            partner_id = int(request.form["partner_id"])
        except:
            return jsonify({"success": False, "message": "partner_id must be integer"})
        
        # If a required input is not provided, return False
        if not invoice_date or not invoice_due_date or not partner_id:
            return jsonify({"success": False, "message": "You need to provide all required data"})

        # Check if the partner to whom the invoice is issued is in the database
        data = db.execute("SELECT * FROM partners WHERE partner_id = :partner_id", {"partner_id": partner_id}).fetchone()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": f"There is no partner with id {partner_id} in database"})

        # Validate the invoice date
        # The format in which the user provides the date must be dd.mm.yyyy
        # The format in which the date is stored in the database is yyyy-mm-dd (this way, we can later compare and order dates)
        if len(invoice_date) != 10:
            return jsonify({"success": False, "message": "The format of invoice date must be: dd.mm.yyyy"})

        if invoice_date[2] != "." or invoice_date[5] != ".":
            return jsonify({"success": False, "message": "The format of invoice date must be: dd.mm.yyyy"})

        try:
            day = int(invoice_date[0:2])
        except:
            return jsonify({"success": False, "message": "The format of invoice date must be: dd.mm.yyyy"})

        if day < 1 or day > 31:
            return jsonify({"success": False, "message": "Day must be between 01 and 31"})

        try:
            month = int(invoice_date[3:5])
        except:
            return jsonify({"success": False, "message": "The format of invoice date must be: dd.mm.yyyy"})

        if month < 1 or month > 12:
            return jsonify({"success": False, "message": "Month must be between 01 and 12"})

        if (month == 2 and day > 28) or ((month == 4 or month == 6 or month == 9 or month == 11) and day > 30):
            return jsonify({"success": False, "message": "Invalid date"})
        
        try:
            year = int(invoice_date[6:])
        except:
            return jsonify({"success": False, "message": "The format of invoice date must be: dd.mm.yyyy"})

        if year < 1950 and year > 2500:
            return jsonify({"success": False, "message": "Year must be between 1950 and 2500"})

        day = invoice_date[0:2]
        month = invoice_date[3:5]
        year = invoice_date[6:]

        invoice_date = f"{year}-{month}-{day}"

        # Validate the invoice due date
        # The format in which the user provides the due date must be dd.mm.yyyy
        # The format in which the due date is stored in the database is yyyy-mm-dd (this way, we can later compare and order dates)
        if len(invoice_due_date) != 10:
            return jsonify({"success": False, "message": "The format of invoice due date must be: dd.mm.yyyy"})

        if invoice_due_date[2] != "." or invoice_due_date[5] != ".":
            return jsonify({"success": False, "message": "The format of invoice due date must be: dd.mm.yyyy"})

        try:
            day = int(invoice_due_date[0:2])
        except:
            return jsonify({"success": False, "message": "The format of invoice due date must be: dd.mm.yyyy"})

        if day < 1 or day > 31:
            return jsonify({"success": False, "message": "Day must be between 01 and 31"})

        try:
            month = int(invoice_due_date[3:5])
        except:
            return jsonify({"success": False, "message": "The format of invoice due date must be: dd.mm.yyyy"})

        if month < 1 or month > 12:
            return jsonify({"success": False, "message": "Month must be between 01 and 12"})

        if (month == 2 and day > 28) or ((month == 4 or month == 6 or month == 9 or month == 11) and day > 30):
            return jsonify({"success": False, "message": "Invalid due date"})
        
        try:
            year = int(invoice_due_date[6:])
        except:
            return jsonify({"success": False, "message": "The format of invoice due date must be: dd.mm.yyyy"})

        if year < 1950 and year > 2500:
            return jsonify({"success": False, "message": "Year must be between 1950 and 2500"})

        day = invoice_due_date[0:2]
        month = invoice_due_date[3:5]
        year = invoice_due_date[6:]

        invoice_due_date = f"{year}-{month}-{day}"

        if invoice_due_date < invoice_date:
            return jsonify({"success": False, "message": "The due date can't be before the date"})

        invoice_amount_net = 0
        invoice_vat = 0
        invoice_amount_total = 0

        # Check if the issued invoice already exists in the database
        data = db.execute("""SELECT * FROM invoices WHERE
        invoice_number = :invoice_number AND
        invoice_date = :invoice_date AND
        invoice_due_date = :invoice_due_date AND
        partner_id = :partner_id""", {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "invoice_due_date": invoice_due_date,
            "partner_id": partner_id
        }).fetchone()

        if data is None or len(data) == 0:
            db.execute("""INSERT INTO invoices (
                invoice_number,
                invoice_date,
                invoice_due_date,
                invoice_amount_net,
                invoice_vat,
                invoice_amount_total,
                partner_id
            ) VALUES (
                :invoice_number,
                :invoice_date,
                :invoice_due_date,
                :invoice_amount_net,
                :invoice_vat,
                :invoice_amount_total,
                :partner_id
            )""", {
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "invoice_due_date": invoice_due_date,
                "invoice_amount_net": invoice_amount_net,
                "invoice_vat": invoice_vat,
                "invoice_amount_total": invoice_amount_total,
                "partner_id": partner_id
            })
            conn.commit()

            return jsonify({"success": True, "message": f"Invoice no. {invoice_number} successfully added to database"})
        else:
            return jsonify({"success": False, "message": "This invoice already exists"})


@app.route("/invoice_records", methods=["GET", "POST"])
def invoice_records():
    """Display list of all invoice records (if endpoint is accessed by using a "GET" request,
    and insert a new invoice record in the database (if endpoint is accessed by using a "POST" request"""
    
    # Connect to database
    conn = db_connection()
    db = conn.cursor()

    # If endpoint is accessed using a "GET" request, fetch all invoice records from database and add them to a list that gets returned
    if request.method == "GET":
        # If there are no invoice records in the database, return False
        data = db.execute("SELECT * FROM invoice_records").fetchall()
        if data is None or len(data) == 0:
            return jsonify({"success": False, "message": "There are no invoice records in database"})

        invoice_records = []

        # Each invoice record is a dictionary that gets added to the list
        for row in data:
            invoice_record = {}
            invoice_record["invoice_record_id"] = row[0]
            invoice_record["item_id"] = row[1]
            invoice_record["quantity"] = row[2]
            invoice_record["net_selling_price"] = row[3]
            invoice_record["invoice_record_amount_net"] = row[4]
            invoice_record["invoice_record_vat"] = row[5]
            invoice_record["invoice_record_amount_total"] = row[6]
            invoice_record["invoice_id"] = row[7]
            invoice_record["average_purchase_price"] = row[8]
            invoice_record["vat_amount_per_unit"] = row[9]
            invoice_record["gross_selling_price"] = row[10]

            invoice_records.append(invoice_record)

        return jsonify({"success": True, "invoice_records": invoice_records})

    # If endpoint is accessed using a "POST" request, validate the inputs and insert the new invoice record into the database
    if request.method == "POST":
        # Check if all necessary keys are in the request form
        form_fields = ["item_id", "quantity", "selling_price", "vat_included", "invoice_id"]
        for form_field in form_fields:
            if form_field not in request.form:
                return jsonify({"success": False, "message": f"form-data must contain {form_field}"})

        try:
            item_id = int(request.form["item_id"])
            quantity = float(request.form["quantity"])
            selling_price = float(request.form["selling_price"])
            vat_included = int(request.form["vat_included"])
            invoice_id = int(request.form["invoice_id"])
        except:
            item_id = None
            quantity = None
            selling_price = None
            vat_included = False
            invoice_id = None

        # If a required input is not provided, return False
        if not item_id or not quantity or not selling_price or not invoice_id:
            return jsonify({"success": False, "message": "You must provide all necessary data"})

        if vat_included == 0:
            vat_included = False
        elif vat_included == 1:
            vat_included = True
        else:
            return jsonify({"success": False, "message": "\"vat_included\" should be 0 if VAT is not included in the selling price, otherwise it should be 1"})

        # Check if the item that gets invoiced is in the database
        check_item = db.execute("SELECT * FROM items WHERE item_id = :item_id", {"item_id": item_id}).fetchone()
        if check_item is None or len(check_item) == 0:
            return jsonify({"success": False, "message": f"There is no item with id {item_id} in database"})

        # Check if the invoice that the record is a part of exists in the database
        check_invoice = db.execute("SELECT * FROM invoices WHERE invoice_id = :invoice_id", {"invoice_id": invoice_id}).fetchone()
        if check_invoice is None or len(check_invoice) == 0:
            return jsonify({"success": False, "message": f"There is no invoice with id {invoice_id} in database"})

        # Check if there is actually enough quantity on stock up to the invoice date
        invoice_date = str(check_invoice[2])
        
        item_purchased_quantity_and_amount = db.execute("""SELECT SUM(quantity), SUM(bill_record_amount_net)
        FROM bill_records 
        JOIN bills ON bill_records.bill_id = bills.bill_id 
        WHERE 
        item_id = :item_id AND
        bills.bill_date <= :invoice_date""", {
            "item_id": item_id,
            "invoice_date": invoice_date
        }).fetchone()

        if item_purchased_quantity_and_amount is None or len(item_purchased_quantity_and_amount) == 0:
            return jsonify({"success": False, "message": "You have no quantity on stock. Cannot continue until you have quantity."})
        
        item_purchased_quantity = item_purchased_quantity_and_amount[0]
        item_purchased_amount = item_purchased_quantity_and_amount[1]

        if item_purchased_quantity is None:
            item_purchased_quantity = 0
            item_purchased_amount = 0

        print(f"item_purchased_quantity: {item_purchased_quantity}")
        print(f"item_purchased_amount: {item_purchased_amount}")

        item_sold_quantity_and_amount = db.execute("""SELECT SUM(quantity), SUM(quantity*average_purchase_price)
        FROM invoice_records
        JOIN invoices ON invoice_records.invoice_id = invoices.invoice_id
        WHERE
        item_id = :item_id AND
        invoices.invoice_date <= :invoice_date""", {
            "item_id": item_id,
            "invoice_date": invoice_date
        }).fetchone()
        
        if item_sold_quantity_and_amount is None or len(item_sold_quantity_and_amount) == 0:
            item_sold_quantity = 0
            item_sold_amount = 0
        else:
            item_sold_quantity = item_sold_quantity_and_amount[0]
            item_sold_amount = item_sold_quantity_and_amount[1]

        if item_sold_quantity is None:
            item_sold_quantity = 0
            item_sold_amount = 0

        item_quantity_on_stock = item_purchased_quantity - item_sold_quantity
        item_amount_on_stock = item_purchased_amount - item_sold_amount

        if item_quantity_on_stock < quantity:
            return jsonify({"success": False, "message": f"You don't have enough quantity on stock. Maximum quantity allowed: {item_quantity_on_stock}"})
        
        average_purchase_price = item_amount_on_stock / item_quantity_on_stock
        
        vat_rate = db.execute("""SELECT vat_rate FROM vat_rates WHERE vat_rate_id = 
        (SELECT vat_rate_id FROM items WHERE item_id = :item_id)""", {"item_id": item_id}).fetchone()

        vat_rate = int(vat_rate[0])

        if vat_included:
            net_selling_price = selling_price / (1 + (vat_rate / 100))
            gross_selling_price = selling_price
        else:
            net_selling_price = selling_price
            gross_selling_price = net_selling_price * (1 + (vat_rate / 100))

        vat_amount_per_unit = gross_selling_price - net_selling_price        
        invoice_record_amount_net = quantity * net_selling_price
        invoice_record_vat = invoice_record_amount_net * (vat_rate / 100)
        invoice_record_amount_total = invoice_record_amount_net + invoice_record_vat

        db.execute("""INSERT INTO invoice_records (
            item_id,
            quantity,
            net_selling_price,
            invoice_record_amount_net,
            invoice_record_vat,
            invoice_record_amount_total,
            invoice_id,
            average_purchase_price,
            vat_amount_per_unit,
            gross_selling_price
            ) VALUES (
            :item_id,
            :quantity,
            :net_selling_price,
            :invoice_record_amount_net,
            :invoice_record_vat,
            :invoice_record_amount_total,
            :invoice_id,
            :average_purchase_price,
            :vat_amount_per_unit,
            :gross_selling_price
            )""", {
                "item_id": item_id,
                "quantity": quantity,
                "net_selling_price": net_selling_price,
                "invoice_record_amount_net": invoice_record_amount_net,
                "invoice_record_vat": invoice_record_vat,
                "invoice_record_amount_total": invoice_record_amount_total,
                "invoice_id": invoice_id,
                "average_purchase_price": average_purchase_price,
                "vat_amount_per_unit": vat_amount_per_unit,
                "gross_selling_price": gross_selling_price
            })
        conn.commit()

        item_quantity = check_item[5] - quantity

        item_total_sales = db.execute("""SELECT SUM(invoice_record_amount_net), SUM(quantity)
        FROM invoice_records
        WHERE item_id = :item_id""", {
            "item_id": item_id
        }).fetchone()

        item_total_selling_value = item_total_sales[0]
        item_total_selling_quantity = item_total_sales[1]
        average_net_selling_price = item_total_selling_value / item_total_selling_quantity

        # Update item information regarding quantity and prices
        db.execute("""UPDATE items SET
        item_quantity = :item_quantity,
        latest_net_selling_price = :latest_net_selling_price,
        average_net_selling_price = :average_net_selling_price
        WHERE
        item_id = :item_id""", {
            "item_quantity": item_quantity,
            "latest_net_selling_price": net_selling_price,
            "average_net_selling_price": average_net_selling_price,
            "item_id": item_id
        })
        conn.commit()

        return jsonify({"success": True, "message": "Invoice record successfully added to database"})


if __name__=="__main__":
    app.run(debug=True)