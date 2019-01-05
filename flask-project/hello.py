from datetime import datetime
from flask import Flask,request,make_response,redirect,abort,render_template,session,url_for,flash
from threading import Thread
from flask.ext.script import Manager,Shell
from flask.ext.moment import Moment
from flask.ext.mail import Mail,Message
from flask.ext.wtf import Form
from flask.ext.migrate import Migrate,MigrateCommand
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.bootstrap import Bootstrap
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='hard to guess string'

app.config['MAIL_SERVER']='smtp.163.com'
app.config['MAIL_PORT']=25
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USERNAME']='15735929342@163.com'
app.config['MAIL_PASSWORD']='lrx123456'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <15735929342@163.com>'
app.config['FLASKY_ADMIN']='15735929342@163.com'

db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app,db)
mail = Mail(app)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt',**kwargs)
    msg.html = render_template(template + '.html',**kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
#    mail.send(msg)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    user = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<role %r' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User> %r' % self.username


class NameForm(Form):
    name = StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/',methods=['GET','POST'])
def index():
#    user_agent = request.headers.get('User-Agent')
#    return '<p>Your browser is %s</p>' % user_agent
#    return '<h1>Hello World!</h1>'
#    return '<h1>Bad Request</h1>',400
#    response = make_response('<h1>This document carries a cookie!</h1>')
#    response.set_cookie('answer','42')
#    return response
#    return redirect('http://www.example.com')
#    return render_template('index.html', current_time=datetime.utcnow())
#    name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known']=False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user',user=user)
        else:
            session['known']=True
        session['name']=form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',
            form = form,name=session.get('name'),
            known = session.get('known',False))
#        old_name = session.get('name')
#        if old_name is not None and old_name != form.name.data:
#            flash('Looks like you have changed your name!')
#        session['name'] = form.name.data
#        return redirect(url_for('index'))
#        name = form.name.data
#        form.name.data = ''
#    return render_template('index.html',current_time=datetime.utcnow(),form=form,name=session.get('name'))


def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.route('/user/<name>')
def user(name):
#    return '<h1>Hello,%s!</h1>' % name
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_errpr(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
#    app.run(debug=True)
    manager.run()
#    bootstrap.run()
