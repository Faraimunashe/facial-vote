import face_recognition
from flask import Flask, jsonify, request, redirect, render_template, url_for, flash, session,wrappers
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
from models import *
from functools import wraps
from textblob import TextBlob
from flask_mail import Mail, Message
import random
import json
from face import detect


# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ProfessorSecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/facial_db'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'faraimunashe.m11@gmail.com'
app.config['MAIL_PASSWORD'] = 'mrozgibgzynlanel'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db.init_app(app)
mail = Mail(app)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


#check roles
def admin_role(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        user = User.query.filter_by(id=session['userid']).first()
        if user.role == 1:
            return f(*args, **kwargs)
        else:
            return redirect("/vote")
    return decorated_func


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_faces_in_image(file_stream, natid):
    try:

        user = User.query.filter_by(natid=natid).first()
        if not user:
            result = {
                "face_found_in_image": False,
                "is_picture_known": False,
                "next_url": '/login'
            }
            return result
        
        if user.img == None:
            result = {
                "face_found_in_image": False,
                "is_picture_known": False,
                "next_url": '/login'
            }
            return result

        response = detect(file_stream, "static/known_faces/"+user.img)

        if response == True:
            print(user.id)
            login_user(user)
            session['userid'] = user.id
            print('logged user')
            # Return the result as json
            result = {
                "face_found_in_image": True,
                "is_picture_known": True,
                "next_url": "/",
                "user_id" : user.id
            }

            print(result)
            return result
        else:
            result = {
                "face_found_in_image": False,
                "is_picture_known": False,
                "next_url": '/login'
            }
            return result
    except :
        result = {
            "face_found_in_image": False,
            "is_picture_known": False,
            "next_url": '/login'
        }
        return result




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Image not posted')
            return redirect(url_for(login))

        file = request.files['file']
        natid = request.form.get('natid')

        if file.filename == '' or natid == '':
            flash('file name is empty')
            return redirect(url_for(login))

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            response = detect_faces_in_image(file, natid)
            print(response['is_picture_known'])
            if response['is_picture_known'] == True:
                #login_user(response['user_id'])
                return jsonify(response)
            flash('INVALID FACIAL LOGIN')
            return jsonify(response)

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
@admin_role
def index():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            flash('Image not posted')
            return redirect(url_for('index'))

        file = request.files['file']
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        sex = request.form.get('sex')
        natid = request.form.get('natid')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if file.filename == '' or fname == '' or lname == '' or natid == '' or sex == '' or phone == '' or address == '':
            flash('some fields are empty')
            return redirect(url_for('index'))
        
        user = User.query.filter_by(natid=natid).first()
        if user:
            flash('error National Id already exists!')
            return redirect(url_for('index'))
        
        now = datetime.datetime.now()
        extension = file.filename.split('.')[1]
        image_name = str(random.randint(10000000, 99999999)) +"."+ extension
        path = os.path.join("static/known_faces", image_name)
        file.save(path)
        
        new_user = User(fname=fname, lname=lname, sex=sex, natid=natid, address=address, phone=phone, img=image_name, role=2)
        db.session.add(new_user)
        db.session.commit()

        
        flash('Successfully register new user!')
        return redirect(url_for('index'))
        
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/candidates', methods=['GET', 'POST'])
@login_required
@admin_role
def candidates():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            flash('error Image not posted')
            return redirect(url_for('candidates'))

        file = request.files['file']
        fullname = request.form.get('fullname')
        title = request.form.get('title')
        sex = request.form.get('sex')
        part = request.form.get('part')

        if file.filename == '' or fullname == '' or title == '' or sex == '' or part == '':
            flash('error some fields are empty')
            return redirect(url_for('candidates'))
        
        candidate = Candidate.query.filter_by(part=part).first()
        if candidate:
            flash('error This part is already registered!')
            return redirect(url_for('candidates'))
        
        extension = file.filename.split('.')[1]
        
        image_name =  str(random.randint(1000, 9999)) +"."+ extension
        path = os.path.join("static/candidates", image_name)
        file.save(path)
        
        new_candidate = Candidate(fullname=fullname, title=title, sex=sex, part=part, image=image_name)
        db.session.add(new_candidate)
        db.session.commit()

        
        flash('Successfully register new candidate!')
        return redirect(url_for('candidates'))
        
    candidates = Candidate.query.all()
    return render_template('candidates.html', candidates=candidates)


@app.route('/results', methods=['GET', 'POST'])
@login_required
@admin_role
def results():
    if request.method == 'POST':
        exist = Result.query.all()
        if len(exist) == 0:
            flash('error there are no results to publish!')
            return redirect(url_for('results'))

        new_publish = Publish(status=1, period=1)
        db.session.add(new_publish)
        db.session.commit()
        
        flash('Successfully register new candidate!')
        return redirect(url_for('results'))
        
    res = db.session.query(Candidate.id, Candidate.fullname, Candidate.part, db.func.count(Result.id)).\
        join(Result, Candidate.id == Result.candidateid).\
        group_by(Candidate.id).all()
    
    print(res)
    return render_template('results.html', candidates=res)


################user######################
@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id')
        user_id = session['userid']

        if candidate_id == None or user_id == None:
            flash('error missing fields')
            return redirect(url_for('vote'))
        
        voted = Result.query.filter_by(userid=user_id).first()
        if voted:
            flash('error you cannot vote more than once!')
            return redirect(url_for('vote'))
        
        new_result = Result(candidateid=candidate_id, userid=user_id)
        db.session.add(new_result)
        db.session.commit()
        
        flash('Successfully voted!')
        return redirect(url_for('vote'))
        
    candidates = Candidate.query.all()
    rezo =  Result.query.filter_by(userid=session['userid']).first()
    return render_template('vote.html', candidates=candidates, result=rezo)


@app.route('/vote-results', methods=['GET', 'POST'])
@login_required
def vote_results():
    published = Publish.query.filter_by(status=1).first()
    if not published:
        flash('error results not yet available!')
        return redirect(url_for('vote'))
        
    res = db.session.query(Candidate.id, Candidate.fullname, Candidate.part, db.func.count(Result.id)).\
        join(Result, Candidate.id == Result.candidateid).\
        group_by(Candidate.id).all()
    
    # res = db.session.query(
    #         Candidate.id,
    #         Candidate.fullname,
    #         Candidate.part,
    #         db.func.count(Result.id)
    #     ).join(Result, Candidate.id == Result.candidateid).group_by(Candidate.id).order_by(db.func.count(Result.id).desc()).all()

    return render_template('vote-result.html', candidates=res)

################end user######################



@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    g=None
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)