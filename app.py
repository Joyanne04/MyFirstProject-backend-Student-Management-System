from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate

from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

# Create the Flask application
app = Flask(__name__)

# Allow requests from all origins
CORS(app)

# Configure the MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskapp_db'    # Tells SQLAlchemy how to connect to the MySQL db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Disables Modification tracking.

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # Access token valid for 15 minutes
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days= 7)  # Refresh token expiration


# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)  # Initialize JWT Manager


# Create the Student model (table)
class Student(db.Model):    # Defines the student class
    __tablename__ = "students_x"

    studentID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)  # Added email field
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)

    # Convert object to dictionary
    def to_dict(self):
        return {
            "studentID": self.studentID,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "email": self.email
        }
    
# Create the database tables
# with app.app_context():
#     db.create_all()

# Create the TokenBlocklist model (table) for storing revoked tokens
class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)  # JWT ID
    token_type = db.Column(db.String(20), nullable=False)


# Create the Unit model (table)
class Unit(db.Model):
    __tablename__ = "units"

    unitID = db.Column(db.Integer, primary_key=True)
    unitCode = db.Column(db.String(20), nullable=False)
    unitName = db.Column(db.String(100), nullable=False)
    

    # Convert object to dictionary
    def to_dict(self):
        return {
            "unitID": self.unitID,
            "unitCode": self.unitCode,
            "unitName": self.unitName,          
        }

# Create the student_units model (table) for the many-to-many relationship
class StudentUnit(db.Model):
    __tablename__ = "student_units"

    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.Integer, db.ForeignKey("students_x.studentID"), primary_key=True)
    unitID = db.Column(db.Integer, db.ForeignKey("units.unitID"), primary_key=True)

    def to_dict(self):
        return {
            "studentID": self.studentID,
            "unitID": self.unitID
        }

# CREATE - Add a new student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()

    if not data or not data.get("password"):
        return jsonify({"error": "Password is required"}), 400

    new_student = Student(
        studentID = data["studentID"],
        name= data["name"],
        gender= data["gender"],
        age= data["age"],
        email= data["email"]  # Added email field
    )
    new_student.set_password(data["password"])

    db.session.add(new_student)
    db.session.commit()

    return jsonify(new_student.to_dict())


# READ - Get all students
@app.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()

    return jsonify([student.to_dict() for student in students])


# READ - Get one student by ID
@app.route("/students/<int:studentID>", methods=["GET"])
def get_student(studentID):
    student = Student.query.get(studentID)

    if not student:
        return jsonify({"error": "Student not found"})

    return jsonify(student.to_dict())


# AUTHENTICATE - Log in a student with email and password
@app.route("/login", methods=["POST"])  
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    student = Student.query.filter_by(email=email).first()
    if not student or not student.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful", "student": student.to_dict()})


# UPDATE - Update a student
@app.route("/students/<int:studentID>", methods=["PUT"])
def update_student(studentID):
    student = Student.query.get(studentID)

    if not student:
        return jsonify({"error": "Student not found"})

    data = request.get_json()

    student.studentID = data.get("studentID", student.studentID)
    student.name = data.get("name", student.name)
    student.gender = data.get("gender", student.gender)
    student.age = data.get("age", student.age)
    student.email = data.get("email", student.email)  # Added email field
    if "password" in data:
        if not data["password"]:
            return jsonify({"error": "Password cannot be empty"}), 400
        student.set_password(data["password"])
    db.session.commit()

    return jsonify({"message": "Student updated successfully"})


# DELETE - Delete a student
@app.route("/students/<int:studentID>", methods=["DELETE"])
def delete_student(studentID):
    student = Student.query.get(studentID)

    if not student:
        return jsonify({"error": "Student not found"})

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message": "Student deleted successfully"})


# Units CRUD operations
# CREATE - Add a new unit
@app.route("/units", methods=["POST"])
def add_unit():
    data = request.get_json()

    new_unit = Unit(
        unitCode = data["unitCode"],
        unitName = data["unitName"]
    )
    db.session.add(new_unit)
    db.session.commit()

    return jsonify(new_unit.to_dict())

