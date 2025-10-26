RESOLUTION = 1300
RESOLUTION1 = 800
is_running = True #If False, game restarts
is_collided = False #Checks if chicken is attached to log or lilypad
new_game_mode = False #2nd Level
further_game_mode = False #Third Level
ending_mode = False #Ending Screen
level = 0
add_library('minim')
player = Minim(this)
add_library('sound')
import time, random, copy
timer = 0
highest_positions = [0]
score = 0
highestscore = 0
lastscore = 0
character = random.randint(0,1)
flag = True
position1 = 0
position2 = 0
position3 = 0
marker = True 
all_the_highscores = [0,0,0,0,0,0] 

class Game: 
    def __init__(self):
        self.score = 0
        self.TEXTSIZE = 15
        self.bgMusic = player.loadFile(os.getcwd() + '/sounds/background.mp3')
        self.waterSound = SoundFile(this, os.getcwd() + '/sounds/water.mp3')
        self.bgMusic.loop()
    def restart_game(self):
        global is_running,flag, new_game_mode, further_game_mode, ending_mode, all_highscores, position1, position2, position3, highestscore, lastscore
        flag = True
        is_running = True
        new_game_mode = False
        further_game_mode = False
        highestscore = 0
        for i in all_the_highscores: #Take the highestscore of the first position
            if i > highestscore:
                highestscore = i
                position1 = i
        secondlist = []
        secondlist = copy.deepcopy(all_the_highscores) #Deep copied this to avoid changing highestscores and all_the_highscores
        print(secondlist)
        secondlist.remove(position1) #Removes position1 to calculate the second best highestscore
        
        highestscore = 0
        for i in secondlist: #Take the highestscore of the second position
            if i > highestscore:
                highestscore = i
                position2 = i
        thirdlist = []
        thirdlist = copy.deepcopy(secondlist)
        thirdlist.remove(position2) #Removes position2 to calculate the third best highscore
        
        highestscore = 0
        for i in thirdlist: #Take the highestscore of the third position
            if i > highestscore:
                highestscore = i
                position3 = i

        ending_mode = False
        
        chicken.x = 608
        chicken.y = 736

    def show_score(self):
        global highestscore, timer, flag, is_running, all_the_highscores, lastscore
        textSize(self.TEXTSIZE)
        fill(0)
        highestscore = highest_positions[0]
        for num in highest_positions:
            if num > highestscore: #Takes the highest position
                highestscore = num
        timer = float(timer + 0.016666666667) #Frame Rate is 60 so therefore, it increases by 1/60
        #print(timer)
        displaytimer = int(timer)        
        
        if displaytimer == 3: #This decreases until the game restarts
            fill(256, 0, 0)
            displaytimer = " Game ENDS IN 3"
        if displaytimer == 4:
            fill(256, 0, 0)
            displaytimer = " Game ENDS IN 2"
        if displaytimer == 5:
            fill(256, 0, 0)
            displaytimer = " Game ENDS IN 1"  
            
        if int(timer) == 6: 
            is_running = False
            timer = 0

        text("The score is " + str(highestscore)+ " Time : " + str(displaytimer), 150, 20)
        lastscore = copy.deepcopy(highestscore)
        
    def show_level(self):
        global level
        text("Level " + str(level), 1245, 12) #Displays the level in every game mode
        
    def display_background(self): #Generates the first background for level 1
        global level, flag
        level = 1
        fill(144,249,100)
        rect(0,0,RESOLUTION,RESOLUTION1)
        fill(100,100,246)
        rect(0,50, RESOLUTION, RESOLUTION1)
        fill(144,249,100)
        rect(0,237,RESOLUTION,RESOLUTION1)
        fill(150)
        rect(0,360,RESOLUTION,RESOLUTION1)
        fill(150)
        rect(0, 420, RESOLUTION,RESOLUTION1)
        fill(144,249,120)
        rect(0, 476, RESOLUTION, RESOLUTION1)
        fill(144,249,100)
    def adjust_background(self): 
        global new_game_mode
        if chicken.y < 38: #Chickens if the chicken crosses a threshold to move to the next level
            new_game_mode = True
            chicken.x = chicken.x
            chicken.y = 736
    def display_new_background(self): #2nd Level Background
        global level
        level = 2
        fill(144,249,100)
        rect(0,0, RESOLUTION, RESOLUTION)
        fill(150) 
        rect(0, 170, RESOLUTION, RESOLUTION)
        fill(144,249,100)
        rect(0, 230, RESOLUTION, RESOLUTION)
        fill(150)
        rect(0, 280, RESOLUTION, RESOLUTION)
        fill(150)
        rect(0,340,RESOLUTION,RESOLUTION)
        fill(150)
        rect(0, 400, RESOLUTION, RESOLUTION)
        fill(100,100,246)
        rect(0,476,RESOLUTION,RESOLUTION)
        fill(144,249,100)
        rect(0, 662, RESOLUTION, RESOLUTION)
    def new_background(self):
        global further_game_mode, new_game_mode
        if chicken.y < 10: #Checks the chicken position to move to level 3
            further_game_mode = True
            new_game_mode = False
            chicken.x = chicken.x
            chicken.y = 736
            
    def further_background(self): #The function name is a bit weird but this is for level 3
        global level
        level = 3
        fill(144, 249, 100)
        rect(0,0, RESOLUTION, RESOLUTION)
        fill(100, 100, 246)
        rect(0, 120, RESOLUTION, RESOLUTION)
        fill(150)
        rect(0, 340, RESOLUTION, RESOLUTION)
        fill(150)
        rect(0, 400, RESOLUTION, RESOLUTION)
        fill(144, 249, 100)
        rect(0, 460, RESOLUTION, RESOLUTION)
        fill(144, 249, 100)
        rect(0, 530, RESOLUTION, RESOLUTION)
        fill(150)
        rect(0, 590, RESOLUTION, RESOLUTION)
        fill(100, 100, 246)
        rect(0, 650, RESOLUTION, RESOLUTION)
        fill(144,249,100)
        rect(0, 725, RESOLUTION, RESOLUTION)
    def newest_background(self):
        global further_game_mode, ending_mode
        if chicken.y < 10:
            further_game_mode = False
            is_running = False
            ending_mode = True
    def ending_background(self): #Displays the final background
        global new_game_mode, ending_mode
        fill(150)
        rect(0,0, RESOLUTION, RESOLUTION)
    def ending_message(self):
        textSize(50)
        text("Game ended", 500,400)
        textSize(30)
        text("Press the mouse to continue", 460,500)
        
