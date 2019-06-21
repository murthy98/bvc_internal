from flask import Flask, render_template, flash, request, url_for, redirect,session
from dbconnection import connection
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt
import gc
import flask_excel as excel
from flask_socketio import SocketIO, emit
global down
down=False
app = Flask(__name__)
excel.init_excel(app)
app.config['SECRET_KEY'] = 'redsfsfsfsfis'
socketio = SocketIO(app)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.googlemail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'bvcec.marks@gmail.com',
	MAIL_PASSWORD = 'xgxhgwtreazidkkh'
	)
mail = Mail(app)
def send_mail(email):
	try:
        
		msg = Message("Forgot Password",sender="bvcec.marks@gmail.com",recipients=[str(email)])
		msg.body = "Please click the below link to change your password\n\n http://studentgradebvc.herokuapp.com/pwchange"
		mail.send(msg)
		return 'Mail sent!'
	except Exception as e:
		return(str(e)) 
@socketio.on('disconnect')
def disconnect_user():
    session.clear()
@app.route("/")
def homepage():
    session.clear()

    return render_template("login.html")
@app.route("/pwchange")
def pwchange():

    return render_template("pwchange.html")
@app.route('/passchange',methods=['GET','POST'])
def passchange():
    c,conn = connection()
   
    try:
        
        if request.method == "POST" :
                c.execute("UPDATE users SET password=%s WHERE id=%s",(sha256_crypt.encrypt(request.form["password"]),request.form["id"]))
                conn.commit()
                conn.close()
                gc.collect()
                flash('Please login')
                return render_template("login.html",type=type)
    except Exception as e:
        flash('Invalid Credentials')
        return render_template("login.html")
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")
@app.route("/initial",methods=['GET','POST'])
def initial():

    return render_template('home.html')
@app.route("/home",methods=['GET','POST'])
def login():
    
    c,conn = connection()
   
    try:
        
        if request.method == "POST" :
            if 'submit' in request.form:
                c.execute("SELECT * FROM users WHERE id = ('%s')" %request.form["id"])
               
                data = c.fetchone()
                if sha256_crypt.verify(request.form['password'],data[1] ):
                    type=data[2]
                    c.close()
                    session['logged_in'] = True
                    session['username'] = request.form['id']
                    conn.commit()
                    conn.close()
                    gc.collect()
                    return render_template("home.html",type=type)
    except Exception as e:
        flash('Invalid Credentials')
        return render_template("login.html")
    return render_template("login.html")
@app.route('/forgot')
def forgot():
    return render_template('forgot.html')
@app.route('/forgotpw',methods=['GET','POST'])
def forgotpw():
    try:
        
        if request.method == "POST" :
            c,conn=connection()
            c.execute("SELECT email FROM users WHERE id=('%s')" %request.form["id"])
            data=c.fetchall()
            x=send_mail(data[0][0])
            if(x=='Mail sent!'):
                flash("pleasecheck your mail")
            else:
                flash('please contact admin. we are unable to sent the mail!!.please provide correct mail.')
            return render_template('login.html')

    except Exception as e:
        flash('please contact admin. we are unable to sent the mail!!.please provide correct mail.')
        return render_template('login.html')
    return render_template('forgot.html')
@app.route('/user',methods=['GET','POST'])
def user():
    try:
        
        if request.method == "POST" :
            cond=request.form["customRadio1"]
            id=request.form["id"]
            password=sha256_crypt.encrypt(request.form["password"])
            typ=request.form.get('type')
            email=request.form["email"]
            if(cond=='adduser'):
                c,conn=connection()
                c.execute("INSERT INTO users VALUES (%s,%s, %s,%s)",(id,password,typ,email))
                conn.commit()
                conn.close()
                gc.collect()
                flash('Succeccfully added new user')
                return render_template("home.html",type=type)
            if(cond=='deluser'):
                c,conn=connection()
                c.execute("DELETE FROM users WHERE id=%s",(id))
                conn.commit()
                conn.close()
                gc.collect()
                flash('Succeccfully deleted user')
                return render_template("home.html",type=type)

    except Exception as e:
       flash("Invalid Credentials")
    return render_template("home.html",type=type)

@app.route('/addstudent',methods=['GET','POST'])
def addstudent():
    try:
        
        if request.method == "POST" :
            cond=request.form["customRadio"]
            if(cond=='addstudent'):
                name=request.form['name']
                roll=request.form['roll']
                year=request.form['acyear']
                branch=request.form['branch']
                c,conn=connection()
                try:
                    c.execute("INSERT INTO student VALUES (%s,%s, %s,%s)",(roll,name,branch,year))
                    conn.commit()  
                    conn.close()
                    gc.collect()
                    flash(roll+' Added Successfully') 
                except Exception:
                    flash('Invalid Credentials')    
            elif(cond=='viewstudent'):
                c,conn=connection()
                year=request.form['acyear']
                branch=request.form['branch']
                try:
                    c.execute("SELECT roll,name,branch,acyear FROM student WHERE acyear=%s AND branch=%s",(year,branch,))
                    data=c.fetchall()
                    if data:
                        colname=[desc[0] for desc in c.description]
                        data.insert(0,colname)
                    return render_template('view.html',data=data,down=down)
                except Exception as e:
                    flash('Invalid Credentials')    
            else:
                c,conn=connection()
                roll=request.form['roll']
                try:
                    c.execute("DELETE FROM student WHERE roll = %s",(roll))
                    conn.commit()
                    conn.close()
                    gc.collect()
                    flash(roll+' Deleted Successfully')
                except Exception:
                    flash('Unable to find given details')
    except Exception as e:
        flash('Unable to connect Please try again')
    return render_template('home.html')
