# makesure the following libraries are installed in your environment
from flask import Flask,jsonify,make_response,request,redirect,url_for,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

import jwt
from datetime import datetime
import time
from functools import wraps

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.config['SECRET_KEY']='privatekey'
db=SQLAlchemy(app)

#fn to verifying token 
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        if 'x-access-token' in request.cookies:
            token=request.cookies.get('x-access-token')
        if not token:
            # no login data available
            return jsonify({'message': 'Token is missing'}),401
        try:    
            data=jwt.decode(token,app.config['SECRET_KEY'], algorithms=['HS256'])   
            expiration_time = datetime.fromtimestamp(data['exp'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args,**kwargs)
    return decorated

#creating tables for user and video entries
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False,unique=True)
    password=db.Column(db.String(50),nullable=False)

class List(db.Model):
    id=db.Column(db.Integer,primary_key="True")
    title=db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(500), nullable=False)
    status = db.Column(db.Enum('active', 'archived'), default='active')  
    date_created = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f"{self.title}"

@app.before_request
def create_table():
    db.create_all()

#creating user
@app.route('/create_user',methods=['POST'])
def create_user():
    data = request.form
    try:
        if 'username' not in data or 'password' not in data:
            raise ValueError('username and password are required')

        new_user = User(username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return make_response("user_created"),200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username already taken'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

#login and setting token
@app.route('/login',methods=['POST'])
def login():
    auth=request.form
    if not auth or not auth["username"] or not auth["password"]:
        return make_response('Could not verify',400)
    user=User.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('No User found',404)
    if user.password==auth['password']:
        # creating 5 min token and setting at cookie
        exp_time=time.time()+60*30
        token=jwt.encode({'username':user.username,'exp':exp_time},app.config['SECRET_KEY'],algorithm="HS256")
        response = make_response("Logged IN")
        response.set_cookie('x-access-token',token)
        return response
    return make_response("Incorrect password",401)

# CRUD END-POINTS

@app.route('/create_entry',methods=['POST'])
@token_required
def create_entry():
    Entry = request.form
    new_entry = List()
    try:
        new_entry.title = Entry['title']
        new_entry.description = Entry['description']
        new_entry.status = Entry['status']  # Assuming the form includes a field named 'status'
        if new_entry.status not in ['active', 'archived']:
            return jsonify({'error': 'Invalid status value'}), 400  # Correct status code
        db.session.add(new_entry)
        db.session.commit()
        return jsonify("New Entry Created")
    except KeyError as e:
        # Handle the case where a required form field is missing
        return jsonify(f"Missing form field: {e}"),400
    except Exception as e:
        # Handle other exceptions (e.g., database errors)
        return jsonify(f"Error creating new entry: {e}"),500

@app.route('/', methods=['GET'])
def retrieve():
    # Query all entries from the List table
    entries = List.query.all()
    
    # Convert the list of List objects to a list of dictionaries
    entries_list = []
    for entry in entries:
        entry_dict = {
            'id': entry.id,
            'title': entry.title,
            'description': entry.description,
            'status': entry.status
            # Add more fields if needed
        }
        entries_list.append(entry_dict)
    
    # Return the list of dictionaries as JSON
    return jsonify(entries_list)

@app.route('/update_entry/<int:id>', methods=['PUT'])
@token_required
def update_entry(id):
    entry_data = request.form
    entry = List.query.get(id)
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    try:
        

        # Update entry fields if provided in the form data
        if 'title' in entry_data:
            entry.title = entry_data['title']
        if 'description' in entry_data:
            entry.description = entry_data['description']
        if 'status' in entry_data:
            if entry_data['status'] not in ['active', 'archived']:
                return jsonify({'error': 'Invalid status value'}), 400  # Correct status code
            entry.status = entry_data['status']
        db.session.commit()
        return jsonify({'message': 'Entry updated successfully'})
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/delete_entry/<int:id>',methods=['DELETE'])
@token_required
def delete(id):
    entry=List.query.filter_by(id=id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify(id,"deleted")
    except:
        return jsonify("Invalid id")


if __name__=="__main__":
    app.run(debug="True")