class Chicken:
    def __init__(self):
        global is_collided, character
        self.is_match = False
        if character == 0:
            self.img_right = loadImage(os.getcwd() + "/images/chicken_right.png")
            self.img_left = loadImage(os.getcwd() + "/images/chicken_left.png")
            self.img_down = loadImage(os.getcwd() + "/images/chicken_down.png")
            self.img_up = loadImage(os.getcwd() + "/images/chicken.png")
        elif character == 1:
            self.img_right = loadImage(os.getcwd() + "/images/bluechicken_right.png")
            self.img_left = loadImage(os.getcwd() + "/images/bluechicken_left.png")
            self.img_down = loadImage(os.getcwd() + "/images/bluechicken_down.png")
            self.img_up = loadImage(os.getcwd() + "/images/bluechicken.png")
        self.img = self.img_up
        self.img.resize(50,50)
        self.x = 618 #Bottom middle of screen for x and y
        self.y = 734
        self.speed = 62
        self.lowest = 0
        self.jumpSound = SoundFile(this, os.getcwd() + '/sounds/jump.mp3')
    def display(self):
        image(self.img,self.x, self.y)
    def move_left(self):
        self.img = self.img_left
        self.img.resize(50,50)
        self.x -= self.speed
        self.jumpSound.play()
    def move_right(self):
        self.img = self.img_right
        self.img.resize(50,50)
        self.x += self.speed
        self.jumpSound.play()
    def move_up(self):
        self.img = self.img_up
        self.img.resize(50,50)
        self.x_up = self.x
        self.y -= self.speed
        self.jumpSound.play()
    def move_down(self):
        self.img = self.img_down
        self.img.resize(50,50)
        self.x_down = self.x
        self.y += self.speed
        self.has_moved = False
        self.jumpSound.play()
    def attachment(self, x, y, new_speed, number, new_number, other_number, sizex):
        global is_collided
        if self.x + self.img.width / 2 >= x and abs(x-self.x) <= other_number and abs(y-self.y) <= number: #I am using self.img.width to check the whole width so that the chicken has an easier time to attaching to larger logs
            self.x = x
            self.y = y - new_number #Chicken position was a bit too high so we shift it
            is_collided = True
    def attachment_left(self, x, y, new_speed, number, new_number, other_number, sizex): #Attahcment for the other logs
        global is_collided
        if self.x - self.img.width / 2 <= x and abs(x-self.x) <= other_number and abs(y-self.y) <= number: #Since pixels are not perfectly even this checks if the difference is between a certain number so that it can easily attach
            self.x = x
            self.y = y - new_number
            is_collided = True
    
        
