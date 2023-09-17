import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication,QSplashScreen,QWidget

from my_ui import MY_ui

if __name__ == '__main__':
    app = QApplication(sys.argv)  
    
    picture = QPixmap('D:/Vs Code/python/socket_test/img/heart_rate.png')
    splash =  QSplashScreen(picture)
    splash.show()

    mywidget = QWidget()
    ui = MY_ui()
    ui.setupUi(mywidget)
    ui.default_init()
    ui.chart_init()
    mywidget.show()
 
    splash.finish(mywidget)
    
    sys.exit(app.exec_())


