from tkinter import *
from PIL import Image, ImageTk
import random
import argparse


# function to place bombs into mine_board
def place_mines(pick_x, pick_y):
    board = [[False] * board_x for i in range(board_y)]
    for i in range(mine_count):
        mine_placed = False
        around_click = []
        for h in [-1, 0, 1]:
            for k in [-1, 0, 1]:
                around_click.append((pick_x + h, pick_y + k))
        while not mine_placed:
            x = random.randint(0, board_x - 1)
            y = random.randint(0, board_y - 1)
            # check if space is already a mine and check if its the square clicked and check if near square clicked
            if not board[y][x] and (x, y) not in around_click:
                board[y][x] = True
                mine_placed = True
    return board


# check number of bombs surrounding a square
def check_square(y, x):
    global surrounding_bombs
    global mine_board
    count = 0
    for a in [-1, 0, 1]:
        for b in [-1, 0, 1]:
            try:
                if 0 <= y + a <= board_y - 1 and 0 <= x + b <= board_x - 1:
                    if mine_board[y + a][x + b]:
                        count += 1
            except IndexError:
                pass

    value = surrounding_bombs.setdefault(count, [])
    value.append((x, y))
    surrounding_bombs[count] = value

    if count == 0:
        for c in [-1, 0, 1]:
            for d in [-1, 0, 1]:
                if (c, d) != (0, 0):
                    if 0 <= x + c <= board_x - 1 and 0 <= y + d <= board_y - 1 and not (x + c, y + d) in [r for t in
                                                                                                          surrounding_bombs.values()
                                                                                                          for r in t]:
                        check_square(y + d, x + c)


# functions for digging and marking
def dig(event):
    global planted_mines
    global mine_board
    global surrounding_bombs
    global buttons
    global dug_tiles
    global offset
    global game_over

    info = event.widget.grid_info()
    row, column = info["row"], info["column"]

    # checks if mines have been placed
    if not planted_mines:
        # if they have not, then generate them making sure clicked spot is not a mine
        mine_board = place_mines(column, row)
        planted_mines = True

    # stop player if game is over
    if not game_over:
        # check if clicked space is flagged then do not let it be dug
        if not event.widget.cget("image") == str(flag) and event.widget.cget("image") == str(tile):
            # check if clicked space is a mine
            if mine_board[row][column]:
                event.widget.config(image=hit_mine)
                game_over = True
            else:
                # check if bombs around square
                # if blank do same for all surrounding squares
                # repeat until exhausted
                surrounding_bombs = {}
                # do check_square - done
                # use global surrounding bombs to loop through all cells and update their icons
                check_square(row, column)

                for key in surrounding_bombs.keys():
                    for cell in surrounding_bombs[key]:
                        buttons[cell[1]][cell[0]].config(image=mine_numbers[key])
                        if (cell[0], cell[1]) not in dug_tiles:
                            dug_tiles.append((cell[0], cell[1]))

            if len(dug_tiles) == (board_x * board_y) - mine_count:
                label = Label(root, text="You Win", fg="green", bg="#acacac", font=("Comic Sans", 30), anchor=CENTER)
                label.place(x=root.winfo_width() / 2, y=30, anchor="n")
                game_over = True


def mark(event):
    # we use event.widget to get button id clicked
    # then configure it to set image as flag
    # if it is already a flag we can remove the flag
    # if the space is already dug, ie not a flag or blank then dont let mark it
    if not game_over:
        if event.widget.cget("image") in [str(flag), str(tile)]:
            if event.widget.cget("image") == str(flag):
                event.widget.config(image=tile)
            else:
                event.widget.config(image=flag)


def resize_image(img):
    img = img.resize((cell_size, cell_size), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    return img


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--width", type=int, default=14, help="defines the width of the grid")
    parser.add_argument("--height", type=int, default=10, help="defines the height of the grid")
    parser.add_argument("--scale", type=float, default=1.0, help="defines the scale of the grid")

    args = parser.parse_args()

    board_x = args.width
    board_y = args.height
    scale = args.scale

    if scale < 0.5 or scale > 2:
        raise argparse.ArgumentTypeError("Scale must be between 0.5 and 2")

    # create tk parent window
    root = Tk()
    frame = Frame(root)
    # create blank array to store button objects in
    buttons = [[0] * board_x for i in range(board_y)]

    cell_size = int(40*scale)

    # fetch tile images
    image_names = ["tile", "flag", "mine", "hit_mine"]
    tile, flag, mine, hit_mine = [resize_image(Image.open("assets/{}.png".format(x))) for x in image_names]

    mine_numbers = [resize_image(Image.open("assets/{}.png".format(x))) for x in range(9)]

    # driver / set-up code

    planted_mines = False
    mine_count = int((board_x * board_y) / 6.4)
    dug_tiles = []
    offset = 0
    game_over = False

    # create buttons into grid
    for x in range(board_x):
        for y in range(board_y):
            var = Button(root, image=tile, height=cell_size, width=cell_size)
            var.grid(row=y, column=x)
            var.bind("<Button-1>", dig)
            var.bind("<Button-3>", mark)
            buttons[y][x] = var

    root.title("Minesweeper")
    root.mainloop()
