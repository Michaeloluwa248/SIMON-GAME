import pytest
from simon_main import Button, SimonGame as Game, Audio, TextDisplay, DARKBLUE, DARKGREEN, DARKRED, DARKYELLOW

# Helper function for checking button attributes
def assert_button_attributes(button, expected_x, expected_y, expected_colour):
    assert button.x == expected_x, f"Expected x: {expected_x}, got {button.x}"
    assert button.y == expected_y, f"Expected y: {expected_y}, got {button.y}"
    assert button.colour == expected_colour, f"Expected colour: {expected_colour}, got {button.colour}"

def test_button_clicked():
    button = Button(110, 50, DARKYELLOW)
    assert button.clicked(120, 60)
    assert not button.clicked(90, 40)

def test_game_initialization():
    game = Game()
    
    game.empty_high_score_file() # Prepares text file for testing.

    assert game.pattern == []
    assert game.current_step == 0
    assert game.score == 0
    assert game.get_high_score() == 0
    assert not game.awaiting_player_input

# Integration Testing
def test_game_update_integration():
    game = Game()
    game.pattern = [DARKYELLOW, DARKBLUE, DARKRED]
    game.current_step = 0
    game.clicked_button = DARKYELLOW
    game.update()
    assert game.current_step == 0

def test_game_buttons_initialization():
    game = Game()
    assert len(game.buttons) == 4
    expected_button_data = [
        (110, 50, DARKYELLOW),
        (330, 50, DARKBLUE),
        (110, 270, DARKRED),
        (330, 270, DARKGREEN),
    ]

    for i, button in enumerate(game.buttons):
        expected_x, expected_y, expected_colour = expected_button_data[i]
        assert_button_attributes(button, expected_x, expected_y, expected_colour)

# Test writing and reading from file
def test_save_and_read_high_score():
    game = Game()
    game.save_scores(4298859)
    assert game.get_high_score() == 4298859

if __name__ == "__main__":
    pytest.main()