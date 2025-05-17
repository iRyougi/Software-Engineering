from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, jsonify, flash
from flask_mail import Mail, Message
import mysql.connector
import os
import random
import base64
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key'

# ---- 数据库配置（可统一管理） ----
DB_CONFIG_TESTDB = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'testdb'
}
DB_CONFIG_EMAIL = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'email'
}

# 初始化操作对象
data_operation = DataUser(DB_CONFIG_TESTDB)
pay_operation = Pay(DB_CONFIG_TESTDB)
course_operation = Course_configuration(DB_CONFIG_TESTDB)
gpa_operation = GPA_management(DB_CONFIG_TESTDB)

# Flask-Mail配置
app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'xxxx'
app.config['MAIL_PASSWORD'] = 'xxxx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# ========== 各个模块的路由合并 ==========

@app.route('/user/')
def user_home():
    # 你的User原来/路由逻辑
    return render_template('home.html')

# ==== Data User模块，路由加前缀 /datauser ====
@app.route('/datauser/', methods=['GET', 'POST'])
def datauser_index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        # Query the database for the user
        query = "SELECT * FROM user WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchall()  # Fetch the first matching row
        # Check if the user exists
        if user:
            query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
            cursor.execute(query, (username, "Login successfully"))
            connection.commit()
            cursor.close()
            connection.close()
            return render_template('loginsuccess.html', username=username)
        else:
            cursor.close()
            connection.close()
            return render_template('loginfailure.html')
    return render_template('index.html')

@app.route('/datauser/<string:username>')
def datauser(username):
    return render_template('datauser.html', username=username)

@app.route('/browsepolicy/<string:username>')
def browsepolicy(username):
    policies = data_operation.browsePolicy(username)
    return render_template('browsepolicy.html', policies=policies, username=username)

@app.route('/browselog/<string:username>')
def browselog(username):
    logs = data_operation.browseLog(username)
    return render_template('browselog.html', logs=logs, username=username)

@app.route('/browsebankaccount/<string:username>')
def browsebankaccount(username):
    bankaccounts = data_operation.browseBankAccount(username)
    return render_template('browsebankaccount.html', bankaccounts=bankaccounts, username=username)

@app.route('/browsestudentrecord/<string:username>')
def browsestudentrecord(username):
    studentrecords = data_operation.browseStudentRecord(username)
    return render_template('browsestudentrecord.html', studentrecords=studentrecords, username=username)

@app.route('/browsethesis/<string:username>')
def browsethesis(username):
    thesis = data_operation.browseThesis(username)
    return render_template('browsethesis.html', thesis = thesis, username = username)

@app.route('/searchthesis/<string:username>', methods=['GET', 'POST'])
def searchthesis(username):
    if request.method == 'POST':
        keyword = request.form['keyword']
        thesis = data_operation.searchThesisByTitle(username, keyword)
        return render_template('searchthesis.html', 
                             username=username,
                             thesis=thesis,
                             message="No results found" if not thesis else None)
    return render_template('searchthesis.html', username=username)

@app.route('/downloadthesis/<string:username>', methods=['GET', 'POST'])
def downloadthesis(username):
    if request.method == 'POST':
        keyword = request.form['keyword']
        thesis = data_operation.searchThesisWithTitle(username, keyword)
        return render_template('downloadthesis.html', 
                             username=username,
                             thesis=thesis,
                             message="No results found" if not thesis else None)
    return render_template('downloadthesis.html', username=username)

@app.route('/download/<title>')
def download_thesis(title):
    return send_from_directory('static/thesis', f"{title}.pdf", as_attachment=True)

@app.route('/getstudentrecord/<string:username>', methods=['GET', 'POST'])
def getstudentrecord(username):
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        try:
            student_id = int(student_id)
        except ValueError:
            return render_template('getstudentrecord.html', 
                                 username=username, 
                                 error="ID must be a number")
        studentrecords = data_operation.getStudentRecordByIdAndName(username, student_id, name)
        return render_template('getstudentrecord.html', 
                             username=username, 
                             studentrecords=studentrecords)
    return render_template('getstudentrecord.html', username=username)

@app.route('/checkidentity/<string:username>', methods=['GET', 'POST'])
def checkidentity(username):
    result = None
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        dob = request.form.get('dob')
        try:
            student_id = int(student_id)
        except ValueError:
            return render_template('checkidentity.html', 
                                 username=username, 
                                 error="ID must be a number")
        exists = data_operation.checkIdentity(username, student_id, name, dob)
        result = "Yes" if exists else "No"
    return render_template('checkidentity.html', 
                         username=username, 
                         result=result)

@app.route('/seekhelp/<string:username>', methods=['GET', 'POST'])
def seekhelp(username):
    if request.method == 'POST':
        question = request.form['question']
        data_operation.seekHelp(username, question)
        return render_template('sendsuccess.html', username = username)
    # Redirect to a success page
    return render_template('seekhelp.html', username = username)

@app.route('/payment/<string:username>')
def payment(username):
    return render_template('payment.html', username = username)

@app.route('/transfer/<string:username>')
def transfer(username):
    return render_template('transfer.html', username = username)

@app.route('/process_payment/<string:username>', methods=['POST'])
def process_payment(username):
    if request.method == 'POST':
        amount = float(request.form['amount'])
        account = request.form['account']
        password = request.form['password']
        if pay_operation.payProcess(username, amount, account, password):
            return render_template('paysuccess.html', username = username)
        else:
            return render_template('payfailure.html', username = username)
    return redirect(url_for('transfer', username = username))

@app.route('/vipservice/<string:username>')
def vipservice(username):
    return render_template('vipservice.html', username = username)

# ==== Service模块，路由加前缀 /service ====
@app.route('/service/')
def service_index():
    # ...
    return render_template('index.html')

# ========== Email模块路由，全部加 /email 前缀 ==========
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG_EMAIL)

@app.route('/email/')
def email_index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()
    # print(f"[DEBUG] 查询到 {len(emails)} 封邮件")
    cursor.close()
    conn.close()

    return render_template('email_index.html',emails = emails)

@app.route('/email/write')
def write_email():
    return render_template('write_email.html')

@app.route('/email/send_email', methods=['POST'])
def send_email():
    sender = "user@example.com"
    recipient = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']

    # 插入数据库
    conn = mysql.connector.connect(**DB_CONFIG_EMAIL)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emails (sender, recipient, subject, body) VALUES (%s, %s, %s, %s)",
        (sender, recipient, subject, body)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/complete')

@app.route('/email/complete')
def email_complete():
    return render_template('email_complete.html')

# ========== 启动 ==========
if __name__ == '__main__':
    app.run(debug=True)