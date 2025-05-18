from flask import Flask, Blueprint,render_template, request, redirect, url_for,jsonify
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
def login():#用数据库确定登录者是否为管理员
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s AND user_type = %s AND permission_level = %s',(username, password, 'Data_Provider', 3))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return redirect(url_for('user_bp.index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@service_bp.route('/')
def home():#重定向至主页
    return redirect(url_for('service_bp.login'))

@service_bp.route('/index')
def index():
    return render_template('index.html')#5.14新增主界面渲染

@service_bp.route('/courses', methods=['GET'])
def course_page():
    return render_template('course.html')#5.13 新增渲染课程管理页面

@service_bp.route('/api/courses', methods=['GET'])
def get_courses():#从数据库获取所有课程数据并返回JSON格式
    try:
        courses = data_operation.get_all_courses()
        return jsonify({'status': 'success', 'data': courses})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/add_course', methods=['POST'])
def add_course():#接收填入数据，验证课程并添加新课程
    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name')
    description = request.form.get('description')
    try:
        course_id = int(course_id)
        data_operation.add_course(course_id, course_name, description)
        return jsonify({'status': 'success', 'message': 'Add course successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/edit_course/<int:old_id>', methods=['PUT'])
def edit_course(old_id):#更新课程数据时处理旧ID数据防止冲突
    new_id = request.form.get('new_id')
    new_name = request.form.get('new_name')
    new_description = request.form.get('new_description')
    try:
        new_id = int(new_id)
        data_operation.edit_course(old_id, new_id, new_name, new_description)
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
    return render_template('thesis.html')


@service_bp.route('/api/thesis', methods=['GET'])
def get_papers():#从数据库获取所有论文数据并返回JSON格式
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM thesis')
        papers = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': papers})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@service_bp.route('/upload_thesis', methods=['POST'])
def upload_thesis():#处理论文上传与验证标题、作者等必填项
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description')
        file = request.files.get('file')
        
        if not all([title, author, file]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
 
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO thesis (title, author, file_path, description)
            VALUES (%s, %s, %s, %s)
        ''', (title, author, filename, description))
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
    return render_template('gpa.html')

@service_bp.route('/api/gpa', methods=['GET'])
def get_gpa_records():#从数据库获取所有gpa记录并返回JSON格式
    try:
        records = gpa_data_operation.get_all_gpa()
        return jsonify({'status': 'success', 'data': records})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/add_gpa', methods=['POST'])
def add_gpa():#添加gpa
    try:
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        grade = request.form.get('grade')
        gpa = request.form.get('gpa')
        
        if not all([student_id, name, grade, gpa]):
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

        gpa_data_operation.add_gpa_record(student_id, name, grade, gpa)
        return jsonify({'status': 'success', 'message': 'GPA record added successfully'})
    
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@service_bp.route('/delete_gpa/<string:student_id>', methods=['DELETE'])
def delete_gpa(student_id):#删除gpa
    try:
        gpa_data_operation.delete_gpa_record(student_id)
        return jsonify({'status': 'success', 'message': 'GPA record deleted successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500