from flask import send_from_directory, Blueprint
from flask import Flask, render_template, request, redirect, url_for
from Data_User.dataclass_datauser import DataUser, Pay
import mysql.connector

datauser_bp = Blueprint('datauser_bp',  __name__, template_folder='templates') 

# MySQL configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'debugdatabase'
}

data_operation = DataUser(DB_CONFIG)
pay_operation = Pay(DB_CONFIG)

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Route to display the main page
@datauser_bp.route('/', methods=['GET', 'POST'])
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

@datauser_bp.route('/datauser/<string:username>')
def datauser(username):
    return render_template('datauser.html', username = username)

@datauser_bp.route('/browsepolicy/<string:username>')
def browsepolicy(username):
    policies = data_operation.browsePolicy(username)
    return render_template('browsepolicy.html', policies=policies, username = username)

@datauser_bp.route('/browselog/<string:username>')
def browselog(username):
    logs = data_operation.browseLog(username)
    return render_template('browselog.html', logs = logs, username = username)

@datauser_bp.route('/browsebankaccount/<string:username>')
def browsebankaccount(username):
    bankaccounts = data_operation.browseBankAccount(username)
    return render_template('browsebankaccount.html', bankaccounts = bankaccounts, username = username)

@datauser_bp.route('/browsestudentrecord/<string:username>')
def browsestudentrecord(username):
    studentrecords = data_operation.browseStudentRecord(username)
    return render_template('browsestudentrecord.html', studentrecords = studentrecords, username = username)

@datauser_bp.route('/browsethesis/<string:username>')
def browsethesis(username):
    thesis = data_operation.browseThesis(username)
    return render_template('browsethesis.html', thesis = thesis, username = username)

@datauser_bp.route('/searchthesis/<string:username>', methods=['GET', 'POST'])
def searchthesis(username):
    if request.method == 'POST':
        keyword = request.form['keyword']
        thesis = data_operation.searchThesisByTitle(username, keyword)
        return render_template('searchthesis.html', 
                             username=username,
                             thesis=thesis,
                             message="No results found" if not thesis else None)
    return render_template('searchthesis.html', username=username)

@datauser_bp.route('/downloadthesis/<string:username>', methods=['GET', 'POST'])
def downloadthesis(username):
    if request.method == 'POST':
        keyword = request.form['keyword']
        thesis = data_operation.searchThesisWithTitle(username, keyword)
        return render_template('downloadthesis.html', 
                             username=username,
                             thesis=thesis,
                             message="No results found" if not thesis else None)
    return render_template('downloadthesis.html', username=username)

@datauser_bp.route('/download/<title>')
def download_thesis(title):
    return send_from_directory('static/thesis', f"{title}.pdf", as_attachment=True)

@datauser_bp.route('/getstudentrecord/<string:username>', methods=['GET', 'POST'])
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

@datauser_bp.route('/checkidentity/<string:username>', methods=['GET', 'POST'])
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

@datauser_bp.route('/seekhelp/<string:username>', methods=['GET', 'POST'])
def seekhelp(username):
    if request.method == 'POST':
        question = request.form['question']
        data_operation.seekHelp(username, question)
        return render_template('sendsuccess.html', username = username)
    # Redirect to a success page
    return render_template('seekhelp.html', username = username)

@datauser_bp.route('/payment/<string:username>')
def payment(username):
    return render_template('payment.html', username = username)

@datauser_bp.route('/transfer/<string:username>')
def transfer(username):
    return render_template('transfer.html', username = username)

@datauser_bp.route('/process_payment/<string:username>', methods=['POST'])
def process_payment(username):
    if request.method == 'POST':
        # 获取所有表单字段
        from_bank = request.form['from_bank']
        from_name = request.form['from_name']
        from_account = request.form['from_account']
        password = request.form['password']
        to_bank = request.form['to_bank']
        to_name = request.form['to_name']
        to_account = request.form['to_account']
        amount = int(request.form['amount'])  # 假设金额为整数
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # 验证源账户信息是否完全匹配
            source_query = """
                SELECT * FROM bankaccount 
                WHERE bank = %s AND account_name = %s AND account_number = %s AND password = %s
            """
            cursor.execute(source_query, (from_bank, from_name, from_account, password))
            source_account = cursor.fetchone()
            
            if not source_account:
                # 源账户验证失败
                cursor.execute(
                    "INSERT INTO activityrecord (username, action) VALUES (%s, %s)",
                    (username, f"Failed transfer: invalid source account information")
                )
                connection.commit()
                cursor.close()
                connection.close()
                return render_template('payfailure.html', username=username, 
                                      error="Invalid source account information. Please check bank, account name, account number and password.")
            
            # 验证目标账户信息是否存在且匹配
            target_query = """
                SELECT * FROM bankaccount 
                WHERE bank = %s AND account_name = %s AND account_number = %s
            """
            cursor.execute(target_query, (to_bank, to_name, to_account))
            target_account = cursor.fetchone()
            
            if not target_account:
                # 目标账户验证失败
                cursor.execute(
                    "INSERT INTO activityrecord (username, action) VALUES (%s, %s)",
                    (username, f"Failed transfer: invalid destination account information")
                )
                connection.commit()
                cursor.close()
                connection.close()
                return render_template('payfailure.html', username=username, 
                                      error="Invalid destination account information. Please check bank, account name and account number.")
            
            # 所有验证都通过，记录转账信息
            transfer_query = """
                INSERT INTO transfer 
                (from_bank, from_name, from_account, password, to_bank, to_name, to_account, amount) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(transfer_query, (
                from_bank, from_name, from_account, password, 
                to_bank, to_name, to_account, amount
            ))
            
            # 记录成功的转账活动
            cursor.execute(
                "INSERT INTO activityrecord (username, action) VALUES (%s, %s)",
                (username, f"Successful transfer of {amount} from {from_bank}/{from_account} to {to_bank}/{to_account}")
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            return render_template('paysuccess.html', username=username, 
                                  amount=amount, from_account=from_account, to_account=to_account)
            
        except Exception as e:
            connection.rollback()
            # 记录错误
            cursor.execute(
                "INSERT INTO activityrecord (username, action) VALUES (%s, %s)",
                (username, f"Transfer error: {str(e)}")
            )
            connection.commit()
            cursor.close()
            connection.close()
            return render_template('payfailure.html', username=username, error=f"An error occurred: {str(e)}")
    
    return redirect(url_for('user_bp.transfer', username=username))

@datauser_bp.route('/vipservice/<string:username>')
def vipservice(username):
    return render_template('vipservice.html', username = username)