import math
import random

WIDTH = 2560
HEIGHT = 1440

class Blob:
    def __init__(self):
        self.point_number = 20
        self.posi = [400,400]
        self.pos = []
        self.vit = []
        self.d   = []
        self.r = 75
        self.g = 0.2
        self.force = 0.01
        self.blink = 0
        self.on_ground = False
        for i in range(self.point_number):
            self.pos.append([math.cos(math.radians(i*360/self.point_number))*self.r+self.posi[0],math.sin(math.radians(i*360/self.point_number))*self.r+self.posi[1]])
            self.vit.append([0,0])
        for i in range(len(self.pos)):
            self.d.append([])
            for j in range(i+1,len(self.pos)):
                dx = self.pos[i][0]-self.pos[j][0]
                dy = self.pos[i][1]-self.pos[j][1]
                distance = math.sqrt(dx*dx+dy*dy)
                self.d[i].append(distance)
        self.dist = (2*math.pi*self.r)/self.point_number
        self.relax = 1

    def mid_point(self):
        pos = [0,0]
        for i in self.pos:
            pos[0] += i[0]
            pos[1] += i[1]
        return [pos[0]/len(self.pos),pos[1]/len(self.pos)]

    def draw(self):
        e = self.mid_point()
        corp = []
        fioriture = []
        if random.random() > 0.995:
            self.blink = 10
        if self.blink <= 0:
            fioriture.append([-8,-30,-8,10])
            fioriture.append([8,-30,8,10])
        else :
            fioriture.append([-8,12,-8,10])
            fioriture.append([8,12,8,--10])
            self.blink -= 1


        for i in range(len(self.pos)):
            p = self.pos[i]
            p2 = self.pos[(i+1)%(len(self.pos))]
            corp.append([p[0],p[1],p2[0],p2[1]])        
        return [fioriture,corp]

    def cadre(self):
        top = HEIGHT
        bottom = 0
        left = WIDTH
        right = 0
        for i in range(len(self.pos)):
            if self.pos[i][0] < left:
                left = self.pos[i][0]
            if self.pos[i][0] > right:
                right = self.pos[i][0]
            if self.pos[i][1] < top:
                top = self.pos[i][1]
            if self.pos[i][1] > bottom:
                bottom = self.pos[i][1]
        #mid_point = self.mid_point()
        #pl = 15
        #left = mid_point[0] - (self.r + pl)
        #right = mid_point[0] + (self.r + pl)
        #top = mid_point[1] - (self.r + pl)
        #bottom = mid_point[1] + (self.r + pl)
        return [int(left),int(top),int(right),int(bottom)]

    def roll(self,speed):
        top = HEIGHT
        ind = 0
        for i in range(len(self.pos)):
            if self.pos[i][1] < top:
                top = self.pos[i][1]
                ind = i

        nb = 5
        for i in range(-1*nb,nb+1):
            self.vit[(ind+i)%(len(self.pos))][0] += speed

    def jump(self):
        self.on_ground = False
        top = HEIGHT
        ind = 0
        for i in range(len(self.pos)):
            if self.pos[i][1] < top:
                top = self.pos[i][1]
                ind = i

        nb = 7
        for i in range(-1*nb,nb+1):
            self.vit[(ind+i)%(len(self.pos))][1] -= 20


    def spr(self,i1,i2,dist):
        pt1 = self.pos[i1]
        pt2 = self.pos[i2]
        dx = pt2[0]-pt1[0]
        dy = pt2[1]-pt1[1]
        distance = math.sqrt(dx*dx+dy*dy)   
        if distance < 1:
           distance = 1 
        r = self.relax
        if distance > dist:
            r = -self.relax
        dxn = dx/distance * abs(distance - dist + r)
        dyn = dy/distance * abs(distance - dist + r)

        if distance > dist +self.relax:
            self.vit[i1][1]  += dyn*self.force
            self.vit[i2][1] -= dyn*self.force
            self.vit[i1][0]  += dxn*self.force
            self.vit[i2][0] -= dxn*self.force
        elif distance < dist - self.relax:
            self.vit[i1][1]  -= dyn*self.force
            self.vit[i2][1] += dyn*self.force
            self.vit[i1][0]  -= dxn*self.force
            self.vit[i2][0] += dxn*self.force

    def update(self):
        for i in range(len(self.pos)):
            maxi = 15
            if self.vit[i][0] > maxi:
                self.vit[i][0] = maxi
            if self.vit[i][0] < -maxi:
                self.vit[i][0] = -maxi
            if self.vit[i][1] > maxi:
                self.vit[i][1] = maxi
            if self.vit[i][1] < -maxi:
                self.vit[i][1] = -maxi
            self.pos[i][0] += self.vit[i][0]
            self.pos[i][1] += self.vit[i][1]

            self.vit[i][0] = self.vit[i][0]*0.8
            self.vit[i][1] = self.vit[i][1]*0.8

        for i in range(len(self.pos)):
            for j in range(i+1,len(self.pos)):
                self.spr(i, j, self.d[i][j-i-1])
        
        for i in range(len(self.pos)):
            self.vit[i][1] += self.vit[i][1]*self.g + self.g
            if self.pos[i][0] < 66:
                self.pos[i][0] = 66
                self.vit[i][0] = 0
            elif self.pos[i][0] > WIDTH:
                self.pos[i][0] = WIDTH
                self.vit[i][0] = 0
            if self.pos[i][1] < 0:
                self.pos[i][1] = 0
                self.vit[i][1] = 0
            elif self.pos[i][1] > HEIGHT:
                self.on_ground = True
                self.pos[i][1] = HEIGHT
                self.vit[i][1] = 0