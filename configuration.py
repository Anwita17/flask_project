class BaseConfig:
    firebase_config={
    "apiKey": "AIzaSyDVlVnZHhNYlMD5ZXRf4mZQDpj9wWypcpI",
    "authDomain": "pcount-users.firebaseapp.com",
    "projectId": "pcount-users",
    "databaseURL":"",
    "storageBucket": "pcount-users.appspot.com",
    "messagingSenderId": "51521810156",
    "appId": "1:51521810156:web:9e9954f2b7c5c768aaffc9",
    "measurementId": "G-PN455M9936"
}
    secret_key="fdsfsdafsdfdsfn,dsfmnas,thisshouldbethewierdestsecretkeypossible"
    SQLALCHEMY_DATABASE_URI='sqlite:///p_count.db'
    SQLALCHEMY_BINDS={'two':'sqlite:///task.db'}
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    UPLOAD_FOLDER = './Uploader'

class PageConfig:
    home_page='/home'
    details_page='/view_details'
    upload_page='/upload'
    send_mail_page='/send_mail'
    login_page='/'
    register_page='/register'
    set_reminder_page='/set_reminder'
    view_reminder_page='/view_reminder'
    delete_page='/delete/<int:sno>'

class HtmlConfig:
    index_html='index'
    login_html='login'
    register_html='register'
    send_mail_html='send_mail'
    set_reminder_html='set_reminder'
    upload_html='upload'
    view_reminder_html='view_reminder'
    view_details_html='view_details'
