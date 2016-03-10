import pymongo
from bson import ObjectId
from datetime import datetime


class MongoUtils():

    def __init__(self, mongo):
        self.mongo = mongo
        # FIXME: Let's change the collection name to entries.
        self.collection_name = 'factchecks'

    def insert(self, doc):
        self.mongo.db[self.collection_name].insert(doc)

    def get_entries_for_classifications(self, classifications):
        query = {
            "classification": {
                "$in": classifications
            }
        }

        # FIXME: Is the date parameter still associate to a key in the root of the doc? I don't think so. This should be article.date.
        docs = self.mongo.db[self.collection_name].find(query).sort("date", pymongo.DESCENDING).limit(20)

        return list(docs)

    def edit_entry_doc(self, query=None):

        query_param = {
            "_id": ObjectId(query['doc_id'])
        }

        update_fields = {
            "mark": query['evaluation_mark'],
            'grade': query['grade'],
            'classification': query['classification'],
            'category': query['category'],
            'article': {
                'author': query['author_of_article'],
                 # FIXME: Why are we storing a date String?
                'dateString': query['date_of_article_pub'],
                'date': self.convert_date(query['date_of_article_pub'])
            },
            'quote': {
                 # FIXME: Is this stored as a boolean?
                'politician': query['politician'],
                'author': query['quote_author'],
                'affiliation': query['quote_author_affiliation'],
                 # FIXME: Why are we storing a date String?
                'dateString': query['date_of_statement'],
                'date': self.convert_date(query['date_of_statement'])
            }
        }

        if 'promise_due_date' in query:
            # FIXME: why are you story a date String? We only need ISODate
            # FIXME: You have user_chrome_id key and dateString key. Please stick with one standard. JSON standard is camelCase
            update_fields['promise'] = {
                'dateString': query['promise_due_date'],
                'due': self.convert_date(query['promise_due_date'])
            }

        # Call the function to update fields based on query params
        self._update(query_param, update_fields)

    def flag_entry_as_inappropriate(self, query):

        query_param = {
            "_id": ObjectId(query['doc_id'])
        }

        update_fields = {
            # FIXME: What is the point of flg_inappropriate if it's always going to be set to True?
            # FIXME: What is inappropriate_rsn?
            # FIXME: You only need one key, use "inappropriate"
            "flg_inappropriate": True,
            'inappropriate_rsn': query['inappropriate']
        }

        # Call the function to update fields based on query params
        self._update(query_param, update_fields)

    def _update(self, query_param, update_fields):

        self.mongo.db[self.collection_name].update(query_param, {"$set": update_fields})

    def find(self, query={}):

        # FIXME: Is the date parameter still associate to a key in the root of the doc? I don't think so. This should be article.date.
        docs = self.mongo.db[self.collection_name].find(query).sort("date", pymongo.DESCENDING)

        return docs

    def fetch_dynamic_data(self, query=None):

        query_params = {}

        if query['marks']:
            query_params = {
                "mark": {"$in": query['marks']}
            }

        if query["classifications"]:
            query_params = {
                "classification": {"$in": query['classifications']}
            }
            if "Promise" in query["classifications"]:
                # FIXME: What if the user hasn't provided dueFrom date but provided dueTo date?
                # FIXME: What if the user hasn't provided dueTo date but provided dueFrom date?
                # FIXME: What if the usern hasn't provided dueTo nor dueFrom dates?
                query_params['promise.due'] = {
                    '$gte': self.convert_date(query['promise']['dueFrom']),
                    '$lte': self.convert_date(query['promise']['dueTo'])
                }

        if query['grades']:
            query_params = {
                "grade": {"$in": query['grades']}
            }

        if query['categories']:
            query_params = {
                "category": {"$in": query['categories']}
            }

        if query['article']['authors']:
            query_params = {
                "article.author": {"$in": query['article']['authors']},
                # FIXME: What if the user hasn't provided from date but provided to date?
                # FIXME: What if the user hasn't provided to date but provided from date?
                # FIXME: What if the user hasn't provided to nor from dates?
                'article.date': {
                    '$gte': self.convert_date(query['article']['date']['from']),
                    '$lte': self.convert_date(query['article']['date']['to'])
                }
            }

        if query['quote']['author']:
            query_params = {
                "quote.author": query['quote']['author'],
                'quote.politician': query['quote']['politician'],
                # FIXME: What if the user hasn't provided from date but provided to date?
                # FIXME: What if the user hasn't provided to date but provided from date?
                # FIXME: What if the user hasn't provided to nor from dates?
                'quote.date': {
                    '$gte': self.convert_date(query['quote']['date']['from']),
                    '$lte': self.convert_date(query['quote']['date']['to']),
                }
            }

        docs = self.find(query_params)
        return docs

    @staticmethod
    def convert_date(inputs):
        if inputs.strip() != '':
            date = datetime.strptime(inputs, "%d/%m/%Y")
        else:
             # FIXME: Why this date? Why is this hardcoded?
            date = datetime.strptime("01/01/2015", "%d/%m/%Y")
        return date
