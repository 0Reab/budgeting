# Budgeting CRUD Backend Application

Upload photos of receipts for quick and easy personal budgeting.

## Description

This application parses the QR code from the receipt photo.<br>
And allows you to annotate each item with custom category eg. food or bills.<br>
Saves the items in the SQL table designed for later analysis of cost or spending habits.<br>
Includes features like adding your income, graphs, tables, balance tracking and editing.

### Dependencies

* Flask - python web server
* MySql - Database
* QReader - QR code reader
* Docker - Optional for containerization

### Setup

* Clone the repository ```git clone <url>``` (main branch).
* Navigate to project ```cd budgeting-main```.
* Create Flask key ```echo "<your_long-key>" > key.txt && chmod 400 key.txt```

* Create cert (optional) ```openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes```.
* Set cert permissions (optional) ```chmod 644 cert.pem && chmod 400 key.pem```.

### Run with Docker

* Build and run image ```docker compose up --build```.
* Live on ```http(s)://localhost:1337``` ((s) if you created the cert).

### Or run with venv 

* Create environment ```python -m venv .venv```.
* Activate venv ```source .venv/bin/activate``` or on windows ```.venv\Scripts\Activate.ps1```.
* Install dependencies ```pip install -r requirements.txt```.
* Run the server (default port 1337) ```python -m server.app```.

### Security note

This application was not developed or secured for multiple users, but rather for personal self-hosted project.<br>
Later updates will include, user auth, code security audit for web app bugs such as OWASP top 10 and etc.
