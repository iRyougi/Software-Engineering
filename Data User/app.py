from flask import Flask, render_template, request, redirect, url_for
from dataclass import DataUser, Pay
import mysql.connector

# Initialize Flask app
app = Flask(__name__)

# MySQL configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'testdb'
}
1
data_operation = DataUser(DB_CONFIG)
pay_operation = Pay(DB_CONFIG)

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Route to display the main page
@app.route('/', methods=['GET', 'POST'])
def index():
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
    return render_template('datauser.html', username = username)

@app.route('/browsepolicy/<string:username>')
def browsepolicy(username):
    policies = data_operation.browsePolicy(username)
    return render_template('browsepolicy.html', policies=policies, username = username)

@app.route('/browselog/<string:username>')
def browselog(username):
    logs = data_operation.browseLog(username)
    return render_template('browselog.html', logs = logs, username = username)

@app.route('/browsebankaccount/<string:username>')
def browsebankaccount(username):
    bankaccounts = data_operation.browseBankAccount(username)
    return render_template('browsebankaccount.html', bankaccounts = bankaccounts, username = username)

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
    
if __name__ == '__main__':
    app.run(debug=True)