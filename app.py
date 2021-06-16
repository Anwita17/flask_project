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
import configuration
import mail_config

logging.basicConfig(level=logging.DEBUG)
firebase = pyrebase.initialize_app(configuration.BaseConfig.firebase_config)
auth = firebase.auth()
app = Flask(__name__)
app.secret_key=configuration.BaseConfig.secret_key
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config['SQLALCHEMY_DATABASE_URI'] = configuration.BaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_BINDS']=configuration.BaseConfig.SQLALCHEMY_BINDS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=configuration.BaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)
mail = Mail(app) # instantiate the mail class

app.config['UPLOAD_FOLDER'] = configuration.BaseConfig.UPLOAD_FOLDER 

scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


# configuration of mail
app.config['MAIL_SERVER']=mail_config.mail_conf.MAIL_SERVER
app.config['MAIL_PORT'] = mail_config.mail_conf.MAIL_PORT
app.config['MAIL_USERNAME'] = mail_config.mail_conf.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = mail_config.mail_conf.MAIL_PASSWORD
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
    '''
    Function for sending mail

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
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
        msg = Message(subject = request.form.get('subject'), body = request.form.get('body'), sender = mail_config.mail_conf.MAIL_USERNAME, recipients = [request.form.get('email')])  

        with app.open_resource('Uploader/'+filename) as fp:  
            msg.attach(filename,"application/vnd.ms-excel",fp.read())  
        mail.send(msg)
        return configuration.HtmlConfig.index_html
    except:
        return "email"
    
    
    


def upload_file():
        '''
        Function for uploading the excel file data into the database.
        The data is then converted into dictionary which is then converted to dataframe to remove unnecessary rows and
        uploaded to database.

        Returns:
        String: The name of page to which it needs to be redirected.
        '''
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
                    return configuration.HtmlConfig.upload_html


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
            return configuration.HtmlConfig.index_html
        except:
            return "error"


@app.route(configuration.PageConfig.home_page, methods=['GET', 'POST'])
def index():
    '''
    Function that checks which form is submitted and takes appropriate actions according to it.

    Returns:
    String: The name of page to which it needs to be redirected along with a message 
    '''
    try:
        x=session['user_id']
        
        val=configuration.HtmlConfig.index_html
        msg=""
        if request.method == 'POST':
            
            if 'sm' in request.form: 
                val=snd_mail()
                if val=="email":
                    val=configuration.HtmlConfig.send_mail_html
                    msg="Message cannot be delivered to this domain!"
            if 'up' in request.form:
                val=upload_file()
                if(val==configuration.HtmlConfig.upload_html):
                    msg="Sorry the file for this month already exists!"
                if(val=="error"):
                    val=configuration.HtmlConfig.upload_html
                    msg="Incorrect type of file uploaded. Please check and upload!"
            
            

        
        return render_template(val+".html",msg=msg)
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for(configuration.HtmlConfig.login_html))


@app.route(configuration.PageConfig.details_page,methods=['GET','POST'])
def details():
    '''
    Function for viewing the patching count details of the particular month chosen by the user.

    Returns:
    String: The name of page to which it needs to be redirected along with the details of the query.
    '''
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
                    return render_template(configuration.HtmlConfig.view_details_html+".html",details=details,month=month,year=year,assigned=sum_a,completed=sum_c,remaining=sum_r,
                                        vname=vname,vassigned=vassigned,vcompleted=vcompleted,vrem=vrem)
        
        else:
            return render_template(configuration.HtmlConfig.view_details_html+".html")
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for(configuration.HtmlConfig.login_html))


@app.route(configuration.PageConfig.upload_page,methods=['GET', 'POST'])
def upload():
    '''
    Function for rendering the upload page.

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    try:
        
        x=session['user_id']
        if request.method == 'POST':    
            return redirect(url_for(configuration.PageConfig.home_page))
            
        return render_template(configuration.HtmlConfig.upload_html+".html")
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for(configuration.HtmlConfig.login_html))


