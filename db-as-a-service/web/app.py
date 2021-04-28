from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db['Users']

def verifyPw(username, password):
    hashed_pw = users.find({
        'Username': username
    })[0]['Password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        'Username': username
    })[0]['Tokens']
    return tokens

class Register(Resource):
    def post(self):
        #Get posted data from the user
        postedData = request.get_json()

        #Get the data
        username = postedData['username']
        password = postedData['password']

        #hash(password + salt) = usd7assdf89af7gh987ayf9
        hash_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #store username and pw in the database
        users.insert({
            "Username": username,
            "Password": hash_pw,
            "Sentence": "",
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }

        return jsonify(retJson)

class Store(Resource):
    def post(self):
        #Get posted data
        postedData = request.get_json()

        #read the data
        username = postedData['username']
        password = postedData['password']
        sentence = postedData['sentence']

        #Verify if username and pw match
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson={
                "status": 302
            }
            return jsonify(retJson)

        #verify if user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson={
                'status': 301
            }
            return jsonify(retJson)
        #store sentence and return 200 OK and take one token
        users.update({
            'Username': username,
        }, {
            '$set': {
                'Sentence': sentence,
                'Tokens': num_tokens-1
            }
        })

        retJson = {
            'status': 200,
            'msg': 'Sentence saved successfully'
        }
        return jsonify(retJson)

class retrieveSentence(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                'status': 301
            }
            return jsonify(retJson)

        #make the user pay :)
        users.update({
            'Username': username,
        }, {
            '$set': {
                'Tokens': num_tokens - 1
            }
        })

        sentence = users.find({
            'Username':username
        })[0]['Sentence']

        retJson = {
            'status': 200,
            'sentence': sentence
        }
        return jsonify(retJson)

api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(retrieveSentence, '/retrievesentence')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
