# Budgeting CRUD Backend Application

Upload photos of receipts for quick and easy personal budgeting.

## Description

This application parses the QR code from the receipt photo.<br>
And allows you to annotate each item with custom category eg. food or bills.<br>
Saves the items in the SQL table designed for later analysis of cost or spending habits.

### Dependencies

* Flask - python web server
* MySql - Database
* QReader - QR code reader

### Installing

* Clone the repository ```git clone <url>``` (main branch).
* Install dependencies ```pip install -r requirements.txt``` (not yet added!).
* Run the server ```python -m server.app```.

### Security note

This application was not developed or secured for multiple users, but rather for personal self-hosted project.<br>
Later updates will include, user auth, code security audit for web app bugs such as OWASP top 10 and etc.
