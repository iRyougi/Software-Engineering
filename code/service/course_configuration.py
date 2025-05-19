import mysql.connector

class Course_configuration:
    def __init__(self, db_config):
        self.db_config = db_config
        self._create_table()

    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def _create_table(self):#初始化时如果课程数据不存在自动创建课程数据表
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INT PRIMARY KEY,
                course_name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                organization VARCHAR(255)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def add_course(self, course_id, course_name, description, organization):  # add organization
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM courses WHERE id = %s', (course_id,))
            if cursor.fetchone():
                raise ValueError(f"Course ID {course_id} already exists")

            cursor.execute(
                'INSERT INTO courses (id, course_name, description, organization) VALUES (%s, %s, %s, %s)',
                (course_id, course_name, description, organization)
            )
            conn.commit()
        except mysql.connector.IntegrityError as e:
            if "Duplicate entry" in str(e):
                raise ValueError(f"Course name '{course_name}' already exists")
            else:
                raise e
        finally:
            cursor.close()
            conn.close()

    def edit_course(self, old_id, new_id, new_name, new_description, new_organization):  # add organization
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if old_id != new_id:
                cursor.execute('SELECT id FROM courses WHERE id = %s', (new_id,))
                if cursor.fetchone():
                    raise ValueError(f"CourseID {new_id} already exists")

            cursor.execute(
                'UPDATE courses SET id = %s, course_name = %s, description = %s, organization = %s WHERE id = %s',
                (new_id, new_name, new_description, new_organization, old_id)
            )
            if cursor.rowcount == 0:
                raise ValueError("Course is not exist")
            conn.commit()
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            if "Duplicate entry" in str(e):
                raise ValueError(f"Course name '{new_name}' already exists")
            else:
                raise e
        finally:
            cursor.close()
            conn.close()
    
    def delete_course(self, course_id): #删除课程
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM courses WHERE id = %s',
            (course_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError("Course does not exists")
        conn.commit()
        cursor.close()
        conn.close()

    def get_all_courses(self):#查询并返回所有课程数据以呈现在页面下方列表
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return courses

    def get_courses_by_organization(self, organization):
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM courses WHERE organization = %s', (organization,))
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return courses