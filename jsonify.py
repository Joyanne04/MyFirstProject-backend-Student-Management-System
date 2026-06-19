from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route("/student")
def get_student():
    student = {
        "name": "Joy", 
        "age": 20, 
        "Course": "Python",
        }
    return jsonify(student)

# GET
app = Flask(__name__)
@app.route("/todos", methods=["GET"])
def get_todos():
    return {"todos": []}

# POST
@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    return {"message": "Todo added", "todo": data}

# PUT
@app.route("/todos/1", methods=["PUT"])
def update_todo():
    return {"message": "Todo updated"}

# DELETE
@app.route("/todos/1", methods=["DELETE"])
def delete_todo():
    return {"message": "Todo deleted"}


if __name__ == "__main__":
    app.run(debug=True)
