from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/view_details')
def details():
    return render_template("view_details.html")


@app.route('/upload')
def upload():
    return render_template("upload.html")


@app.route('/send_mail')
def send_mail():
    return render_template("send_mail.html")


if __name__ == "__main__":
    app.run(debug=True)
