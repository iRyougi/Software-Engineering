from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import mysql.connector, base64, random
from PyPDF2 import PdfReader
from io import BytesIO
import pandas as pd
from User.dataclass_user import DataUser
from flask_mail import Mail

user_bp = Blueprint('user_bp', __name__, template_folder='templates') 

# MySQL configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'debugdatabase'
}

data_operation = DataUser(DB_CONFIG)

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

mail = Mail()

def init_mail(app):
    mail.init_app(app)

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
@user_bp.route('/')
def home():
    return render_template('home.html')

#Register Application page for convener
@user_bp.route('/registerApplication', methods=['GET', 'POST'])
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
@user_bp.route('/send_verification_code', methods=['POST'])
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
@user_bp.route('/E_admin/<string:username>')
def E_admin(username):
    return render_template('E_admin.html', username = username)

#Senior E_admin page
@user_bp.route('/Senior_admin/<string:username>')
def Senior_admin(username):
    return render_template('Senior_admin.html', username = username)

#Review Application (E_admin) 
@user_bp.route('/applicationreview/<string:username>')
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
            application['file_url'] = url_for('user_bp.preview_pdf', shortname=application['shortname'])

    return render_template('applicationreview.html', applications=applications, username=username)

#Review Application (Senior E_admin)
@user_bp.route('/seniorapplicationreview/<string:username>')
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
@user_bp.route('/preview_pdf/<string:shortname>')
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
@user_bp.route('/accept_application/<string:shortname>', methods=['POST'])
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
@user_bp.route('/senioraccept_application/<string:shortname>', methods=['POST'])
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
@user_bp.route('/reject_application/<string:shortname>', methods=['POST'])
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
@user_bp.route('/T_admin/<string:username>')
def T_admin(username):
    return render_template('T_admin.html', username = username)

# Route to display login page
@user_bp.route('/index', methods=['GET', 'POST'])
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
            elif user['usertype'] == 'Data_consumer':
                return render_template('data_consumer.html', username=username)
        else:
            return render_template('failure.html')
    return render_template('index.html')

@user_bp.route('/logout/<string:username>', methods=['GET'])
def logout(username):
    # Here, add additional logout functionality as needed.
    log_activity(username, "Logout")
    return redirect(url_for('user_bp.index'))

@user_bp.route('/logs/<string:username>', methods=['GET'])
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

@user_bp.route('/datauser/<string:username>')
def datauser(username):
    return render_template('datauser.html', username = username)

@user_bp.route('/browsepolicy/<string:username>')
def browsepolicy(username):
    policies = data_operation.browsePolicy()
    return render_template('browsepolicy.html', policies=policies, username = username)

@user_bp.route('/seekhelp/<string:username>', methods=['GET', 'POST'])
def seekhelp(username):
    if request.method == 'POST':
        question = request.form['question']
        data_operation.seekHelp(username, question)
        return render_template('sendsuccess.html', username = username)
    # Redirect to a success page
    return render_template('seekhelp.html', username = username)

@user_bp.route('/view_questions')
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

@user_bp.route('/T_admin_questions/<string:username>')
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

@user_bp.route('/answer_question/<int:question_id>', methods=['POST'])
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
@user_bp.route('/manage_policy/<string:username>')
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
@user_bp.route('/add_policy/<string:username>', methods=['GET', 'POST'])
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
@user_bp.route('/update_policy/<int:policy_id>/<string:username>', methods=['GET', 'POST'])
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
@user_bp.route('/delete_policy/<int:policy_id>/<string:username>', methods=['POST'])
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
@user_bp.route('/preview_policy/<int:policy_id>/<string:username>')
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
    
#O_convener page
@user_bp.route('/O_convener/<string:username>')
def O_convener(username):
    # Get organization full name for this convener
    connection_org = get_db_connection()
    cursor_org = connection_org.cursor(dictionary=True)
    query_org = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
    cursor_org.execute(query_org, (username,))
    result_org = cursor_org.fetchone()
    cursor_org.close()
    connection_org.close()
    if result_org and result_org['fullname']:
        organization = result_org['fullname']
    else:
        organization = "Unknown"

    return render_template('O_convener.html', username = username, organization=organization)

@user_bp.route('/upload_members_page/<string:username>')
def upload_members_page(username):
    # Render the upload page
    return render_template('upload_members.html', username=username)

# Route to show all members for the convener
@user_bp.route('/manage_members/<string:username>')
def manage_members(username):
    connection_org = get_db_connection()
    cursor_org = connection_org.cursor(dictionary=True)
    query_org = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
    cursor_org.execute(query_org, (username,))
    result_org = cursor_org.fetchone()
    cursor_org.close()
    connection_org.close()
    if result_org and result_org['fullname']:
        organization = result_org['fullname']
    else:
        organization = "Unknown"
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM e_dba_members WHERE organization=%s"
    cursor.execute(query, (organization,))
    members = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('manage_members.html', members=members, username=username)

@user_bp.route('/add_member_page/<string:username>')
def add_member_page(username):
    # Render the add_members page
    return render_template('add_member.html', username=username)

