from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QPainter, QColor


from find_window import listen_for_window_changes, get_all_windows_pos

import sys
import time
import threading

class TransparentWindow(QWidget):
    def __init__(self,app : QApplication):
        self.screen_size = app.primaryScreen().size()
        self.x = 1000
        self.y = 200
        self.width = 50
        self.height = 50
        self.velocity = [0,0]
        self.vitesse = 5
        self.windows = get_all_windows_pos()
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)  # Key line
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(self.width, self.height)
        self.move(self.x,self.y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a red rectangle — background stays transparent
        painter.setBrush(QColor("red"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 50, 50)

    def check_if_inside(self,id,x,y,width,height):
        self.windows[id] = (x,y,width,height)

    def apply_collision(self):
        for (x,y,width,height) in self.windows.values():
            if self.x <= x + width and self.x + self.width > x and self.y <= y +height and self.y+self.height >= y:
                if self.x + self.width > x + width:
                    self.velocity[0] += x + width - self.x
                elif self.x < x:
                    self.velocity[0] += x - (self.x+self.width)
                elif self.y + self.height > y + height:
                    self.velocity[1] += y + height - self.y
                elif self.y < y:
                    self.velocity[1] += y - (self.y+self.height)
            
    def gravity(self):
        if self.y + self.height < self.screen_size.height():
            self.velocity[1] += 1
        

    def apply(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        if self.y <= 0 :
            self.y = 32
            self.velocity[1] = 0
        if self.x < 0:
            print("Here")
            self.x = 0
            self.velocity[0] = 0
        if self.y + self.height >= self.screen_size.height():
            self.y = self.screen_size.height() - self.height
            self.velocity[1] = 0
        if self.x + self.width >= self.screen_size.width():
            self.x = self.screen_size.width() - self.width
            self.velocity[0] = 0

        drag = 1/100 * self.velocity[0]**2
        if self.velocity[0] > 0:
            self.velocity[0] =  int(self.velocity[0] - drag)
            #if self.velocity[0] < 0:
            #    self.velocity[0] = 0
        elif self.velocity[0] < 0:
            self.velocity[0] = int(self.velocity[0] + drag)
            if self.velocity[0] > 0:
                self.velocity[0] = 0
        self.move(self.x,self.y)

    def follow_cursor(self):
        pos = QCursor.pos()
        print(pos.x(),self.x,self.x - self.vitesse*2, self.x + self.vitesse*2)
        if (self.x + self.vitesse*2) < pos.x():
            print("less")
            self.velocity[0] += self.vitesse
        elif (self.x - self.vitesse*2) > pos.x():
            print("more")
            self.velocity[0] -= self.vitesse
        print(self.velocity)

    def mainLoop(self):
        while True:
            self.gravity()
            self.apply_collision()
            self.follow_cursor()
            self.apply()
            time.sleep(0.02)  # Sleep to reduce CPU usage


def main():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    win = TransparentWindow(app)
    update_thread = threading.Thread(target=win.mainLoop)
    update_thread.daemon = True
    update_thread.start()
    windows_subscriber_thread = threading.Thread(target=listen_for_window_changes,args=(win,))
    windows_subscriber_thread.daemon = True
    windows_subscriber_thread.start()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()