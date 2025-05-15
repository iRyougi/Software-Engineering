import mysql.connector

class GPA_management:
    def __init__(self, db_config):
        self.db_config = db_config
        self._create_table()

    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)
    
    def _create_table(self):#初始化时如果没有gpa数据表会进行创建
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_gpa (
                student_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                grade VARCHAR(20) NOT NULL,
                gpa DECIMAL(3,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()    

    def add_gpa_record(self, student_id, name, grade, gpa):#插入gpa信息并处理学号重复异常
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO student_gpa (student_id, name, grade, gpa)
                VALUES (%s, %s, %s, %s)
            ''', (student_id, name, grade, gpa))
            conn.commit()
        except mysql.connector.IntegrityError:
            raise ValueError("Student ID already exists")
        finally:
            cursor.close()
            conn.close()

    def get_all_gpa(self):#查询并返回所有gpa记录至下方表单
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM student_gpa')
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records

    def delete_gpa_record(self, student_id):#删除gpa记录
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM student_gpa WHERE student_id = %s', (student_id,))
            if cursor.rowcount == 0:
                raise ValueError("Student record does not exist")
            conn.commit()
        finally:
            cursor.close()
            conn.close()