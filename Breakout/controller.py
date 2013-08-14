# controller.py
# Rene Zhang (rz99)
# December 1, 2012
# Extensions:
# Added a 3 second countdown for serving the ball.
# Added the ability to try again after either victory or game over.
# Added a lives indicator to the bottom left.
# Added a score indicator to the top left.
# Added a pause button in the bottom right.
# Added a combo system.
# Added a better menu screen.
# Added better collisions and movement. 
# Added a high score list. 

"""Controller module for Breakout

This module contains a class and global constants for the game Breakout.
Unlike the other files in this assignment, you are 100% free to change
anything in this file. You can change any of the constants in this file
(so long as they are still named constants), and add or remove classes."""
import colormodel
import random
import os.path
from graphics import *

# CONSTANTS

# Width of the game display (all coordinates are in pixels)
GAME_WIDTH  = 480
# Height of the game display
GAME_HEIGHT = 620

# Width of the paddle
PADDLE_WIDTH = 58
# Height of the paddle
PADDLE_HEIGHT = 11
# Distance of the (bottom of the) paddle up from the bottom
PADDLE_OFFSET = 30

# Horizontal separation between bricks
BRICK_SEP_H = 5
# Vertical separation between bricks
BRICK_SEP_V = 4
# Height of a brick
BRICK_HEIGHT = 8
# Offset of the top brick row from the top
BRICK_Y_OFFSET = 70

# Number of bricks per row
BRICKS_IN_ROW = 10
# Number of rows of bricks, in range 1..10.
BRICK_ROWS = 10
# Width of a brick
BRICK_WIDTH = GAME_WIDTH / BRICKS_IN_ROW - BRICK_SEP_H

# Diameter of the ball in pixels
BALL_DIAMETER = 18

# Number of attempts in a game
NUMBER_TURNS = 3

# Basic game states
# Game has not started yet
STATE_INACTIVE = 0
# Game is active, but waiting for next ball
STATE_PAUSED   = 1
# Ball is in play and being animated
STATE_ACTIVE   = 2
# Game is over, deactivate all actions
STATE_COMPLETE = 3

# ADD MORE CONSTANTS (PROPERLY COMMENTED) AS NECESSARY

# List of the possible colors of the bricks in order
BRICK_COLORS = [colormodel.RED, colormodel.ORANGE, colormodel.YELLOW, colormodel.GREEN, colormodel.CYAN]
# Number of rows of bricks per color
BRICK_COLOR_ROWS = 2

# Base score gain per brick
BRICK_SCORE = 50
# Base score increase per combo
COMBO_SCORE = 10

# Size of the pause button
PAUSE_SIZE = 24
# Size of the highscore button
SCORE_SIZE = 24

# Color of the score
COLOR_SCORE = colormodel.BLUE
# Color of the lives
COLOR_LIVES = colormodel.BLUE

# Offset of the welcome message from top
OFFSET_WELCOME = 200
# Offset of the start message from the bottom
OFFSET_START = 150
# Offset of the high score screen
OFFSET_SCORE = 100

# Font size for welcome message
FONT_WELCOME = 30
# Font size for start message
FONT_START = 20
# Font size for countdown message
FONT_COUNTDOWN = 20
# Font size for game over message
FONT_END = 24
# Font size for score
FONT_SCORE = 14
# Font size for lives
FONT_LIVES = 14
# Font size for the high score screen
FONT_HIGHSCORE = 24

# Path to the current directory
PATH = os.path.dirname(__file__)

