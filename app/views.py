import time
import glob
import serial
from threading import Lock
from flask import render_template, session, request, flash, redirect, logging, url_for
from flask_socketio import SocketIO, emit
from passlib.hash import sha256_crypt
from app import app
from app.models import Database, BT809, GetSet, SetForm, RegisterForm
from functools import wraps
import RPi.GPIO as GPIO


async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

bt = BT809()
db = Database()
gs = GetSet()


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = {
   24 : {'name' : '信道1', 'state' : GPIO.LOW},
   25 : {'name' : '信道2', 'state' : GPIO.LOW},
   18 : {'name' : '信道3', 'state' : GPIO.LOW},
   23 : {'name' : '信道4', 'state' : GPIO.LOW}
   }

def pin_initial():
    '''设置每个引脚为输出,置低电平'''
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        """检查登陆"""
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('请登陆浏览', 'danger')
            return redirect(url_for('login'))
    return wrap

def background_thread():
    """后台线程产生数据，即刻推送至前端"""
    count = 0
    while True:
        try:
            socketio.sleep(3)
            r = list(bt.get_809_data(1, '1B'))
            r[0], r[1] = r[0]/10, r[1]/10
            t = time.strftime('%H:%M:%S', time.localtime())
            socketio.emit('server_response', {
                'data': [t] + r, 'count': count}, namespace='/test')
            # socketio.sleep(3)
            if bt.get_809_data(1, 'E4')[4] != 0:
                gs.temp_save()
        except TypeError:
            print("线路不通，请接线好再试")
        except serial.serialutil.SerialException:
            pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/home")
def home():
    """主页"""
    time, number, preset, channel_1, channel_2, channel_3, channel_4 = db.get_temp_newdata()
    templateData = {
        'time': time,
        'number': number,
        'preset': preset,
        'channel_1': channel_1,
        'channel_2': channel_2,
        'channel_3': channel_3,
        'channel_4': channel_4
    }
    return render_template('home.html', **templateData)


@socketio.on('connect', namespace='/test')
def test_connect():
    """与前端建立 socket 连接后，启动后台线程"""
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


@app.route("/table", methods=['POST', 'GET'])
@is_logged_in
def table():
    """获取数据库提交"""
    data = db.get_temp_all()
    return render_template("table.html", data=data)


@app.route('/parameter')
@is_logged_in
def parameter():
    """bt809参数设定"""
    data = db.select_all()
    return render_template('parameter.html', data=data)


@app.route('/status')
@is_logged_in
def status():
    """bt809初始化"""
    gs.get_values()
    flash('初始化完成', 'success')
    return render_template('parameter.html')


@app.route('/edit/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit(id):
    """设置参数值"""
    data = db.select_id(id)
    form = SetForm(request.form)
    form.n.data = data[1]
    form.d.data = data[2]
    form.v.data = data[3]
    if request.method == 'POST' and form.validate():
        v = request.form['v']
        db.update(v, id)
        gs.set_value(id)
        flash('设置完成', 'success')
        return redirect(url_for('parameter'))
    return render_template('edit.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        db.log_user_info(name, email, username, password)
        flash('注册成功', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登陆"""
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        data = db.get_user_info(username)
        if data is not None:
            password = data[4]
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('登陆成功', 'success')
                return redirect(url_for('parameter'))

            else:
                error = '密码不对'
                return render_template('login.html', error=error)
        else:
            error = '没有此用户'
            return render_template('login.html', error=error)
    return render_template('login.html')





@app.route('/logout')
def logout():
    session.clear()
    """退出"""
    flash('你已经退出', 'success')
    return redirect(url_for('login'))


pin_initial()


@app.route("/vents")
@is_logged_in
def vents():
   '''读引脚状态发送到前端'''
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
   templateData = {
      'pins' : pins
      }
   return render_template('vents.html', **templateData)


@app.route("/<int:changePin>/<action>", methods=['GET', 'POST'])
def vent(changePin, action):
    '''执行前端发来请求'''
    if action == "on":
        '''通电'''
        GPIO.output(changePin, GPIO.HIGH)

    if action == "off":
        '''断电'''
        GPIO.output(changePin, GPIO.LOW)

    for pin in pins:
        '''读引脚状态发送到网页'''
        pins[pin]['state'] = GPIO.input(pin)

    templateData = {
    'pins' : pins
    }

    return render_template('vents.html', **templateData)


if __name__ == '__main__':
    # socketio.run(app, debug=True)
    app.run(host='0.0.0.0', debug=True)
