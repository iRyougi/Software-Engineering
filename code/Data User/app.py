<<<<<<< HEAD
<<<<<<< HEAD
=======
from flask import send_from_directory
>>>>>>> origin/main
=======
from flask import send_from_directory
>>>>>>> origin/main
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/main
@app.route('/browsestudentrecord/<string:username>')
def browsestudentrecord(username):
    studentrecords = data_operation.browseStudentRecord(username)
    return render_template('browsestudentrecord.html', studentrecords = studentrecords, username = username)

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

<<<<<<< HEAD
>>>>>>> origin/main
=======
>>>>>>> origin/main
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