from enum import auto
import pandas as pd
from flask import Flask, render_template,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from werkzeug.utils import secure_filename
import os
import logging
import sys
from datetime import datetime

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///p_count.db'
db = SQLAlchemy(app)
mail = Mail(app) # instantiate the mail class
UPLOAD_FOLDER = './Uploader'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
   
# configuration of mail
app.config['MAIL_SERVER']='smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'anonymousanwitashobhit@outlook.com'
app.config['MAIL_PASSWORD'] = 'Anonymous22'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

class User(db.Model):
    sno=db.Column(db.Integer,autoincrement=True,primary_key=True)
    dba = db.Column(db.String(80))
    cluster_assigned_12c= db.Column(db.Integer)
    cluster_completed_12c= db.Column(db.Integer)
    #cluster_rem_12c= db.Column(db.Integer)
    restart_assigned_12c= db.Column(db.Integer)
    restart_completed_12c= db.Column(db.Integer)
    #restart_rem_12c= db.Column(db.Integer)
    total_assigned= db.Column(db.Integer)
    #total_rem= db.Column(db.Integer)
    total_completed= db.Column(db.Integer)
    month=db.Column(db.String(80))
    year=db.Column(db.Integer)
    
    def __repr__(self) -> str:
        return f"{self.dba}-{self.cluster_assigned_12c}"

def snd_mail():
    file=request.files['finput']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    print('2')
    print(request.form.get('subject'))
    msg = Message(subject = request.form.get('subject'), body = request.form.get('body'), sender = "anonymousanwitashobhit@outlook.com", recipients = [request.form.get('email')])  
    print('3')

    with app.open_resource('Uploader/'+filename) as fp:  
        msg.attach(filename,"application/vnd.ms-excel",fp.read())  
    mail.send(msg)

def upload_file():
        xlsx_file = request.files['file']
        data_xls = pd.read_excel(xlsx_file)
        data_xls.columns=["DBA_Name","12c_clusters_assigned",
        "12c_clusters_completed",
        "12c_restarts_assigned"
       ,"12c_restarts_completed"
        ,"total_assigned"
        ,"total_completed"]
        dict1=data_xls.to_dict()
        df=pd.DataFrame(dict1)
        df.drop(0,inplace=True)
        df.drop(df.tail(1).index,inplace=True)
        df.reset_index(drop=True)
        month_form=request.form.get('month')
        year_calc=int(datetime.today().year)
        for ind in df.index:
            # print(df["DBA_Name"][ind])
            user = User(dba=df["DBA_Name"][ind], cluster_assigned_12c=df["12c_clusters_assigned"][ind],cluster_completed_12c=df["12c_clusters_completed"][ind],
            restart_assigned_12c=df["12c_restarts_assigned"][ind],restart_completed_12c=df["12c_restarts_completed"][ind],total_assigned=df["total_assigned"][ind],
            total_completed=df["total_completed"][ind],month=month_form,year=year_calc)
            db.session.add(user)
            db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    print('ind')
    if request.method == 'POST':
        print('0')
        if 'sm' in request.form: 
            print('sm')
            snd_mail()
        if 'up' in request.form:
            print('p_count')
            upload_file()
       

    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #    # next(csv_reader)
    #     for row in csv_reader:
    #         user = User(dba=row[0], cluster_assigned_12c=row[1],cluster_completed_12c=row[2],
    #         restart_assigned_12c=row[3],restart_completed_12c=row[4],total_assigned=row[5],
    #         total_completed=row[6])
    #         db.session.add(user)
    #         db.session.commit()
    return render_template("index.html")


@app.route('/view_details')
def details():
    return render_template("view_details.html")


@app.route('/upload',methods=['GET', 'POST'])
def upload():
    
    mon=[]
    for value in db.session.query(User.month).distinct():
        mon.append(value[0])

    if request.method == 'POST':    
        return redirect(url_for('/'))
        
    return render_template("upload.html",month=mon)

@app.route('/send_mail',methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':    
        return redirect(url_for('/'))
    return render_template("send_mail.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
