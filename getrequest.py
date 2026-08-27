from flask import Flask, jsonify
app = Flask(__name__)
students = [
    {"name": "Joy", "age": 20},
    {"name": "Alice", "age": 22}
]
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)
if __name__ == "__main__":
    app.run(debug=True)
    