@user_bp.route('/edit_member_page/<string:username>')
def edit_member_page(username):
    # Render the add_members page
    return render_template('edit_member.html', username=username)

# Route for uploading the Excel file containing the member list
@user_bp.route('/upload_members/<string:username>', methods=['GET', 'POST'])
def upload_members(username):
    if request.method == 'POST':
        if 'excel_file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('upload_members', username=username))
        file = request.files['excel_file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('upload_members', username=username))
        if file and file.filename.endswith(('.xls', '.xlsx')):
            try:
                # Retrieve the o-convener's organization full name from registerapplication table
                connection_org = get_db_connection()
                cursor_org = connection_org.cursor(dictionary=True)
                query_org = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
                cursor_org.execute(query_org, (username,))
                result_org = cursor_org.fetchone()
                cursor_org.close()
                connection_org.close()
                if result_org and result_org['fullname']:
                    organization = result_org['fullname']
                else:
                    organization = "Unknown"

                # Read the excel file using pandas
                df = pd.read_excel(file)
                # Process each row
                connection = get_db_connection()
                cursor = connection.cursor()
                for index, row in df.iterrows():
                    name = row.get('name')
                    email = row.get('email')
                    access_right = row.get('access right')
                    quota = row.get('Quota for thesis download')
                    
                    # If name is missing, treat it as NULL
                    if pd.isna(name):
                        name = None
                        
                    # Insert (or update) record using the organization full name
                    query = """
                        INSERT INTO e_dba_members (organization, name, email, access_right, thesis_quota)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE name=VALUES(name), access_right=VALUES(access_right), thesis_quota=VALUES(thesis_quota)
                    """
                    cursor.execute(query, (organization, name, email, access_right, quota))
                connection.commit()
                cursor.close()
                connection.close()
                flash('Member list uploaded successfully!', 'success')
            except Exception as e:
                flash('Error processing file: ' + str(e), 'error')
        else:
            flash('Please upload a valid Excel file.', 'error')
        return redirect(url_for('O_convener', username=username))
    return render_template('upload_members.html', username=username)

# Route to add an individual member
@user_bp.route('/add_member/<string:username>', methods=['GET', 'POST'])
def add_member(username):
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        access_right = request.form.get('access_right')
        quota = request.form.get('thesis_quota')
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            connection_org = get_db_connection()
            cursor_org = connection_org.cursor(dictionary=True)
            query_org = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
            cursor_org.execute(query_org, (username,))
            result_org = cursor_org.fetchone()
            cursor_org.close()
            connection_org.close()
            if result_org and result_org['fullname']:
                organization = result_org['fullname']
            else:
                organization = "Unknown"

            query = "INSERT INTO e_dba_members (organization, name, email, access_right, thesis_quota) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (organization, name, email, access_right, quota))
            connection.commit()
            flash('Member added successfully.', 'success')
        except Exception as e:
            connection.rollback()
            flash('Error adding member: ' + str(e), 'error')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('manage_members', username=username))
    return render_template('add_member.html', username=username)

# Route to edit an individual member
@user_bp.route('/edit_member/<int:member_id>/<string:username>', methods=['GET', 'POST'])
def edit_member(member_id, username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    connection_org = get_db_connection()
    cursor_org = connection_org.cursor(dictionary=True)
    query_org = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
    cursor_org.execute(query_org, (username,))
    result_org = cursor_org.fetchone()
    cursor_org.close()
    connection_org.close()
    if result_org and result_org['fullname']:
        organization = result_org['fullname']
    else:
        organization = "Unknown"

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        access_right = request.form.get('access_right')
        quota = request.form.get('thesis_quota')
        try:
            query = "UPDATE e_dba_members SET name=%s, email=%s, access_right=%s, thesis_quota=%s WHERE id=%s"
            cursor.execute(query, (name, email, access_right, quota, member_id))
            connection.commit()
            flash('Member updated successfully.', 'success')
        except Exception as e:
            connection.rollback()
            flash('Error updating member: ' + str(e), 'error')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('manage_members', username=username))
    else:
        query = "SELECT * FROM e_dba_members WHERE id=%s"
        cursor.execute(query, (member_id,))
        member = cursor.fetchone()
        cursor.close()
        connection.close()
        if member:
            return render_template('edit_member.html', member=member, username=username)
        else:
            flash('Member not found.', 'error')
            return redirect(url_for('manage_members', username=username))

# Route to delete an individual member
@user_bp.route('/delete_member/<int:member_id>/<string:username>', methods=['POST'])
def delete_member(member_id, username):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM e_dba_members WHERE id=%s"
        cursor.execute(query, (member_id,))
        connection.commit()
        flash('Member deleted successfully.', 'success')
    except Exception as e:
        connection.rollback()
        flash('Error deleting member: ' + str(e), 'error')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('manage_members', username=username))

