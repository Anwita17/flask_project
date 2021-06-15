from enum import auto
import flask
from flask.helpers import flash
import pandas as pd
from flask import Flask, render_template,request, redirect, url_for,session,g
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from sqlalchemy.sql.elements import Null
from werkzeug.utils import secure_filename
import os
import logging
import sys
from datetime import datetime,timedelta,date
import pyrebase
from flask_apscheduler import APScheduler
from celery import Celery
from apscheduler.schedulers.blocking import BlockingScheduler

config={
    "apiKey": "AIzaSyDVlVnZHhNYlMD5ZXRf4mZQDpj9wWypcpI",
    "authDomain": "pcount-users.firebaseapp.com",
    "projectId": "pcount-users",
    "databaseURL":"",
    "storageBucket": "pcount-users.appspot.com",
    "messagingSenderId": "51521810156",
    "appId": "1:51521810156:web:9e9954f2b7c5c768aaffc9",
    "measurementId": "G-PN455M9936"
}
logging.basicConfig(level=logging.DEBUG)
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
app = Flask(__name__)
app.secret_key="fdsfsdafsdfdsfn,dsfmnas,thisshouldbethewierdestsecretkeypossible"
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///p_count.db'
app.config['SQLALCHEMY_BINDS']={'two':'sqlite:///task.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
mail = Mail(app) # instantiate the mail class
UPLOAD_FOLDER = './Uploader'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


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

class Task(db.Model):
    __bind_key__='two'
    sno=db.Column(db.Integer,autoincrement=True,primary_key=True)
    title=db.Column(db.String(80))
    desc=db.Column(db.String(200))
    usr_nm=db.Column(db.String(80))
    date_rem=db.Column(db.String(80))
    time_rem=db.Column(db.String(80))

def snd_mail():
    comm_email=['gmail.com','outlook.com','yahoo.com','hotmail.com','rediff.com']
    eid=str(request.form.get('email'))
    edomain=eid.split('@')
    try:
        if edomain[1] not in comm_email:
            
            raise "email"
        # print(edomain[1])
        file=request.files['finput']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        # print(request.form.get('subject'))
        msg = Message(subject = request.form.get('subject'), body = request.form.get('body'), sender = "anonymousanwitashobhit@outlook.com", recipients = [request.form.get('email')])  

        with app.open_resource('Uploader/'+filename) as fp:  
            msg.attach(filename,"application/vnd.ms-excel",fp.read())  
        mail.send(msg)
        return "index"
    except:
        return "email"
    
    
    


def upload_file():
        try:
            xlsx_file = request.files['file']
            data_xls = pd.read_excel(xlsx_file,'Overview',usecols="A:G")
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
        except:
            return "error"


@app.route('/home', methods=['GET', 'POST'])
def index():
    try:
        x=session['user_id']
        
        val="index"
        msg=""
        if request.method == 'POST':
            
            if 'sm' in request.form: 
                val=snd_mail()
                if val=="email":
                    val="send_mail"
                    msg="Message cannot be delivered to this domain!"
            if 'up' in request.form:
                val=upload_file()
                if(val=="upload"):
                    msg="Sorry the file for this month already exists!"
                if(val=="error"):
                    val="upload"
                    msg="Incorrect type of file uploaded. Please check and upload!"
            
            

        
        return render_template(val+".html",msg=msg)
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for('login'))

@app.route('/view_details',methods=['GET','POST'])
def details():
    try:
        # print(session['email'])
        x=session['user_id']
        month_ar=['January','February','March','April','May','June','July','August','September','October','November','December']
        get_month=request.form.get('month')
        
        if get_month!=None and get_month!='':
            
            if 'data' in request.form: 
                    get_month=str(request.form.get('month'))
                    ar=get_month.split("-")
                    year=int(ar[0])
                    month=month_ar[int(ar[1])-1]
                    details=User.query.filter_by(month=month,year=year)
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
        
        else:
            return render_template("view_details.html")
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for('login'))


@app.route('/upload',methods=['GET', 'POST'])
def upload():
    try:
        
        x=session['user_id']
        if request.method == 'POST':    
            return redirect(url_for('/home'))
            
        return render_template("upload.html")
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for('login'))


@app.route('/send_mail',methods=['GET', 'POST'])
def send_mail():
    try:
        x=session['user_id']
        if request.method == 'POST':    
            return redirect(url_for('/home'))
        return render_template("send_mail.html")
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for('login'))

