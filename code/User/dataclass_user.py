import mysql.connector

class User(): 
  def __init__(self, db_config):
    self.db_config = db_config

  def get_db_connection(self):
    return mysql.connector.connect(**self.db_config)
   
class Convener(User):
  def submitRegistrationApplication(self):
    pass

class T_admin(User):
  def answerQuestion(self):
    pass

class registerApplication():
    __applicationStatus = "no_pass"
    __applicationReviewed = False

    def __init__(self, id, email, proof, nameFull, nameShort):
        self.applicationId = id
        self.convenerEmail = email
        self.proofDocument = proof
        self.organizationNameFull = nameFull
        self.organizationNameShort = nameShort
    
    def acceptApplication(self):
      pass
                
    def rejectApplication(self):
      pass

    
class DataUser(User):

  def browsePolicy(self):
    connection = self.get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for easier data handling
    cursor.execute("SELECT * FROM policies")
    policies = cursor.fetchall()
    cursor.close()
    connection.close()
    return policies
  
  def seekHelp(self, username, question):
    connection = self.get_db_connection()
    cursor = connection.cursor()
    # Insert the question into the database
    query = "INSERT INTO userquestion (username, question) VALUES (%s, %s)"
    cursor.execute(query, (username, question))
    connection.commit()
    # Close the database connection
    cursor.close()
    connection.close()
  
  def accessCourseInfo(self):
    pass
  
  def accessThesis(self):
    pass
  
  def accessStudentInfo(self):
    pass
  
  def provideDatabaseinterfaceInfo(self):
    pass
  
  def provideCourseInfo(self):
    pass

class Pay():
    def __init__(self, paymentNo, datetime, amount, receiver, sender, paymentMethod, paymentStatus):
        self.paymentNo = paymentNo
        self.datetime = datetime
        self.amount = amount
        self.receiver =receiver
        self.sender = sender
        self.paymentMethod = paymentMethod
        self.paymentStatus = paymentStatus
    def verifyPayment(self):
        pass

class UserQuestion():
    def __init__(self, number, state, content, answer):
        self.questionNo = number
        self.state = state
        self.content = content
        self.answer = answer

class LOG():
    def __init__(self, logID, userEmail, time, service):
        self.logID = logID
        self.userEmail = userEmail
        self.time = time
        self.service = service
    