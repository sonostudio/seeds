import py5
import random

letters = []

# CONFIGURATION
# ---------------------------------------------------------
# Exact filename of the font in your 'data' folder
font_filename = "Silkscreen-Regular.ttf"

# Neon Green
fixed_color = "#F5F5F5"
background_color = "#013220"
# ---------------------------------------------------------

main_font = None


def settings():
    py5.size(420, 280)
    py5.smooth(0)  # Keep pixels sharp


def setup():
    global main_font
    py5.window_title("8-Bit Google Font")
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.rect_mode(py5.CENTER)
    py5.background(py5.color(background_color))

    print(f"Loading font file: {font_filename}")

    # LOAD FONT FROM FILE
    # py5 will automatically look in the 'data' folder
    try:
        main_font = py5.create_font(font_filename, 24)
        print("Success! Google Font loaded.")
    except Exception as e:
        print(f"❌ Error loading font: {e}")
        print("Make sure the .ttf file is inside a 'data' folder next to this script.")
        # Fallback to system font if file is missing
        main_font = py5.create_font("Courier New", 24)


def draw():
    if len(letters) == 0:
        py5.background(py5.color(background_color))

    for item in letters:
        item.display()


class Letter:
    def __init__(self, char, x, y):
        self.char = char
        self.x = x
        self.y = y
        self.rotation = 0
        self.color = py5.color(fixed_color)
        self.size = 24

    def display(self):
        py5.push_matrix()
        py5.translate(self.x, self.y)

        py5.text_font(main_font)
        py5.text_size(self.size)

        py5.fill(self.color)
        py5.text(self.char, 0, 0)

        py5.pop_matrix()


def organize_text():
    # 1. Configuration for your "Page"
    margin_left = 50
    margin_top = 100
    line_height = 30  # Vertical space between lines
    char_width = 15  # Horizontal space (Monospace font makes this easy)
    max_width = py5.width - margin_left

    # 2. Reset the "Cursor"
    cursor_x = margin_left
    cursor_y = margin_top

    # 3. Loop through every letter and move it
    for item in letters:
        # Move the letter to the cursor position
        item.x = cursor_x
        item.y = cursor_y

        # Advance the cursor
        cursor_x += char_width

        # 4. Line Wrapping (Typewriter style)
        # If we hit the right edge, reset X and move down Y
        if cursor_x > max_width:
            cursor_x = margin_left
            cursor_y += line_height

    # Redraw background immediately to clear the "messy" trails
    py5.background(py5.color(background_color))


# GLOBAL STATE
is_organized = False  # Tracks if we are currently in "Documentation Mode"


def key_pressed():
    global is_organized

    # -----------------------------------------------------
    # 1. ENTER KEY LOGIC (TOGGLE)
    # -----------------------------------------------------
    if py5.key == py5.ENTER:
        if is_organized:
            # If already organized, clear everything
            letters.clear()
            py5.background(py5.color(background_color))
            is_organized = False
        else:
            # If in chaos mode, organize it
            organize_text()
            is_organized = True
        return

    # If we type or delete, we are "dirtying" the organized view,
    # so we reset the flag. Next Enter will re-organize, not clear.
    if py5.key == py5.BACKSPACE:
        if len(letters) > 0:
            letters.pop()
            py5.background(py5.color(background_color))
            is_organized = False
        return

    if py5.key == py5.CODED:
        return

    # User is typing -> Reset organized flag
    is_organized = False

    # -----------------------------------------------------
    # 2. COLLISION & HYPER JUMP LOGIC
    # -----------------------------------------------------

    # Standard Jump Settings
    min_step = 20
    max_step = 35

    # Hyper Jump Settings (Emergency Mode)
    hyper_min = 100
    hyper_max = 400

    safe_distance = 18
    max_attempts = 50

    valid_spot_found = False
    candidate_x = 0
    candidate_y = 0

    if len(letters) == 0:
        candidate_x = py5.width / 2
        candidate_y = py5.height / 2
        valid_spot_found = True
    else:
        prev = letters[-1]

        # PHASE 1: Try Local Jump (Standard)
        for i in range(max_attempts):
            if attempt_jump(prev, min_step, max_step, safe_distance):
                valid_spot_found = True
                candidate_x = temp_x
                candidate_y = temp_y
                break

        # PHASE 2: Hyper Jump (If local failed)
        if not valid_spot_found:
            print("⚠️ Area crowded! Attempting HYPER JUMP...")
            for i in range(max_attempts):
                # Try jumping much further to escape the cluster
                if attempt_jump(prev, hyper_min, hyper_max, safe_distance):
                    valid_spot_found = True
                    candidate_x = temp_x
                    candidate_y = temp_y
                    break

    if valid_spot_found:
        letters.append(Letter(py5.key, candidate_x, candidate_y))
    else:
        # If even Hyper Jump fails (rare), we finally give up
        print("❌ Screen is totally full!")


# Helper variables to store temporary coordinates inside the loop
temp_x = 0
temp_y = 0


def attempt_jump(prev_letter, min_dist, max_dist, safe_dist):
    global temp_x, temp_y

    direction = random.choice([-1, 1])
    distance = random.randint(min_dist, max_dist) * direction
    axis = random.choice(['x', 'y'])

    if axis == 'x':
        cx = prev_letter.x + distance
        cy = prev_letter.y
    else:
        cx = prev_letter.x
        cy = prev_letter.y + distance

    # Wrap around screen
    if cx > py5.width - 20: cx = 20
    if cx < 20: cx = py5.width - 20
    if cy > py5.height - 20: cy = 20
    if cy < 20: cy = py5.height - 20

    # Check Collision
    for other in letters:
        d = py5.dist(cx, cy, other.x, other.y)
        if d < safe_dist:
            return False  # Failed

    # Success
    temp_x = cx
    temp_y = cy
    return True


py5.run_sketch()