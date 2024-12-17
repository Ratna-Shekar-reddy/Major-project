import hashlib

from flask import *
import pandas as pd
import numpy as np
from mysql import connector
import mysql.connector
mydb=mysql.connector.connect(user='root',host="localhost",password='new_password',port=3306,database='ehealthsystems')
cur=mydb.cursor()
from flask_mail import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint


app=Flask(__name__)
app.secret_key="kjabcnsnc89yr84rfwe7ry"


@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/userreg",methods=["POST","GET"])
def userreg():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        age=request.form['age']
        number=request.form['number']
        password=request.form['password']
        confirmpassword=request.form['confirmpassword']
        if password == confirmpassword:
            sql="select * from userregistration where Email='%s'"%(email)
            cur.execute(sql)
            data=cur.fetchall()
            mydb.commit()
            if data == []:
                pri_key=randint(000000,999999)
                sql="insert into userregistration(Name,Email,Age,Number,Password,Prikey)values(%s,%s,%s,%s,%s,%s)"
                val=(name,email,age,number,password,pri_key)
                cur.execute(sql,val)
                mydb.commit()
                content = f"The key to login :key 1 : {pri_key}  "
                sender_address = 'ratnashekarreddy30082003@gmail.com'
                sender_pass = 'zksd ieob cjbb rbzc'
                receiver_address = email
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'Agriculture Product Supply Chain'
                message.attach(MIMEText(content, 'plain'))
                section = smtplib.SMTP('smtp.gmail.com', 587)
                section = smtplib.SMTP('smtp.gmail.com', 587)
                section.starttls()
                section.login(sender_address, sender_pass)
                text = message.as_string()
                section.sendmail(sender_address, receiver_address, text)
                section.quit()
                return render_template("userlog.html")
            else:
                msg="details already exist"
                return render_template('userreg.html',msg=msg)
    return render_template('userreg.html')


@app.route("/userlog",methods=['POST','GET'])
def userlog():
    if request.method=='POST':
        email=request.form['email']
        session['useremail']=email
        password=request.form['password']
        OTP=request.form['key']
        sql="select * from userregistration Where Email='%s' and Password='%s'"%(email,password)
        cur.execute(sql)
        data=cur.fetchall()
        mydb.commit()
        if data==[]:
            msg = "details are not valid"
            return render_template("userlog.html", msg=msg)
        else:
            if OTP == data[0][-1]:
                return render_template("userhome.html")
            else:
                msg="OTP is not valid"
                return render_template("userlog.html",msg=msg)

    return render_template("userlog.html")

@app.route('/cloudlogin',methods=['POST','GET'])
def cloudlogin():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        if email=="shekarreddyrathna93982@gmail.com" and password=='cloud@30':
            return render_template("cloudhome.html")
        else:
            msg="details are not valid"
            return render_template("cloudlogin.html",msg=msg)
    return render_template("cloudlogin.html")



@app.route("/uploadfile",methods=['POST','GET'])
def uploadfile():
    global x
    if request.method=='POST':
        filedata=request.files['filedata']
        filename=filedata.filename
        session['filename']=filename
        
        data=pd.read_csv(filedata)
        x=data
        return render_template("uploadfile.html",data=x)
    return render_template("uploadfile.html")


@app.route("/viewrecords")
def viewrecords():
    df=x
    import pymysql
    pymysql.install_as_MySQLdb()
    from sqlalchemy import create_engine
    sql = "TRUNCATE table filedata"
    cur = mydb.cursor()
    cur.execute(sql)
    mydb.commit()
    # sql="insert into finalreport(User,filename)values('%s','%s')"%(session['useremail'],session['filename'])
    # cur.execute(sql)
    # mydb.commit()
   
    engine = create_engine("mysql://{user}:{pw}@localhost:{port}/{db}".format(user="root", pw="new_password",port=3306, db="ehealthsystems"))
    df.to_sql('filedata', con=engine, if_exists='append', chunksize=150,index=False)

    sql="select * from filedata"
    data=pd.read_sql_query(sql,mydb)
    return render_template('viewrecords.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/encryptfiles')
def encryptfiles():
    sql="select * from filedata"
    data=pd.read_sql_query(sql,mydb)
    print(data)
    for i in range(len(data)):
        i=data.values[i]
        age = str(i[1])
        sex=str(i[2])
        cp=str(i[3])
        trestbps=str(i[4])
        chol=str(i[5])
        fbs=str(i[6])
        restecg=str(i[7])
        thalach=str(i[8])
        exang=str(i[9])
        oldpeack=str(i[10])
        slope=str(i[11])
        ca=str(i[12])
        thal=str(i[13])
        target=str(i[14])
        pid=(i[15])

        # sql="update filedata set useremail='%s' where useremail=''"%(session['useremail'])
        # cur.execute(sql)
        # mydb.commit()
        sql="insert into filedata_encdata(age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target,Generatedkey,useremail)values(AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),%s,%s)"
        val = (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeack, slope, ca, thal, target,pid,session['useremail'])
        cur.execute(sql,val)
        mydb.commit()
    return render_template('encryptfiles.html')


