from __future__ import print_function
from flask import Flask,redirect, flash,url_for,render_template,jsonify,make_response, request
from mimetypes import guess_extension
from werkzeug.utils import secure_filename
from collections import OrderedDict
import os,sys
app = Flask(__name__)

loginMap = OrderedDict([('u563994', 'N'), ('u12345', 'Y'), ('u308988', 'N')])
# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        for key in loginMap.keys():
            print(request.form['username'],file=sys.stderr)
            if key == request.form['username']:
                if loginMap.get(key) == 'N':
                    return render_template('enrollmentLink.html',userId = request.form['username'])
                else:
                    return render_template('transferLink.html',userId = request.form['username'])
    return render_template('login.html', error=error)

@app.route("/enrollment/<userId>",methods=['POST','GET'])
def enroll(userId):
    questions = ["Q1", "Q2", "Q3","Q4","Q5","Q6","Q7","Q8"]
    return render_template("enrollment.html",enrollQ= questions,userId=userId)

@app.route('/upload', methods=['POST'])
def upload():
    for uploaded_file in request.files.getlist('file'):
        print(uploaded_file.filename, file=sys.stderr)
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join('enrolled_voice_recordings',
                               uploaded_file.filename))
    return render_template('enrollmentSuccess.html',userId=request.form['userId'])

@app.route('/2FAupload', methods=['POST'])
def twoFAupload():
    for uploaded_file in request.files.getlist('file'):
        print(uploaded_file.filename, file=sys.stderr)
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join('enrolled_voice_recordings',
                               uploaded_file.filename))
        print(uploaded_file.filename, file=sys.stderr)
    return render_template('transferSuccess.html',userId=request.form['userId'])

@app.route("/enrollmentSuccess/<userId>",methods=['GET','POST'])
def enrollmentSuccess(userId):
    return render_template("enrollmentSuccess.html",userId= userId)

@app.route("/transfer/<userId>",methods=['GET'])
def transfer(userId):
    questions = ["Random Question"]
    return render_template("transfer2FA.html",enrollQ= questions,userId= userId)
if __name__ == "__main__":
    app.run()
