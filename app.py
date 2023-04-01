import sqlite3
from sqlite3 import Error
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re
import pandas as pd
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from helpers import login_required, create_connection, execute_read_query, execute_query

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    #Log out any current user that was in
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("redirect.html")
        elif not request.form.get("password"):
            return render_template("redirect.html")

        #Connect to SQL database for use
        connection = create_connection("pFinances.db")

        userSQL = ("SELECT * FROM users WHERE username = " + "'" + request.form.get("username") + "'")
        users = execute_read_query(connection, str(userSQL))

        #Check username is present and passwords are a match via hash
        if len(users) != 1 or not check_password_hash(users[0][2], request.form.get("password")):
            return render_template("redirect.html")

        #store users user id in session dictionary
        session["user_id"] = users[0][0]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        if name == "":
            return render_template("redirect.html")
        elif password == "":
            return render_template("redirect.html")
        elif password != confirmation:
            return render_template("redirect.html")
        elif email == "":
            return render_template("redirect.html")

        #Connect to SQL database for use
        connection = create_connection("pFinances.db")

        userSQL = ("SELECT * FROM users WHERE username = " + "'" + request.form.get("username") + "'")
        users = execute_read_query(connection, str(userSQL))

        if users:
            return render_template("redirect.html")
        else:
            insertSQL = ("INSERT INTO users (username, passHash, email) VALUES" + "('" + name + "'" + ", '" + generate_password_hash(password) + "', '" + email + "')")
            execute_query(connection, str(insertSQL))

            return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Connect to SQL database for use
    connection = create_connection("pFinances.db")

    incomeSQL = ("SELECT amount FROM income WHERE userID = " + str(session["user_id"]))
    incomeTuple = execute_read_query(connection, str(incomeSQL))

    i = 0
    income = 0
    while i < len(incomeTuple):
        temp = incomeTuple[i]
        income = income + temp[0]
        i = i + 1

    fixCostsSQL = ("SELECT amount FROM fixedCosts WHERE userID = " + str(session["user_id"]))
    fixCostsTuple = execute_read_query(connection, str(fixCostsSQL))

    i = 0
    fixCosts = 0
    while i < len(fixCostsTuple):
        temp = fixCostsTuple[i]
        fixCosts = fixCosts + temp[0]
        i = i + 1

    varCostsSQL = ("SELECT amount FROM varCosts WHERE userID = " + str(session["user_id"]))
    varCostsTuple = execute_read_query(connection, str(varCostsSQL))

    i = 0
    varCosts = 0
    while i < len(varCostsTuple):
        temp = varCostsTuple[i]
        varCosts = varCosts + temp[0]
        i = i + 1

    balance = income - fixCosts - varCosts

    usernameSQL = ("SELECT username FROM users WHERE id = " + str(session["user_id"]))
    usernameTuple = execute_read_query(connection, str(usernameSQL))
    username = "%s" % usernameTuple[0]

    return render_template("index.html", username=username, income=income, fixCosts=fixCosts, varCosts="{:.2f}".format(varCosts), balance=round(balance,2))