# READ - Get all units
@app.route("/units", methods=["GET"])
def get_units():
    units = Unit.query.all()

    return jsonify([unit.to_dict() for unit in units])

# READ - Get one unit by unitID
@app.route("/units/<int:unitID>", methods=["GET"])
def get_unit(unitID):
    unit = Unit.query.get(unitID)

    if not unit:
        return jsonify({"error": "Unit not found"})

    return jsonify(unit.to_dict())

# UPDATE - Update a unit
@app.route("/units/<int:unitID>", methods=["PUT"])
def update_unit(unitID):
    unit = Unit.query.get(unitID)

    if not unit:
        return jsonify({"error": "Unit not found"})

    data = request.get_json()

    unit.unitID = data.get("unitID", unit.unitID)
    unit.unitCode = data.get("unitCode", unit.unitCode)
    unit.unitName = data.get("unitName", unit.unitName)
    db.session.commit()

    return jsonify({"message": "Unit updated successfully"})

# DELETE - Delete a unit
@app.route("/units/<int:unitID>", methods=["DELETE"])
def delete_unit(unitID):        
    unit = Unit.query.get(unitID)

    if not unit:
        return jsonify({"error": "Unit not found"})

    db.session.delete(unit)
    db.session.commit()

    return jsonify({"message": "Unit deleted successfully"})


# CREATE - Add a unit to a student
@app.route("/students-units", methods=["POST"])
def attach_unit_to_student():
    data = request.get_json()

    student_id = data["studentID"]
    unit_id = data["unitID"]

    # Validate if the student exists
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Validate if the unit exists
    unit = Unit.query.get(unit_id)

    if not unit:
        return jsonify({"error": "Unit not found"}), 404

    # Check if the unit is already attached to the student
    existing_student_unit = StudentUnit.query.filter_by(
        studentID=student_id,
        unitID=unit_id,
    ).first()

    if existing_student_unit:
        return jsonify({"error": "This unit is already attached to the student"}), 400

    # Create the relationship between the student and the unit
    student_unit = StudentUnit(studentID=student_id, unitID=unit_id)

    db.session.add(student_unit)
    db.session.commit()

    return jsonify({"message": "Unit attached to student successfully"}), 201

# READ - Get all units attached to a student
@app.route("/students/<int:studentID>/units", methods=["GET"])
def get_units_for_student(studentID):
    student = Student.query.get(studentID)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    student_units = StudentUnit.query.filter_by(studentID=studentID).all()

    units = []
    for student_unit in student_units:
        unit = Unit.query.get(student_unit.unitID)
        if unit:
            units.append(unit.to_dict())

    return jsonify({
        "studentID": student.studentID,
        "name": student.name, 
        "units": units}), 200

# READ - Get all students attached to one unit
@app.route("/units/<int:unitID>/students", methods=["GET"])
def get_students_for_unit(unitID):
    unit = Unit.query.get(unitID)

    if not unit:
        return jsonify({"error": "Unit not found"}), 404

    student_units = StudentUnit.query.filter_by(unitID=unitID).all()

    students = []
    for student_unit in student_units:
        student = Student.query.get(student_unit.studentID)
        if student:
            students.append(student.to_dict())

    return jsonify({
        "unitID": unit.unitID,
        "unitCode": unit.unitCode,
        "unitName": unit.unitName,
        "students": students}), 200

# DELETE - Remove a unit from a student
@app.route("/students/<int:studentID>/units/<int:unitID>", methods=["DELETE"])
def remove_unit_from_student(studentID, unitID):
    student_unit = StudentUnit.query.filter_by(studentID=studentID, unitID=unitID).first()

    if not student_unit:
        return jsonify({"error": "This unit is not attached to the student"}), 404

    db.session.delete(student_unit)
    db.session.commit()

    return jsonify({"message": "Unit removed from student successfully!"}), 200

