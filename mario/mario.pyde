add_library('minim')
player = Minim(this)
add_library('sound')

import os

class Game:
    def __init__(self, w, h, g):
        self.w = w
        self.h = h
        self.g = g
        self.mario = Mario(100, 100, self.g, 35, 100, 70, 10)
        self.bg = loadImage(os.getcwd() + '/images/layer_01.png')
        self.bgMusic = player.loadFile(os.getcwd() + '/sounds/background.mp3')
        self.bgMusic.loop()
        self.pause = False
        
        self.platforms = []
        self.platforms.append(Platform(300, 500, 200, 51, "platform.png"))
        self.platforms.append(Platform(600, 450, 200, 51, "platform.png"))
        self.platforms.append(Platform(1000, 300, 200, 51, "platform.png"))
        
        self.gombas = []
        self.gombas.append(Gomba(100, 200, self.g, 35, 70, 70, 5))
    
    def display(self):
        stroke(0)
        line(0, self.g, self.w, self.g)
        image(self.bg, 0, 0)
        for platform in self.platforms:
            platform.display()
        self.mario.display()
        for gomba in self.gombas:
            gomba.display()


class Creature:
    def __init__(self, x, y, g, r, w, h, F):
        self.x = x
        self.y = y
        self.g = g
        self.r = r
        self.vx = 0
        self.vy = 1
        self.w = w
        self.h = h
        self.F = F
        
    def display(self):
        self.update()
        ellipse(self.x, self.y, 2*self.r, 2*self.r)
        
    def gravity(self):
        if self.y + self.r < self.g:
            self.vy += 1
        else:
            self.vy = 0
            
        if self.y + self.r > self.g:
            self.y = self.g - self.r
            
        # Platform collision
        for p in game.platforms:
            if p.x <= self.x < p.x + p.w and self.y + self.r <= p.y:
                self.g = p.y
                return
        self.g = game.g
        
    def update(self):
        self.gravity()
        self.x += self.vx
        self.y += self.vy


class Mario(Creature):
    def __init__(self, x, y, g, r, w, h, F):
        Creature.__init__(self, x, y, g, r, w, h, F)
        self.keyHandler = {LEFT:False, RIGHT:False, UP:False}
        self.img_right = loadImage(os.getcwd() + '/images/mario.png')
        self.img_left = loadImage(os.getcwd() + '/images/mario_left.png')
        self.img = self.img_right
        self.f = 0
        self.jumpSound = SoundFile(this, os.getcwd() + '/sounds/jump.mp3')
        self.jumpSound.amp(1.0)
        
    def update(self):
        self.gravity()
        
        if self.keyHandler[LEFT]:
            self.vx = -5
            self.img = self.img_left
        elif self.keyHandler[RIGHT]:
            self.vx = 5
            self.img = self.img_right
        else:
            self.vx = 0
            
        if self.keyHandler[UP] and self.y + self.r == self.g: 
            self.vy = -20
            self.jumpSound.play()
        
        self.x += self.vx
        self.y += self.vy
        
    def display(self):
        self.update()
        self.f = (self.f + 0.3) % self.F
        image(self.img, self.x - self.r, self.y - self.r, self.w, self.h, int(self.f) * self.w, 0, (int(self.f)+1) * self.w, self.h)


class Gomba(Creature):
    def __init__(self, x, y, g, r, w, h, F):
        Creature.__init__(self, x, y, g, r, w, h, F)
        self.x1 = x - 200
        self.x2 = x + 200
        self.vx = 2
        
    def update(self):
        self.gravity()
        self.x += self.vx
        self.y += self.vy
        
        if self.y + self.r > self.g:
            self.y = self.g - self.r
            
        if self.x > self.x2:
            self.vx = -2
        elif self.x < self.x1:
            self.vx = 2


class Platform:
    def __init__(self, x, y, w, h, imgName):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = loadImage(os.getcwd() + '/images/' + imgName)
        
    def display(self):
        image(self.img, self.x, self.y)


# Initialize game
game = Game(1280, 720, 585)

def setup():
    size(game.w, game.h)
        
def draw():
    if not game.pause:
        background(255)
        game.display()
    
def keyPressed():
    if keyCode == LEFT:
        game.mario.keyHandler[LEFT] = True
    elif keyCode == RIGHT:
        game.mario.keyHandler[RIGHT] = True
    elif keyCode == UP:
        game.mario.keyHandler[UP] = True
        
    if key == 'p':
        game.pause = not game.pause
        if game.pause:
            game.bgMusic.pause()
        else:
            game.bgMusic.play()
        
def keyReleased():
    if keyCode == LEFT:
        game.mario.keyHandler[LEFT] = False
    if keyCode == RIGHT:
        game.mario.keyHandler[RIGHT] = False
    if keyCode == UP:
        game.mario.keyHandler[UP] = False
