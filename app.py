import pandas as pd
from flask import Flask, render_template,request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///p_count.db'
db = SQLAlchemy(app)

class User(db.Model):
    dba = db.Column(db.String(80),primary_key=True)
    cluster_assigned_12c= db.Column(db.Integer)
    cluster_completed_12c= db.Column(db.Integer)
    #cluster_rem_12c= db.Column(db.Integer)
    restart_assigned_12c= db.Column(db.Integer)
    restart_completed_12c= db.Column(db.Integer)
    #restart_rem_12c= db.Column(db.Integer)
    total_assigned= db.Column(db.Integer)
    #total_rem= db.Column(db.Integer)
    total_completed= db.Column(db.Integer)
    
    def __repr__(self) -> str:
        return f"{self.dba}-{self.cluster_assigned_12c}"
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
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
        for ind in df.index:
            # print(df["DBA_Name"][ind])
            user = User(dba=df["DBA_Name"][ind], cluster_assigned_12c=df["12c_clusters_assigned"][ind],cluster_completed_12c=df["12c_clusters_completed"][ind],
            restart_assigned_12c=df["12c_restarts_assigned"][ind],restart_completed_12c=df["12c_restarts_completed"][ind],total_assigned=df["total_assigned"][ind],
            total_completed=df["total_completed"][ind])
            db.session.add(user)
            db.session.commit()

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
    
     if request.method == 'POST':    
        return redirect(url_for('/'))
        
     return render_template("upload.html")

@app.route('/send_mail')
def send_mail():
    return render_template("send_mail.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
