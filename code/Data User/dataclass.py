import mysql.connector

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
    #Create Log
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
    #Create Log
    cursor.execute(query, (username, "Browse bank accounts"))
    connection.commit()
    cursor.close()
    connection.close()
    return bankaccounts
  
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
    