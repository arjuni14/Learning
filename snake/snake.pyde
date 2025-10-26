RESOLUTION = 600
ROWS = 20
COLS = 20
TOTAL = ROWS * COLS
import random
WIDTH = RESOLUTION / ROWS
HEIGHT = RESOLUTION / COLS
game_running = True

class Game:
    def __init__(self):
        self.board_width = RESOLUTION // COLS #Game Board Dimensions
        self.board_height = RESOLUTION // ROWS
        self.score = 0
        self.TEXTSIZE = 15
        
    def show_score(self):
        fill(0)
        textSize(self.TEXTSIZE) 
        text("The score is " + str(self.score), 10, 12) #Displays the score
class SnakeElement:
    def __init__(self, x, y, size, type):
        self.x = x
        self.y = y
        self.size = size
        self.type = type #Serves to differentiate colors for snake, apple, and banana
        
    def display():
        pass

class Snake():
    def __init__(self):
        self.img_left = loadImage(os.getcwd() + "/snake_images/head_left.png")
        self.img_right = loadImage(os.getcwd() + "/snake_images/head_right.png")
        self.img_up = loadImage(os.getcwd() + "/snake_images/head_up.png")
        self.img_down = loadImage(os.getcwd() + "/snake_images/head_down.png")
        self.img = self.img_left #Originally set to img_left
        self.snake_parts = [] #Empty List to store elements
        self.head = SnakeElement(RESOLUTION // 2, RESOLUTION // 2, 30, "snake")  
        self.snake_parts.append(self.head)
        self.tail1 = SnakeElement(self.head.x, self.head.y, 30, "snake")
        self.snake_parts.append(self.tail1)
        self.tail2 = SnakeElement(self.head.x, self.head.y, 30, "snake")
        self.snake_parts.append(self.tail2)
        self.velo = [0, 0]

    def display(self):
        for part in self.snake_parts[1:]: #Indexes after the head
            if part.type == "snake": #This changes color based on what it ate
                fill(80, 153, 32)
            elif part.type == "apple":
                fill(173,48,32)
            elif part.type == "banana":
                fill(251,226,76)
            ellipse(part.x + 15, part.y + 15, part.size, part.size)  
        image(self.img, self.head.x,self.head.y)  #Initialized afterward so that the ellipses don't overlap on the head
        

    def move(self):
        for i in range(len(self.snake_parts) - 1, 0, -1): #It iterates from the end to the second part and in reverse order
            self.snake_parts[i].x = self.snake_parts[i - 1].x #sets the x coordinate
            self.snake_parts[i].y = self.snake_parts[i - 1].y
        self.head.x += self.velo[0] * self.head.size #Updates based on velocity
        self.head.y += self.velo[1] * self.head.size

    def move_left(self):
        if self.velo != [1, 0]: #This makes sure the condition is not already right 
            self.velo = [-1, 0]
            self.img = self.img_left #This ensures that the image cannot go to the right
    
    def move_right(self):
        if self.velo != [-1, 0]:
            self.velo = [1, 0]
            self.img = self.img_right #Override the image here
        
    def move_up(self):
        if self.velo != [0, 1]:
            self.velo = [0, -1]  
            self.img = self.img_up
        
    def move_down(self):
        if self.velo != [0, -1]:
            self.velo = [0, 1]  
            self.img = self.img_down
            
    def collision(self, fruit_x, fruit_y):
        if self.head.x == fruit_x and self.head.y == fruit_y : #Checks that the head does not equal the fruit
                return False
        for parts in self.snake_parts[3:]: #This checks after the initial snake since the initial snake(head + 2 ellipses) will not hit each other
            if parts.x == self.head.x and parts.y == self.head.y: #Collision condition
                return True
        return False

class Fruit(SnakeElement): #Inheritance
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.cols = COLS
        self.rows = ROWS
        self.img_apple = loadImage(os.getcwd() + "/snake_images/apple.png")
        self.img_banana = loadImage(os.getcwd() + "/snake_images/banana.png")
        self.is_displayed = False

    def generate_fruit(self, snake_parts): #snake_parts allow us to access the snake body parts in the snake class
        if not self.is_displayed: #Checks if the fruit is not displayed
            while True:
                self.x = int(random.randrange(self.cols)) * self.size #Randomly selects coordinates
                self.y = int(random.randrange(self.rows)) * self.size
                self.new_fruit = random.choice([self.img_apple, self.img_banana]) #Randomly selects a banana or apple from the list
                same_position = False #Checks for overlapping with the tail or another part of the snake
                for part in snake_parts[1:]: #Everything after the head
                    if part.x == self.x and part.y == self.y:
                        same_position = True 
                        break
                if not same_position: #This shows the fruit is ready to be displayed
                    self.is_displayed = True
                    break
                
    def display(self):
        if self.is_displayed:
            image(self.new_fruit, self.x, self.y, self.size, self.size) #Generates the image

    def eat_fruit(self, snake_x, snake_y):
        if self.x == snake_x and self.y == snake_y:
            self.is_displayed = False #This won't display the same fruit again
            return True
        return False
            
basic = Game()
snake = Snake()
fruit = Fruit(RESOLUTION // 2, RESOLUTION // 2, 30)


def setup():
    size(RESOLUTION, RESOLUTION)

def draw():
    global game_running
    if game_running and frameCount % 12 == 0:
        background(205) #Clears the screen by redrawing the background
        snake.move()  
        snake.display()
        fruit.generate_fruit(snake.snake_parts) 
        fruit.display()
        if fruit.eat_fruit(snake.head.x, snake.head.y): 
            if fruit.new_fruit == fruit.img_apple: 
                new_tail = SnakeElement(snake.head.x, snake.head.y, 30, "apple")
                snake.snake_parts.append(new_tail) #Appends a new tail everything it grows
                basic.score += 1 #Increase score
            elif fruit.new_fruit == fruit.img_banana:
                new_tail = SnakeElement(snake.head.x, snake.head.y, 30, "banana")
                snake.snake_parts.append(new_tail)
                basic.score += 1 
        if len(snake.snake_parts) >= TOTAL: #Ensures that the snake does not exceed the total number of columns and rows
            textSize(35)
            text("GAME OVER", 212, 313)
            game_running = False
        if (snake.head.x < 0 or snake.head.x >= RESOLUTION or snake.head.y < 0 or snake.head.y >= RESOLUTION) or snake.collision(fruit.x, fruit.y) == True:
            textSize(35) #The code above ensures that the snake does not go off the screen and does not collide with itself
            text("GAME OVER", 212, 313)
            game_running = False
            snake.snake_parts = [] #Reset the list
        basic.show_score()

def keyPressed():
    if keyCode == LEFT:
        snake.move_left()
    elif keyCode == RIGHT:
        snake.move_right()
    elif keyCode == UP:
        snake.move_up()
    elif keyCode == DOWN:
        snake.move_down()
        
def mousePressed():
    global game_running, basic, snake, fruit
    if game_running == False:
        game_running = True #Resets the game
        basic = Game() #Recall all the functions
        snake = Snake()
        fruit = Fruit(RESOLUTION // 2, RESOLUTION // 2, 30)
        
        
        
