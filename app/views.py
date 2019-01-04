import time
import glob
from threading import Lock
from flask import render_template, session, request
from flask_socketio import SocketIO, emit
from app import app
from app.models import Database, BT809, GetSet
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

def background_thread():
    """后台线程产生数据，即刻推送至前端"""
    count = 0
    while True:
        socketio.sleep(2)
        r = list(bt.get_data(1, '1B'))
        r[0], r[1] = r[0]/10, r[1]/10
        t = time.strftime('%H:%M:%S', time.localtime())  # 获取系统时间
        socketio.emit('server_response', {
                      'data': [t] + r, 'count': count}, namespace='/test')
        if bt.get_data(1,'E4')[4]!=0:
            gs.temp_save()



@app.route("/")
def index():
    """主页"""
    time, number,preset,channel_1, channel_2, channel_3, channel_4 = db.get_temp_newdata()
    templateData = {
        'time': time,
        'number':number,
        'preset':preset,
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
def table():
    """获取数据库提交"""
    data = db.get_temp_all()
    return render_template("table.html", data=data)

    
@app.route('/articles')
def articles():
    """bt809状态"""
    data = db.select_all()
    return render_template('articles.html', data =data)

@app.route('/status')
def status():
    """bt809状态"""
    gs.save_temp_value(1)
    gs.save_temp_values()
    gs.save_time_values()
    gs.save_time_value(202)
    gs.save_time_value(204)
    msg = '更新完成'
    return render_template('articles.html', msg=msg)

pin_initial()


@app.route("/vents")
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
