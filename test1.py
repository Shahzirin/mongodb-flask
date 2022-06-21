



#import modules
from flask_pymongo import PyMongo
from flask import Flask , render_template , request , flash ,json, session,send_file ,redirect, url_for , after_this_request,app
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os
from datetime import datetime,timedelta
from functools import wraps

app = Flask(__name__)
#for session encrypting
app.secret_key = '\xef\xabVk\x0b\xde\xa6\x987\xa8\x8aU\xd7\xc6o\x1e\xf9\xa4\xbe\x12\x15\x0fK'


#connection
app.config['MONGO_URI'] = 'mongodb+srv://' + url
mongo = PyMongo(app)


#session expire after 8 minutes of no activity
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=8)


#to check db for username and password
def check_dbuser(username, password):
    auth = False
    roleCheck = False
    uri = 'mongodb+srv://'+ username.lower() + url
    client = MongoClient(uri)
    try:
        client.admin.command({'connectionStatus': 1})
        roleCheck = client.admin.command({'connectionStatus': 1})

    except OperationFailure as e:
        print(e)

    #additional role check in future, to see if not manager, cannot edit
    else:
        roleCheck = client.admin.command({'connectionStatus': 1})
        auth = True
        roleCheck = roleCheck['authInfo']['authenticatedUserRoles'][0]['role']

    return auth,roleCheck,uri


#decorator to return no access if have yet to login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if session['username'] != None:
                return f(*args, **kwargs)
            else:
                return render_template("noLogin.html")
        except Exception as e:
            print(e)
            return render_template("noLogin.html")

    return wrap

#decorator to return no access if roles have no rights
def role_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if session['role'] in ["manager"]:
                return f(*args, **kwargs)
            else:
                return render_template("noAccess.html")
        except Exception as e:
            print(e)
            return render_template("noAccess.html")

    return wrap


@app.route("/", methods =['GET','POST'])
def homepage():
     if 'username' in session:
        return redirect(url_for('validation', check=True, roleCheck = session['role'] ,userID = session['username'].capitalize() ))
     return render_template("loginpage.html")

 
