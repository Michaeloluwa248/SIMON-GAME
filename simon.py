import pygame
import numpy
import math
import random
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 155)
RED = (255, 0, 0)
DARKRED = (155, 0, 0)
YELLOW = (255, 255, 0)
DARKYELLOW = (155, 155, 0)
BG_COLOR = BLACK

# Game settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 500
FPS = 60
GAME_TITLE = "Simon Says"
BUTTON_SIZE = 200
ANIMATION_SPEED = 20
BEEP_HIGH = 880
BEEP_MEDIUM = 659
BEEP_LOW = 554
BEEP_VERY_LOW = 440

pygame.mixer.init()

# Class for game buttons
class Button:
    def __init__(self, x, y, colour):
        self.x, self.y = x, y
        self.colour = colour

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, BUTTON_SIZE, BUTTON_SIZE))

    def clicked(self, mouse_x, mouse_y):
        return self.x <= mouse_x <= self.x + BUTTON_SIZE and self.y <= mouse_y <= self.y + BUTTON_SIZE

# Class for handling game audio
class Audio:
    def __init__(self, frequency: int):
        # Generate sound data for a specific frequency
        duration = 0.5
        bits = 16
        sample_rate = 44100
        total_samples = int(round(duration * sample_rate))
        data = numpy.zeros((total_samples, 2), dtype=numpy.int16)
        max_sample = 2 ** (bits - 1) - 1
        for sample in range(total_samples):
            sample_time = float(sample) / sample_rate
            for channel in range(2):
                data[sample][channel] = int(round(max_sample * math.sin(2 * math.pi * frequency * sample_time)))
        self.sound = pygame.sndarray.make_sound(data)
        self.current_channel = None

    def play(self):
        # Play the sound using pygame mixer
        self.current_channel = pygame.mixer.find_channel(True)
        self.current_channel.play(self.sound)

# Class for Displaying Texts on Game Screen
class TextDisplay:
    def __init__(self, x, y, text):
        self.x, self.y = x, y
        self.text = text

    def draw(self, screen):
        # Draw UI text on the screen
        font = pygame.font.SysFont("Arial", 16)
        text = font.render(self.text, True, WHITE)
        screen.blit(text, (self.x, self.y))


