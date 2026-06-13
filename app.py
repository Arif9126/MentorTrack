from flask import Flask, render_template, request, redirect
import dbm
import re

app = Flask(__name__)

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "vvce2026":
            return redirect("/")

    return render_template("login.html")

@app.route("/")
def home():

    db = dbm.open("studentdb", "c")

    total_students = len(db)

    total_cgpa = 0
    total_attendance = 0
    total_backlogs = 0
    high_attendance = 0
    low_attendance = 0

    no_backlogs = 0
    has_backlogs = 0

    for key in db.keys():

        data = db[key].decode()

        details = data.split("|")

        total_cgpa += float(details[0])

        if int(details[1]) > 0:
            total_backlogs += 1

        total_attendance += float(details[2])
        attendance = float(details[2])
        backlogs = int(details[1])

        if attendance >= 85:
            high_attendance += 1
        else:
            low_attendance += 1

        if backlogs == 0:
            no_backlogs += 1
        else:
            has_backlogs += 1

    if total_students > 0:

        avg_cgpa = round(
            total_cgpa / total_students,
            2
        )

        avg_attendance = round(
            total_attendance / total_students,
            2
        )

    else:

        avg_cgpa = 0

        avg_attendance = 0

    db.close()

    return render_template(
    "dashboard.html",
    total_students=total_students,
    avg_cgpa=avg_cgpa,
    avg_attendance=avg_attendance,
    total_backlogs=total_backlogs,
    high_attendance=high_attendance,
    low_attendance=low_attendance,
    no_backlogs=no_backlogs,
    has_backlogs=has_backlogs
)



@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        usn = request.form["usn"]
        pattern = r"^4[EVT]V25(CS|AI|CV|EC|EE)\d{3}$"

        if not re.match(pattern, usn):
            return render_template(
                "add_student.html",
                error="Invalid USN Format"
            )
        cgpa = request.form["cgpa"]
        backlogs = request.form["backlogs"]
        attendance = request.form["attendance"]

        db = dbm.open("studentdb", "c")

        if usn in db:
            db.close()
            return render_template(
                "add_student.html",
                error="USN Already Exists"
            )

        db[usn] = f"{cgpa}|{backlogs}|{attendance}"

        db.close()

    return render_template("add_student.html")

@app.route("/search", methods=["GET", "POST"])
def search_student():
    result = None

    if request.method == "POST":
        usn = request.form["usn"]

        db = dbm.open("studentdb", "c")

        if usn in db:
            data = db[usn].decode()
            details = data.split("|")

            result = {
                "usn": usn,
                "cgpa": details[0],
                "backlogs": details[1],
                "attendance": details[2]
            }

        db.close()

    return render_template(
        "search_student.html",
        result=result
    )

@app.route("/view")
def view_students():
    db = dbm.open("studentdb", "c")

    students = []

    for key in db.keys():
        usn = key.decode()
        data = db[key].decode()
        details = data.split("|")

        students.append({
            "usn": usn,
            "cgpa": details[0],
            "backlogs": details[1],
            "attendance": details[2]
        })

    db.close()

    return render_template(
    "view_student.html",
    students=students
)


@app.route("/delete/<usn>")
def delete_student(usn):

    db = dbm.open("studentdb", "w")

    if usn in db:
        del db[usn]

    db.close()

    return redirect("/view")

@app.route("/edit/<usn>", methods=["GET","POST"])
def edit_student(usn):

    db = dbm.open("studentdb", "c")

    if request.method == "POST":

        cgpa = request.form["cgpa"]
        backlogs = request.form["backlogs"]
        attendance = request.form["attendance"]

        db[usn] = f"{cgpa}|{backlogs}|{attendance}"

        db.close()

        return redirect("/view")

    data = db[usn].decode()

    details = data.split("|")

    db.close()

    student = {
        "usn": usn,
        "cgpa": details[0],
        "backlogs": details[1],
        "attendance": details[2]
    }

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/logout")
def logout():
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)