# Pivot table endpoint to get all student-unit relationships
@app.route("/students-units/pivot", methods=["GET"])
def get_student_units_pivot():

    students = Student.query.all()    # Get all students
    units = Unit.query.all()

    pivot_data = []    # List to store pivot table data

    for student in students:
        student_data = {
            "studentID": student.studentID,
            "name": student.name,
            "units": {}
        }

        for unit in units:
            relationship = StudentUnit.query.filter_by(
                studentID = student.studentID,
                unitID = unit.unitID
            ).first()

            student_data["units"][str(unit.unitID)] = True if relationship else False

        pivot_data.append(student_data)    # Add student data to pivot table

    return jsonify({"students": pivot_data, "units": [unit.to_dict() for unit in units]})


# READ - Get student details by ID
@app.route("/students/<int:studentID>/details", methods=["GET"])
def get_student_details(studentID):
    student = Student.query.get(studentID)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    enrollments = StudentUnit.query.filter_by(studentID=studentID).all()

    units = []
    for enrollment in enrollments:
        unit = Unit.query.get(enrollment.unitID)
        if unit:
            units.append({
                "unitID": unit.unitID,
                "unitCode": unit.unitCode,
                "unitName": unit.unitName
            })

    return jsonify({
        "student": {
            "studentID": student.studentID,
            "name": student.name,
            "gender": student.gender,
            "age": student.age,
            "email": student.email
        },

        "units": units
    }), 200 


# READ - Get unit details by ID
@app.route("/units/<int:unitID>/details", methods=["GET"])
def get_unit_details(unitID):
    unit = Unit.query.get(unitID)

    if not unit:
        return jsonify({"error": "Unit not found"}), 404

    enrollments = StudentUnit.query.filter_by(unitID=unitID).all()

    students = []
    for enrollment in enrollments:
        student = Student.query.get(enrollment.studentID)
        if student:
            students.append({
                "studentID": student.studentID,
                "name": student.name,
                "gender": student.gender,
                "age": student.age, 
                "email": student.email
            })

    return jsonify({
        "unit": {
            "unitID": unit.unitID,
            "unitCode": unit.unitCode,
            "unitName": unit.unitName
        },
        "students": students
    }), 200


# CREATE enrollment - Add a unit to a student
@app.route("/enrollments", methods=["POST"])
def enroll_student():

    data = request.get_json()

    studentID = data["studentID"]
    unitID = data["unitID"]

    if not studentID or not unitID:
        return jsonify({"error": "Both studentID and unitID are required"}), 400

    # Validate if the student exists
    student = Student.query.get(studentID)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Validate if the unit exists
    unit = Unit.query.get(unitID)

    if not unit:
        return jsonify({"error": "Unit not found"}), 404

    # Check if the unit is already attached to the student
    existing_enrollment = StudentUnit.query.filter_by(
        studentID=studentID,
        unitID=unitID,
    ).first()

    if existing_enrollment:
        return jsonify({"error": "This unit has already been enrolled by the student"}), 400

    # Relationship between the student and the unit
    enrollment = StudentUnit(studentID=studentID, unitID=unitID)

    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"message": "Student successfully enrolled in unit"}), 201


# GET enrollment - Get all enrollments
@app.route("/enrollments", methods=["GET"])
def get_enrollments():

    enrollments = StudentUnit.query.all()
    enrollment_list = []

    for enrollment in enrollments:
        student = Student.query.get(enrollment.studentID)
        unit = Unit.query.get(enrollment.unitID)

        if student and unit:
            enrollment_list.append({
                "ID": enrollment.id,
                "studentID": student.studentID,
                "studentName": student.name,
                "unitID": unit.unitID,
                "unitCode": unit.unitCode,
                "unitName": unit.unitName
            })
        
    return jsonify(enrollment_list), 200