@app.route('/subject',methods=['GET','POST'])
def subject():
    try:
        
        if request.method == "POST" :
            c,conn=connection()
            cond=request.form["customRadio1"]
            subname=request.form['subname']
            sem=request.form.get('sem')

            if(cond=='addsubj'):
                s=''
                try:
                    c.execute("INSERT INTO subject VALUES (%s,%s)",(subname,sem))
                    s="ALTER TABLE student ADD "+str(subname)+str(sem)+"mid1 INTEGER"
                    c.execute(s)
                    s="ALTER TABLE student ADD "+str(subname)+str(sem)+"mid2 INTEGER"
                    c.execute(s)

                    conn.commit()
                    conn.close()
                    gc.collect()
                    flash('successfully added')
                except Exception:
                    flash("Invalid credentials")
            if(cond=='delsubj'):
                s=''
                try:
                    s="ALTER TABLE student DROP "+str(subname)+str(sem)+'mid1'
                    c.execute("DELETE FROM subject WHERE sem = %s AND name=%s",(sem,subname))
                    c.execute(s)
                    s="ALTER TABLE student DROP "+str(subname)+str(sem)+'mid2'
                    c.execute(s)
                    conn.commit()
                    conn.close()
                    gc.collect()
                    flash("successfully removed")
                except Exception:
                    flash('Invalid credentials')
            if(cond=='viewsubj'):
                try:
                    c.execute("SELECT name,sem FROM subject WHERE sem=%s",(sem))
                    data=c.fetchall()
                    if data:
                        colname=[desc[0] for desc in c.description]
                        data.insert(0,colname)
                    return render_template('view.html',data=data,down=down)
                except Exception as e:
                    flash('Invalid Credentials')
    except Exception as e:
        flash('Invalid Credentials')
    return render_template("home.html")
   

@app.route('/marks',methods=['GET','POST'])
def marks():
    try:
        global st
        if request.method == "POST" :
            sem=request.form.get('sem')
            subname=request.form['subname']
            mid=request.form["customRadio3"]
            c,conn=connection()
            cond=request.form["customRadio2"]
            year=request.form['acyear'] 
            branch=request.form['branch']
            if(cond=='uploadmarks'):
                st=[]
                s=''
                
                s+=str(subname)+' '+str(sem)+' '+str(mid)
                st.append(year)
                st.append(s)
             
                c.execute("SELECT roll FROM student WHERE acyear=%s AND branch=%s",(year,branch))
                st.append(c.fetchall())                
                return render_template('marks.html',data=st)
            if(cond=='modifymarks'):
                st=[]
                s=''
                roll=request.form['roll']   
                s+=str(subname)+' '+str(sem)+' '+str(mid)
                st.append(year)
                st.append(s)
                roll=tuple([str(roll)])
                st.append([roll])
                return render_template('marks.html',data=st)
           
            if(cond=='viewmarks'):
                global view
                s=ct=''
                s+=str(subname)+str(sem)+str(mid)
                ct="SELECT roll,name,branch,"+s+" FROM student WHERE acyear=%s AND branch=%s"
                c.execute(ct,(year,branch,))
                view=c.fetchall()
                if view:
                    colname=[desc[0] for desc in c.description]
                    view.insert(0,colname)
                down=True
                return render_template('view.html',data=view,down=down)
    except Exception as e:
        flash("Invalid Credentials")
    return render_template('home.html')
@app.route('/upload',methods=['GET','POST'])
def upload():
    try:
        c,conn=connection()
        s=''
        if request.method == "POST" :
            for i in st[2:]:
                for j in i:
                    marks=request.form[j[0]]
                    s='UPDATE student SET '+st[1].replace(' ','')+'=%s WHERE roll=%s'
                    c.execute(s,(marks,j[0]))
                    conn.commit()
                    conn.close()
                    gc.collect()
            flash('Successfully Uploaded')
        
        return render_template('home.html')
    except Exception as e:
        flash('Invalid Credentials')
    return render_template('home.html')

@app.route("/download", methods=['GET','POST'])
def download():
    c,conn=connection()
    with conn:
        with c:
            v=[]
            v=[list(item) for item in view]           
            return excel.make_response_from_array(v, "csv",file_name="mid_marks")
if __name__ == "__main__":
    app.secret_key="dwqwfewfwqdqw"
    
    app.run(debug=True)