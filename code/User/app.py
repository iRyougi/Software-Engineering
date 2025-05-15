from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from dataclass import User, DataUser 
import mysql.connector, base64, random
from PyPDF2 import PdfReader
from io import BytesIO
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages


app.config['SECRET_KEY'] = 'your_secret_key'  

# MySQL configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'testdb'
}

data_operation = DataUser(DB_CONFIG)

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Configure Flask-Mail for register application
app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 's230026238@mail.uic.edu.cn'
app.config['MAIL_PASSWORD'] = 'Swjp@#(97=k'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Store verification codes for registration application temporarily
verification_codes = {}

# Updated function to record activity logs
def log_activity(username, activity):
    # First, do a cross-search in the registerapplication table to find the matching row.
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if result and result['fullname']:
        organization = result['fullname']
    else:
        organization = "Unknown"

    # Now store the log with the found organization.
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO activity_logs (username, organization, activity) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, organization, activity))
    connection.commit()
    cursor.close()
    connection.close()

#Home page, app begins here
@app.route('/')
def home():
    return render_template('home.html')

#Register Application page for convener
@app.route('/registerApplication', methods=['GET', 'POST'])
def registerApplication():
    if request.method == 'POST':
        email = request.form['email']
        proof = request.files['pdf_file']
        nameFull = request.form['fullname']
        nameShort = request.form['shortname']
        verification_code = request.form['verification_code']

        # Verify the code
        if email not in verification_codes or verification_codes[email] != verification_code:
            flash('Invalid or missing verification code.', 'error')
            return redirect(url_for('registerApplication'))

        # Validate the uploaded file
        if proof and proof.filename.endswith('.pdf'):
            try:
                pdf_reader = PdfReader(proof)
                # If valid, save the file as a BLOB
                proof.seek(0)  # Reset the file pointer after reading
                proof_data = proof.read()
            except Exception as e:
                flash('Invalid PDF file: ' + str(e), 'error')
                return redirect(url_for('registerApplication'))
        else:
            flash('Please upload a valid PDF file.', 'error')
            return redirect(url_for('registerApplication'))

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Insert the application form into the database
            query = "INSERT INTO registerApplication (email, file, fullname, shortname) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (email, proof_data, nameFull, nameShort))

            # Register the user in the user table
            user_query = """
                INSERT INTO user (username, password, email, usertype, level)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(user_query, (email, verification_code, email, 'O_convener', 3))

            # Commit the transaction
            connection.commit()
            cursor.close()
            flash('Application submitted successfully and user registered!', 'success')
        except Exception as e:
            connection.rollback()
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('registerApplication'))

    return render_template('registerApplication.html')

#Verification for email in Register Application 
@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'}), 400

    # Generate a 4-digit verification code
    code = str(random.randint(1000, 9999))
    verification_codes[email] = code

    # Send the code via email
    try:
        msg = Message('Application Registration Verification Code', sender='s230026238@mail.uic.edu.cn', recipients=[email])
        msg.body = f'Your verification code is: {code}'
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

#E_admin page
@app.route('/E_admin/<string:username>')
def E_admin(username):
    return render_template('E_admin.html', username = username)

#Senior E_admin page
@app.route('/Senior_admin/<string:username>')
def Senior_admin(username):
    return render_template('Senior_admin.html', username = username)

#Review Application (E_admin) 
@app.route('/applicationreview/<string:username>')
def applicationreview(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for easier data handling
    query = "SELECT email, fullname, shortname, file FROM registerapplication WHERE reviewed = FALSE AND status = 0"
    cursor.execute(query)
    applications = cursor.fetchall()
    cursor.close()
    connection.close()

    # Generate a URL for each PDF file
    for application in applications:
        if application['file']:
            # Create a unique route for each file preview
            application['file_url'] = url_for('preview_pdf', shortname=application['shortname'])

    return render_template('applicationreview.html', applications=applications, username=username)

#Review Application (Senior E_admin)
@app.route('/seniorapplicationreview/<string:username>')
def seniorapplicationreview(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for easier data handling
    query = "SELECT email, fullname, shortname, file FROM registerapplication WHERE reviewed = FALSE AND status = 1"
    cursor.execute(query)
    applications = cursor.fetchall()
    cursor.close()
    connection.close()

    # Generate a URL for each PDF file
    for application in applications:
        if application['file']:
            # Create a unique route for each file preview
            application['file_url'] = url_for('preview_pdf', shortname=application['shortname'])

    return render_template('seniorapplicationreview.html', applications=applications, username=username)

#PDF prevew - for application review
@app.route('/preview_pdf/<string:shortname>')
def preview_pdf(shortname):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT file FROM registerapplication WHERE shortname = %s"
    cursor.execute(query, (shortname,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result and result['file']:
        # Serve the PDF file as a response
        return send_file(BytesIO(result['file']), mimetype='application/pdf', download_name=f"{shortname}.pdf")
    else:
        flash("PDF file not found.", "error")
        return redirect(url_for('applicationreview'))

#E_admin : accept registration application
@app.route('/accept_application/<string:shortname>', methods=['POST'])
def accept_application(shortname):
    connection = get_db_connection()
    cursor = connection.cursor()
    # Increment the "status" value by one
    query = """
        UPDATE registerapplication
        SET status = status + 1
        WHERE shortname = %s
    """
    cursor.execute(query, (shortname,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('applicationreview', username=request.args.get('username')))

#Senior E_admin : accept registration application
@app.route('/senioraccept_application/<string:shortname>', methods=['POST'])
def senioraccept_application(shortname):
    connection = get_db_connection()
    cursor = connection.cursor()
    # Increment the "status" value by one
    query = """
        UPDATE registerapplication
        SET status = status + 1,
        reviewed =  TRUE
        WHERE shortname = %s
    """
    cursor.execute(query, (shortname,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('seniorapplicationreview', username=request.args.get('username')))

#Reject registration application
@app.route('/reject_application/<string:shortname>', methods=['POST'])
def reject_application(shortname):
    connection = get_db_connection()
    cursor = connection.cursor()
    # Set "reviewed" to True 
    query = "UPDATE registerapplication SET reviewed = TRUE WHERE shortname = %s"
    cursor.execute(query, (shortname,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('applicationreview', username=request.args.get('username')))


#T_admin page
@app.route('/T_admin/<string:username>')
def T_admin(username):
    return render_template('T_admin.html', username = username)

# Route to display login page
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            # Log the login activity. (Assuming user['organization'] exists; adjust as needed.)
            log_activity(username, "Login")
            if user['usertype'] == 'datauser':
                return render_template('datauser.html', username=username)
            elif user['usertype'] == 'O_convener':
                return render_template('O_convener.html', username=username)
            elif user['usertype'] == 'T_admin':
                return render_template('T_admin.html', username=username)
            elif user['usertype'] == 'Senior_admin':
                return render_template('Senior_admin.html', username=username)
            elif user['usertype'] == 'E_admin':
                return render_template('E_admin.html', username=username)
        else:
            return render_template('failure.html')
    return render_template('index.html')

@app.route('/logout/<string:username>', methods=['GET'])
def logout(username):
    # Here, add additional logout functionality as needed.
    log_activity(username, "Logout")
    return redirect(url_for('index'))

@app.route('/logs/<string:username>', methods=['GET'])
def view_logs(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM activity_logs WHERE 1=1 "  # 1=1 allows easy appending of AND clauses
    filters = []
    
    if request.args.get('activity'):
        query += "AND activity LIKE %s "
        filters.append('%' + request.args.get('activity') + '%')
    if request.args.get('username_filter'):
        query += "AND username = %s "
        filters.append(request.args.get('username_filter'))
    if request.args.get('date'):
        query += "AND DATE(timestamp) = %s "
        filters.append(request.args.get('date'))
    if request.args.get('organization'):
        query += "AND organization = %s "
        filters.append(request.args.get('organization'))
    
    query += "ORDER BY timestamp DESC"
    
    cursor.execute(query, tuple(filters))
    logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('log_management.html', logs=logs, username=username)

@app.route('/datauser/<string:username>')
def datauser(username):
    return render_template('datauser.html', username = username)

@app.route('/browsepolicy/<string:username>')
def browsepolicy(username):
    policies = data_operation.browsePolicy()
    return render_template('browsepolicy.html', policies=policies, username = username)

@app.route('/seekhelp/<string:username>', methods=['GET', 'POST'])
def seekhelp(username):
    if request.method == 'POST':
        question = request.form['question']
        data_operation.seekHelp(username, question)
        return render_template('sendsuccess.html', username = username)
    # Redirect to a success page
    return render_template('seekhelp.html', username = username)

@app.route('/view_questions')
def view_questions():
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling

    # Query the database for all questions
    query = "SELECT username, question, timestamp FROM Userquestion ORDER BY timestamp DESC"
    cursor.execute(query)
    questions = cursor.fetchall()

    # Close the database connection
    cursor.close()
    connection.close()

    # Pass the questions to the template
    return render_template('view_questions.html', questions=questions)

@app.route('/T_admin_questions/<string:username>')
def T_admin_questions(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Get both answered and unanswered questions
    query = """
        SELECT question_id, title, description, email, user_role, 
               submit_time, response_time, response
        FROM userquestion 
        ORDER BY submit_time DESC
    """
    cursor.execute(query)
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('T_admin_questions.html', 
                         questions=questions, 
                         username=username)

@app.route('/answer_question/<int:question_id>', methods=['POST'])
def answer_question(question_id):
    response = request.form.get('response')
    username = request.form.get('username')

    if not response:
        flash('Response cannot be empty', 'error')
        return render_template('T_admin_questions.html', questions=question_id, username=username)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = """
        UPDATE userquestion 
        SET response = %s,
            response_time = CURRENT_TIMESTAMP
        WHERE question_id = %s
    """
    cursor.execute(query, (response, question_id))
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('T_admin_questions', username=username))

# Route to manage policies
@app.route('/manage_policy/<string:username>')
def manage_policy(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id, title FROM policies"
    cursor.execute(query)
    policies = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('policy_management.html', policies=policies, username=username)

# Route to add a new policy
@app.route('/add_policy/<string:username>', methods=['GET', 'POST'])
def add_policy(username):
    if request.method == 'POST':
        title = request.form['title']
        policy_file = request.files.get('policy_file')
        if not title or not policy_file or not policy_file.filename.endswith('.pdf'):
            flash('A valid title and PDF file are required.', 'error')
            return redirect(url_for('add_policy', username=username))
        try:
            policy_data = policy_file.read()
        except Exception as e:
            flash("Error reading file: " + str(e), 'error')
            return redirect(url_for('add_policy', username=username))
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO policies (title, content) VALUES (%s, %s)"
        cursor.execute(query, (title, policy_data))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Policy added successfully.', 'success')
        return redirect(url_for('manage_policy', username=username))
    return render_template('add_policy.html', username=username)

# Route to update an existing policy
@app.route('/update_policy/<int:policy_id>/<string:username>', methods=['GET', 'POST'])
def update_policy(policy_id, username):
    connection = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        policy_file = request.files.get('policy_file')
        cursor = connection.cursor()
        if policy_file and policy_file.filename.endswith('.pdf'):
            policy_data = policy_file.read()
            query = "UPDATE policies SET title=%s, content=%s WHERE id=%s"
            cursor.execute(query, (title, policy_data, policy_id))
        else:
            query = "UPDATE policies SET title=%s WHERE id=%s"
            cursor.execute(query, (title, policy_id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Policy updated successfully.', 'success')
        return redirect(url_for('manage_policy', username=username))
    else:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, title FROM policies WHERE id = %s", (policy_id,))
        policy = cursor.fetchone()
        cursor.close()
        connection.close()
        if policy:
            return render_template('update_policy.html', policy=policy, username=username)
        else:
            flash('Policy not found.', 'error')
            return redirect(url_for('manage_policy', username=username))

# Route to delete a policy
@app.route('/delete_policy/<int:policy_id>/<string:username>', methods=['POST'])
def delete_policy(policy_id, username):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM policies WHERE id=%s"
    cursor.execute(query, (policy_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash('Policy deleted successfully.', 'success')
    return redirect(url_for('manage_policy', username=username))

# New route to preview a policy PDF file by its id
@app.route('/preview_policy/<int:policy_id>/<string:username>')
def preview_policy(policy_id, username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT title, content FROM policies WHERE id = %s"
    cursor.execute(query, (policy_id,))
    policy = cursor.fetchone()
    cursor.close()
    connection.close()
    if policy and policy['content']:
        return send_file(BytesIO(policy['content']),
                         mimetype='application/pdf',
                         download_name=f"{policy['title']}.pdf")
    else:
        flash("PDF file not found.", "error")
        return redirect(url_for('manage_policy', username=username))

if __name__ == '__main__':
    app.run(debug=True)