import serial
import struct as sru


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