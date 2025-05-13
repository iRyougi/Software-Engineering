from flask import Flask, render_template, request, jsonify
from course_configuration import Course_configuration
import mysql.connector

app = Flask(__name__, template_folder='templates')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'testdb'
}

data_operation = Course_configuration(DB_CONFIG)

def get_db_connection(self):
    return mysql.connector.connect(**self.db_config)

@app.route('/')
def index():
    return render_template('index.html')#5.13 进行过修改 把flask变成渲染主页

@app.route('/courses', methods=['GET'])
def course_page():
    return render_template('course.html')#5.13 新增渲染课程管理页面
@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        courses = data_operation.get_all_courses()
        return jsonify({'status': 'success', 'data': courses})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/add_course', methods=['POST'])
def add_course():
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

@app.route('/edit_course/<int:old_id>', methods=['PUT'])
def edit_course(old_id):
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

    
@app.route('/delete_course/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        data_operation.delete_course(course_id)
        return jsonify({'status': 'success', 'message': 'Delete course successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True,port=5001)