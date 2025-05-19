import mysql.connector

class GPA_management:
    def __init__(self, db_config):
        self.db_config = db_config
        self._create_table()

    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def _create_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpa_records (
                student_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255),
                grade VARCHAR(50),
                gpa FLOAT,
                organization VARCHAR(255)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def add_gpa_record(self, student_id, name, grade, gpa, organization):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT student_id FROM student_gpa WHERE student_id = %s', (student_id,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise ValueError(f"Student ID {student_id} already exists")
        cursor.execute(
            'INSERT INTO student_gpa (student_id, name, grade, gpa, organization) VALUES (%s, %s, %s, %s, %s)',
            (student_id, name, grade, gpa, organization)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def edit_gpa_record(self, student_id, name, grade, gpa, organization):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE student_gpa SET name = %s, grade = %s, gpa = %s, organization = %s WHERE student_id = %s',
            (name, grade, gpa, organization, student_id)
        )
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise ValueError("GPA record does not exist")
        conn.commit()
        cursor.close()
        conn.close()

    def delete_gpa_record(self, student_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM student_gpa WHERE student_id = %s', (student_id,))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise ValueError("GPA record does not exist")
        conn.commit()
        cursor.close()
        conn.close()

    def get_all_gpa(self):
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM student_gpa')
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records

    def get_gpa_by_organization(self, organization):
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM student_gpa WHERE organization = %s', (organization,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records