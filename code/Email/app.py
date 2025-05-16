from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'email'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/')
def email_index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()
    # print(f"[DEBUG] 查询到 {len(emails)} 封邮件")
    cursor.close()
    conn.close()

    return render_template('email_index.html',emails = emails)



@app.route('/write')
def write_email():
    return render_template('write_email.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    sender = "user@example.com"
    recipient = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']

    # 插入数据库
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emails (sender, recipient, subject, body) VALUES (%s, %s, %s, %s)",
        (sender, recipient, subject, body)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/complete')

@app.route('/complete')
def email_complete():
    return render_template('email_complete.html')

if __name__ == '__main__':
    app.run(debug=True)