@user_bp.route('/banking_info/<string:username>', methods=['GET', 'POST'])
def banking_info(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM o_convener_banking WHERE username = %s"
    cursor.execute(query, (username,))
    bank_info = cursor.fetchone()

    if request.method == 'POST':
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        account_name = request.form.get('account_name')
        password = request.form.get('password')
        
        if bank_info:
            update_query = """
                UPDATE o_convener_banking 
                SET bank_name=%s, account_number=%s, account_name=%s, password=%s 
                WHERE username=%s
            """
            cursor.execute(update_query, (bank_name, account_number, account_name, password, username))
            flash('Banking info updated successfully!', 'success')
        else:
            insert_query = """
                INSERT INTO o_convener_banking (username, bank_name, account_number, account_name, password)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (username, bank_name, account_number, account_name, password))
            flash('Banking info added successfully!', 'success')
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('O_convener', username=username))
    else:
        cursor.close()
        connection.close()
        return render_template('banking_info.html', username=username, bank_info=bank_info)

@user_bp.route('/o_convener_logs/<string:username>', methods=['GET'])
def o_convener_logs(username):
    # Get organization full name for this convener
    connection_org = get_db_connection()
    cursor_org = connection_org.cursor(dictionary=True)
    query_org = "SELECT fullname FROM registerapplication WHERE email = %s ORDER BY id DESC LIMIT 1"
    cursor_org.execute(query_org, (username,))
    result_org = cursor_org.fetchone()
    cursor_org.close()
    connection_org.close()
    if result_org and result_org['fullname']:
        organization = result_org['fullname']
    else:
        organization = "Unknown"

    # Build query for logs
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM activity_logs WHERE organization = %s"
    filters = [organization]

    # Optional filters
    if request.args.get('activity'):
        query += " AND activity LIKE %s"
        filters.append('%' + request.args.get('activity') + '%')
    if request.args.get('username_filter'):
        query += " AND username = %s"
        filters.append(request.args.get('username_filter'))
    if request.args.get('date'):
        query += " AND DATE(timestamp) = %s"
        filters.append(request.args.get('date'))

    query += " ORDER BY timestamp DESC"
    cursor.execute(query, tuple(filters))
    logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('o_convener_logs.html', logs=logs, username=username)


@user_bp.route('/manage_workspace/<string:username>', methods=['GET', 'POST'])
def manage_workspace(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT fullname FROM registerapplication WHERE email=%s ORDER BY id DESC LIMIT 1", (username,))
    org_row = cursor.fetchone()
    organization = org_row['fullname'] if org_row and org_row['fullname'] else "Unknown"
    cursor.execute("SELECT * FROM workspaces WHERE organization=%s", (organization,))
    workspace = cursor.fetchone()
    if request.method == 'POST':
        course_sharing = bool(request.form.get('course_sharing'))
        id_authentication = bool(request.form.get('id_authentication'))
        id_price = request.form.get('id_price') or 0
        thesis_sharing = bool(request.form.get('thesis_sharing'))
        thesis_price = request.form.get('thesis_price') or 0
        if workspace:
            query = """UPDATE workspaces SET course_sharing=%s, id_authentication=%s, id_price=%s,
                       thesis_sharing=%s, thesis_price=%s WHERE organization=%s"""
            cursor.execute(query, (course_sharing, id_authentication, id_price, thesis_sharing, thesis_price, organization))
        else:
            query = """INSERT INTO workspaces (organization, course_sharing, id_authentication, id_price, thesis_sharing, thesis_price)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (organization, course_sharing, id_authentication, id_price, thesis_sharing, thesis_price))
        connection.commit()
        cursor.execute("SELECT * FROM workspaces WHERE organization=%s", (organization,))
        workspace = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('manage_workspace.html', workspace=workspace, organization=organization, username=username)

@user_bp.route('/data_consumer/<string:username>', methods=['GET'])
def data_consumer(username):
    # Show search page, optionally with results
    org_query = request.args.get('org_query')
    workspaces = []
    if org_query:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM workspaces WHERE organization LIKE %s", ('%' + org_query + '%',))
        workspaces = cursor.fetchall()
        cursor.close()
        connection.close()
    return render_template('data_consumer.html', username=username, workspaces=workspaces)

@user_bp.route('/search_workspace/<string:username>', methods=['GET'])
def search_workspace(username):
    org_query = request.args.get('org_query')
    workspaces = []
    if org_query:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM workspaces WHERE organization LIKE %s", ('%' + org_query + '%',))
        workspaces = cursor.fetchall()
        cursor.close()
        connection.close()
    return render_template('data_consumer.html', username=username, workspaces=workspaces)

@user_bp.route('/workspace/<string:username>/<string:organization>')
def workspace(username, organization):
    # Get user level
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT level FROM user WHERE username=%s", (username,))
    user = cursor.fetchone()
    user_level = int(user['level']) if user and user['level'] else 1
    cursor.execute("SELECT * FROM workspaces WHERE organization=%s", (organization,))
    workspace = cursor.fetchone()
    cursor.close()
    connection.close()
    if not workspace:
        flash('Workspace not found.', 'error')
        return redirect(url_for('user_bp.data_consumer', username=username))
    return render_template('workspace.html', username=username, organization=organization, workspace=workspace, user_level=user_level)