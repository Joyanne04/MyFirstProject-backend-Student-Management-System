from flask import Flask, request, jsonify
app = Flask(__name__)
students = []

@app.route('/')
def hello():
    return "Hello, World!"




# CREATE - Add a new student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()    # Reads JSON data sent by the client
    new_student = {
        "name": data["name"],
        "id": data["id"] ,   # Gets the task sent by the client
        "gender": data["gender"],
        "age": data["age"]
    }
    students.append(new_student)    # Adds the new student to the list
    return jsonify({'status': 'success', 'student': students}), 201 # sends a JSON response back to the client

# READ - Get all students
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)

# UPDATE - Modifies a student's information
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json()
    for student in students:
        if student["id"] == student_id:
            student["name"] = data.get("name", student["name"])
            student["id"] = data.get("id", student["id"])
            student["gender"] = data.get("gender", student["gender"])
            student["age"] = data.get("age", student["age"])
            return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

# DELETE - Removes a student
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    for student in students:
        if student["id"] == student_id:
            students.remove(student)
            return jsonify({"message": "Student deleted"})
    return jsonify({"error": "Student not found"}), 404

if __name__ == '__main__':''
app.run(debug=True)


# READ - Get one student
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    for student in students:
        if student["id"] == student_id:
            return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

# DELETE - Remove all student
@app.route("/students", methods=["DELETE"])
def delete_all_students():
    students.clear()
    return jsonify({"message": "All students deleted"})



# CREATE A VIRTUAL ENVIRONMENT (why needed) , RUN FLASK ON TERMINAL



