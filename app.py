from flask import Flask,jsonify,make_response,request,redirect,url_for,render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
from datetime import datetime,timedelta
from functools import wraps
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.config['SECRET_KEY']='privatekey'
db=SQLAlchemy(app)

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        if 'x-access-token' in request.cookies:
            token=request.cookies.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing'})
        try:    
            data=jwt.decode(token,app.config['SECRET_KEY'], algorithms=['HS256'])   
            expiration_time = datetime.fromtimestamp(data['exp'])

            # Compare expiration time with current time
            current_time = datetime.now()
            if current_time > expiration_time:
                return jsonify({'message': 'Token has expired','now':current_time+timedelta(seconds=300),'exp':expiration_time}), 401
            current_user=User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'INvalid token'})
        return f(*args,**kwargs)
    return decorated

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

@app.route('/create',methods=['GET','POST'])
def create_user():
    if request.method=='POST':
        data=request.form
        try:
            new_user=User(username=data['username'],password=data['password'])
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        except:
            return jsonify('username_taken')
    else:
        return render_template('create.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        auth=request.form
        if not auth or not auth["username"] or not auth["password"]:
            return make_response('Could not verify')
        user=User.query.filter_by(username=auth['username']).first()
        if not user:
            return make_response('No User found')
        if user.password==auth['password']:
            exp_time=datetime.now()+timedelta(seconds=30)
            token=jwt.encode({'username':user.username,'exp':exp_time},app.config['SECRET_KEY'])
            # try:
            #     data=jwt.decode(token,app.config['SECRET_KEY'], algorithms=['HS256'])
            # except jwt.ExpiredSignatureError:
            #     return "Token has expired"
            # except jwt.DecodeError:
            #     return "Invalid token"
            # except jwt.Exception as e:
            #     return f"Error decoding token: {e}"
            response = make_response(redirect(url_for('home')))
            # response.set_cookie('x-access-token', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlVkYXkzIiwiZXhwIjoxNzE1MDk0NzA4fQ.wMQbL54QFYe_hWpVqdGUvGNoWQkiY7iLkPIUThlduPU")
            # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlVkYXkzIiwiZXhwIjoxNzE1MTEzMzE0fQ.yHiM5qTzhVdRl109D1CKfpEQqZiIrQY13Zd6JPQJ4B4"
            response.set_cookie('x-access-token',token)
            return response
        return make_response("Incorrect password")
    else:
        return render_template('login.html')

@app.route('/create_entry',methods=['POST'])
@token_required
def create_entry():
    Entry = request.form
    new_entry = List()
    try:
        new_entry.title = Entry['title']
        new_entry.description = Entry['description']
        new_entry.status = Entry['status']  # Assuming the form includes a field named 'status'
        db.session.add(new_entry)
        db.session.commit()
        return jsonify("New Entry Created")
    except KeyError as e:
        # Handle the case where a required form field is missing
        return jsonify(f"Missing form field: {e}")
    except Exception as e:
        # Handle other exceptions (e.g., database errors)
        return jsonify(f"Error creating new entry: {e}")

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

@app.route('/update_entry/<int:id>',methods=['POST'])
@token_required
def update(id):
    Entry = request.form
    update_entry = List.query.filter_by(id=id).first()
    try:
        update_entry.title = Entry['title']
        update_entry.description = Entry['description']
        update_entry.status = Entry['status']  # Assuming the form includes a field named 'status'
        db.session.commit()
        return jsonify("Entry Updated")
    except KeyError as e:
        # Handle the case where a required form field is missing
        return jsonify(f"Missing form field: {e}")
    except Exception as e:
        # Handle other exceptions (e.g., database errors)
        return jsonify(f"Error creating new entry: {e}")

@app.route('/delete_entry/<int:id>',methods=['DELETE'])
@token_required
def delete(id):
    entry=List.query.filter_by(id=id).first()
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify(id,"deleted")
    except:
        return jsonify("Invalid id")

@app.route('/home')
@token_required
def home():
    return 'ALL good'


if __name__=="__main__":
    app.run(debug="True")