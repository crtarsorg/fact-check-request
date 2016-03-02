from flask import Blueprint, Response, request
from flask import render_template
from app import mongo_utils
import tldextract
import random
import json
from bson import json_util
from datetime import datetime

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/', methods=['GET'])
def index():
    return render_template('mod_api/index.html')


@mod_api.route('/factcheck/request', methods=['POST'])
def factcheck_request():
    req = request.json

    extracted = tldextract.extract(req['url'])
    domain = "{}.{}".format(extracted.domain, extracted.suffix)
    choices = ["False", "True", "Unverified"]

    doc = {
        'url': req['url'],
        'domain': domain,
        'text': req['text'],
        "date": datetime.fromtimestamp(req['date'] / 1e3),
        'factChecked': random.choice(choices)
    }
    mongo_utils.insert(doc)
    return Response(status=200)


@mod_api.route('/fact-check/classifications', methods=["POST"])
def query_classification():

    classifications = request.args.get('classifications')

    if len(request.json) > 1:
        return Response(400)
    elif 'classifications' not in request.json:
        return Response(400)
    elif not set(request.json['classifications']).issubset(['promise', 'truthfulness', 'consistency']):
        return Response(400)
    else:
        # retrieve data from database, based on classification params
        result = mongo_utils.get_entries_for_classifications(classifications)
        return Response(response=json_util.dumps(result), status=200, mimetype="application/json")



