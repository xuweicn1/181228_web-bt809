#BT809温度监控系统

## 前言

[![build status](https://secure.travis-ci.org/maxcountryman/flask-login.png?branch=master)](https://travis-ci.org/#!/maxcountryman/flask-login)

用Flask框架，`SQlite` ,` Bootstrap` ,`Pyserial`搭建一个温度监控系统，实现远端WEB硬化炉智能操控。

结构示意图：
![](https://img2018.cnblogs.com/blog/720033/201812/720033-20181210182519634-1172375356.png)


### 数据逻辑 ：

- 温度传感器pt100获取温度模拟信号AS
- 信号AS通过温控仪表BT809转换为数字信号DS
- 要求：对数字信号DS加工,实现Web操控

### 控制流程：

上位机每向通道发一条指令，仪表送回一次数据

- 上位机：Raspberry Pi(树莓派)
- 下位机：BT809
- 通信协议：BTBUS_BT800、RS485

### 技术栈

- 数据库：SQLite
- 路由框架：Flask
- CSS框架：Bootstrap
- 前后同步：SocketIO
- 通信接口：Pyserial
- 通信解包：Struct
- 表单：datatables
- 继电器控制：RPi.GPIO

## 运行


### 1. 根目录树莓派命令：

```
$ python3 run.py
```

### 2. 局域网的电脑或者访问：

地址：<http://192.168.0.104:5000/>

`192.168.0.104`换成自己树莓派IP

#### 首页：

![](https://img2018.cnblogs.com/blog/720033/201812/720033-20181228131916985-1947001512.png)


#### 数据库：
![](https://img2018.cnblogs.com/blog/720033/201812/720033-20181228132157967-1850145665.png)

#### 进风口：
![](https://img2018.cnblogs.com/blog/720033/201812/720033-20181228132307518-14955759.png)


## 版本

### 目前能做：

1. 实时展示硬化炉运行状态
2. 存储运行数据
3. 手动控制风口开启关闭


### 下一阶段：

1. 实时曲线添加设定曲线
2. 进风口添加自动控制


