from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QPainter, QColor, QPen


from find_window import listen_for_window_changes, get_all_windows_pos

from blob import Blob

import sys
import time
import threading

class TransparentWindow(QWidget):
    def __init__(self,app : QApplication):
        self.screen_size = app.primaryScreen().size()
        self.blob = Blob()
        dim = self.blob.cadre()
        self._x = dim[0]
        self._y = dim[1]
        self.width = dim[2] - dim[0] + 1
        self.height = dim[3] - dim[1] + 1
        print(self.screen_size)
        self.velocity = [0,0]
        self.vitesse = 3
        self.can_jump = True
        self.windows = get_all_windows_pos()
        super().__init__()
        self.id = None
        self.setAttribute(Qt.WA_TranslucentBackground)  # Key line
        self.setWindowFlags( Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(self.width, self.height)
        self.move(self._x,self._y)
        self.setMouseTracking(True)  # Enable mouse tracking to get mouse move events
        self.color = [255,255,255]
        self._i = 0
        


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(self.color[0],self.color[1],self.color[2]))
        pen = QPen(Qt.white, 2, Qt.SolidLine)
        painter.setPen(pen)
        adding,corp = self.blob.draw()
        dim = self.blob.cadre()
        print(dim, self.x(),self.y())
        self._x = dim[0]
        self._y = dim[1]
        self.width = dim[2] - dim[0]
        self.height = dim[3] - dim[1]
        self.resize(self.width, self.height)
        self.move(self._x,self._y)
        for line in corp:
            painter.drawLine(int(line[0]-dim[0]),int(line[1]-dim[1]),int(line[2]-dim[0]),int(line[3]-dim[1]))
        for line in adding:
            painter.drawLine(int(line[0]+self.width//2),int(line[1]+self.height//2),int(line[2]+self.width//2),int(line[3]+self.height//2))

        #painter.drawRect(0, 0, 50, 50)
        #if self.color[self._i] == 0:
        #    self._i = (self._i + 1) %3
        #else:
        #    self.color[self._i] -= 1
        #    self.color[(self._i+1)%3] += 1


    def check_if_inside(self,id,x,y,width,height,self_id):
        self.id = self_id
        self.windows[id] = (x,y,width,height)

    def delete_window(self,id):
        if id in self.windows:
            self.windows.pop(id) 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.blob.on_ground:
            self.blob.jump()  # Jump velocity

    def apply_collision(self):
        for (id,(x,y,width,height)) in self.windows.items():
            if id == self.id:
                continue
            if self._x <= x + width and self._x + self.width > x and self._y <= y +height and self._y+self.height >= y:
                if self._x + self.width > x + width:
                    self.velocity[0] += x + width - self._x
                elif self._x < x:
                    self.velocity[0] += x - (self._x+self.width)
                elif self._y + self.height > y + height:
                    self.velocity[1] += y + height - self._y
                elif self._y < y:
                    self.velocity[1] += y - (self._y+self.height)
            
    def gravity(self):
        if self._y + self.height < self.screen_size.height():
            self.velocity[1] += 1
        

    #def apply(self):
    #    self._x += self.velocity[0]
    #    self._y += self.velocity[1]
    #    if self._y <= 0 :
    #        self._y = 32
    #        self.velocity[1] = 0
    #    if self._x < 70:
    #        self._x = 70
    #        self.velocity[0] = 0
    #    if self._y + self.height >= self.screen_size.height():
    #        self._y = self.screen_size.height() - self.height
    #        self.can_jump = True
    #        self.velocity[1] = 0
    #    if self._x + self.width >= self.screen_size.width():
    #        self._x = self.screen_size.width() - self.width
    #        self.velocity[0] = 0
    #    drag = 1/100 * self.velocity[0]**2
    #    if self.velocity[0] > 0:
    #        self.velocity[0] =  int(self.velocity[0] - drag)
    #        if self.velocity[0] < 0:
    #            self.velocity[0] = 0
    #    elif self.velocity[0] < 0:
    #        self.velocity[0] = int(self.velocity[0] + drag)
    #        if self.velocity[0] > 0:
    #            self.velocity[0] = 0
    #    self.move(self._x,self._y)

    def apply(self):
        self.blob.update()
        

    def follow_cursor(self):
        pos = QCursor.pos()
        #print(pos.x(),self._x,self._x - self.vitesse*2, self._x + self.vitesse*2)
        #print(self.velocity)
        d = abs(self._x - pos.x())
        if (self._x + self.vitesse*2) < pos.x() - self.width:
            #self.velocity[0] += self.vitesse
            self.blob.roll(self.vitesse)
        elif (self._x - self.vitesse*2) > pos.x():
            self.blob.roll(-self.vitesse)
            #self.velocity[0] -= self.vitesse
        if d > self.vitesse*500 and self.blob.on_ground:
            self.blob.jump()
        #    self.velocity[1] -= 15
        #print(self.velocity)

    def mainLoop(self):
        while True:
            #self.gravity()
            #self.apply_collision()
            self.update()
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