@app.route("/addVarCost", methods=["GET", "POST"])
@login_required
def addVarCost():
    connection = create_connection("pFinances.db")

    if request.method == "POST":
        rowsToDelete = request.form.get("deleteInput")
        deleteMode = request.form.get("removeClicked")

        if rowsToDelete != "" and deleteMode != "" and int(deleteMode) == 1: #check if anything to delete
            rowNums = []
            for x in range(len(rowsToDelete)):
                if (rowsToDelete[x] != ','):
                    rowNums.append(rowsToDelete[x])

            varCostSQL = ("SELECT id FROM varCosts WHERE userID = " + str(session["user_id"]))
            varCostTuple = execute_read_query(connection, str(varCostSQL))

            tupleList = list(varCostTuple)

            idList = []
            for y in range(len(rowNums)):
                if int(rowNums[y]) == 1:
                    idList.append(re.sub("[^0-9]", "", str(tupleList[y])))

            deleteSQL = ("DELETE FROM varCosts WHERE id IN (" +', '.join(idList) + ")")
            execute_query(connection, deleteSQL)
            return redirect("/addVarCost")
        else:
            amount = request.form.get("amount")
            method = request.form.get("method")
            description = request.form.get("description")
            date = request.form.get("date")

            if str(method) == "None":
                method = "Default"

            insertSpending = ("INSERT INTO varCosts (userID, method, description, amount, date) VALUES" + "('" + str(session["user_id"]) + "', '" + method + "', '" + description + "', '" + str(amount) + "', '" + str(date) + "')")
            execute_query(connection, str(insertSpending))

            varCostSQL = ("SELECT amount,method,description,date FROM varCosts WHERE userID = " + str(session["user_id"]))
            varCostTuple = execute_read_query(connection, str(varCostSQL))

            keys = ['amount', 'method','description','date']
            varCostDicts = [dict(zip(keys,d)) for d in varCostTuple]

            total = 0.0
            for x in range(len(varCostDicts)):
                total = total + float(varCostDicts[x]['amount'])

            return redirect("/addVarCost")
    else:
        varCostSQL = ("SELECT amount,method,description,date FROM varCosts WHERE userID = " + str(session["user_id"]))
        varCostTuple = execute_read_query(connection, str(varCostSQL))

        keys = ['amount', 'method','description','date']
        varCostDicts = [dict(zip(keys,d)) for d in varCostTuple]

        total = 0.0
        for x in range(len(varCostDicts)):
            total = total + float(varCostDicts[x]['amount'])

        methodSQL = ("SELECT payMethod FROM payMethods WHERE userID = " + str(session["user_id"]))
        methodTuple = execute_read_query(connection, str(methodSQL))

        keys = ['method']
        methodDicts = [dict(zip(keys,d)) for d in methodTuple]

        return render_template("addVarCost.html", varCostDicts=varCostDicts, total=total, methodDicts=methodDicts)


@app.route("/addIncome", methods=["GET", "POST"])
@login_required
def addIncome():
    # Connect to SQL database for use
    connection = create_connection("pFinances.db")

    if request.method == "POST":
        rowsToDelete = request.form.get("deleteInput")
        deleteMode = request.form.get("removeClicked")

        if rowsToDelete != "" and deleteMode != "" and int(deleteMode) == 1: #check if anything to delete
            rowNums = []
            for x in range(len(rowsToDelete)):
                if (rowsToDelete[x] != ','):
                    rowNums.append(rowsToDelete[x])

            incomeSQL = ("SELECT id FROM income WHERE userID = " + str(session["user_id"]))
            incomeTuple = execute_read_query(connection, str(incomeSQL))

            tupleList = list(incomeTuple)

            idList = []
            for y in range(len(rowNums)):
                if int(rowNums[y]) == 1:
                    idList.append(re.sub("[^0-9]", "", str(tupleList[y])))

            deleteSQL = ("DELETE FROM income WHERE id IN (" +', '.join(idList) + ")")
            execute_query(connection, deleteSQL)
            return redirect("/addIncome")
        else:
            amount = request.form.get("amount")
            description = request.form.get("description")

            insertIncome = ("INSERT INTO income (userID, source, amount) VALUES" + "('" + str(session["user_id"]) + "','" + description + "','" + amount + "')")
            execute_query(connection, str(insertIncome))

            incomeSQL = ("SELECT amount,source FROM income WHERE userID = " + str(session["user_id"]))
            incomeTuple = execute_read_query(connection, str(incomeSQL))

            keys = ['amount', 'source']
            incomeDicts = [dict(zip(keys,d)) for d in incomeTuple]

            total = 0.0
            for x in range(len(incomeDicts)):
                total = total + float(incomeDicts[x]['amount'])

            return render_template("addIncome.html", incomeDicts=incomeDicts, total=round(total,2))
    else:
        incomeSQL = ("SELECT amount,source FROM income WHERE userID = " + str(session["user_id"]))
        incomeTuple = execute_read_query(connection, str(incomeSQL))

        keys = ['amount', 'source']
        incomeDicts = [dict(zip(keys,d)) for d in incomeTuple]

        total = 0.0
        for x in range(len(incomeDicts)):
            total = total + float(incomeDicts[x]['amount'])

        return render_template("addIncome.html", incomeDicts=incomeDicts, total=round(total,2))