# POST - Student login to get access and refresh tokens
@app.route("/auth/student/login", methods=["POST"])
def student_login():    # Handles student login and returns access and refresh tokens

    data = request.get_json()    # Get the JSON data from the request

    email = data.get("email")    # Get the email from the JSON data
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    student = Student.query.filter_by(email=email).first()    # Get the student from the database by email

    if not student or not student.check_password(password):    # Checks whether the student does not exist or the password is incorrect
        return jsonify({"error": "Invalid email or password"}), 401

    # Create access and refresh tokens
    access_token = create_access_token(identity=str(student.studentID))    # Create an access token with the student's ID as the identity
    refresh_token = create_refresh_token(identity=str(student.studentID))

    return jsonify({
        "message": "Login successful",
        "student": {
            "studentID": student.studentID,
            "name": student.name,
            "gender": student.gender,
            "age": student.age,
            "email": student.email
        },
        "access_token": access_token,
        "refresh_token": refresh_token   # Return the access and refresh tokens to the client
    }), 200


# GET - Access protected route for student profile using access token
@app.route("/student/profile", methods=["GET"])    
@jwt_required()    # Protects the endpoint
def student_profile():   # D

    current_student_id = get_jwt_identity()    # Get the current student's ID from the JWT identity
    student = Student.query.get(current_student_id)    # Get the student from the database by ID

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "studentID": student.studentID,
        "name": student.name,
        "gender": student.gender,
        "age": student.age,
        "email": student.email
    }), 200


# PUT - Update Student profile
@app.route("/student/profile", methods=["PUT"])
@jwt_required()    # Protects the endpoint
def update_student_profile():    # Allows the student to update their profile information

    current_student_id = get_jwt_identity()
    student = Student.query.get(current_student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()    # Get the JSON data from the request

    student.name = data.get("name", student.name)
    student.gender = data.get("gender", student.gender)
    student.age = data.get("age", student.age)
    student.email = data.get("email", student.email)

    if "password" in data:
        if not data["password"]:
            return jsonify({"error": "Password cannot be empty"}), 400
        student.set_password(data["password"])

    db.session.commit()

    return jsonify({"message": "Student profile updated successfully"}), 200


# POST - Refresh access token using refresh token
@app.route("/auth/student/refresh", methods=["POST"])
@jwt_required(refresh=True)    # Protects the endpoint and requires a refresh token
def refresh_access_token():

    current_student_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(current_student_id))    # Create a new access token with the student's ID as the identity

    return jsonify({
        "access_token": new_access_token
    }), 200


# Check if the token has been revoked 
@jwt.token_in_blocklist_loader    # This decorator registers a callback function that will be called whenever a protected endpoint is accessed. The callback function checks if the token has been revoked by looking it up in the TokenBlocklist table.
def check_if_token_revoked(jwt_header, jwt_payload):    # This function checks if the token has been revoked by looking it up in the TokenBlocklist table. If the token is found in the blocklist, it means that the token has been revoked and the user will not be able to access protected endpoints.

    jti = jwt_payload["jti"]    # Get the JWT ID (jti) from the JWT payload
    token = TokenBlocklist.query.filter_by(jti=jti).first()    # Query the TokenBlocklist table to check if the token has been revoked
    return token is not None

# POST - Logout student endpoint
@app.route("/auth/student/logout", methods=["POST"])
@jwt_required()    # Protects the endpoint      
def student_logout():

    jti = get_jwt()["jti"]    # Get the JWT ID (jti) from the JWT payload
    token_type = get_jwt()["type"]   # Get the JWT ID (jti) and token type from the JWT payload

    # Add the token to the blocklist
    revoked_token = TokenBlocklist(jti=jti, token_type=token_type)    # Create a new TokenBlocklist object with the jti and token type
    
    db.session.add(revoked_token)    # Add the revoked token to the database session
    db.session.commit()   # Commit the changes to the database

    return jsonify({"message": "Student logged out successfully"}), 200



# Run the application
if __name__ == "__main__":
    app.run(debug=True)                 