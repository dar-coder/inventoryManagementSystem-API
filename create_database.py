import sqlite3

db = sqlite3.connect("database.sqlite3")

db = db.cursor()

db.execute(""" CREATE TABLE IF NOT EXISTS partners (
    partner_id integer PRIMARY KEY,
    partner_name text NOT NULL,
    partner_address text,
    partner_manager_first_name text,
    partner_manager_last_name text
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS bills (
    bill_id integer PRIMARY KEY,
    bill_number text NOT NULL,
    bill_date date NOT NULL,
    bill_due_date date NOT NULL,
    bill_amount integer NOT NULL,
    partner_id integer,
    FOREIGN KEY (partner_id) REFERENCES partnters(partner_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS vat_rates (
    vat_rate_id integer PRIMARY KEY,
    vat_rate integer
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS units_of_measure (
    unit_id integer PRIMARY KEY,
    unit_acronym text NOT NULL,
    unit_name text NOT NULL
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS items (
    item_id integer PRIMARY KEY,
    item_code text NUT NULL,
    item_description text NOT NULL,
    unit_id integer NOT NULL,
    vat_rate_id integer NOT NULL,
    item_quantity numeric DEFAULT 0,
    latest_purchase_price numeric DEFAULT 0,
    average_purchase_price numeric DEFAULT 0,
    latest_net_selling_price numeric DEFAULT 0,
    average_net_selling_price numeric DEFAULT 0,
    FOREIGN KEY (unit_id) REFERENCES units_of_measure(unit_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (vat_rate_id) REFERENCES vat_rates(vat_rate_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS bill_records (
    bill_record_id integer PRIMARY KEY,
    item_id integer NOT NULL,
    quantity numeric NOT NULL,
    price numeric NOT NULL,
    bill_record_amount_net numeric NOT NULL,
    bill_record_vat numeric NOT NULL,
    bill_record_amount_total integer NOT NULL,
    bill_id integer NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items (item_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (bill_id) REFERENCES bills (bill_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS invoices (
    invoice_id integer PRIMARY KEY,
    invoice_number text NOT NULL,
    invoice_date date NOT NULL,
    invoice_due_date date NOT NULL,
    invoice_amount_net integer,
    invoice_vat integer,
    invoice_amount_total integer,
    partner_id integer NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES partners(partner_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) """)

db.execute(""" CREATE TABLE IF NOT EXISTS invoice_records (
    invoice_record_id integer PRIMARY KEY,
    item_id integer NOT NULL,
    quantity numeric NOT NULL,
    net_selling_price numeric NOT NULL,
    invoice_record_amount_net numeric NOT NULL,
    invoice_record_vat numeric NOT NULL,
    invoice_record_amount_total integer NOT NULL,
    invoice_id integer NOT NULL,
    average_purchase_price numeric NOT NULL,
    vat_amount_per_unit numeric NOT NULL,
    gross_selling_price numeric NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) """)