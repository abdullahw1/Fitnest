import threading
import webbrowser
from myapp import myapp_obj, db

DEBUG = False
PORT_NUMBER = 5012



# Create *.db file from schema (if doesn't exists)
try:
    db.create_all()
except:
    pass


# Run flask app server

myapp_obj.run(debug=DEBUG, port=PORT_NUMBER)
