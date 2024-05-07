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

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False,unique=True)
    password=db.Column(db.String(50),nullable=False)
@app.before_request
def create_table():
    db.create_all()
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
@app.route('/home')
@token_required
def home():
    return 'ALL good'
@app.route('/submit_form', methods=['GET'])
def submit_form():
    # Get form data from the request
    form_data = request.form

    # Process the form data
    input1 = form_data.get('input1')
    input2 = form_data.get('input2')

    # Perform any necessary processing or validation
    # For example, you could save the form data to a database

    # Return a JSON response indicating success
    return jsonify({'message': 'Form submitted successfully', 'input1': input1, 'input2': input2})

# class List(db.Model):
#     id=db.Column(db.Integer,primary_key="True")
#     title=db.Column(db.String(50), nullable=False)
#     description=db.Column(db.String(500), nullable=False)
#     status=db.Column(db.String(50), nullable=False)
#     date_created = db.Column(db.DateTime, default=datetime.now)
#     def __repr__(self):
#         return f"{self.title}"
# @app.before_request
# def create_table():
#     db.create_all()
# @app.route('/',methods=["POST","GET"])
# def home():
#     if request.method=="POST":
#         new_instance=List(name=request.form["name"],m_score=request.form["m_score"],p_score=request.form["p_score"],c_score=request.form["c_score"])
#         scores=List.query.filter_by(name=request.form["name"],m_score=request.form["m_score"],p_score=request.form["p_score"],c_score=request.form["c_score"])
#         if scores:
#             return " The response exists."
#         try :
#             db.session.add(new_instance)
#             db.session.commit()
#             return redirect('/')
#         except:
#             return "There is an issue in adding marks"
#     else:
#         list=List.query.all()
#         return render_template('home.html',list=list)
# @app.route('/data/<int:id>')
# def retrieve(id):
#     student=List.query.filter_by(id=id).first()
#     if student:
#         scores=List.query.filter_by(name=student.name)
#         return render_template('data.html',scores=scores)
#     else :
#         return "Id is not valid"
# @app.route('/update/<int:id>',methods=['GET',"POST"])
# def update(id):
#     student=List.query.filter_by(id=id).first()
#     if request.method=="POST":
#         if student:
#             student.m_score=request.form["m_score"]
#             student.p_score=request.form["p_score"]
#             student.c_score=request.form["c_score"]
#             db.session.commit()
#             return redirect('/')
#         else :
            
#             return "Id is not valid"
#     else:
#         return render_template('update.html')
# @app.route('/delete/<int:id>')
# def delete(id):
#     student=List.query.filter_by(id=id).first()
#     if student:
#         db.session.delete(student)
#         db.session.commit()
#         return redirect('/')
#     else :
        
#         return "Id is not valid"

if __name__=="__main__":
    app.run(debug="True")