#! /usr/bin/python3

"""
This is a utility for converting english characters to their equivalent urdu characters as defined by the CRULP Urdu Keyboard Layout v1.1 (and vice versa).
"""

import click
import re
import sys


START = re.compile(r".*startUrdu.*", re.IGNORECASE)
BEGINPARA = re.compile(r"^\\begin{enpara}")
ENDPARA = re.compile(r"^\\end{enpara}")


def eprint(*args, **kwargs):
    """
    Utility function for printing to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)


class Translate:

    # Define the macro names that are considered "urdu macros" meaning there contents SHOULD be translated.
    urdu_macros = ['dialog', 'idialog']


    # Define the map between english and urdu characters (the latter defined using their Unicode code-points)
    # The Urdu characters are easily identifiable as their unicode point starts with 06 i.e. \u06XX

    e2u = {
        # Lower-case mappings
        '1': u'\u06f1',
        '2': u'\u06f2',
        '3': u'\u06f3',
        '4': u'\u06f4',
        '5': u'\u06f5',
        '6': u'\u06f6',
        '7': u'\u06f7',
        '8': u'\u06f8',
        '9': u'\u06f9',
        '0': u'\u06f0',
        'q': u'\u0642',
        'a': u'\u0627',
        'z': u'\u0632',
        'w': u'\u0648',
        's': u'\u0633',
        'x': u'\u0634',
        'e': u'\u0639',
        'd': u'\u062f',
        'c': u'\u0686',
        'r': u'\u0631',
        'f': u'\u0641',
        'v': u'\u0637',
        't': u'\u062a',
        'g': u'\u06af',
        'b': u'\u0628',
        'y': u'\u06d2',
        'h': u'\u062d',
        'n': u'\u0646',
        'u': u'\u0621',
        'j': u'\u062c',
        'm': u'\u0645',
        'i': u'\u06cc',
        'k': u'\u06a9',
        ',': u'\u060c',
        'o': u'\u06c1',
        'l': u'\u0644',
        '.': u'\u06d4',
        'p': u'\u067e',
        ';': u'\u061b',

        # Upper-case (Shift-ed) mapping
        '~': u'\u064b',
        'Q': u'\u0652',
        'A': u'\u0622',
        'Z': u'\u0630',
        'W': u'\u0651',
        'S': u'\u0635',
        'X': u'\u0698',
        'E': u'\u0670',
        'D': u'\u0688',
        'C': u'\u062b',
        'R': u'\u0691',
        'V': u'\u0638',
        'T': u'\u0679',
        'G': u'\u063a',
        'Y': u'\u064e',
        'H': u'\u06be',
        'N': u'\u06ba',
        'U': u'\u0626',
        'J': u'\u0636',
        'M': u'\u0658',
        'I': u'\u0650',
        'K': u'\u062e',
        'O': u'\u06c3',
        '>': u'\u066b',
        'P': u'\u064f',
        '?': u'\u061f',
    }


    def __init__(self):

        # Reverse the e2u mapping to create the u2e mapping
        self.u2e = {}

        for k in self.e2u:
            self.u2e[ self.e2u[k] ] = k

        # Create list of mapped characters in both languages
        self.en = [k for k in self.e2u]
        self.ur = [k for k in self.u2e]


    def read(self, fin):
        """
        Read in the lines from the specified file
        """
        # Retrieve the text from the input file and remove extraneous '\n' from the end of each line
        self.lines = [x.rstrip() for x in fin.readlines()]


    def mu2e(self, char):
        """
        Convert the urdu character to english. A non-urdu character is preserved.
        """
        try:
            return self.u2e[char]

        except KeyError:
            return char


    def me2u(self, char):
        """
        Convert the english character to urdu. A non-english character is preserved.
        """
        try:
            return self.e2u[char]

        except KeyError:
            return char


    def convert_string(self, converter, string):
        """
        Convert the specified 'string' using the 'converter' and return it.
        """
        s = ""

        for c in string:
            s += converter(c)

        return s


    def convert(self, converter):
        """
        Convert characters in lines using the function provided in 'converter'
        """
        for line in self.lines:

            print(self.convert_string(converter, line))


    def urdu_to_english(self):
        """
        Convert urdu characters to english.
        """
        self.convert(self.mu2e)


    def english_to_urdu(self):
        """
        Convert ALL english characters to urdu.
        """
        self.convert(self.me2u)


    def latex(self):
        """
        Convert urdu characters to english in a LaTeX file while preserving LaTeX
        commands, all lines inside the 'enpara' environment, and any text inside
        any macro EXCEPT those declared in self.urdu_macros.
        """
        fEnPara = False

        # We start by ignoring all the lines before \startUrdu (or '% startUrdu')
        count = 0

        for line in self.lines:

            count += 1
            print(line)

            if START.match(line):
                break

        for i in range(count, len(self.lines)):

            line = self.lines[i]

            if fEnPara:  # Do not translate in the middle of an 'enpara' environment

                print(line)

                if ENDPARA.match(line):

                    fEnPara = False

            else:

                if BEGINPARA.match(line):            # 'enpara' environment is beginning

                    fEnPara = True
                    print(line)

                else:  # We are NOT in the 'enpara' environment. We must parse the line
                       # carefully by treating it as nested strings

                    print(self.e2u_substr(line))


    def e2u_substr(self, line):
        """
        Convert substring from English to Urdu. Designed to make heavy use of recursion.
        """

        if len(line) == 0:        # Deal with the possibility of an empty line
            return line


        c = line[0]        # Start with the first character in the line

        if c != '\\':
            return self.me2u(c) + self.e2u_substr(line[1:])        # convert character and pass remaining string recursively to this function

        # If execution arrives here it means the first character is '\'
        if line[1] == "\\":        # Double slash, just render it as is,

            return "\\" + self.e2u_substr(line[2:])        # Use recursion to relegate conversion of the remaining string

        # If a \begin{} environment is found render the \begin{...} as is passing the
        # rest on for translation
        if line[1:7] == "begin{":
            # Find first character after '}'
            j = k = 7

            while k + 1 < len(line) and line[k] != '}':
                k += 1

            return line[:k+1] + self.e2u_substr(line[k+1:])

        # Treat \end{} the same way as \begin{} above
        elif line[1:5] == "end{":
            # Find first character after '}'
            j = k = 5

            while k + 1 < len(line) and line[k] != '}':
                k += 1

            return line[:k+1] + self.e2u_substr(line[k+1:])


        # We have a macro to deal with. We must figure out what type of macro is it:
        #
        # 1. Hanging: \itshape ends in a space
        # 2. Arguments (possibly more than one): \en{} or \rule{\textwdith}{0pt}

        # We will find the end of this macro
        j = 1

        try:
            while j + 1 < len(line) and line[j] not in ['{', ' ']:
                j += 1

            if line[j] == ' ':        # Hanging macro (e.g. \itshape)
                return line[:j] + self.e2u_substr(line[j:])

            if j + 1 == len(line):
                return line[:j + 1]

            # Macro has an opening brace.
            macro = line[1:j]

            if '[' in macro:        # Macro contains an optional argument which has been attached to the macro name. We must extract the latter
                macro = macro[:macro.index('[')]        # Extract substring up to position of first '[' character

            # First we figure if it is a urdu macro that is a macro that is allowed to contain urdu text
            if macro in self.urdu_macros:
                return line[:j] + self.e2u_substr(line[j:])            # If it is an urdu macro we return the macro and pass the rest on for conversion

            # We now find the end of the (Non-Urdu) macro (including its argument)
            k = j + 1

            fArg = True

            while fArg:
                while line[k] != '}':
                    k += 1

                if k + 1 != len(line) and line[k + 1] == '{':        # We deal with the possibility of the macro ending the line or multiple arguments {...} of the macro
                    k += 1
                else:
                    fArg = False            # Arguments complete we can leave this macro

            return line[:k] + self.e2u_substr(line[k:])        # Copy the entire macro (including arguments) untranslated and translate from there-on

        except IndexError as e:
            eprint("ERROR - End of string arrived before macro ended - line: " + line)
            raise e


# We use click to access the arguments, commands and flags

@click.command()            # Essential to get click working
@click.argument('file')        # Declare a mandatory argument which will be the input file
@click.option('--urdu-to-english', '-u', is_flag=True, help="Convert all Urdu characters to English")        # Optional Flag which decides if we are translating from urdu to english
@click.option('--english-to-urdu', '-e', is_flag=True, help="Convert all English characters to Urdu")
@click.option('--latex', '-l', is_flag=True, help="Convert Urdu characters in LaTeX file to English while preserving LaTeX commands and text wrapped in \en{}")
def main(file, **kwargs):

    with open(file) as fin:

        t = Translate()   # Create Translate object
        t.read(fin)   # Pass in file stream to enable translation

        if kwargs['urdu_to_english']:            # The options passed are stored in the 'kwargs' dictionary received by this function ('main')
            t.urdu_to_english()

        elif kwargs['english_to_urdu']:
            t.english_to_urdu()

        elif kwargs['latex']:
            t.latex()

        else:
            print("Missing conversion flag. See --help.")


if __name__ == '__main__':

    main()