#logout and clear session
@app.route("/logout", methods =['GET','POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)

    return render_template("loginpage.html")


#login
@app.route("/login", methods =['GET','POST'])
def validation():

    #get default url
    url = request.url_root
    if 'username' in session:
        check = True

        return render_template("homepage.html",check = check, homepage = url,roleCheck= session['role'] ,userID = session['username'].capitalize())
    else:
        userID = request.form.get("userID")
        if userID is None:
            return render_template("noLogin.html")
        password = request.form.get("password")
        check,roleCheck,uri = check_dbuser(userID , password)
        if check:
            #check is true if user id and password is correct
            session['username'] = userID
            session['role'] = roleCheck
            session['api'] = uri
            print(session['role'])
        else:
            return render_template("homepage.html",check = check, homepage = url,roleCheck =None ,userID = None)
        return render_template("homepage.html",check = check, homepage = url,roleCheck = session['role'] ,userID = session['username'].capitalize())


#access to create project role with Apps
@app.route("/addApp", methods =['GET','POST'])
@login_required
@role_required
def addApp():
    ##access database to extract data
    cursor = mongo.db.applications.find({},{"_id": False})
    data = [item for item in cursor]
    jsonData = []
    #append per item
    for item in data:
        jsonData.append(item)

    #to view all assigned app table
    checkDB = mongo.db.assignedApp.find({},{"_id": False}).sort([("project", 1), ("role", 1)])
    data2 = [item for item in checkDB]
    jsonData2 = []
    for item in data2:
                print(item)
                jsonData2.append(item)
    return render_template("addApp.html",data2 = json.dumps(jsonData2),data = json.dumps(jsonData),roleCheck = session['role'] ,userID = session['username'].capitalize())


#define app to the role and project
@app.route("/assignApp",methods =['GET','POST'])
@login_required
@role_required
def uploadingAccessList():
    role=request.form.get("role").capitalize()
    project=request.form.get("project").capitalize()
    selectApp=request.form.get("selectApp")
    #find all applications to show
    cursor = mongo.db.applications.find({},{"_id": False})
    data = [item for item in cursor]
    jsonData = []
    #append per item
    for item in data:
            jsonData.append(item)
    #if role project does not have the app, add
    if mongo.db.assignedApp.count_documents({"role": role,'project':project,'selectApp':selectApp})==0:
        mongo.db.assignedApp.insert_one({"role": role,'project':project,'selectApp':selectApp})
    else:
        flash('Please amend input! ' +'Application ' + selectApp + 'has been associated with ' + project + ' / ' + role + ' previously.')
        checkDB = mongo.db.assignedApp.find({},{"_id": False})    
        data2 = [item for item in checkDB]
        jsonData2 = []
        for item in data2:
            jsonData2.append(item)
        return render_template("addApp.html",data2 = json.dumps(jsonData2),data = json.dumps(jsonData),roleCheck = session['role'] ,userID = session['username'].capitalize())

    #check the apps assigned to the project and role,for the table in html
    checkDB = mongo.db.assignedApp.find({},{"_id": False}).sort([("project", 1), ("role", 1)])
    data2 = [item for item in checkDB]
    jsonData2 = []
    for item in data2:
        print(item)
        jsonData2.append(item)
    #find all unique user in project role
    newCursor = mongo.db.assignedRole.find({"role": role,'project':project},{"_id": False}).distinct('uid')
    data3 = [item for item in newCursor]
    for item in data3:
        if mongo.db.requestsRaised.count_documents({'selectApp': selectApp ,'uid': item})==0:
            latestID = mongo.db.requestsRaised.count_documents({}) + 1
            check = mongo.db.applications.find_one({"appName": selectApp}, {"_id": False})
            mongo.db.requestsRaised.insert_one({"requestID" : latestID ,"role": role,'project':project,'selectApp':selectApp , 'uid' : item ,"requestType" : check['requestType'],'status':'pending', "requestRaised":datetime.now(),'raisedBy':session['username']})

    flash('Application ' + selectApp + 'has been associated with ' + project + ' / ' + role)
    return render_template("addApp.html",data2 = json.dumps(jsonData2),data = json.dumps(jsonData),roleCheck = session['role'] ,userID = session['username'].capitalize())

#access to assign user to role and project
@app.route("/assignProjectRole", methods =['GET','POST'])
@login_required
@role_required
def assignProjectRole():
    ##access database to extract data
    cursor = mongo.db.user.find({},{"_id": False})
    data = [item for item in cursor]
    jsonData = []
    #append per item
    for item in data:
        jsonData.append(item)
    #find the assigned roles for table
    checkDB = mongo.db.assignedRole.find({},{"_id": False}).sort([("project", 1), ("role", 1)])
    data2 = [item for item in checkDB]
    jsonData2 = []
    for item in data2:
        print(item)
        jsonData2.append(item)
    return render_template("assignProjectRole.html",data = json.dumps(jsonData),data2 = json.dumps(jsonData2), roleCheck = session['role'] ,userID = session['username'].capitalize())

#define user to the role/project
@app.route("/raiseRequest",methods =['GET','POST'])
@login_required
@role_required
def raiseRequest():
    role=request.form.get("role").capitalize()
    project=request.form.get("project").capitalize()
    selectUID=request.form.get("selectUID")
    #add the assignedRole if it is not yet assigned , else flash already assigned
    if mongo.db.assignedRole.count_documents({"role": role,'project':project,'uid':selectUID})==0:
        mongo.db.assignedRole.insert_one({"role": role,'project':project , 'uid' : selectUID})
        #find al lthe apps assigned to the role and project
        cursor = mongo.db.assignedApp.find({"role": role,'project':project},{"_id": False})
        data = [item for item in cursor]
        jsonData = []
        #append per item
        for item in data:
            print(item['selectApp'])
            #if app doesn exists for the user, insert the data
            if mongo.db.requestsRaised.count_documents({'selectApp':item['selectApp'] ,'uid': selectUID})==0:
                #get the app name etc
                check = mongo.db.applications.find_one({"appName": item['selectApp']}, {"_id": False})

                #check if any request exist, else get latest value and add 1
                if mongo.db.requestsRaised.count_documents({})==0:
                    latestID = 1
                else:
                    latestID = mongo.db.requestsRaised.count_documents({}) + 1
                #get the latest requestID and increment

                mongo.db.requestsRaised.insert_one({"requestID" : latestID ,"role": role,'project':project,'selectApp':item['selectApp'] , 'uid' : selectUID ,"requestType" : check['requestType'],'status':'pending', "requestRaised":datetime.now(),'raisedBy':session['username']})
    else:
        flash('This user previously has been assigned to this project and role, please amend input!')

    cursor = mongo.db.user.find({},{"_id": False})
    data = [item for item in cursor]
    jsonData = []
    #append per item
    for item in data:
        jsonData.append(item)
    checkDB = mongo.db.assignedRole.find({},{"_id": False}).sort([("project", 1), ("role", 1)])
    data2 = [item for item in checkDB]
    jsonData2 = []
    for item in data2:
        print(item)
        jsonData2.append(item)
    flash('Necessary requests will be raised')
    return render_template("assignProjectRole.html",data = json.dumps(jsonData),data2 = json.dumps(jsonData2),roleCheck = session['role'] ,userID = session['username'].capitalize())

#view requests
@app.route("/requests", methods =['GET'])
@login_required
def requests():
    check = False
    #check if user is manager , show all requests, else only show his request
    if session['role'] in ["manager"]:
        cursor = mongo.db.requestsRaised.find({},{"_id": False})
    else:
        cursor = mongo.db.requestsRaised.find({"uid": session['username']},{"_id": False})
    data = [item for item in cursor]
    jsonData = []
    #append per item
    for item in data:
        jsonData.append(item)

    if len(jsonData) == 0:
        check = True
    #check if role is manager, then need to see all request raised
    print(session['role'])
    return render_template("requests.html",check = check,data = json.dumps(jsonData),roleCheck = session['role'] ,userID = session['username'].capitalize())


@app.route("/training", methods =['GET'])
@login_required
def training():

    return render_template("training.html")

@app.route("/calender", methods =['GET'])
@login_required
def calender():

    return render_template("calender.html")

@app.route("/document", methods =['GET'])
@login_required
def document():
    return render_template("document.html")

from waitress import serve
#check executed file is the main then run the file
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080, threads=5)
    #app.run(debug=True)
