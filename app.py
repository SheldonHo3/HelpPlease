import smtplib

from flask import Flask, render_template, flash, request, url_for, redirect, session
from util.database import *
from util.pyrest import *
from forms.sign_in import SignInForm
from models.user import *


app = Flask(__name__)
app.config.from_object('config')
db= Database().db
#app.config mongo
###########3
#mongo=pymongo(app)

print(db.collection_names())

@app.route('/', methods=['GET', 'POST'])
def index():
    all_requests = db.Tasks.find({})
    return render_template('index.html', username = session['username'] if 'username' in session else None, requests=all_requests)

@app.route('/sign_in/', methods=['GET', 'POST'])
def sign_in():
    sign_in_form = SignInForm(request.form)
    print(request.method)
    if request.method == "POST" and sign_in_form.validate_on_submit():
        print('fdsafa')
        if not db.users.find_one({'username': sign_in_form.username.data}):
            user = User(sign_in_form.email.data, sign_in_form.username.data, sign_in_form.password.data)
            db.users.insert_one(user.json())
            session['username']= user.username
            session['email']= user.email
            return redirect(url_for('index'))
        else:
            flash('username already exists')
            return render_template('sign_in.html', form=sign_in_form)
    return render_template('sign_in.html', form=sign_in_form)
#3#
@app.route('/email/<string:username>')
def emailreceive(username):
        receiver = db.Tasks.find_one({'taskauthor': username})
        receiver['accepted'] = True
        db.Tasks.update_one({'taskauthor':username}, {'$set': receiver}, upsert = False)
        ## receiver = 'keshvanidillon@gmail.com'3
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print(receiver['email'])

        server.starttls()

        server.login('temppythontest@gmail.com', 'pythonisdope')
        print(session['email'])
        server.sendmail('temppythontest@gmail.com', receiver['email'], 'Someone is willing to help you! Please contact them at: {0}'.format(session['email']))
        {}
        return render_template('getemailform.html')

@app.route('/payment/', methods = ['GET','POST'])
def payment():
    if request.method == "POST":
        amounts = request.form['amount']
        # The client id and secret
        client_id = 'f2a2ab8e-9a66-4a05-89e4-c29f196f9e33'
        client_secret = 'b11198e6-9939-4d12-90c9-e024c8ae9367'

        # get an access token#
        access_token = retrieve_access_token(client_id, client_secret)
        print('\nACCESS TOKEN: ' + access_token)

        # create a fake billing address
        billing_address = {
            'address1': '123 hello',
            'address2': '123 hello',
            'city': 'Montreal',
            'state': 'QC',
            'zipCode': '12345'
        }

        # initialize a credit card object and get a credit card token from api end point
        example_cc = CreditCard('4134185779995000', '123', 3, 2018, 'Test', billing_address, 'example@example.com')
        credit_card_token = retieve_credit_card_token(example_cc, access_token)
        print('\nCREDIT CARD TOKEN: ' + credit_card_token)

        # make a payment with the access token, credit card token and an amount
        # get the amount from html form then pay#

        make_payment(access_token, credit_card_token, amounts)

    return render_template('paymentform.html')

@app.route('/login/', methods = ['GET','POST'])
def login_page():
    error = ''
    try:
        if request.method== "POST":
            attempted_username = request.form['username']
            attempted_password= request.form['psw']
            attempted_email = request.form['email']

            flash(attempted_username)
            flash(attempted_password)

            if  db.users.find_one({u'username':"{}".format(attempted_username),u'password':attempted_password}):
                flash("found")
                session['username'] = attempted_username
                session['email'] = attempted_email
                return redirect(url_for('index'))
            else:
                error = "Not Valid Credentials. Try again."

        return render_template("login.html", error = error)

    except Exception as e:
        flash(e)
        return render_template("login.html", error= error)

    return render_template('login.html')

@app.route('/newrequest/', methods = ['GET','POST'])
def newrequest():
    if request.method == "POST":
        requestname = request.form['requestname']

        description = request.form['description']
        task = Task(requestname, session['username'], description, session['email']).json()
        print(task.items())
        db.Tasks.insert_one(task)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))





if __name__ == '__main__':
   app.run(debug=app.config['DEBUG'])