@app.route(configuration.PageConfig.send_mail_page,methods=['GET', 'POST'])
def send_mail():
    '''
    Function for rendering the send email page.

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    try:
        x=session['user_id']
        if request.method == 'POST':    
            return redirect(url_for(configuration.PageConfig.home_page))
        return render_template(configuration.HtmlConfig.send_mail_html+".html")
    except KeyError:
        flask.flash('Please Login before proceeding')
        return redirect(url_for(configuration.HtmlConfig.login_html))

@app.route(configuration.PageConfig.login_page,methods=['GET','POST'])
def login():
    '''
    Function for setting the user session if the user already exists.
    

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    if request.method == 'POST':
            if 'logout' in request.form:
                session.pop('user_id',None)
                session.pop('email',None)
                return redirect(url_for(configuration.HtmlConfig.login_html))
    email_id=""
    val=configuration.HtmlConfig.login_html
    msg=""
    try:
        x=session['user_id']
        return redirect(url_for(configuration.HtmlConfig.index_html))
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
                return redirect(url_for(configuration.HtmlConfig.index_html))
            except:
                msg="Incorrect Password!"
        return render_template(val+".html",msg=msg)

@app.route(configuration.PageConfig.register_page,methods=['GET','POST'])
def register():
    '''
    Function for registering the user.
    If new user is registering it checks if the password and confirm password matches or not.If it matches ,
    then it registers the user in the firebase server.

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    val=configuration.HtmlConfig.register_html
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
                        val=configuration.HtmlConfig.login_html
                        msg="User successfully registered!"

                    except Exception as e:
                        val=configuration.HtmlConfig.register_html
                        if "WEAK_PASSWORD" in str(e):
                            msg="Weak Password!"
                        else:
                            msg="User Already Exists!"    
        # return redirect(url_for('/'))
    return render_template(val+".html",msg=msg)

    


c=1
@app.route(configuration.PageConfig.set_reminder_page,methods=['GET','POST'])
def set_reminder():
    '''
    Function for setting the reminder using APScheduler and adding the reminder to the database.

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    try:
        global c
        x=session['user_id']
        msg=""
        if request.method == 'POST':
            title=request.form.get('title')
            desc=request.form.get('desc')
            time_1=request.form.get('time')
            date_1=request.form.get('date')
            d_list=date_1.split("-")
            t_list=time_1.split(':')
            eid=session['email']
            mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            date_str=str(mon[int(d_list[1])-1])+" "+str(d_list[2])+" "+str(d_list[0])
            datetime_object = datetime.strptime(date_str+" "+str(time_1), '%b %d %Y %H:%M')
            if datetime.now()<datetime_object:
                task = Task(title=title, desc=desc,usr_nm=eid,date_rem=date_1,time_rem=time_1)
                db.session.add(task)
                db.session.commit()
                usr_id=Task.query.filter_by(date_rem=date_1,time_rem=time_1,usr_nm=eid).first()
                @scheduler.task('cron',id=str(usr_id.sno),day=d_list[2],month=d_list[1],year=d_list[0],hour=t_list[0],minute=t_list[1])
                def job1():
                    global c
                    with app.test_request_context():
                        try:
                            
                            details=Task.query.filter_by(date_rem=date_1,time_rem=time_1,usr_nm=eid).first()
                            db.session.delete(details)
                            db.session.commit()
                            msg = Message(subject = title, body = desc, sender = mail_config.mail_conf.MAIL_USERNAME, recipients = [eid])  
                            mail.send(msg)
                            
                            
                            app.logger.info('Mail sent')                    
                        except Exception as e:
                            print(e)
            
                msg="Reminder Set Successfully!"   
            else:
                msg="Please set a proper time!" 
        return render_template(configuration.HtmlConfig.set_reminder_html+'.html',msg=msg)
    except KeyError:
        flash('Please Login before proceeding')
        return redirect(url_for(configuration.HtmlConfig.login_html))



@app.route(configuration.PageConfig.view_reminder_page,methods=['GET','POST'])
def view_reminder():
    '''
    Function to render the view reminder page and filtering the reminder according to the session of the user.

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    try:
        x=session['user_id']
        details=Task.query.filter_by(usr_nm=session['email'])
        return render_template(configuration.HtmlConfig.view_reminder_html+'.html',details=details)
    except KeyError:
        flash('Please Login before proceeding')
        return redirect(url_for(configuration.HtmlConfig.login_html))

@app.route(configuration.PageConfig.delete_page)
def delete(sno):
    '''
    Function for deleting a task from the database by its primary key

    Returns:
    String: The name of page to which it needs to be redirected.
    '''
    try:
        task=Task.query.filter_by(sno=sno).first()
        db.session.delete(task)
        db.session.commit()
        scheduler.delete_job(id=str(sno))
    except Exception as e:
        print(e)
    return redirect(url_for(configuration.HtmlConfig.view_reminder_html))


if __name__ == "__main__":
    '''
    Main Function from where execution begins
    
    '''
    db.create_all()
    app.run(debug=True)
