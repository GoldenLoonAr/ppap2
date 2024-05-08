from flask import render_template, request, Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#SQLAlchemy - ORM инструмет для Flask
#ORM - механизм, который позволяет представить данные без данных в виде объекта
#ORM позволяет создавать БД без прямого использоания SQL
app = Flask(__name__, static_folder = 'static', template_folder = 'templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' #конфигурация БД
database = SQLAlchemy(app) #склеивание БД и приложения

locked_flag = True # переменная проверяет, вошёл ли пользователь в систему или нет

# создание таблиц в БД
class Users(database.Model):
    id = database.Column(database.Integer, primary_key = True) #порядковый номер пользователя
    email = database.Column(database.String(100), unique = True) #имеил пользвателя
    password = database.Column(database.String(100), nullable = True) #пароль пользователя
    date = database.Column(database.DateTime, default = datetime.utcnow)

    hook = database.relationship('Profiles', backref = 'Users', uselist = False)

    def __repr__(self): #объект показывается по-другому
        return f'<User {self.id}>'
    

class Profiles(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(100), nullable = True)
    old = database.Column(database.Integer)
    city = database.Column(database.String(100))

    user_id = database.Column(database.Integer, database.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Profile {self.id}>'
 
@app.route('/') #функция обслуживает определённую функцию (/)
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST']) #функция обслуживает определённую функцию (/register)
def register():
    if request.method == 'POST': #возвратное значение со страницы
        try:
            user = Users(email = request.form['email'],password = request.form['password'])
            database.session.add(user)
            database.session.flush()

            profile = Profiles(name = request.form['name'], old = request.form['old'], city = request.form['city'], user_id = user.id)
            database.session.add(profile)
            database.session.commit() #подтвердить изменение в нашей БД
        except:
            database.session.rollback() #если есть какие-то ошибки и не получается регать, то откатывается БД до момента регитрации
            print('Ошибка записи в базу данных')
            
    return render_template('register.html')

@app.route('/locked')
def locked():
    global locked_flag
    if locked_flag == False:
        return render_template('locked.html')
    else: 
        return redirect('/register')

@app.route('/login', methods = ['GET', 'POST']) 
def login():
    if request.method == 'POST':
        # система смотрит в базу данных и находит первое совпадение по email и паролю
        user = Users.query.filter_by(email=request.form['email'], psw=request.form['psw']).first()
        if user:
            global locked_flag
            locked_flag = False
            return redirect('/locked')

    return render_template('login.html')
    
with app.app_context():
    database.create_all() #добавление таблицы в БД

if __name__ == '__main__':
    app.add_url_rule('/', 'index', index) #обслуживание адреса функцией index
    app.add_url_rule('/register', 'register', register)
    app.add_url_rule('/login,','login', login)
    app.add_url_rule('/locked', 'locked', locked)
    app.run(debug = True)
