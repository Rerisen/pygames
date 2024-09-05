import pygame
import random
import time
import sqlite3

pygame.init()

# Const
DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 290
BLOCK_SIZE = 100
TIME_SPEED_DELAY = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Display
game_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("RoadGame")
icon = pygame.image.load('picon.png')
pygame.display.set_icon(icon)

# Font
font = pygame.font.SysFont('Arial', 27)


class Database:
    def __init__(self, db_name='game_scores.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                               (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)''')
        self.conn.commit()

    def insert_score(self, name, score):
        self.cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (name, score))
        self.conn.commit()

    def get_top_scores(self, limit=5):
        self.cursor.execute('SELECT name, score FROM scores ORDER BY score DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

def rand_game_coords():
    return [random.choice((100, 200, 300, 400)), random.choice((291, 295, 300, 305, 310, 320))]

def rand_back_coords():
    return [random.choice((0, 500)), random.choice((290, 310, 320, 330, 340))]

def rand_speed():
    return random.choice((2.2, 2.4, 2.6, 2.8))


class GameObject:
    def __init__(self, image_path, x, y, speed=0, back=False):
        self.image = pygame.image.load(image_path)
        self.x = x
        self.y = y
        self.speed = speed
        self.back = back
    def change_speed(self):
        self.speed += 0.1

    def draw(self, display):
        display.blit(self.image, (self.x, self.y))

    def move(self):
        self.y -= self.speed
        if self.y <= -300:
            self.reset_position()

    def reset_position(self):
        if self.back == True:
            self.x, self.y = rand_back_coords()
        else:
            self.x, self.y = rand_game_coords()

    def reset_back_position(self):
        self.x, self.y = rand_game_coords()


class Player(GameObject):
    def __init__(self, x, y):
        super().__init__('prunninminiggirl.png', x, y)
        self.right_image = pygame.image.load('prunninminiggirl.png')
        self.left_image = pygame.image.load('prunninminiggirlleft.png')
        self.right = True

    def toggle_image(self):
        self.right = not self.right
        self.image = self.right_image if self.right else self.left_image

class Game:
    def __init__(self):
        self.player = Player(200, 0)
        self.cars = [GameObject('pcar.png', *rand_game_coords(), rand_speed()),
                     GameObject('pcar2.png', *rand_game_coords(), rand_speed())]
        self.gift = GameObject('pgift.png', *rand_game_coords(), 1.5)
        self.background_elements = [GameObject('pcristmastree.png', *rand_back_coords(), 1.5, True),
                                    GameObject('pcristmastree.png', *rand_back_coords(), 1.5, True),
                                    GameObject('psnowflake.png', *rand_back_coords(), 2, True),
                                    GameObject('psnowflake.png', *rand_back_coords(), 2.2, True),
                                    GameObject('psnowflake.png', *rand_back_coords(), 2.4, True)]
        self.score = 0
        self.run_game = False
        self.t = 0
        self.girl_change_speed = 20
        self.db = Database()
        self.nickname = ""
        self.input_active = False
        self.input_box = pygame.Rect(200, 100, 140, 35)
        self.start_button = pygame.Rect(250, 150, 100, 50)


    def check_score(self):
        return self.score > 30

    def winning_pic(self):
        self.image_down('victory.png')
    def losing_pic(self):
        self.image_down('losing.png')

    def message_to_screen(self, msg, color, x, y):
        screen_text = font.render(msg, True, color)
        game_display.blit(screen_text, [x, y])

    def collision_checking(self, obj1, obj2):
        return obj1.x == obj2.x and -50 < obj2.y <= 100

    def car_collision_checking(self, obj1, obj2):
        return obj1.x == obj2.x and ((obj1.y - obj2.y) < 100 or (obj2.y - obj1.y) < 100) and (obj1.y > DISPLAY_HEIGHT-10 or obj2.y > DISPLAY_HEIGHT-10)


    def check_collisions(self):
        for car in self.cars:
            if self.collision_checking(self.player, car):
                self.end_game()

        if self.collision_checking(self.player, self.gift):
            self.gift.reset_position()
            self.score += 1
            if self.score%10 == 0:
                self.girl_change_speed -= 2
            for element in self.cars:
                element.change_speed()
            for element in self.background_elements:
                element.change_speed()
            self.gift.change_speed()


        while self.car_collision_checking(self.cars[0], self.cars[1]):

            if self.cars[0].y > self.cars[1].y:
                self.cars[0].x = 200 if self.cars[0].x == 100 else 100
            else:
                self.cars[1].x = 200 if self.cars[1].x == 100 else 100

    def sorttrees(self):
        pass



    def update(self):
        game_display.fill(WHITE)
        game_display.blit(pygame.image.load('proad.png'), (100, 0))

        self.background_elements.sort(key=lambda obj: obj.y)
        for element in self.background_elements:
            element.draw(game_display)
            element.move()

        self.gift.draw(game_display)
        self.gift.move()

        for car in self.cars:
            car.draw(game_display)
            car.move()

        self.player.draw(game_display)
        self.t += 1

        if self.t % self.girl_change_speed == 0:
            self.player.toggle_image()


        self.message_to_screen(f"Score: {self.score}", BLACK, 7, 7)
        pygame.display.update()
        pygame.time.delay(TIME_SPEED_DELAY)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.player.x > 100:
                    self.player.x -= 100
                elif event.key == pygame.K_RIGHT and self.player.x < 400:
                    self.player.x += 100

    def story_image(self, image):
        game_display.blit(pygame.image.load(image), (0, 0))
        pygame.display.update()
        time.sleep(2)
    def image_down(self, image):
        for i in range(160):
            game_display.blit(pygame.image.load(image), (0, -i))
            pygame.display.update()
            time.sleep(0.01)

    def start_game(self):
        self.story_image('p1.png')
        print(1)
        self.story_image('p2.png')
        game_display.blit(pygame.image.load('p3.png'), (0, -80))
        self.message_to_screen('I have to help Santa', WHITE, 340, 50)
        self.message_to_screen('and catch the presents!', WHITE, 340, 80)
        pygame.display.update()
        time.sleep(2)
        game_display.blit(pygame.image.load('arrows.png'), (0,-80))
        self.message_to_screen('Use arrows to move!', BLACK , 200, 30)
        pygame.display.update()
        time.sleep(2)


    def end_game(self):
        time.sleep(2)
        game_display.fill(BLACK)
        self.message_to_screen(f"Game over! Score: {self.score}", WHITE, 200, 150)
        pygame.display.update()
        time.sleep(2)
        self.story_image('end1.png')
        self.story_image('end2.png')
        self.story_image('end4.png')
        self.story_image('end5.png')
        if self.check_score():
            self.winning_pic()
        else:
            self.losing_pic()
        time.sleep(2)
        self.db.insert_score(self.nickname, self.score)
        self.display_top_scores()
        self.run_game = False

    def display_top_scores(self):
        top_scores = self.db.get_top_scores()
        game_display.fill(BLACK)
        y_offset = 50
        self.message_to_screen("Top 5 Players:", WHITE, 200, y_offset)
        for i, (name, score) in enumerate(top_scores):
            y_offset += 30
            self.message_to_screen(f"{name}.......... {score}", WHITE, 200, y_offset)
        pygame.display.update()
        time.sleep(5)

    def start_screen(self):
        while not self.run_game:
            game_display.fill(WHITE)
            self.message_to_screen("Enter your nickname:", BLACK, 200, 50)
            pygame.draw.rect(game_display, BLACK, self.input_box, 2)
            txt_surface = font.render(self.nickname, True, BLACK)
            game_display.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
            self.input_box.w = max(200, txt_surface.get_width() + 10)
            pygame.draw.rect(game_display, BLACK, self.start_button)
            self.message_to_screen("START", WHITE, self.start_button.x + 12, self.start_button.y + 8)
            self.message_to_screen("Can you get more than 30?", BLACK, 180, 250)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.input_active = True
                    else:
                        self.input_active = False
                    if self.start_button.collidepoint(event.pos) and self.nickname:
                        self.start_game()
                        self.run_game = True
                if event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.start_game()
                            self.run_game = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.nickname = self.nickname[:-1]
                        else:
                            self.nickname += event.unicode


    def run(self):
        self.start_screen()
        while self.run_game:
            self.handle_events()
            self.update()
            self.check_collisions()
        self.db.close()


game = Game()
game.run()
pygame.quit()
