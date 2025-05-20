import mysql.connector
import os

class DataUser():
  def __init__(self, db_config):
    self.db_config = db_config
  def get_db_connection(self):
    return mysql.connector.connect(**self.db_config)
  
  def browsePolicy(self, username):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling
    cursor.execute("SELECT * FROM policy")
    policies = cursor.fetchall()
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, "Browse policies"))
    connection.commit()
    cursor.close()
    connection.close()
    return policies
  
  def browseLog(self, username):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling
    cursor.execute("SELECT * FROM activityrecord")
    logs = cursor.fetchall()
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, "Browse logs"))
    connection.commit()
    cursor.close()
    connection.close()
    return logs
  
  def browseBankAccount(self, username):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling
    cursor.execute("SELECT * FROM bankaccount")
    bankaccounts = cursor.fetchall()
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, "Browse bank accounts"))
    connection.commit()
    cursor.close()
    connection.close()
    return bankaccounts
  
  def browseStudentRecord(self, username):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling
    cursor.execute("SELECT * FROM studentrecord")
    studentrecords = cursor.fetchall()
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, "Browse student records"))
    connection.commit()
    cursor.close()
    connection.close()
    return studentrecords
  
  def getStudentRecordByIdAndName(self, username, student_id, name):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM studentrecord WHERE id = %s AND name = %s"
    cursor.execute(query, (student_id, name))
    records = cursor.fetchall()
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, f"Search student record by ID {student_id} and name {name}"))
    connection.commit()
    cursor.close()
    connection.close()
    return records
  
  def checkIdentity(self, username, student_id, name, photo=None):
      connection = self.get_db_connection()
      cursor = connection.cursor(dictionary=True)
      
      # 首先验证学生ID和姓名是否存在
      query = """
          SELECT * FROM studentrecord 
          WHERE id = %s AND name = %s
      """
      cursor.execute(query, (student_id, name))
      record = cursor.fetchone()
      
      is_verified = False
      
      if record:
          # 学生记录存在，检查照片文件名
          if photo and hasattr(photo, 'filename'):
              try:
                  # 统一处理名字和文件名：移除所有空格和下划线
                  simple_name = name.lower().replace(" ", "").replace("_", "")
                  simple_filename = photo.filename.lower().replace(" ", "").replace("_", "")
                  simple_filename = os.path.splitext(simple_filename)[0]  # 移除扩展名
                  
                  # 使用包含关系进行匹配
                  if simple_name == simple_filename or simple_name in simple_filename or simple_filename in simple_name:
                      is_verified = True
                      action = f"Identity verified for ID {student_id}, Name {name}, Photo matched: {photo.filename}"
                  else:
                      action = f"Identity check failed for ID {student_id}, Name {name}, Photo didn't match: {photo.filename}"
              except Exception as e:
                  action = f"Error checking identity for ID {student_id}, Name {name}: {str(e)}"
          else:
              # 没有提供照片
              action = f"Identity check incomplete for ID {student_id}, Name {name}, No photo provided"
      else:
          # 学生记录不存在
          action = f"Identity check failed for ID {student_id}, Name {name}, Student not found in database"
          if photo and hasattr(photo, 'filename'):
              action += f", Photo provided: {photo.filename}"
      
      # 记录活动
      cursor.execute("INSERT INTO activityrecord (username, action) VALUES (%s, %s)",
                    (username, action))
      
      connection.commit()
      cursor.close()
      connection.close()
      
      return is_verified

  def browseThesis(self, username):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling
    cursor.execute("SELECT * FROM thesis")
    thesis = cursor.fetchall()
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, "Browse thesis"))
    connection.commit()
    cursor.close()
    connection.close()
    return thesis
  
  def searchThesisByTitle(self, username, keyword):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM thesis WHERE title LIKE %s"
    cursor.execute(query, ('%' + keyword + '%',))
    results = cursor.fetchall()
    action = f"Search thesis by keyword '{keyword}'"
    cursor.execute("INSERT INTO activityrecord (username, action) VALUES (%s, %s)", (username, action))
    connection.commit()
    cursor.close()
    connection.close()
    return results
  
  def searchThesisWithTitle(self, username, keyword):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM thesis WHERE title = %s"  #different with searchThesisByTitle
    cursor.execute(query, (keyword,))  
    results = cursor.fetchall()
    action = f"Search thesis by keyword '{keyword}'"
    cursor.execute("INSERT INTO activityrecord (username, action) VALUES (%s, %s)", (username, action))
    connection.commit()
    cursor.close()
    connection.close()
    return results

  def seekHelp(self, username, question):
    connection = self.get_db_connection()
    cursor = connection.cursor()
    # Insert the question into the database
    query = "INSERT INTO userquestion (username, question) VALUES (%s, %s)"
    cursor.execute(query, (username, question))
    query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
    cursor.execute(query, (username, "Seek help"))
    connection.commit()
    # Close the database connection
    cursor.close()
    connection.close()

  
class Pay():
  def __init__(self, db_config):
    self.db_config = db_config
  def get_db_connection(self):
    return mysql.connector.connect(**self.db_config)
  
  def payProcess(self, username, amount, account_sender, password_sender):
    account_receiver = "ProjectFundSDW"
    password_receiver = "789"
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT balance FROM bankaccount WHERE account = %s AND password = %s"
    cursor.execute(query, (account_sender, password_sender))
    balance_sender = cursor.fetchall()
    #Get the balance from the sender account
    if balance_sender:
      balance_sender = float(balance_sender[0]['balance'])
      if balance_sender < amount:
        query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
        cursor.execute(query, (username, "Pay unsuccessfully"))
        connection.commit()
        cursor.close()
        connection.close()
        return False
      else:
        new_balance_sender = balance_sender - amount
        query = "UPDATE bankaccount SET balance = %s WHERE account = %s"
        cursor.execute(query, (new_balance_sender, account_sender))
        #Update the balance of the sender account
        query = "SELECT balance FROM bankaccount WHERE account = %s AND password = %s"
        cursor.execute(query, (account_receiver, password_receiver))
        balance_receiver = cursor.fetchall()
        balance_receiver = float(balance_receiver[0]['balance'])
        new_balance_receiver = balance_receiver + amount
        #Get the balance from the receiver account
        query = "UPDATE bankaccount SET balance = %s WHERE account = %s"
        cursor.execute(query, (new_balance_receiver, account_receiver))
        #Update the balance of the receiver account
        query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
        cursor.execute(query, (username, "Pay successfully"))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    else:
      query = "INSERT INTO activityrecord (username, action) VALUES (%s, %s)"
      cursor.execute(query, (username, "Pay unsuccessfully"))
      connection.commit()
      cursor.close()
      connection.close()
      return False
    