@app.route('/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
            if 'logout' in request.form:
                session.pop('user_id',None)
                session.pop('email',None)
                return redirect(url_for('login'))
    email_id=""
    val="login"
    msg=""
    try:
        x=session['user_id']
        return redirect(url_for('index'))
    except KeyError:
        if request.method == 'POST':
            user=request.form.get('email')
            password=request.form.get('pass')
            try:
                user_info=auth.sign_in_with_email_and_password(user,password)
                user_info=auth.refresh(user_info['refreshToken'])
                account_info=auth.get_account_info(user_info['idToken'])
                session['email']=account_info['users'][0]['email']
                session['user_id']=user_info['idToken']
                return redirect(url_for('index'))
            except:
                msg="Incorrect Password!"
            if 'rg' in request.form:    
                user=request.form.get("email")
                password=request.form.get("pass")
                cpassword=request.form.get("cpass")
                # print(1)
                if password != cpassword:
                    # print(password)
                    val="register"
                    msg="Passwords do not match!"
                else:
                    try:
                        new_user=auth.create_user_with_email_and_password(user,password)

                    except Exception as e:
                        val="register"
                        if "WEAK_PASSWORD" in str(e):
                            msg="Weak Password!"
                        else:
                            msg="User Already Exists!"

        
        return render_template(val+".html",msg=msg)

@app.route('/register',methods=['GET','POST'])
def register():
    val="register"
    msg=""
    if request.method == 'POST':
        if 'rg' in request.form:    
                user=request.form.get("email")
                password=request.form.get("pass")
                cpassword=request.form.get("cpass")
                # print(1)
                if password != cpassword:
                    
                    msg="Passwords do not match!"
                else:
                    try:
                        new_user=auth.create_user_with_email_and_password(user,password)
                        val="login"
                        msg="User successfully registered!"

                    except Exception as e:
                        val="register"
                        if "WEAK_PASSWORD" in str(e):
                            msg="Weak Password!"
                        else:
                            msg="User Already Exists!"    
        # return redirect(url_for('/'))
    return render_template(val+".html",msg=msg)

def mail_reminder(title,desc):
    comm_email=['gmail.com','outlook.com','yahoo.com','hotmail.com','rediff.com']
    eid=session['email']
    edomain=eid.split('@')
    try:
        if edomain[1] not in comm_email:
            
            raise "email"
        msg = Message(subject = title, body = desc, sender = "anonymousanwitashobhit@outlook.com", recipients = [eid])  
        mail.send(msg)
        
    except:
        pass
    

    
c=0
job_list=[]

@app.route('/set_reminder',methods=['GET','POST'])
def set_reminder():
    try:
        x=session['user_id']
        msg=""
        global job_list
        if request.method == 'POST':
            title=request.form.get('title')
            desc=request.form.get('desc')
            time_1=request.form.get('time')
            date_1=request.form.get('date')
            d_list=date_1.split("-")
            t_list=time_1.split(':')
            eid=session['email']
            task = Task(title=title, desc=desc,usr_nm=eid,date_rem=date_1,time_rem=time_1)
            db.session.add(task)
            db.session.commit()
            @scheduler.task('cron',day=d_list[2],month=d_list[1],year=d_list[0],hour=t_list[0],minute=t_list[1])
            def job1():
                with app.test_request_context():
                    comm_email=['gmail.com','outlook.com','yahoo.com','hotmail.com','rediff.com']
                    edomain=eid.split('@')
                    try:
                        if edomain[1] not in comm_email:
                            raise "email"
                        msg = Message(subject = title, body = desc, sender = "anonymousanwitashobhit@outlook.com", recipients = [eid])  
                        print('hello')
                        app.logger.info('Mail sent')                    
                    except:
                        pass

            mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            date_str=str(mon[int(d_list[1])-1])+" "+str(d_list[2])+" "+str(d_list[0])
            datetime_object = datetime.strptime(date_str+" "+str(time_1), '%b %d %Y %H:%M')
            x= datetime_object-datetime.now()
            print(x)
            global mail
            
            msg="Reminder Set Successfully!"    
        return render_template('set_reminder.html',msg=msg)
    except KeyError:
        flash('Please Login before proceeding')
        return redirect(url_for('login'))

# @sched.scheduled_job('cron',day=d_list[2],month=d_list[1],year=d_list[0],hour=t_list[0],minute=t_list[1])



@app.route('/view_reminder',methods=['GET','POST'])
def view_reminder():
    try:
        x=session['user_id']
        details=Task.query.filter_by(usr_nm=session['email'])
        return render_template('view_reminder.html',details=details)
    except KeyError:
        flash('Please Login before proceeding')
        return redirect(url_for('login'))

@app.route('/delete/<int:sno>')
def delete(sno):
    task=Task.query.filter_by(sno=sno).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('view_reminder'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
