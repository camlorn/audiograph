"""This file implements the UI, using the helper modules."""
import command_parser
import sonifier
import sympy
from sympy.utilities.lambdify import lambdify, lambdastr
from sympy.parsing import sympy_parser

class Ui(command_parser.CommandParserBase):

    prompt = "y = "

    def __init__(self):
        self.min_x = 0
        self.max_x = 10
        self.min_y = 0
        self.max_y = 10
        self.duration = 5.0
        self.hrtf = False
        self.x_symbol, self.y_symbol = sympy.symbols("x, y")
        self.current_graph = None

    def parse(self, equation):
        return sympy_parser.parse_expr(equation, transformations = 
            sympy_parser.standard_transformations + (sympy_parser.split_symbols, sympy_parser.implicit_multiplication,
                sympy_parser.function_exponentiation))

    def make_graph(self, equation):
        sym = self.parse(equation)
        f = lambdify((self.x_symbol, ), sym)
        return sonifier.Sonifier(f = f, duration = self.duration, min_x = self.min_x,
            max_x = self.max_x, min_y = self.min_y, max_y = self.max_y,
            hrtf = self.hrtf)

    def do_default(self, argument):
        print("Graphing ", argument)
        if self.current_graph is not None:
            self.current_graph.shutdown()
        self.current_graph = self.make_graph(argument)
        self.current_graph.to_audio_device()

    def quit_hook(self):
        if self.current_graph:
            self.current_graph.shutdown()

    def do_xrange(self, argument):
        """Set the range for x.

Syntax:
.xrange: Show the current range for x.
.xrange <min> <max>: configure us to evaluate the graph from x=min to x=max,.

Floating point arguments are allowed."""
        if len(argument) == 0:
            print("Range is {} <= x <= {}".format(self.min_x, self.max_x))
            return
        words = argument.split()
        try:
            min = float(words[0])
            max = float(words[1])
        except:
            print("Couldn't parse.  See .help xrange for syntax.")
            return
        if min >= max:
            print("Error: min must be strictly less than max.")
            return
        self.min_x = min
        self.max_x = max

    def do_yrange(self, argument):
        """Set the range for y.

Syntax:
.yrange: Show the current range for y.
.yrange <min> <max>: configure us to show values of the function between y=min and y=max.

Floating point arguments are allowed."""
        if len(argument) == 0:
            print("Range is {} <= y <= {}".format(self.min_y, self.max_y))
            return
        words = argument.split()
        try:
            min = float(words[0])
            max = float(words[1])
        except:
            print("Couldn't parse.  See .help yrange for syntax.")
            return
        if min >= max:
            print("Error: min must be strictly less than max.")
            return
        self.min_y = min
        self.max_y = max

    def do_duration(self, argument):
        """Set the duration of the graph.
syntax:
.duration: Show the duration.
.duration <seconds>: Set the duration."""
        if len(argument) == 0:
            print("Current duration:", self.duration)
            return
        try:
            new_dur = float(argument)
        except:
            print("Couldn't parse duration. See .help duration for syntax.")
            return
        if new_dur <= 1.0:
            print("Duration must be at least 1 second.")
            return
        self.duration = new_dur

    def do_file(self, argument):
        """Graph an equation to a file.
        
syntax:
.file <name> <equation>: Graph equation to file name.

The file name must not contain spaces and must end in .wav or .ogg.  It will be written to the current working directory."""
        fname, sep, equation = argument.partition(" ")
        if len(fname) == 0 or len(equation) == 0:
            print("Invalid syntax. See .help file.")
        graph = self.make_graph(equation)
        graph.write_file(fname)
        graph.shutdown()


    def do_eval(self, argument):
        """Evaluate the argument with sympy and display.

syntax:
.eval <expression>: Evaluate the expression."""
        if len(argument) == 0:
            print("Invalid syntax. See .help eval for details.")
            return
        try:
            sym = self.parse(argument)
            sympy.simplify(sym)
        except:
            print("Couldn't parse expression.")
            return
        try:
            print(sym.evalf())
        except:
            print(sym)

