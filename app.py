from flask import Flask,render_template,request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer,primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name =  db.Column(db.String, unique = True, nullable = False)
    last_name =  db.Column(db.String)
    courses = db.relationship("Course", backref = "students" , secondary = "enrollments")


class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer,primary_key = True, autoincrement = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name =  db.Column(db.String, nullable = False)
    course_description=  db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id  = db.Column(db.Integer,primary_key = True,autoincrement = True)
    estudent_id = db.Column(db.Integer,db.ForeignKey('student.student_id'), nullable = False)
    ecourse_id = db.Column(db.Integer,db.ForeignKey('course.course_id'), nullable = False)

with app.app_context():
    db.create_all()





@app.route("/", methods = ["GET","POST"])
def home():
    students = Student.query.all()
    return render_template("index.html", students = students),200

@app.route("/student/create", methods = ["GET","POST"])
def addstudent():
    if request.method == "GET":
        return render_template("add_student.html"),200
    
    if request.method == "POST":
        roll =  request.form.get("roll")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        exist = Student.query.filter_by(roll_number = roll).first()
        if exist:
            return render_template("exist.html"),200
        else:
            students = Student(roll_number = roll,first_name = f_name , last_name = l_name)
            db.session.add(students)
            db.session.commit()
            return redirect('/')
        

@app.route("/student/<int:student_id>")
def student_details(student_id):
    student = db.session.get(Student,student_id)
    course_details= student.courses
    # print(course_details,flush = True)
    return render_template("student_details.html",student = student,course_details= course_details)
        
@app.route("/student/<int:student_id>/update", methods = ["GET","POST"])
def update_student(student_id):
    if request.method == "GET":
        student = Student.query.filter_by(student_id = student_id).first()
        courses = Course.query.all()
        return render_template("update_student.html",student = student, courses = courses),200
    elif request.method == "POST":
        exist = Student.query.filter_by(student_id = student_id).first()
        exist.first_name = request.form.get("f_name")
        exist.last_name = request.form.get("l_name")
        new_courses  = int(request.form.get("course"))
        course = Course.query.get(new_courses)
        exist.courses.append(course)
        db.session.commit()
        return redirect("/")
        # for course in exist.courses:
        #     print(course)



@app.route("/student/<int:student_id>/delete", methods = ["GET","POST"])
def delete(student_id):
    Student.query.filter_by(student_id = student_id).delete()
    Enrollments.query.filter_by(estudent_id = student_id).delete()
    db.session.commit()
    return redirect("/")

@app.route("/courses",methods = ["GET","POST"])
def courses():
    courses = Course.query.all()
    return render_template("course.html", courses = courses),200

@app.route("/course/create",methods = ["GET","POST"])
def addcourse():
    if request.method == "GET":
        return render_template("add_course.html"),200
    
    elif request.method == "POST":
        code =  request.form.get("code")
        c_name = request.form.get("c_name")
        desc= request.form.get("desc")
        exist = Course.query.filter_by(course_code = code ).first()
        if exist:
            return render_template("cexist.html"),200
        else:
            Courses = Course(course_code = code ,course_name = c_name , course_description = desc)
            db.session.add(Courses)
            db.session.commit()
            return redirect("/courses")
        
@app.route("/course/<int:course_id>/update", methods = ["GET","POST"])
def update_courses(course_id):
    if request.method == "GET":
        _course = Course.query.filter_by(course_id = course_id).first()
        return render_template("update_course.html",course = _course),200
    elif request.method == "POST":
        exist = Course.query.filter_by(course_id = course_id).first()
        exist.course_name = request.form.get("c_name")
        exist.course_description = request.form.get("desc")
        db.session.add(exist)
        db.session.commit()
        return redirect("/courses")
    

@app.route("/course/<int:course_id>/delete", methods = ["GET","POST"])
def delete_courses(course_id):
    Course.query.filter_by(course_id = course_id).delete()
    db.session.commit()
    return redirect("/")


@app.route("/course/<int:course_id>")
def course_details(course_id):
    course = Course.query.get(course_id)

    # if course is None:     
    #     return "Course not found", 404
    student_details = course.students
    return render_template("course.details.html", course = course, student_details = student_details),200

@app.route("/student/<int:student_id>/withdraw/<int:course_id>",methods = ["GET","POST"])
def withdraw(student_id,course_id):
    if request.method == "GET":
        student = db.session.get(Student,student_id)
        enroll = Enrollments.query.filter_by(estudent_id = student_id ,ecourse_id = course_id ).first()
        db.session.delete(enroll)
        db.session.commit()
        return redirect("/")

if (__name__) == "__main__":
    app.run(debug = True)
