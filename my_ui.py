from Ui_socketUI import Ui_Form
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter,QBrush,QColor,QTextCursor
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QWidget
from PyQt5.QtChart import QChart,QLineSeries
from PyQt5.QtNetwork import QTcpSocket
from scipy import  signal
import heartpy as hp


class MY_ui(Ui_Form):
    def __init__(self):
        super(MY_ui,self).__init__()
    
    def default_init(self):
        self.socket = QTcpSocket()
        self.timer = QTimer()
        self.lineEdit.setText('192.168.1.200')
        self.lineEdit_2.setText('2000')
        self.pushButton.setCheckable(True)
        self.radioButton.setChecked(True)
        self.textEdit_2.setPlaceholderText('数据发送区')
        self.textEdit.setPlaceholderText('数据接收区')
        self.comboBox.setCurrentIndex(3)
        self.doubleSpinBox.setValue(2.5)
        self.doubleSpinBox_2.setValue(0.7)
        self.textEdit_2.setText('s')
        self.lineEdit_3.setText('10')

        self.pushButton.clicked.connect(self.pushButton_slot)
        self.socket.readyRead.connect(self.socket_slot)
        self.pushButton_2.clicked.connect(self.pushButton_2_slot)
        self.pushButton_3.clicked.connect(self.pushButton_3_slot)
        self.pushButton_4.clicked.connect(self.pushButton_4_slot)
        self.pushButton_5.clicked.connect(self.pushButton_5_slot)
        self.checkBox.clicked.connect(self.checkBox_slot)
        self.timer.timeout.connect(self.pushButton_4_slot)
        self.socket.connected.connect(self.socket_slot2)
        self.socket.disconnected.connect(self.socket_slot3)
        self.pushButton_6.clicked.connect(self.pushButton_6_slot)
    def chart_init(self):
        self.x=0.0
        self.qchartview.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        self.chart1 = QChart()  # 创建折线视图
        self.chart1.setBackgroundVisible(visible=False)      # 背景色透明
        self.chart1.setBackgroundBrush(QBrush(QColor("#000FFF")))     # 改变图背景色
        self.series = QLineSeries()
        self.chart1.addSeries(self.series)

        self.chart1.createDefaultAxes()  # 创建默认的轴
        self.chart1.axisX().setRange(0, 500)
        self.chart1.axisY().setTitleText('数值')
        self.chart1.legend().setVisible(False)
        self.chart1.axisY().setRange(1000, 5000)  # 设置y1轴范围
        self.qchartview.setChart(self.chart1)
        self.qchartview.chart().zoom(0.9999)


    def pushButton_slot(self):
        if self.pushButton.isChecked(): 
            self.socket.connectToHost(self.lineEdit.text(),int(self.lineEdit_2.text()))
            
        else:
            self.socket.disconnectFromHost()

    def socket_slot(self):
        # self.serbuff = self.socket.readBufferSize()
        if self.socket.canReadLine():
            self.serbuff = self.socket.readLine()          
            if self.radioButton.isChecked():
                # self.textEdit.insertPlainText(str(self.serbuff, encoding='utf-8')+'\n')
                # self.series.append(self.x, self.serbuff.toFloat()[0])
                self.form = int(str(self.serbuff.split('=')[1].split('#')[0], encoding='utf-8'), base=16)
                self.textEdit.insertPlainText(str(self.form)+'\n')
                self.series.append(self.x, float(self.form))

            else :
                self.textEdit.insertPlainText(str(self.serbuff.toHex().toInt()[0])+'\n')
                self.series.append(self.x,self.serbuff.toHex().toFloat()[0])
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
            self.x+=1
            if self.series.count() > 3000:
                self.series.removePoints(0, self.series.count() - 3000)
    def pushButton_2_slot(self):
        self.textEdit.clear()
        self.x=0.0
        self.series.clear()
    def pushButton_4_slot(self):
        #.encode()字符串转为字节
        self.socket.write(self.textEdit_2.toPlainText().encode())
    def pushButton_3_slot(self):
        textFile = QFileDialog().getOpenFileName(None,'读取数据','','TEXT (*txt)')
        if textFile[0]:
            self.x=0.0
            self.series.clear()
            with open(textFile[0],'r') as openfile:
                my_date = openfile.read()
                self.textEdit.setPlainText(my_date)
                for point in my_date.splitlines():
                    if point.isdigit():        #如果字符串为整数
                        self.series.append(self.x,float(point))   
                        self.x+=1
    def pushButton_5_slot(self):
        ppg_data = []
        sample_rate = 1000/int(self.lineEdit_3.text())
        self.x=0.0
        self.series.clear()

        for line in self.textEdit.toPlainText().splitlines():
            ppg_data.append(int(line))
        self.textEdit.clear()
        # ppg_data = ppg_data[550:850]
        #基线漂移处理
        b, a = signal.butter(8, (2*1)/sample_rate, 'lowpass')   #基线漂移去除， 配置滤波器 8 表示滤波器的阶数 Wn为2*临界频率 / fs
        ppg_outline_data = signal.filtfilt(b, a, ppg_data)  #data为要过滤的信号

        ppg_norm_data = ppg_data - ppg_outline_data #新信号=原信号-基线
        #带通滤波
        
        b, a = signal.butter(int(self.comboBox.currentText()), [(2*self.doubleSpinBox_2.value())/sample_rate,(2*self.doubleSpinBox.value())/sample_rate], 'bandpass')   #最大只能设置为4阶，scipy函数限制
        ppg_filt_data = signal.filtfilt(b, a, ppg_norm_data)#为要过滤的信号
        for point in ppg_filt_data:
            self.series.append(self.x,point)
            self.x+=1
        wd, m = hp.process(hp.scale_data(ppg_filt_data), sample_rate)
        hp.plotter(wd, m)
        for key, value in m.items():
            # print(f'{key:8}====>{value:5f}')
            self.textEdit.insertPlainText(f'{key:8}====>{value:5f}'+'\n')
        self.textEdit.moveCursor(QTextCursor.MoveOperation.EndOfLine)
        self.label_6.setText('心率：'+str(int(m['bpm']))+'次/分钟')
        

        if 'RR_list' in wd.keys():
         # print(wd['RR_list'])
            rr=(wd['RR_list'])

    def checkBox_slot(self):
        if self.checkBox.isChecked():
            self.timer.start(int(self.lineEdit_3.text()))
        else :
            self.timer.stop()
    def socket_slot2(self):
        self.t=self.lineEdit.text()
        self.label_7.setText('连接状态：The NO. 0 TCP socket '+self.t+' is accepted!'+'\n')
    def socket_slot3(self):
        self.label_7.setText('连接状态：TCP socket '+self.t+' is being closed! successfully!'+'\n')
    def pushButton_6_slot(self):
        QMessageBox.information(None,'关于我们','陈国崇\n王兴成\n刘一鹏', QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        