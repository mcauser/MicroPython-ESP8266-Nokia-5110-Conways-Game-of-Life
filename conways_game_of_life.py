from time import sleep_ms
from framebuf import FrameBuffer1
from urandom import getrandbits

class ConwaysGameOfLife:
    def __init__(self, lcd):
        # High score
        self.best = 0
        # PCD8544 (Nokia 5110) LCD
        self.lcd = lcd
        self.width = 84
        self.height = 48
        self.buffer = bytearray((self.height // 8) * self.width)
        self.framebuf = FrameBuffer1(self.buffer, self.width, self.height)

    def draw(self):
        self.lcd.data(self.buffer)

    def intro(self):
        self.framebuf.fill(0)
        self.framebuf.text("Conway's", 10, 8, 1)
        self.framebuf.text("Game", 26, 16, 1)
        self.framebuf.text("of", 34, 24, 1)
        self.framebuf.text("Life", 26, 32, 1)
        self.draw()

    def end(self, score, best, size):
        # The 8x8 font is too wide to fit "Generations", so I called it "Score"
        self.framebuf.fill(0)
        self.framebuf.text("Score", 0, 0, 1)
        self.framebuf.text(str(score), 0, 8, 1)
        self.framebuf.text("Best score", 0, 16, 1)
        self.framebuf.text(str(best), 0, 24, 1)
        self.framebuf.text("Pixel size", 0, 32, 1)
        self.framebuf.text(str(size), 0, 40, 1)
        self.draw()

    def begin(self, size=4, delay=20):
        # Size of lifeforms in pixels
        self.size = size
        # Delay in ms between generations
        self.delay = delay

        # Localised to avoid self lookups
        # Possible performance optimisation, TBC
        draw = self.draw
        delay = self.delay
        tick = self.tick

        # Randomise initial pixels
        self.randomise()

        # Begin
        generations = 0
        try:
            while tick():
                generations = generations + 1
                draw()
                sleep_ms(delay)
        except KeyboardInterrupt:
            pass

        # New high score?
        if generations > self.best:
            self.best = generations

        # End
        self.end(generations, self.best, self.size)

    def randomise(self):
        size = self.size
        width = self.width
        height = self.height
        cell = self.cell

        self.framebuf.fill(0)

        for x in range(0, width, size):
            for y in range(0, height, size):
                # random bit: 0 = pixel off, 1 = pixel on
                cell(x, y, getrandbits(1))

        self.draw()

    def cell(self, x, y, colour):
        size = self.size
        buf = self.framebuf

        for i in range(size):
            for j in range(size):
                buf.pixel(x + i, y + j, colour)

    def get(self, x, y):
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return 0
        return self.framebuf.pixel(x, y) & 1

    def tick(self):
        size = self.size
        width = self.width
        height = self.height
        get = self.get
        cell = self.cell

        # If no pixels are born or die, the game ends
        something_happened = False

        for x in range(0, width, size):
            for y in range(0, height, size):

                # Is the current cell alive
                alive = get(x, y)

                # Count number of neighbours
                neighbours = (
                    get(x - size, y - size) +
                    get(x, y - size) +
                    get(x + size, y - size) +
                    get(x - size, y) +
                    get(x + size, y) +
                    get(x + size, y + size) +
                    get(x, y + size) +
                    get(x - size, y + size)
                )

                # Apply the game rules
                if alive and not 2 <= neighbours <= 3:
                    # This pixel dies
                    cell(x, y, 0)
                    if not something_happened:
                        something_happened = True
                elif not alive and neighbours == 3:
                    # A new pixel is born
                    cell(x, y, 1)
                    if not something_happened:
                        something_happened = True

        return something_happened
