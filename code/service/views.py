from flask import Flask, Blueprint,render_template, request, redirect, url_for,jsonify, session
from service.course_configuration import Course_configuration
from service.gpa_management import GPA_management
import mysql.connector
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

service_bp = Blueprint('service_bp', __name__, template_folder='templates') 

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'debugdatabase'
}

data_operation = Course_configuration(DB_CONFIG)
gpa_data_operation = GPA_management(DB_CONFIG)

@service_bp.route('/login', methods=['GET', 'POST'])
def login():  # 用数据库确定登录者是否为管理员
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user'] = user  # Store the whole user row (including 'level') in session
            session['username'] = user['username']  # Optionally store username for convenience
            return redirect(url_for('service_bp.portal'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@service_bp.route('/')
def home():#重定向至主页
    return redirect(url_for('service_bp.login'))

@service_bp.route('/portal')
def portal():
    return render_template('portal.html')#5.14新增主界面渲染

@service_bp.route('/courses', methods=['GET'])
def course_page():
    user_level = get_user_level()  # Implement this to get current user's level
    if user_level == 3:
        return render_template('course.html')
    else:
        return render_template('course_viewonly.html')

@service_bp.route('/api/courses', methods=['GET'])
def get_courses():#从数据库获取所有课程数据并返回JSON格式
    try:
        organization = request.args.get('organization')
        if organization:
            courses = data_operation.get_courses_by_organization(organization)
        else:
            courses = data_operation.get_all_courses()
        return jsonify({'status': 'success', 'data': courses})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/add_course', methods=['POST'])
def add_course():
    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name')
    description = request.form.get('description')
    organization = request.form.get('organization')  # new
    try:
        course_id = int(course_id)
        data_operation.add_course(course_id, course_name, description, organization)
        return jsonify({'status': 'success', 'message': 'Add course successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/edit_course/<int:old_id>', methods=['PUT'])
def edit_course(old_id):
    new_id = request.form.get('new_id')
    new_name = request.form.get('new_name')
    new_description = request.form.get('new_description')
    new_organization = request.form.get('new_organization')  # new
    try:
        new_id = int(new_id)
        data_operation.edit_course(old_id, new_id, new_name, new_description, new_organization)
        return jsonify({'status': 'success', 'message': 'Edit course successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    
@service_bp.route('/delete_course/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):#根据ID删除数据库中课程信息
    try:
        data_operation.delete_course(course_id)
        return jsonify({'status': 'success', 'message': 'Delete course successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@service_bp.route('/thesis')#5.14新增论文界面渲染
def thesis_management():
    user_level = get_user_level()
    if user_level == 3:
        return render_template('thesis.html')
    else:
        return render_template('thesis_viewonly.html')


@service_bp.route('/api/thesis', methods=['GET'])
def get_papers():
    try:
        organization = request.args.get('organization')
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        if organization:
            cursor.execute('SELECT * FROM thesis WHERE organization = %s', (organization,))
        else:
            cursor.execute('SELECT * FROM thesis')
        papers = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': papers})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@service_bp.route('/upload_thesis', methods=['POST'])
def upload_thesis():
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        organization = request.form.get('organization')
        description = request.form.get('description')
        file = request.files.get('file')

        if not all([title, author, organization, file]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO thesis (title, author, organization, file_path, description)
            VALUES (%s, %s, %s, %s, %s)
        ''', (title, author, organization, filename, description))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Thesis uploaded successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/uploads/<filename>')
def download_file(filename):#提供文件下载接口
    return send_from_directory('uploads', filename)

@service_bp.route('/delete_thesis/<int:thesis_id>', methods=['DELETE'])
def delete_thesis(thesis_id):#删除论文记录与文件（文件本体依然留在uploads文件夹中）
    try:
        file_path = request.args.get('filePath')

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM thesis WHERE id = %s', (thesis_id,))
        if cursor.rowcount == 0:
            raise ValueError("Thesis does not exist")
        conn.commit()
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        return jsonify({'status': 'success', 'message': 'thesis deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@service_bp.route('/gpa')#5.15新增gpa管理界面渲染
def gpa_management():
    user_level = get_user_level()
    if user_level == 3:
        return render_template('gpa.html')
    elif user_level == 2:
        return render_template('gpa_viewonly.html')
    else:
        return "Access Denied", 403

@service_bp.route('/api/gpa', methods=['GET'])
def get_gpa_records():
    try:
        organization = request.args.get('organization')
        if organization:
            records = gpa_data_operation.get_gpa_by_organization(organization)
        else:
            records = gpa_data_operation.get_all_gpa()
        return jsonify({'status': 'success', 'data': records})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/add_gpa', methods=['POST'])
def add_gpa():
    try:
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        grade = request.form.get('grade')
        gpa = request.form.get('gpa')
        organization = request.form.get('organization')
        
        if not all([student_id, name, grade, gpa, organization]):
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

        gpa_data_operation.add_gpa_record(student_id, name, grade, gpa, organization)
        return jsonify({'status': 'success', 'message': 'GPA record added successfully'})
    
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/edit_gpa/<string:student_id>', methods=['PUT'])
def edit_gpa(student_id):
    try:
        name = request.form.get('name')
        grade = request.form.get('grade')
        gpa = request.form.get('gpa')
        organization = request.form.get('organization')
        if not all([name, grade, gpa, organization]):
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
        gpa_data_operation.edit_gpa_record(student_id, name, grade, gpa, organization)
        return jsonify({'status': 'success', 'message': 'GPA record updated successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/delete_gpa/<string:student_id>', methods=['DELETE'])
def delete_gpa(student_id):
    try:
        gpa_data_operation.delete_gpa_record(student_id)
        return jsonify({'status': 'success', 'message': 'GPA record deleted successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/edit_thesis/<int:thesis_id>', methods=['PUT'])
def edit_thesis(thesis_id):
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        organization = request.form.get('organization')
        description = request.form.get('description')
        if not all([title, author, organization]):
            return jsonify({'status': 'error', 'message': 'Title, author, and organization are required'}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE thesis
            SET title = %s, author = %s, organization = %s, description = %s
            WHERE id = %s
        ''', (title, author, organization, description, thesis_id))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Thesis not found'}), 404
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Thesis updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_user_level():
    """
    Returns the user's level as an integer.
    Assumes user info is stored in session after login.
    If not found, returns 1 (lowest access) by default.
    """
    # If you store user info in session after login:
    user = session.get('user')
    if user and 'level' in user:
        return int(user['level'])
    
    # If not in session, try to get from database using username in session
    username = session.get('username')
    if username:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT level FROM users WHERE username = %s', (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row and 'level' in row:
            return int(row['level'])
    
    # Default: lowest access
    return 1