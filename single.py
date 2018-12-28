#!/usr/bin/env python
import time
import serial
import struct
with serial.Serial('/dev/ttyUSB0',4800,timeout=1) as ser:
  # while 1:
    # time.sleep(2)
    s = '818152E3'
    ser.write(bytes.fromhex(s))
    fd = ser.readline()
    if len(fd) == 8:
      r =struct.unpack('hhbbh',fd)
      print('测量温度：{}℃\n设定温度：{}℃\n所读参数：{}'.format(r[0]/10,r[1]/10,r[4]))
      print('输入指令：{}\n输出集：{}'.format(s,r))
