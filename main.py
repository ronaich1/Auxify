# this is where you create the app by calling the function in init.py
from flask import Flask
from Website import *
# TODO: create the app
app = create_app()
# TODO: run the app
app.run(debug=True)