@app.route('/Viewencrecords')
def Viewencrecords():
    sql="select age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target,Generatedkey from filedata_encdata where useremail='%s'"%(session['useremail'])
    data=pd.read_sql_query(sql,mydb)
    return render_template("Viewencrecords.html",cols=data.columns.values,rows=data.values.tolist())

@app.route('/viewresponse')
def viewresponse():
    sql="select distinct Status from filedata_encdata where useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    status=data[0][0]
    if status == 'accept':
        flash("permission granted","success")
        return render_template('viewresponse.html')
    else:
        try:
            flash("permission in not granted", "success")
            msg="notaccepted"
            return render_template('viewresponse.html',msg=msg)
        except:
            pass

    return render_template('viewresponse.html')

@app.route('/blockchain')
def blockchain():
    sql="select Generatedkey from filedata_encdata where useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    return render_template('blockchain.html',data=data)

@app.route('/uploadtocloudserver')
def uploadtocloudserver():

    sql="update filedata_encdata set status='done' where status='accept' and useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    mydb.commit()
    flash("request sent successfully",'success')
    return redirect('blockchain')

@app.route('/sendrequest')
def sendrequest():
    sql="update filedata_encdata set status='pending' where status='none' and useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    mydb.commit()
    flash("request sent successfuly","success")
    return redirect(url_for('Viewencrecords'))


@app.route('/usersrequest')
def usersrequest():
    sql="select distinct useremail from filedata_encdata where status='pending'"
    data=pd.read_sql_query(sql,mydb)
    return render_template('usersrequest.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/downloadrequest')
def downloadrequest():
    return render_template('downloadrequest.html')

@app.route('/filesearch',methods=['POST','GET'])
def filesearch():
    if request.method=='POST':
        fileid=request.form['searchfile']
        sql = "select status from filedata_encdata where Generatedkey=%s and useremail=%s"
        params = (fileid, session['useremail'])
        cur.execute(sql, params)

        data=cur.fetchall()
        mydb.commit()

        if data[0][0]==[]:
            msg="please raise request"
            return render_template('downloadrequest.html', msg=msg)
        elif data[0][0]=='done':
            sql = "update filedata_encdata set status='request' where status='done' and useremail='%s' and Generatedkey='%s'" % (session['useremail'],fileid)
            cur.execute(sql)
            mydb.commit()
            msg="file not found"
            msg1="your request sent to cloud"
            return render_template('downloadrequest.html',msg=msg,msg1=msg1)
        elif data[0][0]=='complete':
            sql="select Slno,age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target from filedata_encdata where useremail='%s' and Generatedkey='%s'" % (session['useremail'],fileid)
            # cur.execute(sql)
            # data = cur.fetchall()
            # mydb.commit()
            data=pd.read_sql_query(sql,mydb)
            # f = [j for i in data for j in i]
            # z=f[0]
            # a = f[1]
            # b = f[2]
            # c = f[3]
            # d = f[4]
            # e = f[5]
            # g = f[6]
            # h = f[7]
            # i = f[8]
            # j = f[9]
            # k = f[10]
            # l = f[11]
            # m = f[12]
            # n = f[13]
            # o = f[14]
            msg = "your request accepted"
            # return render_template('decryptfile.html', a=a, b=b, c=c, d=d, e=e, g=g, h=h, i=i, j=j, k=k, l=l, m=m, n=n,o=o,msg=msg)
            return render_template('downloadrequest.html', msg=msg,cols=data.columns.values,rows=data.values.tolist())
        else:
            msg = "request already sent"
            return render_template('downloadrequest.html', msg=msg)
    return render_template('downloadrequest.html')

