from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import mysql.connector
import matplotlib.pyplot as plt
import mpld3
import numpy as np
#import os
import re

import random
def getColor():
	color = "%06x" % random.randint(0, 0xFFFFFF)
	return "#"+color

from sqlalchemy import null
app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'harshith.4123'
app.config['MYSQL_DB'] = 'geeklogin'

mysql = MySQL(app)




@app.route('/home',methods=['GET','POST'])
def home():
	current_user = str(session['id'])
	cursor = mysql.connection.cursor()
	cursor.execute('SELECT expenses_name,expenses_amount,expenses_budget FROM expenses_list WHERE user_id=%s',[current_user])
	rows=cursor.fetchall()
	dataitems = []
	fld={}
	for i in rows:
		fld['lab'] = i[0]
		fld['val'] = i[1]
		fld['bud'] = i[2]
		fld['color'] = getColor()
		dataitems.append(fld.copy()) 

	return render_template("Home.html",dataitems=dataitems)

@app.route('/result')
def list():
	cur = mysql.connection.cursor()
	current_user = str(session['id'])
	cur.execute('SELECT expenses_name,expenses_amount,expenses_budget FROM expenses_list WHERE user_id=%s',[current_user])
	row = (cur.fetchall())
	cursor = mysql.connection.cursor()
	cursor.execute('SELECT SUM(expenses_budget) FROM expenses_list WHERE user_id=%s',[current_user])
	total_budget = (cursor.fetchall()[0][0])
	value = str(total_budget)
	cursor1 = mysql.connection.cursor()
	cursor1.execute('SELECT SUM(expenses_amount) FROM expenses_list WHERE user_id=%s',[current_user])
	total_expenses = (cursor1.fetchall()[0][0])
	value1 = str(total_expenses)
	data1 = int(value)
	data2 = int(value1)
	data = data1-data2
	saving = str(data)
	return render_template("result.html",value=value,row=row,value1=value1,saving=saving)


   
@app.route('/about',methods =['GET','POST'])
def about():
	if request.method == 'POST' and 'name' in request.form and 'expenses_amount' in request.form and 'expenses_budget' in request.form:
		current_user = session['id']
		expenses_name = request.form['name']
		expenses_amount = request.form['expenses_amount']
		expenses_budget = request.form['expenses_budget']
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO expenses_list(expenses_name,user_id,expenses_amount,expenses_budget) VALUES (%s,%s,%s,%s)',(expenses_name,current_user,expenses_amount,expenses_budget))
		
		mysql.connection.commit()
	return render_template('AddExpenses.HTML')



@app.route('/') 
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor()
		cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			for row in cursor:
				session['loggedin'] = True
				session['id'] = row[0]
				session['username'] = row[1]
			msg = 'Logged in successfully !'
			return render_template('home.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)




@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

	
@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor()
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	if msg == 'You have successfully registered !':
		return render_template('Home.HTML')
	else:
		return render_template('register.html')
	

if __name__=='__main__':
    app.run(debug=True)