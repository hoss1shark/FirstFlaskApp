import flask
from flask import Flask, request, render_template
from data import Articles
from wtforms import Form, TextAreaField, BooleanField, StringField, PasswordField, validators
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)
Articles = Articles()
#Configuring Mysql
app.config.update(
    TESTING=True,
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#inti MySQL
mysql =MySQL(app)
@app.route('/')
def hello_world():  # put application's code here
    return render_template('/Home.html')


@app.route('/aboutus')
def about():
    return render_template('/aboutus.html')


@app.route('/articles')
def articles():
    return render_template('/articles.html', articles=Articles)


@app.route('/article/<string:id>')
def article(id):
    return render_template('/article.html', id=id)


# setting registerion form
class RegisertionForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=50)])
    email = StringField('Email Address', [validators.length(min=6, max=50)])
    password = PasswordField(' Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisertionForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        #create dbcursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,username,email,password) values (%s,%s,%s,%s)",(name,username,email,password))
        #commit
        mysql.connection.commit()
        flask.flash("You have successfully registered in our wonderful App",'sucess')
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run()