@app.route("/addFixedCosts", methods=["GET", "POST"])
@login_required
def addFixedCosts():
    # Connect to SQL database for use
    connection = create_connection("pFinances.db")

    if request.method == "POST":
        rowsToDelete = request.form.get("deleteInput")
        deleteMode = request.form.get("removeClicked")

        if rowsToDelete != "" and deleteMode != "" and int(deleteMode) == 1: #check if anything to delete
            rowNums = []
            for x in range(len(rowsToDelete)):
                if (rowsToDelete[x] != ','):
                    rowNums.append(rowsToDelete[x])

            fixCostSQL = ("SELECT id FROM fixedCosts WHERE userID = " + str(session["user_id"]))
            fixCostTuple = execute_read_query(connection, str(fixCostSQL))

            tupleList = list(fixCostTuple)

            idList = []
            for y in range(len(rowNums)):
                if int(rowNums[y]) == 1:
                    idList.append(re.sub("[^0-9]", "", str(tupleList[y])))

            deleteSQL = ("DELETE FROM fixedCosts WHERE id IN (" +', '.join(idList) + ")")
            execute_query(connection, deleteSQL)
            return redirect("/addFixedCosts")

        else:
            amount = request.form.get("amount")
            description = request.form.get("description")

            insertFixCost = ("INSERT INTO fixedCosts (userID, source, amount, frequency) VALUES" + "('" + str(session["user_id"]) + "','" + description + "','" + amount + "','" + "1" + "')")
            execute_query(connection, str(insertFixCost))

            fixCostsSQL = ("SELECT amount,source FROM fixedCosts WHERE userID = " + str(session["user_id"]))
            fixCostsTuple = execute_read_query(connection, str(fixCostsSQL))
            keys = ['amount', 'source']
            fixCostsDicts = [dict(zip(keys,d)) for d in fixCostsTuple]

            total = 0.0
            for x in range(len(fixCostsDicts)):
                total = total + float(fixCostsDicts[x]['amount'])

            return render_template("addFixedCosts.html", fixCostsDicts=fixCostsDicts, total=round(total,2))

    else:
        fixCostsSQL = ("SELECT amount,source FROM fixedCosts WHERE userID = " + str(session["user_id"]))
        fixCostsTuple = execute_read_query(connection, str(fixCostsSQL))

        keys = ['amount', 'source']
        fixCostsDicts = [dict(zip(keys,d)) for d in fixCostsTuple]

        total = 0.0
        for x in range(len(fixCostsDicts)):
            total = total + float(fixCostsDicts[x]['amount'])

        return render_template("addFixedCosts.html", fixCostsDicts=fixCostsDicts, total=round(total,2))


@app.route("/deleteData", methods=["GET", "POST"])
@login_required
def deleteData():
    # Connect to SQL database for use
    connection = create_connection("pFinances.db")
    usernameSQL = ("SELECT username FROM users WHERE id = " + str(session["user_id"]))
    usernameTuple = execute_read_query(connection, str(usernameSQL))
    username = "%s" % usernameTuple[0]

    emailSQL = ("SELECT email FROM users WHERE id = " + str(session["user_id"]))
    emailTuple = execute_read_query(connection, str(emailSQL))
    email = "%s" % emailTuple[0]

    if request.method == "POST":
        deleteDict = {
            'var': request.form.get("spending"),
            'fixed': request.form.get("fixed"),
            'income': request.form.get("income"),
            'payMethods': request.form.get("payMethods")
        }

        if deleteDict['var'] != None:
            deleteSQL = ("DELETE FROM varCosts WHERE userID = " + str(session["user_id"]))
            execute_query(connection, deleteSQL)
        if deleteDict['fixed'] != None:
            deleteSQL = ("DELETE FROM fixedCosts WHERE userID = " + str(session["user_id"]))
            execute_query(connection, deleteSQL)
        if deleteDict['income'] != None:
            deleteSQL = ("DELETE FROM income WHERE userID = " + str(session["user_id"]))
            execute_query(connection, deleteSQL)
        if deleteDict['payMethods'] != None:
            deleteSQL = ("DELETE FROM payMethods WHERE userID = " + str(session["user_id"]))
            execute_query(connection, deleteSQL)

        return render_template("deleteData.html", username=username, email=email)

    else:
        return render_template("deleteData.html", username=username, email=email)


