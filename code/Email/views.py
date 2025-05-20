from flask import Blueprint, render_template, request, redirect
import mysql.connector

# 定义蓝图：名称为 email，模板文件夹是当前目录下的 templates/
email_bp = Blueprint('email_bp', __name__, template_folder='templates')

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'debugdatabase'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@email_bp.route('/')
def email_index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('email_index.html', emails=emails)

@email_bp.route('/write')
def write_email():
    return render_template('write_email.html')

@email_bp.route('/send_email', methods=['POST'])
def send_email():
    sender = "user@example.com"
    recipient = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emails (sender, recipient, subject, body) VALUES (%s, %s, %s, %s)",
        (sender, recipient, subject, body)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/email/complete')

@email_bp.route('/complete')
def email_complete():
    return render_template('email_complete.html')

# 以上代码定义了一个 Flask 蓝图，用于处理电子邮件相关的路由和数据库操作。