class SimonGame:
    """
    Main game class and settings.
    """
    def __init__(self):
        # Initialize pygame, set up the display, and game attributes
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.beeps = [Audio(BEEP_HIGH), Audio(BEEP_MEDIUM), Audio(BEEP_LOW), Audio(BEEP_VERY_LOW)]
        self.flash_colours = [YELLOW, BLUE, RED, GREEN]
        self.pattern = []  # Stores the pattern of button flashes
        self.current_step = 0  # Tracks the current step in the player's input
        self.score = 0  # Keeps track of the player's score
        self.awaiting_player_input = False  # Indicates whether the game is expecting player input
        self.colours = [DARKYELLOW, DARKBLUE, DARKRED, DARKGREEN]
        self.high_score = self.get_high_score()

        # Initialize game buttons
        self.buttons = [
            Button(110, 50, DARKYELLOW),    # Top left button
            Button(330, 50, DARKBLUE),      # Top right button
            Button(110, 270, DARKRED),      # Bottom left button
            Button(330, 270, DARKGREEN),    # Bottom right button
        ]
    

    def empty_high_score_file(self):
        open('high_scores.txt', 'w').close()

    def get_high_score(self):
        # Read the high score from a file

        file_path = "high_scores.txt"

        if not os.path.exists(file_path):
            # Create an empty file if it doesn't exist
            with open(file_path, "w") as new_file:
                pass
        
        with open(file_path, "r") as file:
            
            try:
                score_str = file.readlines()[0]
            except IndexError:
                score_str = 0

            try:
                score = int(score_str)
            except ValueError:
                print(f"Error: '{score_str}' is not a valid integer.")
                score = 0  # fallback score; in case of error.
        return score

    def save_scores(self, new_score):
        # Save the player's score to the high scores file
        scores = self.get_top_scores()

        # Add the new score to the list
        scores.append(new_score)

        # Sort the scores in descending order
        scores.sort(reverse=True)

        # Save the top 10 scores
        with open("high_scores.txt", "w") as file:
            for score in scores[:10]:
                file.write(f"{score}\n")

    def new(self):
        # Reset game state for a new game
        self.awaiting_player_input = False
        self.pattern = []
        self.current_step = 0
        self.score = 0
        self.high_score = self.get_high_score()

    def events(self):
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if a button is clicked when the mouse is pressed
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.clicked(mouse_x, mouse_y):
                        self.clicked_button = button.colour

    def run(self):
        # Main game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.clicked_button = None
            self.events()
            self.draw()
            self.update()

    def update(self):
        # Update game logic
        if not self.awaiting_player_input:
            # Computer's turn: add a new step to the pattern
            pygame.time.delay(1000)
            self.pattern.append(random.choice(self.colours))
            for button in self.pattern:
                self.button_animation(button)
                pygame.time.wait(200)
            self.awaiting_player_input = True

        else:
            # Player's turn: check if the clicked button matches the pattern
            if self.clicked_button and self.clicked_button == self.pattern[self.current_step]:
                self.button_animation(self.clicked_button)
                self.current_step += 1

                if self.current_step == len(self.pattern):
                    # Player successfully matched the pattern
                    self.score += 1
                    self.awaiting_player_input = False
                    self.current_step = 0

            elif self.clicked_button and self.clicked_button != self.pattern[self.current_step]:
                # Player made a mistake, game over
                self.game_over_animation()
                self.save_scores(self.score)
                self.playing = False

    
    def button_animation(self, colour):
        """
        Flash animation for a button.
        """

        # Find the corresponding sound, flash colour, and button for the specified colour
        for i in range(len(self.colours)):
            if self.colours[i] == colour:
                sound = self.beeps[i]
                flash_colour = self.flash_colours[i]
                button = self.buttons[i]

        # Create a copy of the screen to restore it after the animation
        original_surface = self.screen.copy()

        # Create a transparent surface for the flashing effect
        flash_surface = pygame.Surface((BUTTON_SIZE, BUTTON_SIZE))
        flash_surface = flash_surface.convert_alpha()
        r, g, b = flash_colour

        # Play the corresponding sound
        sound.play()

        # Iterate through alpha values for the flashing effect
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, ANIMATION_SPEED * step):
                # Update the screen with the original surface
                self.screen.blit(original_surface, (0, 0))

                # Fill the flash surface with the specified colour and alpha value
                flash_surface.fill((r, g, b, alpha))

                # Blit the flash surface onto the screen at the button's position
                self.screen.blit(flash_surface, (button.x, button.y))

                # Update the display and control the frame rate
                pygame.display.update()
                self.clock.tick(FPS)

        # Restore the original surface after the animation
        self.screen.blit(original_surface, (0, 0))

    def game_over_animation(self):
        """
        Display a game over screen with "Game Over" text and a restart button.
        """

        # Create a copy of the screen to restore it after the animation
        original_surface = self.screen.copy()

        # Create a transparent surface for the flashing effect
        flash_surface = pygame.Surface((self.screen.get_size()))
        flash_surface = flash_surface.convert_alpha()

        # Play beeps to add audio effect to the animation
        for beep in self.beeps:
            beep.play()

        # Set the initial color to white
        r, g, b = WHITE

        # Display "Game Over" text
        font = pygame.font.Font(None, 36)
        text = font.render("Game Over", True, WHITE)
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(original_surface, (0, 0))
        self.screen.blit(text, text_rect)
        pygame.display.update()

        # Display restart button
        restart_button = pygame.Rect(self.screen.get_width() // 2 - 50, text_rect.bottom + 20, 100, 40)
        pygame.draw.rect(self.screen, WHITE, restart_button)
        restart_text = font.render("Restart", True, BLACK)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        pygame.display.update()

        restart_button_clicked = False

        while not restart_button_clicked:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_button.collidepoint(mouse_pos):
                        restart_button_clicked = True

            # Update the display and control the frame rate
            pygame.display.update()
            self.clock.tick(FPS)

        # Restore the original surface after the animation
        self.screen.blit(original_surface, (0, 0))


    def draw(self):
        # Draw game elements on the screen
        self.screen.fill(BG_COLOR)
        TextDisplay(170, 20, f" {str(self.score)}").draw(self.screen)

        # Display current score
        TextDisplay(20, 20, "Current Score:").draw(self.screen)
        TextDisplay(20, 40, str(self.score)).draw(self.screen)

        # Display top 10 scores
        TextDisplay(470, 20, "Top 10 Scores:").draw(self.screen)
        
        for i, score in enumerate(self.get_top_scores()):
            TextDisplay(540, 40 + i * 20, f"{i + 1}. {score}").draw(self.screen)

        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.update()

    def get_top_scores(self):
        # Read the top 10 scores from a file
        scores = []
        with open("high_scores.txt", "r") as file:
            for line in file:
                score = line.strip()
                try:
                    score = int(score)
                except ValueError:
                    score = 0  # or any default value you prefer
                scores.append(score)
                if len(scores) == 10:
                    break

        # Fill remaining slots with 0
        while len(scores) < 10:
            scores.append(0)

        return scores

if __name__ == "__main__":
    # Run the game
    game = SimonGame()
    while True:
        game.new()
        game.run()