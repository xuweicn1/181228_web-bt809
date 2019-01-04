import serial
import struct as sru


def set_bt809_preset(num, value):
    """
    num：子机编号
    value：温度值
    返回值：设定值的寄存器命令
    """
    pak = sru.pack('h', value*10).hex()
    con = str(80+num) + str(80+num) + '4300' + str(pak)
    return con


def get_bt809_com(n, c):
    """
    num：子机编号
    value：寄存器编号
    返回值：对应编号的寄存器命令
    """
    con = str(80+n) + str(80+n) + '52' + c
    return con


def get_bt809_data(x):
    """
    参数：寄存器命令
    返回值：返回809测量值、给定值、参数值
    """
    with serial.Serial('/dev/ttyUSB0', 4800, timeout=1) as ser:
        ser.write(bytes.fromhex(x))
        fd = ser.readline()
        if len(fd) == 8:
            r = sru.unpack('hhbbh', fd)
        return r


if __name__ == '__main__':

    c_get = get_bt809_com(4, '00')
    r = get_bt809_data(c_get)
    
    # c_set = set_bt809_preset(4,150)
    # r = get_bt809_data(c_set)
    
    print('测量温度：{}℃\n设定温度：{}℃\n所读参数：{}'.format(r[0]/10, r[1]/10, r[4]))
