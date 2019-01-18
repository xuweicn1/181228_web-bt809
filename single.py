import serial
import struct as sru
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Vent():

    def __init__(self, step=53,pin0=18, pin1=23):
    
        """
        pin0 = 18 正转到风口最大处
        pin1 = 23 反转风口到指定位置
        step = 5  定义从最小开到最大的时间
        """
    
        GPIO.setup(pin0,GPIO.OUT,initial=0)
        GPIO.setup(pin1,GPIO.OUT,initial=0)
    

        self.pin0 = pin0
        self.pin1 = pin1
        self.step = step

    def ratio(self, t,s):
        """
        t:开口时间
        s:开口比例
        """
        s = 100 - s
        if s >= 0:
            GPIO.output(self.pin0,1)
            print('阀门扩大中...')
            time.sleep(self.step)
            GPIO.output(self.pin0,0)
            print('阀门已到最大处...')
            GPIO.output(self.pin1,1)
            print('阀门缩小中...')
            time.sleep(self.step*s*0.01)
            print('阀门已到停在:{:.0%}'.format(1-s*0.01))
            GPIO.output(self.pin1,0)
            time.sleep(t)
            print('阀门在{:.0%}停{}秒'.format(1-s*0.01,t))
            
        else:
            GPIO.output(self.pin0,1)
            time.sleep(step)
            GPIO.output(self.pin0,0)
            print('阀门已到最大处...')

            
def get_809_data(n, c):
    """
    n：子机编号
    c：寄存器读写编号
    返回值：返回809测量值、给定值、参数值
    """
    con = str(80+n) + str(80+n) + '52' + c
    # with serial.Serial('/com3', 4800, timeout=1) as ser:
    with serial.Serial('/dev/ttyUSB0', 4800, timeout=1) as ser:
        ser.write(bytes.fromhex(con))
        fd = ser.readline()
        if len(fd) == 8:
            r = sru.unpack('hhbbh', fd)
            return r


if __name__ == '__main__':
    
    try:
        r= get_809_data(1,'00')
        print('测量温度：{}℃\n设定温度：{}℃\n所读参数：{}'.format(r[0]/10, r[1]/10, r[4]))
    except TypeError: 
        print("线路不通，请接线好再试")
    except serial.serialutil.SerialException:
        print("端口被占用")
    finally :
        print("*"*50)
    vt = Vent(53)
    vt.ratio(2,20)