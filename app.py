from flask import Flask,request,redirect,render_template
from sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
db=SQLAlchemy(app)
class List(db.Model):
    id=db.Column(db.Integer,primary_key="True")
    title=db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(500), nullable=False)
    status=db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f"{self.title}"
@app.before_request
def create_table():
    db.create_all()
@app.route('/',methods=["POST","GET"])
def home():
    if request.method=="POST":
        new_instance=List(name=request.form["name"],m_score=request.form["m_score"],p_score=request.form["p_score"],c_score=request.form["c_score"])
        scores=List.query.filter_by(name=request.form["name"],m_score=request.form["m_score"],p_score=request.form["p_score"],c_score=request.form["c_score"])
        if scores:
            return " The response exists."
        try :
            db.session.add(new_instance)
            db.session.commit()
            return redirect('/')
        except:
            return "There is an issue in adding marks"
    else:
        list=List.query.all()
        return render_template('home.html',list=list)
@app.route('/data/<int:id>')
def retrieve(id):
    student=List.query.filter_by(id=id).first()
    if student:
        scores=List.query.filter_by(name=student.name)
        return render_template('data.html',scores=scores)
    else :
        return "Id is not valid"
@app.route('/update/<int:id>',methods=['GET',"POST"])
def update(id):
    student=List.query.filter_by(id=id).first()
    if request.method=="POST":
        if student:
            student.m_score=request.form["m_score"]
            student.p_score=request.form["p_score"]
            student.c_score=request.form["c_score"]
            db.session.commit()
            return redirect('/')
        else :
            
            return "Id is not valid"
    else:
        return render_template('update.html')
@app.route('/delete/<int:id>')
def delete(id):
    student=List.query.filter_by(id=id).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return redirect('/')
    else :
        
        return "Id is not valid"

if __name__=="__main__":
    app.run(debug="True")