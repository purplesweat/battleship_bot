import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class TileType:
    BLANK = 0
    SHIP = 1
    MISS = 2
    HIT = 3

class Boards:
    BLANK_BOARD = [[TileType.BLANK for i in range(10)] for i in range(10)]

class Direction:
    LEFT = (-1,0)
    RIGHT = (1,0)
    UP = (0,-1)
    DOWN = (0,1)
    INVALID_DIRECTION = (-1,-1)

class ShipPlacement:
    SUCCESS = 0
    OUTOFBOUNDS = 1
    OVERLAP = 2
    INVALID_MOVES = 3

class Move:
    INVALID_MOVE = (-1,-1)

class Battleship:
    SHIP_SIZES = (5, 4, 3, 3, 2)
    SHIP_NAMES = ('Aircraft Carrier',
            'Battleship',
            'Cruiser',
            'Submarine',
            'Destroyer')
    def __init__(self):
        self.ships_placed = 0
        self.board = Boards.BLANK_BOARD.copy()
        self.bot_board = Boards.BLANK_BOARD.copy()
        self.init_bot_board()
    
    def init_bot_board(self):
        pass

    def get_ship_to_place(self):
        return self.SHIP_NAMES[self.ships_placed]

    def place_ship(self, pos: (int, int), direction: Direction):
        if pos == Move.INVALID_MOVE or direction == Direction.INVALID_DIRECTION:
            return ShipPlacement.INVALID_MOVES
        col = pos[0]
        row = pos[1]
        size = self.SHIP_SIZES[self.ships_placed]
        if not (0 <= col + size * direction[0] < 10 and 0 <= row + size * direction[1] < 10):
            return ShipPlacement.OUTOFBOUNDS

        blank = 0
        for i in range(size):
            blank += self.board[row + i * direction[1]][col + i * direction[0]]
        if blank > 0:
            return ShipPlacement.OVERLAP

        for i in range(size):
            self.board[row + i * direction[1]][col + i * direction[0]] = TileType.SHIP
        self.ships_placed += 1
        return ShipPlacement.SUCCESS

    def reset(self):
        self.__init__()

class MoveParser:
    def parse_move(move: str):
        if ord('A') <= ord(move[0]) <= ord('J') and 1 <= int(move[1]) <= 10 and len(move) == 2:
            return (ord(move[0]) - ord('A'), int(move[1]) - 1)
        else:
            return Move.INVALID_MOVE
    def parse_rotation(rotation: str):
        match rotation:
            case 'left':
                return Direction.LEFT
            case 'right':
                return Direction.RIGHT
            case 'up':
                return Direction.UP
            case 'down':
                return Direction.DOWN
            case _:
                return Direction.INVALID_DIRECTION

Game = Battleship()

@bot.command(name='battleship', help='starts game of battleship')
async def start_game(ctx):
    Game.reset()
    await ctx.send('started game of battleship: place your five ships, starting with {}'.format(Game.get_ship_to_place()))

@bot.command(name='place_ship', help='places ship: example place_ship E4 left')
async def place_ship(ctx, position: str, direction: str):
    status = Game.place_ship(MoveParser.parse_move(position), MoveParser.parse_rotation(direction))
    match status:
        case ShipPlacement.OUTOFBOUNDS:
            message = 'out of bounds'
        case ShipPlacement.OVERLAP:
            message = 'overlap'
        case ShipPlacement.INVALID_MOVES:
            message = 'invalid moves'
        case ShipPlacement.SUCCESS:
            message = 'now place your {}'.format(Game.get_ship_to_place())
        case _:
            print('?????')
            message = '?????'
    await ctx.send(message)

@bot.command(name='print_board', help = 'prints board')
async def print_board(ctx):
    for i in Game.board:
        message = ''
        for j in i:
            square = ':'
            match j:
                case TileType.BLANK:
                    square += 'black_large'
                case TileType.SHIP:
                    square += 'green'
                case TileType.MISS:
                    square += 'white_large'
                case TileType.HIT:
                    square = 'red'
            square += '_square:'
            message += square
        await ctx.send(message)

bot.run(TOKEN)
