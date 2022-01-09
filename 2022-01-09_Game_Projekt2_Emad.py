import pygame
import os
import random

# Basisvariablen
class Settings(object):
    window_height = 400
    window_width = 600
    title="Bubble"
    fps= 60
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_image = os.path.join(path_file, "imgs")
    path_sounds= os.path.join(path_file, "sounds")
    path_highscore= os.path.join(path_file, "score.txt")
    bubble_image="bubble.png"
    bubble_radius = 5
    bubble_time = 1000
    bubble_quantity= 8
    cursor_size = (25, 20)
    score=0


class Background(pygame.sprite.Sprite):
    def __init__(self, filename) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        pass


class Cursor(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.cursors =[
            pygame.image.load(os.path.join(Settings.path_image, 'cursor1.png')),
            pygame.image.load(os.path.join(Settings.path_image, 'cursor2.png'))]
        self.image = self.cursors[0]
        self.image = pygame.transform.scale(self.image, Settings.cursor_size)
        self.rect = self.image.get_rect()

    def select_cursor(self, cursor_no):        
        self.image = self.cursors[cursor_no]
        self.image = pygame.transform.scale(self.image, Settings.cursor_size)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, position):
        pygame.mouse.set_visible(False)
        self.rect = position

class Bubble(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, Settings.bubble_image)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (Settings.bubble_radius * 5, Settings.bubble_radius * 5))
        self.rect = self.image.get_rect()
        self.rect.center= (random.randint(15,Settings.window_width-15),random.randint(15,Settings.window_height -15)),
        pygame.mixer.Sound.play(game.sound_add_bubble)
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def check_window_collision(self):
        if self.rect.right>= Settings.window_width:
            game.gameover()
        if self.rect.bottom>= Settings.window_height:
            game.gameover()
        if self.rect.top <= 0:
            game.gameover()
        if self.rect.left<= 0:
            game.gameover()

    def update(self):
        self.check_window_collision()

class Timer(object):        
    def __init__(self, duration):
        self.duration = duration
        run=True
        if run:
            self.next_bubble = pygame.time.get_ticks()
        else:
            self.next_bubble = pygame.time.get_ticks() + self.duration

    def nextone(self):
        if pygame.time.get_ticks() > self.next_bubble:
            self.next_bubble = pygame.time.get_ticks() + self.duration
            return True
        return False

class Game(object):
    def __init__(self)->None:
        super().__init__()
        pygame.init()
        pygame.display.set_caption(Settings.title)

# um Redundanz zu vermeiden, habe ich dieselbe Schriftart-größe bei Gameover, Score und Heighscore benutzt
        self.font_pause = pygame.font.Font(pygame.font.get_default_font(), 52)
# um Redundanz zu vermeiden, habe ich Schriftart-größe bei restart benutzt
        self.font_scoure= pygame.font.Font(pygame.font.get_default_font(), 20)

        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.pause = False

        self.background = Background("background.jpg")
        self.bubbles = pygame.sprite.Group()
        self.cursor = Cursor()

        self.bubble_time=Timer(Settings.bubble_time)
        self.sound_add_bubble = pygame.mixer.Sound(os.path.join(Settings.path_sounds, "burst.mp3"))
        self.sound_kill_bubble = pygame.mixer.Sound(os.path.join(Settings.path_sounds, "plopp1.mp3"))

    def run(self):
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.draw()
            self.cursor.update(pygame.mouse.get_pos())
            if  self.pause == False and self.game_over == False:
                self.update()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
# Da mein Spiel noch nicht vollständig fertig ist, habe ich ESC-Button als Verlust"GAMEOVER"gesetzt
                if event.key == pygame.K_ESCAPE:
                    self.gameover()
                elif event.key == pygame.K_p:
                    self.pause = not self.pause
                if self.game_over == True:
                    if event.key == pygame.K_r:
                        self.restart()

            elif event.type == pygame.MOUSEBUTTONDOWN:
# Rechtsklick: pause - unpause
                if event.button == 3:
                    self.pause = not self.pause
                if self.pause:
                    return
# bei Linksklick innerhalb eine Bubble, wird sie zerplatzen
                if event.button == 1:
                    for bubble in self.bubbles:
                        if bubble.rect.collidepoint(event.pos):
                            bubble.kill()
                            pygame.mixer.Sound.play(game.sound_kill_bubble)
                            Settings.score += 5
                            break

