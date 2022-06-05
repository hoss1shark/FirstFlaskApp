import flask
from flask import Flask, request, render_template
from data import Articles
from wtforms import Form, TextAreaField, BooleanField, StringField, PasswordField, validators
from flask_mysqldb import MySQL
app = Flask(__name__)
Articles = Articles()
#Configuring Mysql

app.config['MYSQL_HOST'] = 'localhost'

@app.route('/')
def hello_world():  # put application's code here
    return render_template('/Home.html')


@app.route('/aboutus')
def about():
    return render_template('/aboutus.html')


@app.route('/articles')
def articles():
    return render_template('/articles.html', articles=Articles)
#hello

@app.route('/article/<string:id>')
def article(id):
    return render_template('/article.html', id=id)


# setting registerion form
class RegisertionForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('UserName', [validators.length(min=4, max=50)])
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
        return render_template('register.html')
    return render_template('register.html', form=form)
def test():
    pass

if __name__ == '__main__':
    app.run()
