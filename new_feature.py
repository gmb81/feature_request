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
    '''loads the currnet user'''
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
    '''allows users to register for the site '''
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            username= form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('clients'))
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




#edit feature request
@app.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    '''allows user to edit the feature requests'''
    #need to get the title from the request for the query.
    title = request.args.get('title')
    #need to get the priority for the request for the query
    priority = request.args.get('priority')
    #This will provide a model for the editor of the feature request, which will be the current user.
    editor = g.user._get_current_object()
    #Need to select the record that correspondns with the priority and title. Since the priority is unique, we can just search these two values
    record =models.Feature.select().where((models.Feature.client_priority==priority) & (models.Feature.title==title)).get()

    #create a form variable
    form = forms.EditForm(obj=record)
    #set the values of the two following fields
    form.priority.data = int(record.client_priority)
    form.working_ticket.data=editor.username
    #ensure that the form is valid for processng
    if form.validate_on_submit():
        try:
            record.title = form.title.data
            record.description = form.description.data
            record.client = form.client.data
            record.client_priority = form.priority.data
            record.target_date = form.target_date.data
            record.product_area = form.product_area.data,
            #this query will allow you to save the model of the user in order to determine if the user is a authorized to see the site.
            user_edit = models.User.select().where(models.User.username== form.working_ticket.data)

            record.working_ticket = user_edit,
            record.percent_complete = form.percent_complete.data
            record.save()
            flash('Record updated', 'success')
        except IntegrityError:
            flash("you have an error", 'error')
        return redirect(url_for('client_list', client = record.client))
    return render_template('edit.html', form=form)






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
                product_area = form.product_area.data,
                percent_complete = form.percent_complete.data

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
                product_area = form.product_area.data,
                percent_complete = form.percent_complete.data
                )





        return render_template('add.html', form=form)
    return render_template('add.html', form=form)

#edit or delete a feature request



if __name__ == '__main__':
    models.initialize()
    app.run(debug = DEBUG, host = HOST, port = PORT)