@app.route("/customize", methods=["GET", "POST"])
@login_required
def customize():
    # Connect to SQL database for use
    connection = create_connection("pFinances.db")
    usernameSQL = ("SELECT username FROM users WHERE id = " + str(session["user_id"]))
    usernameTuple = execute_read_query(connection, str(usernameSQL))
    username = "%s" % usernameTuple[0]

    if request.method == "POST":
        rowsToDelete = request.form.get("deleteInput")
        deleteMode = request.form.get("removeClicked")
        if rowsToDelete != "" and deleteMode != "" and int(deleteMode) == 1: #check if anything to delete
            rowNums = []
            for x in range(len(rowsToDelete)):
                if (rowsToDelete[x] != ',' and x != 0):
                    rowNums.append(rowsToDelete[x])

            payMethSQL = ("SELECT id FROM payMethods WHERE userID = " + str(session["user_id"]))
            payMethTuple = execute_read_query(connection, str(payMethSQL))

            tupleList = list(payMethTuple)

            idList = []
            for y in range(len(rowNums)):
                if int(rowNums[y]) == 1:
                    idList.append(re.sub("[^0-9]", "", str(tupleList[y])))

            deleteSQL = ("DELETE FROM payMethods WHERE id IN (" +', '.join(idList) + ")")
            execute_query(connection, deleteSQL)

        #inserting any new payment methods in sql table
        methodField = (request.form.get("method")).splitlines()

        for x in range(len(methodField)):
            insertSQL = ("INSERT INTO payMethods (userID, payMethod) VALUES" + "('" + str(session["user_id"]) + "','" + methodField[x] + "')")
            execute_query(connection, insertSQL)

        payMethSQL = ("SELECT payMethod FROM payMethods WHERE userID = " + str(session["user_id"]))
        payMethTuple = execute_read_query(connection, str(payMethSQL))

        keys = ['payMeth']
        payMethDicts = [dict(zip(keys,d)) for d in payMethTuple]
        return render_template("customize.html", username=username, payMethDicts=payMethDicts)

    else:
        payMethSQL = ("SELECT payMethod FROM payMethods WHERE userID = " + str(session["user_id"]))
        payMethTuple = execute_read_query(connection, str(payMethSQL))

        keys = ['payMeth']
        payMethDicts = [dict(zip(keys,d)) for d in payMethTuple]
        return render_template("customize.html", username=username, payMethDicts=payMethDicts)


@app.route("/export", methods=["GET", "POST"])
@login_required
def export():
    connection = create_connection("pFinances.db")
    usernameSQL = ("SELECT username FROM users WHERE id = " + str(session["user_id"]))
    usernameTuple = execute_read_query(connection, str(usernameSQL))
    username = "%s" % usernameTuple[0]

    varCostSQL = ("SELECT amount,method,description,date FROM varCosts WHERE userID = " + str(session["user_id"]))
    varCostTuple = execute_read_query(connection, str(varCostSQL))
    keys = ['amount', 'method','description','date']
    varCostDicts = [dict(zip(keys,d)) for d in varCostTuple]

    incomeSQL = ("SELECT amount,source FROM income WHERE userID = " + str(session["user_id"]))
    incomeTuple = execute_read_query(connection, str(incomeSQL))
    keys = ['amount', 'source']
    incomeDicts = [dict(zip(keys,d)) for d in incomeTuple]

    fixCostsSQL = ("SELECT amount,source FROM fixedCosts WHERE userID = " + str(session["user_id"]))
    fixCostsTuple = execute_read_query(connection, str(fixCostsSQL))
    keys = ['amount', 'source']
    fixCostsDicts = [dict(zip(keys,d)) for d in fixCostsTuple]

    dictList = [varCostDicts, incomeDicts, fixCostsDicts]
    nameList = ['varCosts', 'income', 'fixCosts']

    filepaths = []
    for x in range(len(dictList)):
        df = pd.DataFrame(dictList[x])
        filepath = 'users/' + nameList[x] + '-' + username + '.xlsx'
        filepaths.append(filepath)
        df.to_excel(filepaths[x])

    smtp_port = 587
    smtp_server = "smtp.gmail.com"

    emailSQL = ("SELECT email FROM users WHERE id = " + str(session["user_id"]))
    emailTuple = execute_read_query(connection, str(emailSQL))
    keys = ['email']
    emailDicts = [dict(zip(keys,d)) for d in emailTuple]

    sender_email = "financepythonapp97@gmail.com"
    receiver_email = str(emailDicts[0]['email'])

    password = "haxmrvwxyutwqate"
    subject = "Personal Finance Monthly Data"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    attachments = []
    for x in range(len(dictList)):
        filepath = 'users/' + nameList[x] + '-' + username + '.xlsx'
        attachment = open(filepath, 'rb')
        attachments.append(attachment)


    for x in range(len(attachments)):
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload((attachments[x]).read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', "attachment; filename= " + filepaths[x])
        msg.attach(attachment_package)

    text = msg.as_string()

    TIE_server = smtplib.SMTP(smtp_server, smtp_port)
    TIE_server.starttls()
    TIE_server.login(sender_email, password)
    TIE_server.sendmail(sender_email, receiver_email, text)
    TIE_server.quit()

    return redirect('/deleteData')