@app.route('/decryptfile/<z>')
def decryptfile(z=0):

    sql="select AES_DECRYPT(age,'keys'),AES_DECRYPT(sex,'keys'),AES_DECRYPT(cp,'keys'),AES_DECRYPT(trestbps,'keys'),AES_DECRYPT(chol,'keys'),AES_DECRYPT(fbs,'keys'),AES_DECRYPT(restecg,'keys'),AES_DECRYPT(thalach,'keys'),AES_DECRYPT(exang,'keys'),AES_DECRYPT(oldpeak,'keys'),AES_DECRYPT(slope,'keys'),AES_DECRYPT(ca,'keys'),AES_DECRYPT(thal,'keys'),AES_DECRYPT(target,'keys') from filedata_encdata where Slno='%s'"%(z)
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    j=[j for i in data for j in i]
    f=[k.decode() for k in j]

    a=f[0]
    b=f[1]
    c=f[2]
    d=f[3]
    e=f[4]
    g=f[5]
    h=f[6]
    i=f[7]
    j=f[8]
    k=f[9]
    l=f[10]
    m=f[11]
    n=f[12]
    o=f[13]

    return render_template('decryptfile.html',a=a,b=b,c=c,d=d,e=e,g=g,h=h,i=i,j=j,k=k,l=l,m=m,n=n,o=o)
    # return render_template('decryptfile.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/downloadfilerequest')
def downloadfilerequest():
    sql="select distinct useremail from filedata_encdata where status='request'"
    data=pd.read_sql_query(sql,mydb)

    return render_template('downloadfilerequest.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/verifyfiles/<c>/')
def verifyfiles(c=''):

    sql="update filedata_encdata set status='complete' where useremail='%s'"%(c)
    cur.execute(sql)
    mydb.commit()
    return redirect(url_for('downloadfilerequest'))

@app.route('/downloadfile')
def downloadfile():

    return redirect(url_for('downloadrequest'))


# viewallrecords

@app.route('/viewallrecords')
def viewallrecords():
    sql="select * from filedata"
    data=pd.read_sql_query(sql,mydb)

    sql1="select age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target from filedata_encdata where status='done' and useremail='%s'"%(session['useremail'])
    data1=pd.read_sql(sql1,mydb)

    # if data1.index==[]:
    #     msgs="notdecrpted"
    #     return render_template('viewallrecords.html', cols=data.columns.values, rows=data.values.tolist(),msgs=msgs)
    return render_template('viewallrecords.html',cols=data.columns.values,rows=data.values.tolist(),cols1=data1.columns.values,rows1=data1.values.tolist())

@app.route('/acceptuserrequest/<n1>')
def acceptuserrequest(n1=""):
    n1=n1[2:len(n1)-1]#modified by mee
    
    #sql="update filedata_encdata set Status='accept' where useremail='%s' and Status='pending'"%(n1)
    sql = "UPDATE filedata_encdata SET Status = 'accept' WHERE useremail = %s AND Status = 'pending'"
    cur.execute(sql, (n1,))
    mydb.commit()

    #cur.execute(sql)
    #mydb.commit()
    # sql="select Email from userregistration where Id='%s'"%(n1)
    # cur.execute(sql)
    # data=cur.fetchall()
    # mydb.commit()

    content = f"User request is verifyed "
    sender_address = 'ratnashekarreddy30082003@gmail.com'
    sender_pass = 'zksd ieob cjbb rbzc'
    receiver_address = n1
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Agriculture Product Supply Chain'
    message.attach(MIMEText(content, 'plain'))
    section = smtplib.SMTP('smtp.gmail.com', 587)
    section.starttls()
    section.login(sender_address, sender_pass)
    text = message.as_string()
    section.sendmail(sender_address, receiver_address, text)
    section.quit()
    return redirect(url_for('usersrequest'))



@app.route('/securefile/<r1>/<r2>')
def securefile(r1=0,r2=''):
    sql="select Filedata from dataowneruploadfiles where Slno='%s'"%(r1)
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    enc_data=data[0][0]

    datalen = int(len(enc_data) / 2)

    g = 0
    a = ''
    b = ''
    c = ''
    for i in range(0, 2):
        if i == 0:
            a = enc_data[g: datalen:1]
            # a=a.decode('utf-8')

            result = hashlib.sha1(a.encode())
            hash1 = result.hexdigest()




    c = enc_data[datalen: len(enc_data):1]

    result = hashlib.sha1(c.encode())
    hash2 = result.hexdigest()
    sql="update dataowneruploadfiles set FileEncData=AES_ENCRYPT('%s','key'),Dataone=AES_ENCRYPT('%s','key'),Datatwo=AES_ENCRYPT('%s','key'),status='allow',Hash1='%s',Hash2='%s' where Slno='%s' and status='accepted'"%(enc_data,a,c,hash1,hash2,r1)
    cur.execute(sql)
    mydb.commit()


@app.route("/hsplogout")
def hsplogout():
    return redirect(url_for('home'))


@app.route("/cloudlogout")
def cloudlogout():
    return redirect(url_for('home'))


if __name__=="__main__":
    app.run(debug=True,port=8000)
