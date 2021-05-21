from enum import auto
import pandas as pd
from flask import Flask, render_template,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from sqlalchemy.sql.elements import Null
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
    cluster_rem_12c= db.Column(db.Integer)
    restart_assigned_12c= db.Column(db.Integer)
    restart_completed_12c= db.Column(db.Integer)
    restart_rem_12c= db.Column(db.Integer)
    total_assigned= db.Column(db.Integer)
    total_completed= db.Column(db.Integer)
    total_rem= db.Column(db.Integer)
    month=db.Column(db.String(80))
    year=db.Column(db.Integer)
    
    def __repr__(self) -> str:
        return f"{self.sno}-{self.dba}-{self.cluster_assigned_12c}-{self.cluster_completed_12c}-{self.restart_assigned_12c}-{self.restart_completed_12c}-{self.total_assigned}-{self.total_completed}"

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
        month_ar=['January','February','March','April','May','June','July','August','September','October','November','December']
        get_month=str(request.form.get('month'))
        ar=get_month.split("-")
        year=int(ar[0])
        month=month_ar[int(ar[1])-1]
        for value in db.session.query(User.month,User.year).distinct():
            if(month==value[0] and year==value[1]):
                 return "upload"

        # print(mon)
        for ind in df.index:
            user = User(dba=df["DBA_Name"][ind], cluster_assigned_12c=df["12c_clusters_assigned"][ind],cluster_completed_12c=df["12c_clusters_completed"][ind],
            cluster_rem_12c=df["12c_clusters_assigned"][ind]-df["12c_clusters_completed"][ind],
            restart_assigned_12c=df["12c_restarts_assigned"][ind],restart_completed_12c=df["12c_restarts_completed"][ind],
            restart_rem_12c=df["12c_restarts_assigned"][ind]-df["12c_restarts_completed"][ind],
            total_assigned=df["total_assigned"][ind],
            total_completed=df["total_completed"][ind],total_rem=df["total_assigned"][ind]-df["total_completed"][ind],
            month=month,year=year)
            db.session.add(user)
            db.session.commit()
        return "index"

@app.route('/', methods=['GET', 'POST'])
def index():
    #print('ind')
    val="index"
    msg=""
    if request.method == 'POST':
        if 'sm' in request.form: 
            snd_mail()
        if 'up' in request.form:
            val=upload_file()
            if(val=="upload"):
                msg="Sorry the file for this month already exists!"
        
       

    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #    # next(csv_reader)
    #     for row in csv_reader:
    #         user = User(dba=row[0], cluster_assigned_12c=row[1],cluster_completed_12c=row[2],
    #         restart_assigned_12c=row[3],restart_completed_12c=row[4],total_assigned=row[5],
    #         total_completed=row[6])
    #         db.session.add(user)
    #         db.session.commit()
    return render_template(val+".html",msg=msg)


@app.route('/view_details',methods=['GET','POST'])
def details():
    month_ar=['January','February','March','April','May','June','July','August','September','October','November','December']
    get_month=request.form.get('month')
    
    if get_month!=None and get_month!='':
        
        if 'data' in request.form: 
                get_month=str(request.form.get('month'))
                ar=get_month.split("-")
                year=int(ar[0])
                month=month_ar[int(ar[1])-1]
                details=User.query.filter_by(month=month,year=year)
                # details=db.session.query(User.dba.distinct(),User.cluster_assigned_12c,
                #                          User.cluster_completed_12c,User.cluster_rem_12c,
                #                          User.restart_assigned_12c,User.restart_assigned_12c,
                #                          User.restart_rem_12c,User.total_assigned,User.total_completed,
                #                          User.total_rem
                #                          ).filter_by(month = month, year=year).all()
                sum_a=0
                sum_c=0
                sum_r=0
                vname=[]
                vassigned=[]
                vcompleted=[]
                vrem=[]
                vname=[]
                for var in details:
                    sum_a=sum_a+var.total_assigned
                    sum_c=sum_c+var.total_completed
                    vname.append(var.dba)
                    vassigned.append(var.total_assigned)
                    vcompleted.append(var.total_completed)
                    vrem.append(var.total_rem)
                sum_r=sum_a-sum_c
                return render_template("view_details.html",details=details,month=month,year=year,assigned=sum_a,completed=sum_c,remaining=sum_r,
                                       vname=vname,vassigned=vassigned,vcompleted=vcompleted,vrem=vrem)
        # if 'charts' in request.form:
        #     print('chart')
        #     cmonth=request.form.get('gmonth')
        #     cyear=request.form.get('gyear')
        #     details=User.query.filter_by(month=cmonth,year=cyear)
        #     sum_a=0
        #     sum_c=0
        #     sum_r=0
            # vcompleted=[]
            # vassigned=[]
            # vrem=[]
            # vname=[]
        #     for var in details:
        #         sum_a=sum_a+var.total_assigned
        #         sum_c=sum_c+var.total_completed
        #         vname.append(var.dba)
        #         vassigned.append(var.total_assigned)
        #         vcompleted.append(var.total_completed)
        #         vrem.append(var.total_rem)
        #     sum_r=sum_a-sum_c
        #     return render_template("view_details.html",details=details,month=cmonth,year=cyear,assigned=sum_a,completed=sum_c,
        #                            remaining=sum_r,vname=vname,vassigned=vassigned,vcompleted=vcompleted,vrem=vrem)
    else:
        return render_template("view_details.html")
    


@app.route('/upload',methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':    
        return redirect(url_for('/'))
        
    return render_template("upload.html")

@app.route('/send_mail',methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':    
        return redirect(url_for('/'))
    return render_template("send_mail.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