# Bubbles hinzufügen
    def add_bubbles(self):
        if len(self.bubbles) < Settings.bubble_quantity:
            if self.bubble_time.nextone():
                self.bubbles.add(Bubble())

    def update(self):
        self.add_bubbles()
        self.bubbles.update()

# wenn Cursor auf Bubble, wird verändern
        cursor_on_bubble = False
        for bubble in self.bubbles.sprites():
            if bubble.rect.collidepoint(pygame.mouse.get_pos()):
                cursor_on_bubble = True
            if cursor_on_bubble:
                self.cursor.select_cursor(1)
            else:
                self.cursor.select_cursor(0)
         
    def draw(self):
        self.background.draw(self.screen)
        self.bubbles.draw(self.screen)
        if self.pause:
            self.pause_window()
        if self.game_over:
            self.gameover_window()
        self.cursor.draw(self.screen)
        text_score = self.font_scoure.render("Score: {0}".format(Settings.score), True, (0, 0, 0))
        self.screen.blit(text_score, dest=(10, Settings.window_height-25))
        pygame.display.flip()

# Pause-Fenster
    def pause_window(self):
        pause = pygame.Surface(self.screen.get_size())
        pause.set_alpha(200)
        self.screen.blit(pause, (0, 0))
        text_pause = self.font_pause.render("PAUSE", True, (255, 0, 0))
        text_pause_rect=text_pause.get_rect()
        text_pause_rect.center = (Settings.window_width // 2, Settings.window_height // 2)
        self.screen.blit(text_pause, text_pause_rect)

# Gameover-Fenster
    def gameover_window(self):
        gameover = pygame.Surface(self.screen.get_size())
        gameover.set_alpha(200)
        self.screen.blit(gameover, (0, 0))
        text_gameover = self.font_pause.render("GAME OVER", True, (255, 0, 0))
        text_gameover_rect=text_gameover.get_rect()
        text_gameover_rect.center = (Settings.window_width // 2, Settings.window_height // 2 +10)
        self.screen.blit(text_gameover, text_gameover_rect)

        score = pygame.Surface(self.screen.get_size())
        score.set_alpha(0)
        score.fill((0, 0, 0))
        self.screen.blit(score, (0, 0))
        text_score = self.font_pause.render("Score: {0}".format(Settings.score), True, (0, 0, 0))
        text_score_rect=text_score.get_rect()
        text_score_rect.center = (Settings.window_width // 2, Settings.window_height // 2 - 70)
        self.screen.blit(text_score, text_score_rect)

        highscore = pygame.Surface(self.screen.get_size())
        highscore.set_alpha(0)
        highscore.fill((0, 0, 0))
        self.screen.blit(highscore, (0, 0))
        text_highscore = self.font_pause.render("Highscore: {0}".format(self.get_highscore()), True, (0, 0, 0))
        text_highscore_rect=text_highscore.get_rect()
        text_highscore_rect.center = (Settings.window_width // 2, Settings.window_height // 2 - 140)
        self.screen.blit(text_highscore, text_highscore_rect)

        restart = pygame.Surface(self.screen.get_size())
        restart.set_alpha(0)
        restart.fill((0, 0, 0))
        self.screen.blit(restart, (0, 0))
        text_restart = self.font_scoure.render("To restart press \"r\"", True, (0, 255, 255))
        text_restart_rect=text_restart.get_rect()
        text_restart_rect.center = (Settings.window_width // 2, Settings.window_height // 2 + 100)
        self.screen.blit(text_restart, text_restart_rect)

# die höchste gespeicherte Score zu holen, setzen und speichern
    def get_highscore(self):
        with open(Settings.path_highscore) as txt:
            highscore = txt.read()
        return highscore

    def set_highscore(self,highscore):
        with open(Settings.path_highscore, 'w') as txt:
            txt.write(str(highscore))

    def save_highscore(self):
        if Settings.score > int(self.get_highscore()):
            self.set_highscore(Settings.score)

    def gameover(self):
        self.save_highscore()
        self.game_over = True

# Zur Widerholung des Spiels
    def restart(self):
        self.game_over=False
        for bubble in self.bubbles:
            bubble.kill() 
        Settings.score=0
        self.running = True
        self.run()
# Hauptprogramm starten
if __name__ == "__main__":
    os.environ["SDL_VIDEO_WINDOW_POS"] = "500, 50"
    game=Game()
    game.run()
