import werkzeug.exceptions
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

    def __repr__(self):
        return f"{self.first_name} {self.last_name} - age: {self.age}, email: {self.email}"


def custom_error(msg, status_code):
    response = jsonify({"message:": msg})
    response.status_code = status_code
    return response


@app.route("/students", methods=["GET", "POST"])
def get_students():
    """This endpoint handles both retrieving all students (GET), and creating new students (POST)"""
    if request.method == "GET":
        students = Student.query.all()
        if not students:
            return custom_error("No students found!", 404)
        # The query returns Student objects, which first must be JSON serialized
        students_serialize = []
        for student in students:
            students_serialize.append({"first_name:": student.first_name, "last_name:": student.last_name,
                                       "age:": student.age, "email:": student.email})

        return {"Students:": students_serialize}, 200
    else:
        try:
            new_student = Student(first_name=request.form["first_name"], last_name=request.form["last_name"],
                                  age=request.form["age"], email=request.form.get("email", None))
        except werkzeug.exceptions.BadRequestKeyError:
            return custom_error("Missing argument!", 400)
        else:
            db.session.add(new_student)
            db.session.commit()
            return {"ID:": new_student.id_}, 201


@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """This endpoint handles retrieving a single student based on their ID"""
    student = Student.query.get(student_id)
    if not student:
        return custom_error(f"No student with ID: {student_id}", 404)
    else:
        return {"First name:": student.first_name, "Last name:": student.last_name, "Age": student.age,
                "Email:": student.email}


@app.route("/students/<int:student_id>", methods=["PUT", "PATCH"])
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return custom_error(f"Student not found with ID {student_id}", 404)
    else:
        if request.method == "PUT":
            try:
                student.first_name = request.form["first_name"]
                student.last_name = request.form["last_name"]
                student.age = request.form["age"]
                student.email = request.form.get("email", None)
            except werkzeug.exceptions.BadRequestKeyError:
                return custom_error("Wrong Key Error!", 400)
            else:
                db.session.commit()
                return {"message:": f"Student with ID {student_id} updated successfully"}, 200
        else:
            keys = request.form.keys()
            keys_q = ["first_name", "last_name", "age", "email"]

            for key in keys:
                if key in keys_q:
                    student.key = request.form[key]

            return {"message": "OK"}, 200


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """This endpoint handles deleting student instances based on their ID"""
    student = Student.query.get(student_id)
    if not student:
        return custom_error(f"No student wth ID: {student_id}", 404)
    else:
        db.session.delete(student)
        db.session.commit()

        return {"message:": f"Student with ID {student_id} was deleted successfully!"}, 204


if __name__ == "__main__":
    app.run(debug=True)
