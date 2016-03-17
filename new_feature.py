from flask import (Flask, render_template, request, url_for,
                  redirect, flash, g)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_moment import Moment
from peewee import IntegrityError
from models import DATABASE


import models, forms




DEBUG= True
PORT = 8000
HOST ='0.0.0.0'


app = Flask(__name__)
app.secret_key = 'a;ldkjanvpdoaienav;lkdanv;alsdfj you will never guess this a;dklvan;mewoifjavndpau-3248uqr9q83ur'

#activate bootstrap and moment for the app
Bootstrap(app)
Moment(app)


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

#initiate LoginManager for the app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None



@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

#index
@app.route('/')
def index():
    return render_template('index.html')




#register
@app.route('/register', methods =('GET','POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            username= form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('customers'))
    return render_template('registration.html', form=form)



#login user
@app.route('/login', methods = ('GET','POST'))
def login():
    """login to the app"""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash('Your username or password does not match!', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You are logged in', 'success')
                return redirect(url_for('clients'))
            else:
                flash("Your username or password doesn't match!", 'error')
    return render_template('login.html', form=form)

#Need to have the user sign out
@app.route('/logout')
@login_required
def logout():
    """logout of the app"""
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))






#new features view by customer


#show the customers
@app.route('/customers')
@login_required
def clients():
    clients = models.Feature.select(models.Feature.client).distinct(models.Feature.client)

    return render_template('client.html', clients=clients)

#show the features by customer
@app.route('/client_list')
@login_required
def client_list():
    client_name= request.args.get('client')
    print(client_name, type(client_name))
    list = models.Feature.select().where(models.Feature.client==client_name)

    return render_template('client_list.html', list=list, client_name=client_name)


#add a new feature request
@app.route('/add', methods =('GET', 'POST'))
@login_required
def add():

    form = forms.FeatureForm()
    if form.validate_on_submit():

        try:
            print(form.target_date.data)

            models.Feature.create(
                user = g.user._get_current_object(),
                title =form.title.data,
                description = form.description.data,
                client = form.client.data,
                client_priority= form.priority.data,
                target_date = form.target_date.data,
                ticket_url = form.ticket_url.data,
                product_area = form.product_area.data

            )

        except IntegrityError:
            print('You are seeing an IntegrityError')
            #see if the prioirty is the problem
            num = int(form.priority.data)
            cust_name = form.client.data
            #get problem record
            records = models.Feature.select().where(models.Feature.client== cust_name)
             #need to update the records for priorities greater than number
            for record in records:
                print(record.client_priority, type(record.client_priority))
                if record.client_priority >= num:
                    with DATABASE.transaction():
                        record.client_priority += 1
                        record.save()
                        print('record saved')

                    print('The new priority is ', record.client_priority)
            with DATABASE.transaction():
                models.Feature.create(
                user = g.user._get_current_object(),
                title =form.title.data,
                description = form.description.data,
                client = form.client.data,
                client_priority= str(num),
                target_date = form.target_date.data,
                ticket_url = form.ticket_url.data,
                product_area = form.product_area.data
                )





        return render_template('add.html', form=form)
    return render_template('add.html', form=form)

#edit or delete a feature request



if __name__ == '__main__':
    models.initialize()
    app.run(debug = DEBUG, host = HOST, port = PORT)
