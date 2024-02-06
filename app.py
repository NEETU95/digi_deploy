from flask import Flask, request
from werkzeug.exceptions import HTTPException
from main import pdf_extraction
from werkzeug.debug import DebuggedApplication

from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app, resources={r"/pred/*": {"origins": "*"}})

class AllTabException(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

@app.route('/pred', methods=['POST', 'GET'])
@cross_origin()
def pred():
    data = request.get_json()
    print("data : ", str(data))
    pdf_info = data.get('pdf_info', str)
    print("pdf_info : ", str(pdf_info))
    try:
        trail = pdf_extraction(pdf_info)
        return trail
    except HTTPException as e:
        print("error from app", e)


@app.errorhandler(HTTPException)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        print("catched exception using flask",e)
        return e

    # now you're handling non-HTTP exceptions only
    return e



if __name__ == '__main__':
    app.run(port=8902, host='0.0.0.0', debug=True)