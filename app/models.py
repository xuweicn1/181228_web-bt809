import sqlite3 as lite
import serial
import struct as sru
import csv
import time
import psutil
import RPi.GPIO as GPIO


from wtforms import Form, validators, StringField, SubmitField, PasswordField, IntegerField


con = lite.connect('BT809Data.db', check_same_thread=False)
cur = con.cursor()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

sampleFreq = 5


class Database():

    def create_users(self):
        """创建用户表"""
        with con:
            sql = """create table users(
                            ID  INTEGER PRIMARY KEY AUTOINCREMENT,
                            name text,
                            email text,
                            username text,
                            password text)"""
            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute(sql)

    def log_user_info(self, name, email, username, password):
        """插入用户信息"""
        with con:
            sql = "INSERT INTO users(name, email, username, password) VALUES(?, ?, ?, ?)"
            cur.execute(sql, (name, email, username, password))  # 插入数据

    def get_user_info(self, username):
        """获取用户信息"""
        with con:
            sql = "SELECT * FROM users WHERE username = (?)"
            cur.execute(sql, [username])  # 插入数据
            data = cur.fetchone()
            return data

    def create_temp(self):
        """创建温度存贮表"""
        with con:
            cur = con.cursor()
            sql = """CREATE TABLE temp(
                        timestamp DATETIME,
                        number NUMERIC,
                        preset NUMERIC,
                        channel_1 NUMERIC,
                        channel_2 NUMERIC,
                        channel_3 NUMERIC,
                        channel_4 NUMERIC)"""
            cur.execute("DROP TABLE IF EXISTS temp")
            cur.execute(sql)

    def log_temp(self, n, p, t1, t2, t3, t4):
        """
        n:子机编号
        p：预设值
        t1:子机1温度值
        t2:子机1温度值
        t3:子机3温度值
        t4:子机4温度值
        数据入库格式：时间、运行号段、设定值、通道1-4
        """
        with con:
            sql = "INSERT INTO temp VALUES(datetime('now','localtime'),(?),(?),(?),(?),(?),(?))"
            cur.execute(sql, (n, p, t1, t2, t3, t4))

    def get_temp_new(self):
        """读取数据库最新数据"""
        with con:
            sql = "SELECT * FROM temp ORDER BY timestamp DESC LIMIT 1"
            cur.execute(sql)
            return cur.fetchone()

    def get_temp_all(self):
        """获取温度表单"""
        with con:
            sql = """select * from temp """
            cur.execute(sql)
            return cur.fetchall()

    def create_register(self):
        """创建寄存器表"""
        with con:
            sql = """create table register (
                            ID  INTEGER PRIMARY KEY AUTOINCREMENT,
                            Num text,
                            Meaning text,
                            Size text)"""
            cur.execute("DROP TABLE IF EXISTS register")
            cur.execute(sql)

    def csv_save(self):
        """打开csv文件，存入sqlite"""
        with con:
            sql = """ INSERT INTO register (Num,Meaning) VALUES (?,?) """
            csv_data = csv.reader(open('register.csv'))
            for line in csv_data:
                cur.execute(sql, (line[0], line[1]))

    def select_all(self):
        """SELECT 操作"""
        with con:
            sql = """select * from register """
            cur.execute(sql)
            data = cur.fetchall()
            return data

    def select_id(self, id):
        """查询第几行"""
        with con:
            sql = """select * from register where id = (?) """
            cur.execute(sql, [id])
            data = cur.fetchone()
            return data

    def update(self, value, id):
        """更新register表的值"""
        with con:
            sql = """update register set Value = (?) where ID=(?)"""
            cur.execute(sql, (value, id))

    def row_len(self):
        """返回表单的行数"""
        with con:
            sql = """  select count(*) from register"""
            cur.execute(sql)
            return cur.fetchone()

    def create_vent(self):
        """创建风口表"""
        with con:
            sql = """create table vent (
                            ID  INTEGER PRIMARY KEY AUTOINCREMENT,
                            Temp NUMERIC,
                            Time NUMERIC,
                            Size NUMERIC)"""
            cur.execute("DROP TABLE IF EXISTS vent")
            cur.execute(sql)

    def vent_csv_save(self):
        """打开csv文件，存入sqlite"""
        with con:
            sql = """ INSERT INTO vent (Temp,Time,Size) VALUES (?,?,?) """
            csv_data = csv.reader(open('vent.csv'))
            for line in csv_data:
                cur.execute(sql, (line[0], line[1], line[2]))

    def vent_update(self, Temp, id):
        """更新vent表的值"""
        with con:
            sql = """update vent set Priority = (?) where ID=(?)"""
            cur.execute(sql, (Temp, id))

    def row_len(self):
        """返回vent表单的行数"""
        with con:
            sql = """  select count(*) from vent"""
            cur.execute(sql)
            return cur.fetchone()

    def vent_select_all(self):
        """SELECT 操作"""
        with con:
            sql = """select * from vent """
            cur.execute(sql)
            data = cur.fetchall()
            return data

    def vent_select_id(self, id):
        """查询第几行"""
        with con:
            sql = """select * from vent where id = (?) """
            cur.execute(sql, [id])
            data = cur.fetchone()
            return data

    def vent_update_values(self, Temp, Time, Size, id):
        """更新vent表的值"""
        with con:
            sql = """update vent set Temp = (?), Time = (?), Size = (?) where ID=(?)"""
            cur.execute(sql, (Temp, Time, Size, id))