class Car: #This possibly could have been inherited however it uses different conditions than the chicken and the image part is a huge part as well
    def __init__(self, car_x = 530, car_y = 428, speed = 5, image_path = "/images/car.png"):
        self.image_path = image_path
        self.img_car = loadImage(os.getcwd() + image_path)
        self.img_car.resize(70,40)
        self.x = car_x
        self.y = car_y
        self.speed = speed
        self.cSound = SoundFile(this, os.getcwd() + '/sounds/collision.mp3')
    def display(self):
        image(self.img_car, self.x, self.y)
    def move_left(self):
        self.x -= self.speed
    def move_right(self):
        self.x += self.speed
    def collision(self, new_list): #collision the cars moving right
        global is_running
        for car in new_list: #Takes a list of cars and displays them to save time
                car.display()
                car.move_left()
                if car.x < -100: #Resets the cars position when it goes off the screen
                    car.x = RESOLUTION
                for other_car in new_list: #This checks if the other car bumped into our car
                    if car != other_car:
                        if (car.x < other_car.x + 70 and car.x + 70 > other_car.x):
                            car.x = car.x + 50 #Shifts the car to reflect a bump
                            car.speed = other_car.speed #Adjusts the speed as well
                            other_car.speed = other_car.speed + 1 #This allows us to change the speed over time to so it is not continous
                        if abs(car.y - chicken.y) <= 35 and abs(car.x - chicken.x) <= 35:#If the collision position is met, game is over
                            is_running = False
                            self.cSound.play()
    def collision_left(self, new_list): #This is the collision condition for the cars moving left
        global is_running
        for car in new_list:
            car.display()
            car.move_right()
            if car.x > RESOLUTION:
                car.x = 1
            for other_car in new_list:
                if car != other_car:
                    if (car.x < other_car.x + 70 and car.x + 70 > other_car.x):
                        car.x = car.x - 50
                        car.speed = other_car.speed
                        other_car.speed = other_car.speed + 1
                    if abs(car.y - chicken.y) <= 40 and abs(car.x - chicken.x) <= 40 :
                        is_running = False
                        self.cSound.play()
        
class Log(Car): #Inheritance!
    def __init__(self, x, y, sizex, sizey, speed):
        global is_running
        self.x = x
        self.y = y
        self.sizex = sizex #This allows us to change the logs size
        self.sizey = sizey
        self.img_log = loadImage(os.getcwd() + "/images/logs1.png")
        self.img_log.resize(self.sizex, self.sizey)
        self.speed = speed
    def display(self): #Polymorism 
        image(self.img_log, self.x, self.y)
    def reset(self, chickenx, chickeny): #Resets the logs position after it falls us the screen
        if abs(chickenx - self.x) < 35  and abs(chickeny - self.y) < 35 and self.x > RESOLUTION:
            is_running = False
        elif self.x > RESOLUTION:
            self.x = 0
    def reset_left(self, chickenx, chickeny): #Resets the opposite logs
        if abs(chickenx - self.x) < 35  and abs(chickeny - self.y) < 35 and self.x > RESOLUTION:
            is_running = False
        elif self.x < 0:
            self.x = RESOLUTION
            
class Lilypad:
    def __init__(self, x, y, sizex, sizey):
        self.x = x
        self.y = y
        self.img_lily = loadImage(os.getcwd() + "/images/lilypad.png")
        self.sizex = sizex
        self.sizey = sizey
        self.img_lily.resize(self.sizex, self.sizey)
        self.speed = 0
    def display(self):
        image(self.img_lily, self.x, self.y)
        
class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = loadImage(os.getcwd() + "/images/tree.png")
        self.img.resize(50,50)
    def display(self):
        image(self.img, self.x, self.y)
    def tree_collision(self): #Checks if the chicken and tree are near each other
        global is_running
        if abs(chicken.x - self.x) <= 35 and abs(chicken.y - self.y) <= 35:
            is_running = False