# CLASSES
class Breakout(GameController):
    """Instance is the primary controller for Breakout.

    This class extends GameController and implements the various methods
    necessary for running the game.

        Method initialize starts up the game.

        Method update animates the ball and provides the physics.

        The on_touch methods handle mouse (or finger) input.

    The class also has fields that provide state to this controller.
    The fields can all be hidden; you do not need properties. However,
    you should clearly state the field invariants, as the various
    methods will rely on them to determine game state."""
    # FIELDS.

    # Current play state of the game; needed by the on_touch methods
    # Invariant: One of STATE_INACTIVE, STATE_PAUSED, STATE_ACTIVE
    _state  = STATE_INACTIVE

    # List of currently active "bricks" in the game.
    #Invariant: A list of  objects that are instances of GRectangle (or a
    #subclass) If list is  empty, then state is STATE_INACTIVE (game over)
    _bricks = []

    # The player paddle
    # Invariant: An object that is an instance of GRectangle (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over)
    _paddle = None

    # The ball to bounce about the game board
    # Invariant: An object that is an instance of GEllipse (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over) or
    # STATE_PAUSED (waiting for next ball)
    _ball = None

    # ADD MORE FIELDS (AND THEIR INVARIANTS) AS NECESSARY

    # Whether the user has paused or not
    # Invariant: A boolean
    _state_paused = False

    # The message in the welcome screen of the game
    # Invariant: A list of objects that are instances of GLabel (or a subclass)
    # If list is empty, then state is not STATE_INACTIVE
    _m_welcome = []
    
    # The message used to indicate how much time left until a new ball
    # Invariant: An object that is an instance of GLabel (or a subclass)
    # Also can be None; if None, then the game is not serving a new ball
    _m_countdown = None

    # The message used to indicate the end of a game
    # Invariant: An object that is an instance of GLabel (or a subclass)
    # Also can be None; if None, then state is not STATE_COMPLETE
    _m_end = None

    # The message used to indicate the number of lives the player has left
    # Invariant: A list of objects that are instances of GObject (or a subclass)
    # If list is empty, then state is STATE_INACTIVE
    _m_lives = []

    # The message used to indicate the score of the player
    # Invariant: An object that is an instance of GLabel (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE
    _m_score = None

    # The icon used to indicate whether the game is paused or not
    # Invariant: An object that is an instance of GImage (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE
    _m_pause = None

    # The text used to display the high score screen
    # Invariant: A list of objects that are instances of GObject (or a subclass)
    # If list is empty, then state is not STATE_INACTIVE
    _m_highscore = []

    # The offset from the left side of the paddle where the user previously clicked
    # Invariant: An positive float <= PADDLE_WIDTH
    # Also can be None; if None, then paddle is currently not in motion
    _anchor = None

    # The location where the mouse was pressed down.
    # Invariant: A tuple of floats
    # Also can be None; if None, then the mouse is not being held down 
    _press = None

    # The x-coordinate of the mouse during the previous moment when its pressed down.
    # Invariant: A float that is >= 0
    # Also can be None; if None, then the mouse is not being held down
    _prev = None

    # The high scores
    # Invariant a list of integers
    _highscore = []

    # The "velocity" of the paddle currently
    # Invariant: A float
    _vel = 0

    # The amount of balls left available to the player
    # Invariant: An integer >= 0 and < 100
    _lives = 0

    # The score of the player
    # Invariant: An integer >= 0
    _score = 0

    # The combo counter of the player
    # Increases every time the ball hits a brick
    # Resets to 0 when ball hits the paddle.
    # Invariant: An integer >= 0
    _combo = 0

    # METHODS

    def initialize(self):
        """Initialize the game state.

        Initialize any state fields as necessary to satisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game.
        Also initializes the high scores."""
        title = GLabel(text = 'Breakout', font_size = FONT_WELCOME, bold = True)
        title.halign = 'center'
        title.valign = 'middle'
        title.center = (GAME_WIDTH/2, GAME_HEIGHT - OFFSET_WELCOME)
        start = GLabel(text = 'Press to Start', font_size = FONT_START)
        start.halign = 'center'
        start.valign = 'middle'
        start.center = (GAME_WIDTH/2, OFFSET_START)
        self._m_welcome.append(title)
        self._m_welcome.append(start)
        self.view.add(title)
        self.view.add(start)
        self._state = STATE_INACTIVE
        self._init_highscore()

    def update(self, dt):
        """Animate a single frame in the game.

        This is the method that does most of the work.  It moves the ball, and
        looks for any collisions.  If there is a collision, it changes the
        velocity of the ball and removes any bricks if necessary. Score is
        added every time a ball collides with a brick. 

        This method may need to change the state of the game.  If the ball
        goes off the screen, change the state to either STATE_PAUSED (if the
        player still has some tries left) or STATE_COMPLETE (the player has
        lost the game).  If the last brick is removed, it needs to change
        to STATE_COMPLETE (game over; the player has won).

        Precondition: dt is the time since last update (a float).  This
        parameter can be safely ignored."""
        if self._state == STATE_ACTIVE and not self._state_paused:
            self._ball.move()
            self._bounding()
            collision = self._get_colliding_object()
            if collision is not None:
                if collision[0] is self._paddle:
                    self._paddle_collision(collision[1])
                if collision[0] in self._bricks:
                    self._brick_collision(collision[0],collision[1])
            if self._ball.y < 0:
                self._combo = 0
                self._death()
            if len(self._bricks) == 0:
                self._game_end(1)

    def on_touch_down(self,view,touch):
        """Respond to the mouse (or finger) being pressed (but not released)

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should
        check if the user clicked inside the paddle and begin movement of the
        paddle.  Otherwise, if it is one of the other states, it moves to the
        next state as appropriate. If state is STATE_INACTIVE or STATE_COMPLETE,
        then this method should create the bricks and the paddle and start the
        countdown for serving the ball. This also draws the other messages.
        This method also records the last location pressed.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        self._press = (touch.x, touch.y)
        if self._state == STATE_INACTIVE or self._state == STATE_COMPLETE:
            if self._m_highscore is None or (self._m_highscore[0].source == 'scores.png' and not self._m_highscore[0].collide_point(touch.x, touch.y)):
                self._reset()
                self._state_paused = False
                self._lives = NUMBER_TURNS - 1
                self._score = 0
                self._combo = 0
                self._state = STATE_PAUSED
                self._setup()
                self._draw()
                self._new_ball()
        if self._state == STATE_ACTIVE or self._state == STATE_PAUSED:
            self._prev = touch.x
            if self._paddle.collide_point(touch.x,touch.y):
                self._anchor = touch.x - self._paddle.x

    def on_touch_move(self,view,touch):
        """Respond to the mouse (or finger) being moved.

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should move
        the paddle. The distance moved should be the distance between the
        previous touch event and the current touch event. For all other
        states, this method is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        if self._state == STATE_ACTIVE or self._state == STATE_PAUSED:
            if self._prev is not None:
                self._vel = (touch.x - self._prev) / 50.0
                self._vel = max(self._vel,-2.5)
                self._vel = min(self._vel,2.5)
                self._prev = touch.x
            if self._anchor is not None and not self._state_paused:
                new_x = touch.x - self._anchor
                new_x = max(new_x, 0)
                new_x = min(new_x, GAME_WIDTH - PADDLE_WIDTH)
                self._paddle.x = new_x

    def on_touch_up(self,view,touch):
        """Respond to the mouse (or finger) being released

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should
        stop moving the paddle. For all other states, it is ignored.
        This method also checks if the player has pressed the pause icon
        and then changes the _state_paused accordingly. This also sets the
        variable recording the previous location of the mouse to None.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        if self._state == STATE_ACTIVE or self._state == STATE_PAUSED:
            self._anchor = None
            if self._m_pause.collide_point(self._press[0], self._press[1]):
                if self._m_pause.collide_point(touch.x, touch.y):
                    if self._state_paused:
                        self._state_paused = False
                        self._m_pause.source = 'pause.png'
                    else:
                        self._state_paused = True
                        self._m_pause.source = 'play.png'
            self._vel = 0
            self._prev = None
        if self._state == STATE_INACTIVE:
            if self._m_highscore[0].collide_point(self._press[0], self._press[1]):
                if self._m_highscore[0].collide_point(touch.x, touch.y):
                    self._draw_highscore()
        self._press = None

    # ADD MORE HELPER METHODS (PROPERLY SPECIFIED) AS NECESSARY

    def _reset(self):
        """Resets and removes all messages and objects on the screen.
        
        This is used to prepare for a new game. This method removes all messages
        and objects on the screen."""
        
        if self._state == STATE_INACTIVE:
            self.view.remove(self._m_welcome[0])
            self.view.remove(self._m_welcome[1])
            self._m_welcome = None
            self.view.remove(self._m_highscore[0])
            self._m_highscore = None
        if self._state == STATE_COMPLETE:
            self.view.remove(self._m_end)
            self._m_end = None
            self.view.remove(self._paddle)
            self._paddle = None
            for brick in self._bricks:
                self.view.remove(brick)
            self._bricks = []
            for obj in self._m_lives:
                self.view.remove(obj)
            self._m_lives = []
            self.view.remove(self._m_score)
            self._m_score = None
            self.view.remove(self._m_pause)
            self._m_pause = None

    def _setup(self):
        """Sets up the the grid of bricks and the paddle on the playing board.
        
        Creates BRICK_ROWS number of rows of BRICKS_IN_ROW bricks.
        The bricks are GRectangle objects and are initialized in a grid
        and are added to the view. The colors of the bricks are RED, ORANGE,
        YELLOW, GREEN, CYAN, respectively for every two rows.
        Also creates a BLACK paddle centered and offset PADDLE_OFFSET from the
        bottom of the game window."""
        for r in range(BRICK_ROWS):
            for c in range(BRICKS_IN_ROW):
                brick = GRectangle()
                brick.pos = (c*BRICK_WIDTH + c*BRICK_SEP_H + BRICK_SEP_H/2, GAME_HEIGHT - BRICK_Y_OFFSET - r*BRICK_HEIGHT - r*BRICK_SEP_V)
                brick.size = (BRICK_WIDTH, BRICK_HEIGHT)
                brick.linecolor = BRICK_COLORS[r % (5*BRICK_COLOR_ROWS) / 2]
                brick.fillcolor = BRICK_COLORS[r % (5*BRICK_COLOR_ROWS) / 2]
                self.view.add(brick)
                self._bricks.append(brick)
        paddle = GRectangle()
        paddle.size = (PADDLE_WIDTH, PADDLE_HEIGHT)
        paddle.y = PADDLE_OFFSET
        paddle.center_x = GAME_WIDTH/2
        paddle.linecolor = colormodel.BLACK
        paddle.fillcolor = colormodel.BLACK
        self.view.add(paddle)
        self._paddle = paddle

    def _init_highscore(self):
        """Initializes the highscores.
        
        Reads information from the highscores text file and initializes
        all of the high scores, along with the objects for the high score
        screen."""
        icon = GImage(source = 'scores.png')
        icon.size = (SCORE_SIZE, SCORE_SIZE)
        icon.center = (GAME_WIDTH - 3 - SCORE_SIZE/2, GAME_HEIGHT - 3 - SCORE_SIZE/2)
        self._m_highscore.append(icon)
        self.view.add(icon)
        title = GLabel(text = 'High Scores', font_size = FONT_HIGHSCORE, bold = True)
        title.halign = 'center'
        title.valign = 'middle'
        title.center = (GAME_WIDTH/2, GAME_HEIGHT - OFFSET_SCORE)
        self._m_highscore.append(title)
        f = open(PATH + '\highscores.txt')
        for line in f:
            line = int(line.strip())
            self._highscore.append(line)
            score = GLabel(text = '\n' + str(self._highscore[-1]), font_size = FONT_HIGHSCORE)
            score.halign = 'left'
            score.valign = 'middle'
            score.pos = (150, self._m_highscore[-1].y - FONT_HIGHSCORE - 3)
            self._m_highscore.append(score)
        f.close()
        for _ in range(10 - len(self._highscore)):
            self._highscore.append(0)
            score = GLabel(text = '\n' + str(self._highscore[-1]), font_size = FONT_HIGHSCORE)
            score.halign = 'left'
            score.valign = 'middle'
            score.pos = (150, self._m_highscore[-1].y - FONT_HIGHSCORE - 3)
            self._m_highscore.append(score)

    def _serve(self):
        """Serves the ball object and begins the game.
        
        Creates a Ball object at the center of the screen.
        This also sets the state to STATE_ACTIVE to begin
        the game"""
        ball = Ball()
        ball.size = (BALL_DIAMETER, BALL_DIAMETER)
        ball.center = (GAME_WIDTH/2, GAME_HEIGHT/2)
        ball.linecolor = colormodel.BLACK
        ball.fillcolor = colormodel.BLACK
        self.view.add(ball)
        self._ball = ball
        self._draw()
        self._state = STATE_ACTIVE

    def _new_ball(self):
        """Starts a count down to a new ball.
        
        Creates a label that tells the user that a new
        ball is incoming. The label counts down from 3 seconds."""
        self._m_countdown = GLabel(text = 'Incoming ball in...\n3', font_size = FONT_COUNTDOWN, bold = True)
        self._m_countdown.halign = 'center'
        self._m_countdown.valign = 'middle'
        self._m_countdown.center = (GAME_WIDTH/2, GAME_HEIGHT/2 + FONT_COUNTDOWN/2)
        self.view.add(self._m_countdown)
        self.delay(self._count,1)

    def _count(self):
        """Counts down from 3 seconds and then serves a ball.
        
        If countdown is at 1, removes it and serves the ball.
        Otherwise, decrement the countdown by 1 and delays 1 second
        to call itself again."""
        if self._m_countdown is not None:
            if self._m_countdown.text[-1] == '1':
                self.view.remove(self._m_countdown)
                self._m_countdown = None
                self._serve()
            else:
                self._m_countdown.text = self._m_countdown.text[:-1] + str(int(self._m_countdown.text[-1]) - 1)
                self.delay(self._count,1)

    def _bounding(self):
        """Bounds the ball within the game window.
        
        Sets the y-velocity to negative when the ball exceeds
        the top of the window. Sets the x-velocity to positive
        and negative when the ball exceeds the left and right
        sides of the window respectively."""
        if self._ball.right > GAME_WIDTH:
            self._ball.vx = -abs(self._ball.vx)
        if self._ball.x < 0:
            self._ball.vx = abs(self._ball.vx)
        if self._ball.top > GAME_HEIGHT:
            self._ball.vy = -abs(self._ball.vy)

    def _get_colliding_object(self):
        """Returns the object colliding with the ball.
        
        Returns None if nothing is colliding with the ball.
        Otherwise, checks the paddle and the bricks for collision.
        Detects collision my using a circular mask around the ball."""
        col = [0,0,0,0]
        x = [self._ball.center_x, self._ball.x, self._ball.center_x, self._ball.right]
        y = [self._ball.y, self._ball.center_y, self._ball.top, self._ball.center_y]
        px = [self._paddle.right, self._paddle.right, self._paddle.x, self._paddle.x]
        py = [self._paddle.top, self._paddle.y, self._paddle.y, self._paddle.top]
        for i in range(4):
            if self._paddle.collide_point(x[i],y[i]):
                col[i] = 1
            if self._ball.collide_point(px[i],py[i]):
                col[i] = 1
                col[(i+1) % 4] = 1
            if not col == [0,0,0,0]:
                return (self._paddle, col)
        for brick in self._bricks:
            bx = [brick.right, brick.right, brick.x, brick.x]
            by = [brick.top, brick.y, brick.y, brick.top]
            for i in range(4):
                if brick.collide_point(x[i],y[i]):
                    col[i] = 1
                if self._ball.collide_point(bx[i],by[i]):
                    col[i] = 1
                    col[(i+1) % 4] = 1
                if not col == [0,0,0,0]:
                    return (brick, col)
        return None

    def _paddle_collision(self,col):
        """The method that handles the collision of the ball with the paddle.
        
        This method sets the ball's y-velocity to a positive value. Then,
        it returns the ball left if it hit the left 1/4 of the paddle, and
        returns the ball right if it hit the right 1/4 of the paddle."""
        if self._ball.vy < 0 and col[2] == 0:
            self._combo = 0
            if col[0] == 1 or self._ball.center_x > self._paddle.center_y:
                self._ball.vy = abs(self._ball.vy)
                self._ball.y = self._paddle.top
            if self._ball.center_x > self._paddle.center_x + self._paddle.width/4.0:
                self._ball.vx = abs(self._ball.vx)
            elif self._ball.center_x < self._paddle.center_x - self._paddle.width/4.0:
                self._ball.vx = -abs(self._ball.vx)
            self._ball.vx += self._vel
            self._ball.vx = max(self._ball.vx, -7.5)
            self._ball.vx = min(self._ball.vx, 7.5)

    def _brick_collision(self,brick,col):
        """The method that handles the collision of the ball with a brick.
        
        This method handles differences between side, top, bottom and corner
        collisions onto the brick."""
        self._score += BRICK_SCORE + self._combo * COMBO_SCORE
        self._m_score.text = 'Score:  ' + str(self._score)
        self._combo += 1
        self.view.remove(brick)
        self._bricks.remove(brick)
        if col[1] == 1 and self._ball.vx < 0:
            if self._ball.center_x > brick.x:
                self._ball.vx = abs(self._ball.vx)
            if col[0] == 1 or col[2] == 1:
                if self._ball.center_y > brick.center_y + brick.height/4.0:
                    self._ball.vy = abs(self._ball.vy)
                elif self._ball.center_y < brick.center_y - brick.height/4.0:
                    self._ball.vy = -abs(self._ball.vy)
        elif col[3] == 1 and self._ball.vx > 0:
            if self._ball.center_x < brick.x:
                self._ball.vx = -abs(self._ball.vx)
            if col[0] == 1 or col[2] == 1:
                if self._ball.center_y > brick.center_y + brick.height/4.0:
                    self._ball.vy = abs(self._ball.vy)
                elif self._ball.center_y < brick.center_y - brick.height/4.0:
                    self._ball.vy = -abs(self._ball.vy)
        else:
            if col[0] == 1:
                self._ball.vy = abs(self._ball.vy)
            if col[2] == 1:
                self._ball.vy = -abs(self._ball.vy)

    def _death(self):
        """The method called when the current ball dies
        
        This method ends the game if there are no more lives.
        If there are still lives, then it lowers the lives and
        calls the _new_ball method."""
        if self._lives == 0:
            self._game_end(0)
        else:
            self._lives -= 1
            lives = ' ' + str(self._lives)
            self._m_lives[0].text = 'Lives:  ' + lives[-2:]
            self._state = STATE_PAUSED
            self.view.remove(self._ball)
            self._ball = None
            self._new_ball()

    def _game_end(self,win):
        """Displays a message for the end of the game.
        
        Sets state to STATE_COMPLETE and then displays a message
        depending on whether the player won or lost the game."""
        self.view.remove(self._ball)
        self._ball = None
        self._anchor = None
        self._press = None
        self._prev = None
        self._state = STATE_COMPLETE
        if win == 1:
            self._m_end = GLabel(text = "Congratulations!\nYou Completed the Game!\nTry Again?")
        elif win == 0:
            self._m_end = GLabel(text = "Game Over!\nYou have no more Lives\nTry Again?")
        self._m_end.font_size = FONT_END
        self._m_end.bold = True
        self._m_end.halign = 'center'
        self._m_end.valign = 'middle'
        self._m_end.center = (GAME_WIDTH/2, GAME_HEIGHT/2)
        self.view.add(self._m_end)
        if not self._score == min(self._highscore + [self._score]):
            self._m_end.text = 'New High Score!\n' + self._m_end.text
            self._highscore.append(self._score)
            self._highscore.sort(reverse = True)
            self._highscore = self._highscore[:-1]
            write = ''
            for i in range(10):
                write += str(self._highscore[i]) + '\n'
            f = open(PATH + '\highscores.txt','w')
            f.write(write)
            f.close()

    def _draw_highscore(self):
        """Draws the highscore screen.
        
        Changes the highscore select button between the scores button
        and the back button. Also changes the text displayed on screen
        between welcome screen and high score screen."""
        if self._m_highscore[0].source == 'scores.png':
            self._m_highscore[0].source = 'back.png'
            self.view.remove(self._m_welcome[0])
            self.view.remove(self._m_welcome[1])
            for i in range(1,12):
                self.view.add(self._m_highscore[i])
        elif self._m_highscore[0].source == 'back.png':
            self._m_highscore[0].source = 'scores.png'
            for i in range(1,12):
                self.view.remove(self._m_highscore[i])
            self.view.add(self._m_welcome[0])
            self.view.add(self._m_welcome[1])

    def _draw(self):
        """Displays the messages that appear during the game
        
        This method calls _draw_lives(self), _draw_score(self),
        and _draw_pause(self)"""
        self._draw_lives()
        self._draw_score()
        self._draw_pause()

    def _draw_lives(self):
        """Displays the counter for number of lives.
        
        The counter is displayed in the bottom left corner with a
        font size of FONT_LIVES. It uses a numerical representation
        followed by a graphical ball icon.
        
        If the lives is already drawn, it just redraws (to account for
        the bottom up drawing that kivy uses) to make sure that the ball is
        drawn below the lives."""
        if len(self._m_lives) > 0:
            for obj in self._m_lives:
                self.view.remove(obj)
                self.view.add(obj)
        elif len(self._m_lives) == 0:
            lives = ' ' + str(self._lives)
            text = GLabel(text = 'Lives:  ' + lives[-2:], font_size = FONT_LIVES)
            text.linecolor = COLOR_LIVES
            text.halign = 'left'
            text.valign = 'middle'
            text.center_y = 3 + FONT_LIVES/2
            text.x = 3
            icon = GEllipse(size = (FONT_LIVES, FONT_LIVES))
            icon.center = (FONT_LIVES * 6.2,text.center_y)
            icon.linecolor = COLOR_LIVES
            icon.fillcolor = COLOR_LIVES
            self._m_lives.append(text)
            self._m_lives.append(icon)
            self.view.add(text)
            self.view.add(icon)

    def _draw_score(self):
        """Displays the counter for the current score.
        
        The counter is displayed at the top left corner with a
        font size of FONT_SCORE.
        
        If the score is already drawn, it just redraws (to account for
        the bottom up drawing that kivy uses) to make sure that the ball
        is drawn below the score."""
        if self._m_score is not None:
            self.view.remove(self._m_score)
            self.view.add(self._m_score)
        else:
            text = GLabel(text = 'Score:  ' + str(self._score), font_size = FONT_SCORE)
            text.linecolor = COLOR_SCORE
            text.halign = 'left'
            text.valign = 'middle'
            text.center_y = GAME_HEIGHT - 3 - FONT_SCORE/2
            text.x = 3
            self._m_score = text
            self.view.add(text)

    def _draw_pause(self):
        """Displays the icon for the pause/resume button.
        
        The icon is displayed at the bottom right corner.
        
        If the icon is already drawn, it just redraws (to account for
        the bottom up drawing that kivy uses) to make sure that the ball
        is drawn below the icon."""
        if self._m_pause is not None:
            self.view.remove(self._m_pause)
            self.view.add(self._m_pause)
        else:
            if self._state_paused:
                icon = GImage(source = 'play.png')
            else:
                icon = GImage(source = 'pause.png')
            icon.size = (PAUSE_SIZE, PAUSE_SIZE)
            icon.center = (GAME_WIDTH - 3 - PAUSE_SIZE/2, 3 + PAUSE_SIZE/2)
            self._m_pause = icon
            self.view.add(icon)


class Ball(GEllipse):
    """Instance is a game ball.

    We extends GEllipse because a ball does not just have a position; it
    also has a velocity.  You should add a constructor to initialize the
    ball, as well as one to move it.

    Note: The ball does not have to be a GEllipse. It could be an instance
    of GImage (why?). This change is allowed, but you must modify the class
    header up above."""
    # FIELDS.  You may wish to add properties for them, but that is optional.

    # Velocity in x direction.  A number (int or float)
    _vx = 0.0
    # Velocity in y direction.  A number (int or float)
    _vy = 0.0

    @property
    def vx(self):
        """The ball's velocity in the x direction
        
        **Invariant**: Must be a float"""
        return self._vx

    @vx.setter
    def vx(self,value):
        assert (type(value) == int or type(value) == float), `value`+' is an invalid number'
        self._vx = float(value)

    @property
    def vy(self):
        """The ball's velocity in the y direction
        
        **Invariant**: Must be a float"""
        return self._vy

    @vy.setter
    def vy(self,value):
        assert (type(value) == int or type(value) == float), `value`+' is an invalid number'
        self._vy = float(value)

    # ADD MORE FIELDS (INCLUDE INVARIANTS) AS NECESSARY

    # ADD MORE METHODS (PROPERLY SPECIFIED) AS NECESSARY

    def move(self):
        """Moves the ball based on the velocity of the ball.
        
        Sets the ball's position by adding on the velocity
        of the ball the the current position."""
        self.x += self.vx
        self.y += self.vy 

    def __init__(self,**keywords):
        """**Constructor**: creates a new ball.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create an ball centered at
        (0,0) with radius 10 and with velocity of (5.0,5.0),
        use the constructor call
        
            Ball(center=(0,0),size=(20,20),vel=(5,5))
        
        Note that we specify Ball size by diameter, not radius
        This class supports the same keywords as `GEllipse`."""
        super(Ball,self).__init__(**keywords)
        vy = -5.0
        vx = random.uniform(1.0,5.0)
        vx = vx * random.choice([-1, 1])
        if 'vx' in keywords:
            vx = keywords['vx']
        if 'vy' in keywords:
            vy = keywords['vy']
        if 'vel' in keywords:
            (vx,vy) = keywords['vel']
        self.vx = vx
        self.vy = vy



# ADD MORE CLASSES AS NECESSARY