class BT809():

    def set_809_data(self, n, c, v):
        """
        n：子机编号
        c：寄存器读写编号
        v：设置参数值
        返回值：返回809测量值、给定值、写入的参数值
        """
        pak = sru.pack('h', v).hex()
        con = str(80+n) + str(80+n) + '43' + c + str(pak)
        # with serial.Serial('/com3', 4800, timeout=1) as ser:
        with serial.Serial('/dev/ttyUSB0', 4800, timeout=1) as ser:
            ser.write(bytes.fromhex(con))

    def get_809_data(self, n, c):
        """
        n：子机编号
        c：寄存器读写编号
        返回值：返回809测量值、给定值、参数值
        """
        con = str(80+n) + str(80+n) + '52' + c
        # with serial.Serial('/com3', 4800, timeout=1) as ser:
        with serial.Serial('/dev/ttyUSB0', 4800, timeout=1) as ser:
            ser.write(bytes.fromhex(con))
            time.sleep(0.3)
            fd = ser.readline()
            if len(fd) == 8:
                r = sru.unpack('hhbbh', fd)
                return r


class SetForm(Form):
    """表单取值"""
    n = StringField('读写编号')
    d = StringField('参数说明')
    v = StringField('设定值')


class SetVent(Form):

    temp = IntegerField('温度')
    time = IntegerField('时间')
    size = IntegerField('开口')


class RegisterForm(Form):
    """用户注册类"""
    name = StringField('姓名', [validators.Length(min=1, max=50)])
    username = StringField('用户名', [validators.Length(min=4, max=25)])
    email = StringField('邮箱', [validators.Length(min=6, max=50)])
    password = PasswordField('密码', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="密码不对")
    ])
    confirm = PasswordField('重复密码')


class Baffle():

    def __init__(self, step=53, pin0=18, pin1=23):
        """
        pin0 = 18 正转到风口最大处
        pin1 = 23 反转风口到指定位置
        step = 53  定义从最小开到最大的时间
        """

        GPIO.setup(pin0, GPIO.OUT, initial=0)
        GPIO.setup(pin1, GPIO.OUT, initial=0)

        self.pin0 = pin0
        self.pin1 = pin1
        self.step = step

    def ratio(self, t, s):
        """
        t:开口时间
        s:开口比例
        """
        s = 100 - s
        if s >= 0:
            GPIO.output(self.pin0, 1)
            print('阀门扩大中...')
            time.sleep(self.step)
            GPIO.output(self.pin0, 0)
            print('阀门已到最大处...')
            GPIO.output(self.pin1, 1)
            print('阀门缩小中...')
            time.sleep(self.step*s*0.01)
            print('阀门已到停在:{:.0%}'.format(1-s*0.01))
            GPIO.output(self.pin1, 0)
            print('阀门将在{:.0%}停{}分钟'.format(1-s*0.01, int(t/60)))
            time.sleep(t)
            

        else:
            GPIO.output(self.pin0, 1)
            time.sleep(step)
            GPIO.output(self.pin0, 0)
            print('阀门已到最大处...')


bt = BT809()
db = Database()


class GetSet():

    """视图中的方法"""

    def temp_save(self):
        """4通道温度存入数据库"""

        try:
            n = bt.get_809_data(1, 'E3')[4]
            p = bt.get_809_data(1, '00')[1]/10
            t1 = bt.get_809_data(1, '00')[0]/10
            t2 = bt.get_809_data(2, '00')[0]/10
            t3 = bt.get_809_data(3, '00')[0]/10
            t4 = bt.get_809_data(4, '00')[0]/10
            db.log_temp(n, p, t1, t2, t3, t4)

        except serial.serialutil.SerialException:
            pass
        except TypeError:
            print("线路不通，请接线好再试")
        else:
            print("Deposit data...")
            time.sleep(sampleFreq)

    def set_value(self, id):
        """ 存储指定项设定值 """
        try:
            find = db.select_id(id)
            id = int(id)
            if id == 1:
                bt.set_809_data(1, find[1], int(find[3])*10)
            elif id < 201:
                if id % 2 == 0:
                    bt.set_809_data(1, find[1], int(find[3])*10)
                else:
                    bt.set_809_data(1, find[1], int(find[3]))
            else:
                bt.set_809_data(1, find[1], int(find[3]))
        except serial.serialutil.SerialException:
            pass
        except TypeError:
            print("线路不通，请接线好再试")

    def get_values(self):
        """读取仪表所有设定状态"""
        n = db.row_len()[0] + 1
        try:
            for id in range(1, n):
                find = db.select_id(id)
                if id == 1:
                    r = bt.get_809_data(1, find[1])[4]/10
                elif id < n-4:
                    if id % 2 == 0:
                        r = bt.get_809_data(1, find[1])[4]/10
                    else:
                        r = bt.get_809_data(1, find[1])[4]
                else:
                    r = bt.get_809_data(1, find[1])[4]
                db.update(r, id)
                print("正在读取第{}个状态".format(id))
        except serial.serialutil.SerialException:
            pass
        except TypeError:
            print("线路不通，请接线好再试")

    def get_value(self, id):
        """读取选定仪表设定状态"""
        id = int(id)
        try:
            find = db.select_id(id)
            if id == 1:
                r = bt.get_809_data(1, find[1])[4]/10
            elif id < 201:
                if id % 2 == 0:
                    r = bt.get_809_data(1, find[1])[4]/10
                else:
                    r = bt.get_809_data(1, find[1])[4]
            else:
                r = bt.get_809_data(1, find[1])[4]
            db.update(r, id)
        except serial.serialutil.SerialException:
            pass
        except TypeError:
            print("线路不通，请接线好再试")




if __name__ == '__main__':

    bt = BT809()
    db = Database()
    gs = GetSet()

    # baffle = Baffle(7)
    # baffle.ratio(2,20)