chicken = Chicken() # DISPLAYS ALL THE ELEMENTS IN THE CODE
car1 = Car(500, 428, 15)
car2 = Car(420, 428, 14, "/images/car_purple.png")
car3 = Car(781, 428, 13, "/images/car_green.png")
car4 = Car(1200, 428, 6, "/images/car_orange.png")
car5 = Car(1, 370, 12, "/images/car_purple_right.png")
car6 = Car(130, 370, 13, "/images/car_blue_right.png")
car7 = Car(530, 370, 14, "/images/car_orange_right.png")
car8 = Car(200, 290, 6)
car9 = Car(500, 290, 7, "/images/car_purple.png")
car10 = Car(330, 290, 4, "/images/car_orange.png")
car11 = Car(1000, 370, 14, "/images/car_purple_right.png")
car12 = Car(700, 370, 11, "/images/car_blue_right.png")
car13 = Car(700, 180, 3, "/images/car_orange.png")
car14 = Car(300, 180, 5, "/images/car_purple.png")
car15 = Car(900, 180, 4, "/images/car_green.png")
car35 = Car(130, 180, 6, "/images/car_green.png")
car16 = Car(500, 415, 6)
car17 = Car(781, 415, 8, "/images/car_green.png")
car18 = Car(420, 415, 7, "/images/car_purple.png")
car19 = Car(1, 350, 3, "/images/car_purple_right.png")
car20 = Car(130, 350, 5, "/images/car_blue_right.png")
car21 = Car(530, 350, 6, "/images/car_orange_right.png")
car22 = Car(130, 600, 5, "/images/car_purple_right.png")
car23 = Car(430, 600, 7, "/images/car_orange_right.png")
car24 = Car(600, 600, 9, "/images/car_blue_right.png")
car25 = Car(800, 600, 8, "/images/car_purple_right.png")
car26 = Car(900, 600, 6, "/images/car_orange_right.png")
car27 = Car(900, 410, 10, "/images/car_purple.png")
car28 = Car(500, 410, 9, "/images/car_green.png")
car29 = Car(100, 410, 10, "/images/car_orange.png")
car30 = Car(600, 350, 10, "/images/car_blue_right.png")
car31 = Car(800, 350, 9, "/images/car_orange_right.png")
car32 = Car(200, 350, 10, "/images/car_purple_right.png")
car33 = Car(400, 350, 10, "/images/car_blue_right.png")
game = Game()
log1 = Log(4, 190, 80, 50, 3)
log2 = Log(300, 190, 50, 50, 3)
log3 = Log(200, 190, 100, 50, 3)
log6 = Log(400, 190, 70, 50, 3)
log7 = Log(550, 190, 50, 50, 3)
lily = Lilypad(459, 130, 50, 50)
lily2 = Lilypad(100, 130, 50, 50)
log4 = Log(RESOLUTION, 70, 50, 50, 3)
log5 = Log(350, 70, 70, 50, 3)
log8 = Log(150, 70, 100, 50, 3)
log9 = Log(450, 70, 80, 50, 3)
log10 = Log(900, 548, 70, 50, 6)
log11 = Log(500, 548, 100, 50, 6)
log12 = Log(150, 548, 80, 50, 6)
log13 = Log( 700, 485, 100, 50, 8)
log14 = Log( 522, 485, 80, 50, 8)
log15 = Log( 356, 485, 40, 50, 8)
log16 = Log( 1000, 485, 100, 50, 8)
log18 = Log(100, 670, 50, 50, 8)
log19 = Log(100, 290, 50, 50, 8)
log20 = Log(800, 150, 50, 50, 8)
lily3 = Lilypad(700, 130, 50, 50)
lily4 = Lilypad(1114, 610, 50, 50)
lily5 = Lilypad(804, 610, 50, 50)
lily6 = Lilypad(184, 610, 50, 50)
lily7= Lilypad(600, 215, 50, 50)
tree = Tree(1252, 674)
tree1 = Tree(1000, 674)
tree2 = Tree(860, 674)
tree3 = Tree(730, 674)
tree4 = Tree(600, 674)
tree5 = Tree(470, 674)
tree6 = Tree(346, 674)
tree7 = Tree(220, 674)
tree8 = Tree(96, 674)
tree9 = Tree(0, 674)
tree10 = Tree(220, 120)
tree11 = Tree(600, 80)
tree12 = Tree(400, 20)
tree13 = Tree(900, 120)
tree14 = Tree(1100, 20)
tree15 = Tree(100, 20)
tree16 = Tree(100, 540)
tree17 = Tree(300, 540)
tree18 = Tree(450, 540)
tree19 = Tree(600, 540)
tree20 = Tree(800, 540)
tree21 = Tree(1000, 540)
tree22 = Tree(1200, 540)
tree23 = Tree(400, 470)
tree24 = Tree(1131, 470)
tree25 = Tree(724, 470)
def setup():
    size(RESOLUTION, RESOLUTION1)
    frameRate(45)
