import random
from flask import Flask, request
from flask import jsonify
#from flask.ext.uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__, static_folder='../static/dist', template_folder='../static')

@app.route('/')
def index():
    print(request.json)
    return "succ"


if __name__ == '__main__':
    app.run()