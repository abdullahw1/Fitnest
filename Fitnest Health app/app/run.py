#!/usr/bin/env python3
import threading
import webbrowser
from myapp import myapp_obj, db

DEBUG = False
PORT_NUMBER = 5005



# Create *.db file from schema (if doesn't exists)
db.create_all()
# Launch webbrowser after 1 seconds
# Run flask app server
myapp_obj.run(debug=DEBUG, port=PORT_NUMBER)