def draw():
    global is_running
    global is_collided
    global new_game_mode, further_game_mode, ending_mode
    global score, timer, flag, character
    global highest_positions, highestscore, all_the_highscores, position1, position2, position3, marker, lastscore
    background(255)
    if is_running == True: #If it is running is false, the game resets
        if flag == True: # This makes the game go to the home page
            character = 0 
            textAlign(CENTER)
            textSize(55)
            fun_font = createFont("Comic Sans MS", 55)
            textFont(fun_font)
            fill(0)
            background1 = loadImage(os.getcwd() + "/images/Background.jpg")
            background1.resize(RESOLUTION,RESOLUTION1)
            image(background1, 0, 0)
    
            text("Instructions", width / 2, 50) #This displays the Instructions
            
            textSize(25)
            text("Controls:", width / 2, 100)
            text("Use arrow keys to move:", width / 2, 130)
            text(" - UP: Move up", width / 2, 160)
            text(" - DOWN: Move down", width / 2, 190)
            text(" - LEFT: Move left", width / 2, 220)
            text(" - RIGHT: Move right", width / 2, 250)
            
            
            if len(all_the_highscores) == 0: #This Checks for the highest score for the leaderboard
                position1 = 0
                position2 = 0
                position3 = 0
            
            else:
                #print(position1, position2, position3)
                pass
            
        
                
            text(" Leaderboards:", 100, 40)
            text(" Position 1: " + str(position1), 100, 90)
            text(" Position 2: " + str(position2), 100, 160)
            text(" Position 3: " + str(position3), 100, 230)
            #text(" Your Last Score was: " + str(lastscore), 961, 144)
            
            
            if int(lastscore) > 0: #Checks to make sure we don't print the last score of 0
                textSize(35)
                if lastscore >=70:
                    fill(0)
                    text(" CONGRATULATIONS !!!!!!!!!!!!: " + str(lastscore), 961, 144)
                    textSize(25)
                else:
                    fill(256,0,0)
                    text("GAME OVER ! ! ! ! ! ",1000, 100)
                    fill(0)
                    text(" Your Last Score was: " + str(lastscore), 1000, 144)
                    fill(0)
                    textSize(25)
                    
                
                
            
            text("Avoid:", width / 2, 300)
            text(" - Trees", width / 2, 330)
            text(" - Water", width / 2, 360)
            text(" - Cars", width / 2, 390)
            
            text("Objective:", width / 2, 440)
            text("Beat 3 Levels to win the game", width / 2, 470)
            
            text("Timer:", width / 2, 520)
            text("The game timer will end in 5 seconds if no controls are pressed.", width / 2, 550)
            text("Keep moving!", width / 2, 580)
            text("Please Press Enter to BEGIN!", width / 2, 640)
            
            left_arrow = loadImage(os.getcwd() + "/images/Left_arrow.png") # This displays the section to choose player
            left_arrow.resize(60,60)
            image(left_arrow, 381, 679)
            right_arrow = loadImage(os.getcwd() + "/images/Right_arrow.png")
            right_arrow.resize(60,60)
            image(right_arrow, 919, 679)
            
            
            if keyCode == LEFT:
                character = 1
                
            if keyCode == RIGHT:
                character = 0
                
            if character == 0: #Checks for which character we can choose
                Green_Chicken = loadImage(os.getcwd() + "/images/chicken.png")
                Green_Chicken.resize(180,180)
                image(Green_Chicken, (RESOLUTION/2) - 50, 628)
            
                
            elif character == 1:
                blue_Chicken = loadImage(os.getcwd() + "/images/bluechicken.png")
                blue_Chicken.resize(180,180)
                image(blue_Chicken, (RESOLUTION/2)- 50, 628)

                
    
            
            #print(keyCode)
            
            
            
            
            
            if key == RETURN or key == ENTER:
                flag = False
            
        elif flag == False and new_game_mode == False and further_game_mode == False and ending_mode == False: #Level 1 # THIS RUNS THE WHOLE GAME BY SHIFTING THINGS
            game.display_background()
            game.adjust_background()
            log1.move_right()
            log2.move_right()
            log3.move_right()
            lily.display()
            lily2.display()
            logs = [log1,log2,log3,log4,log5,log6,log7,log8,log9]
            for i in logs:
                i.display()
            log4.move_left()
            log5.move_left()
            log6.move_right()
            log7.move_right()
            log8.move_left()
            log9.move_left()
            
            lily3.display()
            chicken.display()
            chicken.attachment(log1.x, log1.y, log1.speed, 35, 20, 70, 80) 
            chicken.attachment(log2.x, log2.y, log2.speed, 35, 20, 35, 50)
            chicken.attachment(log3.x, log3.y,log3.speed, 35, 20, 90, 100)
            chicken.attachment(lily.x, lily.y, 0, 30, 20, 30, 50)
            chicken.attachment_left(log4.x, log4.y, log4.speed, 35, 20, 35, 80)
            chicken.attachment_left(log5.x, log5.y, log5.speed, 35, 20, 80, 50)
            chicken.attachment(log6.x, log6.y , log6.speed, 30, 20, 70, 20)
            chicken.attachment(lily2.x, lily2.y, 0, 30, 20, 30, 50)
            chicken.attachment(log7.x, log7.y, log7.speed, 35, 20, 35, 50)
            chicken.attachment(log8.x, log8.y, log8.speed, 35, 20, 90, 100)
            chicken.attachment(log9.x, log9.y, log9.speed, 35, 20, 70, 50)
            chicken.attachment(lily3.x, lily3.y, 0, 30, 20, 30, 50)
            log1.reset(chicken.x, chicken.y)
            log3.reset(chicken.x, chicken.y)
            log2.reset(chicken.x, chicken.y)
            log4.reset_left(chicken.x, chicken.y)
            log5.reset_left(chicken.x, chicken.y)
            log6.reset(chicken.x, chicken.y)
            log7.reset(chicken.x, chicken.y)
            log8.reset_left(chicken.x, chicken.y)
            log9.reset_left(chicken.x, chicken.y)

            if chicken.x < RESOLUTION and chicken.y < 220 and chicken.y > 34 and is_collided == False:
                is_running = False
                game.waterSound.play()
            if is_collided == True and not abs(chicken.x - log1.x) < 20 and not abs(chicken.y - log1.y) < 20:
                is_collided = False
            game.show_score()
            game.show_level()
            car1.collision([car1,car2,car3,car4])
            car5.collision_left([car5, car6, car11, car12])
            if chicken.x < 5 or chicken.x > RESOLUTION - 17:
                is_running = False
                chicken.move_down()
        elif new_game_mode == True: #Level 2
            game.display_new_background()
            game.new_background()
            game.show_score()
            game.show_level()
            LOOGS = [log10, log11, log12, log13, log14, log15, log16] #Don't mind the variable names we were running out of ideas
            for i in LOOGS:
                i.display()
                
            LOOGS = [log10, log11, log12, log13, log14, log15, log16]
            for i in LOOGS:
                i.move_left()
            
            LOOGS = [log10, log11, log12, log13, log14, log15, log16]
            for i in LOOGS:
                i.reset_left(chicken.x, chicken.y)
            lily4.display()
            lily5.display()
            lily6.display()
            chicken.attachment(log10.x, log10.y, log10.speed, 35, 20, 80, 50)
            chicken.attachment(log11.x, log11.y, log11.speed, 35, 20, 90, 100)
            chicken.attachment(log12.x, log12.y, log12.speed, 35, 20, 70, 80)
            chicken.attachment(log13.x, log13.y, log13.speed, 35, 20, 90, 100)
            chicken.attachment(log14.x, log14.y, log14.speed, 35, 20, 70, 80)
            chicken.attachment(log15.x, log15.y, log15.speed, 35, 20, 30, 40)
            chicken.attachment(log16.x, log16.y, log16.speed, 35, 20, 90, 100)
            chicken.attachment(lily4.x, lily4.y, 0, 30, 20, 30, 50)
            chicken.attachment(lily5.x, lily5.y, 0, 30, 20, 30, 50)
            chicken.attachment(lily6.x, lily6.y, 0, 30, 20, 30, 50)
            chicken.display()
            if chicken.x < 5 or chicken.x > RESOLUTION - 17:
                is_running = False
                chicken.move_down()
            if chicken.x < RESOLUTION and chicken.y < 660 and chicken.y > 474 and is_collided == False: #This checks if the chicken hits the water and is not attached to logs or lilys
                is_running = False
                game.waterSound.play()
            if is_collided == True and not abs(chicken.x - log10.x) < 20 and not abs(chicken.y - log10.y) < 20: #This is because is_collided is not reset properly so after it is away from a log, it resets
                is_collided = False
            trees=[tree,tree1,tree2,tree3,tree4,tree5,tree6,tree7,tree8,tree9]
            for i in trees:
                i.tree_collision()
                i.display()
            car1.collision([car16, car17, car18])
            car5.collision_left([car19, car20, car21])
            car8.collision([car8, car9, car10])
            car13.collision([car13, car14, car15, car35]) #New Code Added
            new_trees = [tree10, tree11, tree12, tree13, tree14, tree15]
            for new in new_trees:
                new.display()
                new.tree_collision()
        elif further_game_mode == True: #Level 3
            game.newest_background()
            game.further_background()
            legos = [log18, log19]
            for lego in legos:
                lego.display()
                lego.move_right()
                lego.reset(chicken.x, chicken.y)
            chicken.attachment(log18.x, log18.y, log18.speed, 35, 20, 35, 50)
            chicken.attachment(log19.x, log19.y, log19.speed, 35, 20, 35, 50)
            lily7.display()
            chicken.attachment(lily7.x, lily7.y, 0, 30, 20, 30, 50)
            log20.display()
            log20.move_left()
            log20.reset_left(chicken.x, chicken.y)
            chicken.attachment(log20.x, log20.y, log20.speed, 35, 20, 35, 50)
            chicken.display()
            if chicken.y < 710 and chicken.y > 645 and is_collided == False: #water Detection
                is_running = False
                game.waterSound.play()
            if chicken.y < 305 and chicken.y > 115 and is_collided == False: #water detection
                is_running = False
                game.waterSound.play()
            if is_collided == True and not abs(chicken.x - log18.x) < 20 and not abs(chicken.y - log18.y) < 20 or not(chicken.x - log19.x) and not(chicken.x - log19.y):
                is_collided = False
            if chicken.x < 5 or chicken.x > RESOLUTION - 17:
                is_running = False
                chicken.move_down()
            car22.collision_left([car22, car23, car24, car25, car26])
            car27.collision([car27, car28, car29])
            car30.collision_left([car30, car31, car32, car33])
            treo = [tree16, tree17, tree18, tree19, tree20, tree21, tree22, tree23, tree24, tree25]
            for teo in treo:
                teo.display()
                teo.tree_collision()
            game.show_score()
            game.show_level()
        elif ending_mode == True: #Ending Screen
            game.ending_background()
            game.show_score()
            game.ending_message()
                
    elif is_running == False: #restarts the game after player dies
        if highestscore not in all_the_highscores:
            all_the_highscores.append(highestscore)
        if key:
            game.restart_game()
            score = 0
            highest_positions = [0]

                    
def keyPressed(): # LOOKS FOR THE KEY PRESSES
    global score , highest_positions, ns, highestscore, collision_impact, timer
    if keyCode == LEFT:
        chicken.move_left()
        timer = 0
    elif keyCode == RIGHT:
        chicken.move_right()
        #(chicken.x,chicken.y)
        timer = 0
    elif keyCode == UP:
        chicken.move_up()
        #print(chicken.x,chicken.y)
        score += 2
        highest_positions.append(score)
        timer = 0
    elif keyCode == DOWN:
        score -= 2
        print(chicken.x,chicken.y)
        timer = 0
        highest_positions.append(score)
        if chicken.y < 720:
            chicken.move_down()
    
def mousePressed(): #If mouse is pressed, restarts to the original screen
    global ending_mode, flag, is_running
    print(mouseX,mouseY)
    if ending_mode == True:
        ending_mode = False
        is_running = False
