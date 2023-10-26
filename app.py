import os
import jwt
# import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

CORS(
    app=app,
    origins=['http://localhost:5173']
)

IS_PRODUCTION = os.getenv('ENVIRONMENT') == 'production'

if IS_PRODUCTION:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    last_verification_token = db.Column(db.String)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
  
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(email=data['email']).first()
        except Exception as e:
            return jsonify({'message' : 'Invalid token', 'error': f'{e}'}), 401
        return  f(current_user, *args, **kwargs)
  
    return decorated


@app.route('/users', methods =['GET'])
@token_required
def get_all_users(current_user):
    print(current_user)
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id': user.id,
            'name' : user.name,
            'email' : user.email
        })
  
    return jsonify({'users': output})


@app.route('/login', methods =['POST'])
def login():
    auth = request.form
  
    if not auth or not auth.get('email') or not auth.get('password'):
        print("Missing parameters")
        return make_response('Missing parameters', 400)
  
    user = User.query.filter_by(email=auth.get('email')).first()
  
    if not user:
        return make_response('User does not exist', 401)

    if bcrypt.check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({
            'email': user.email,
        }, app.config['SECRET_KEY'], algorithm="HS256")
  
        return make_response(jsonify({'token' : token}), 201)

    return make_response('Incorrect credentials', 401)


@app.route('/signup', methods =['POST'])
def signup():
    data = request.form

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return make_response('Missing parameters', 400)

    user = User.query.filter_by(email=data.get('email', None)).first()
    if not user:
        user = User(
            name = data.get('name'),
            email = data.get('email'),
            password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()
  
        return make_response('Successfully registered.', 201)
    else:
        return make_response('User already exists. Please Log in.', 202)


@app.route('/forgot-password', methods =['POST'])
def forgot_password():
    data = request.form

    if not data.get('email'):
        return make_response('Missing parameters', 400)

    user = User.query.filter_by(email=data.get('email', None)).first()
    if not user:
        return make_response('User does not exist', 401)

    token = jwt.encode({
        'email': user.email,
    }, app.config['SECRET_KEY'], algorithm="HS256")

    user.last_verification_token = token
    db.session.commit()

    return make_response('Successfully sent verification token.', 200)


@app.route('/reset-password', methods =['POST'])
def reset_password():
    data = request.form

    if not data.get('email') or not data.get('password') or not data.get('token'):
        return make_response('Missing parameters', 400)

    user = User.query.filter_by(email=data.get('email', None)).first()
    if not user:
        return make_response('User does not exist', 401)

    if user.last_verification_token != data.get('token'):
        return make_response('Invalid token', 401)

    user.password = bcrypt.generate_password_hash(data.get('password'))
    user.last_verification_token = None
    db.session.commit()

    return make_response('Successfully reset password.', 200)


@app.route('/products', methods =['GET'])
@token_required
def get_all_products(current_user):
    products = Product.query.all()
    output = []
    for product in products:
        output.append({
            'id': product.id,
            'name' : product.name,
            'price' : product.price,
            'quantity' : product.quantity
        })
  
    return jsonify({'products': output})


@app.route('/products', methods =['POST'])
@token_required
def create_product(current_user):
    data = request.form

    if not data.get('name') or not data.get('price') or not data.get('quantity'):
        return make_response('Missing parameters', 400)

    product = Product(
        name = data.get('name'),
        price = data.get('price'),
        quantity = data.get('quantity')
    )
    db.session.add(product)
    db.session.commit()

    return make_response('Successfully created.', 201)


@app.route('/products/<product_id>', methods =['GET'])
@token_required
def get_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return make_response('Product not found.', 404)

    return jsonify({
        'id': product.id,
        'name' : product.name,
        'price' : product.price,
        'quantity' : product.quantity
    })


@app.route('/products/<product_id>', methods =['PUT'])
@token_required
def update_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return make_response('Product not found.', 404)

    data = request.form

    if data.get('name'):
        product.name = data.get('name')
    if data.get('price'):
        product.price = data.get('price')
    if data.get('quantity'):
        product.quantity = data.get('quantity')

    db.session.commit()

    return make_response('Successfully updated.', 200)


@app.route('/products/<product_id>', methods =['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return make_response('Product not found.', 404)

    db.session.delete(product)
    db.session.commit()

    return make_response('Successfully deleted.', 200)

if __name__ == "__main__":
    debug = not IS_PRODUCTION
    app.run(debug=debug, host="0.0.0.0", port=5000)
