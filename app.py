import flask
from flask import Flask, request, render_template, flash, session, redirect, url_for
# from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
# Articles = Articles()
# Configuring Mysql
app.config.update(
    TESTING=True,
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# inti MySQL
mysql = MySQL(app)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('/Home.html')


@app.route('/aboutus')
def about():
    return render_template('/aboutus.html')


@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    result = cur.execute("select * from articles")

    if result > 0:
        articles = cur.fetchall()
        cur.close()
        return render_template('/articles.html', articles=articles)
    return render_template('/articles.html')


@app.route('/article/<string:id>')
def article(id):
    cur = mysql.connection.cursor()

    result = cur.execute("select * from articles where id=%s",(id))
    if result > 0:
        article = cur.fetchone()
        cur.close()
        return render_template('/article.html', article=article)
    return render_template('/article.html', id=id)



# setting addarticle form
class ArticleForm(Form):
    title = StringField('Title', [validators.length(min=1, max=50)])
    body = TextAreaField('Body', [validators.length(min=4)])


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
        # create dbcursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,username,email,password) values (%s,%s,%s,%s)",
                    (name, username, email, password))
        # commit
        mysql.connection.commit()
        flask.flash("You have successfully registered in our wonderful App", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_C = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            if sha256_crypt.verify(password_C, data['password']):
                # redirect
                session['logged_in'] = True
                session['username'] = username
                flash("You are now logged in", 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'NOT MATCHED'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'User dosen\'t exist'
            return render_template('login.html', error=error)
    return render_template('login.html')


# checks if logged_in
def isLoggedin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unautherized, please login", 'danger')
            return redirect(url_for('login'))

    return wrap


# dashboard
@app.route('/dashboard')
@isLoggedin
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("select * from articles")

    if result > 0:
        articles = cur.fetchall()
        cur.close()
        return render_template('/dashboard.html', articles=articles)
    return render_template('/dashboard.html')


# logout
@app.route('/logout')
@isLoggedin
def logout():
    session.clear()
    flash("You have logged out sucessfully", 'success')
    return redirect(url_for('login'))

#add article
@app.route('/addarticle', methods=['GET', 'POST'])
@isLoggedin
def addArticle():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        title = form.title.data
        body = form.body.data
        auther = session['username']
        cur.execute("INSERT into articles(title,body,auther) value(%s,%s,%s)", (title, body, auther))
        mysql.connection.commit()
        cur.close()
        flash("Article add successfully", 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)
#Edit article
@app.route('/editarticle/<string:id>', methods=['GET', 'POST'])
@isLoggedin
def editArticle(id):
    cur = mysql.connection.cursor()
    result = cur.execute("select * from articles where id=%s ",[id])
    if result > 0 :
        article = cur.fetchone()
        cur.close()
    form = ArticleForm(request.form)
    form.title.data = article['title']
    form.body.data = article['body']
    if request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cur.execute("update articles set title=%s,body=%s where id=%s",(title,body,id))
        mysql.connection.commit()
        cur.close()
        flash("Article edited successfully", 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

#delete article
@app.route('/deletearticle/<string:id>')
@isLoggedin
def deleteArticle(id):
    cur= mysql.connection.cursor()
    result = cur.execute("delete from articles where id =%s",id)
    if result == 1:
        mysql.connection.commit()
        cur.close()
        flash("Article deleted successfully", 'success')
        return redirect(url_for('dashboard'))
    print("error happend")
    return redirect(url_for('dashboard'))   

if __name__ == '__main__':
    app.run()
