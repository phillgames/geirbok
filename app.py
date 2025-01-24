import re
from flask import Flask, request, render_template, url_for, redirect, session # type: ignore
from werkzeug.security import generate_password_hash # type: ignore
from flask_mail import Mail, Message #type: ignore
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user #type: ignore
import uuid
import pymysql # type: ignore
import socket
pymysql.install_as_MySQLdb()

app = Flask(__name__, static_folder='static', template_folder='templates')

# secret_key = uuid.uuid4()
# app.secret_key = secret_key
# login_manager = LoginManager()
# login_manager.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'geir.translator.services@gmail.com'
app.config['MAIL_PASSWORD'] = 'hbwj lnbx yeqh rife'

mail = Mail(app)

db_config = {
    'host': 'localhost',
    'user': 'geir',
    'password': 'password',
    'database': 'geirbok'
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id
    
    @staticmethod
    def get(user_id):
        conn =pymysql.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (id))


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
IPAddr = s.getsockname()[0]
s.close()
print(IPAddr)


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/login')
def login():
    if request.method == 'POST':
        if valid_username_password(request.form['fullname'], request.form['password']): # type: ignore
            session['logged_in'] = True

            return redirect(url_for('protected'))
        else:
            error = 'Invalid username or password'
            return render_template('form.html')
    else:
        return render_template('form.html')

@app.route('/Verify-account')
def Verify():
    verify_code = request.args.get('token')
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE verify = %s"
    cursor.execute(query, (verify_code))
    rowcount = cursor.rowcount

    if rowcount == 0:
        return "Sorry something went wrong!"
    else:
        query = "UPDATE users SET verified = %s WHERE verify = %s"
        cursor.execute(query, (True, verify_code))
        conn.commit()
        return render_template('Verify-account.html')

    # If found - set "verified true" and render "verified.html"
    # UPDATE users SET verified = true WHERE  verify = token"
    # If not found - render "not_verified.html"


    return render_template('Verify-account.html')

# @app.route('/submit')
# def submit():
#     return render_template('submit.html')

@app.route("/submit", methods=["POST"])
def submit():
    fullname = request.form["fullname"]
    password = request.form["password"]
    email = request.form["email"]
    verifcode = uuid.uuid4()

    if not is_valid_email(email):
        return

    hashed_password = generate_password_hash(password)



    try:
        str(uuid.uuid4())
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO users (user, email, pass, verify, verified) VALUES (%s, %s, %s, %s, false)"
        cursor.execute(query, (fullname, email, hashed_password, verifcode))
        conn.commit()
        cursor.close()
        conn.close()

        subject = "Welcome to Geirbok!"
        body = f"Hi {fullname},\n\nHello! Your account has been created successfully.\n\nClick this link http://{IPAddr}:5000/Verify-account?token={verifcode} \n\nto verify your account\n\n Best regards, \n\nThe Geirbok Team"


        msg = Message(subject, sender="your-email@gmail.com", recipients=[email])
        msg.body = body
        mail.send(msg)
        return render_template('main.html')
    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/update_score", methods=["POST"])
def update_score():
    username = request.form["username"]
    new_score = request.form["score"]

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        query = "UPDATE users Set score = %s WHERE user =%s"
        cursor.execute(query, (new_score, username))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('main.html')
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)