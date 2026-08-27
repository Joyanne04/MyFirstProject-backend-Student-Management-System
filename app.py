from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate

# Create the Flask application
app = Flask(__name__)

# Allow requests from all origins
CORS(app)

# Configure the MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskapp_db'    # Tells SQLAlchemy how to connect to the MySQL db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Disables Modification tracking.

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create the Student model (table)
class Student(db.Model):    # Defines the student class
    __tablename__ = "students_x"

    studentID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)  # Added email field

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

    new_student = Student(
        studentID = data["studentID"],
        name= data["name"],
        gender= data["gender"],
        age= data["age"],
        email= data["email"]  # Added email field   
    )

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


# Run the application
if __name__ == "__main__":
    app.run(debug=True)                 