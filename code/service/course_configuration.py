import mysql.connector

class Course_configuration:
    def __init__(self, db_config):
        self.db_config = db_config
        self._create_table()

    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def _create_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INT PRIMARY KEY,
                course_name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT  
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def add_course(self, course_id, course_name, description):#add course
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM courses WHERE id = %s', (course_id,))
            if cursor.fetchone():
                raise ValueError(f"Course ID {course_id} already exists")

            cursor.execute(
                'INSERT INTO courses (id, course_name, description) VALUES (%s, %s, %s)',  
                (course_id, course_name, description)  
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

    def edit_course(self, old_id, new_id, new_name, new_description):#edit course
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if old_id != new_id:
                cursor.execute('SELECT id FROM courses WHERE id = %s', (new_id,))
                if cursor.fetchone():
                    raise ValueError(f"CourseID {new_id} already exist")

            cursor.execute(
                'UPDATE courses SET id = %s, course_name = %s, description = %s WHERE id = %s',
                (new_id, new_name, new_description, old_id)
            )
            if cursor.rowcount == 0:
                raise ValueError("Course is not exist")
            conn.commit()
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            if "Duplicate entry" in str(e):
                raise ValueError(f"Course name '{new_name}' already exist")
            else:
                raise e
        finally:
            cursor.close()
            conn.close()
    
    def delete_course(self, course_id): #delete course 
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM courses WHERE id = %s',
            (course_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError("Course does not exist")
        conn.commit()
        cursor.close()
        conn.close()

    def get_all_courses(self):#check all the course from sql and give a list
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return courses