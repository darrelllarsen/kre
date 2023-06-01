#KRE: Support for Korean regular expression searches.
#Version 0.5.2
#Author: Darrell Larsen
#
#Distributed under GNU General Public License v3.0

"""
This module is built on top of re.  See re documentation for information
on special characters, etc, not affected by this module.

This module provides support for conducting regular expression searches
over Unicode strings containing Korean text.  This is designed for users
wishing to search for Korean text at the sub-syllable level; those 
wishing to conducted re searches using full Korean syllables can do so 
using the standard re module.  This module breaks Korean syllables up 
into their composite letters in both the regular expression and the text
to be searched prior to conducting the search.  By default, indices are 
then calculated based on the original input text, and a kre.SRE_Match 
object is returned.  kre.KRE_Match objects are designed to behave like
_sre.SRE_Match objects, with a few additional attributes.  As such, the 
output of this module may usually be handled in the same manner as the 
output of the standard re module. 

With the exception of the set of vowels being placed after the set of 
consonants, the precedence of characters is based the order used in 
South Korean dictionaries (see Unicode chart U3130). Older characters 
are placed after all modern consonants and vowels. 

[ㄱ-ㅎ] : matches all Korean consonants and null ㅇ in initial position
[ㅏ-ㅣ] : matches all Korean vowels
[ㄱ-ㅣ] : matches all Korean letters

By default, syllable-final consonant clusters are NOT split (i.e. ㅄ 
is treated as a single character; it is not split into ㅂㅅ), though 
the option to split these up should be implemented at some point. 
Likewise, vowels such as ㅖ and ㅢ are treated as single characters
by default, but researchers may find it help to be able to split them.

By default, kre does NOT track boundaries between syllable characters, 
even if the search string is entered as a syllabary (e.g. 일 rather 
than ㅇㅣㄹ).  Thus, a search for 'ㅣㄹ' will match both '일' and
'이라'.  To track boundaries, set boundaries=True.  The default 
boundary symbol is the semicolon <;> and may be changed using 
boundary_symbol=new_symbol.


TODO:

    Improve documentation.

    Complete and improve implementation of KRE_Match class. One
    significant consideration is whether to implement the re.Match
    object within the KRE_Match object, or to return the original
    re.Match object on the linearized data along with the KRE_Match
    objects on the unlinearized data.

    Implement the functions sub, subn.

    Implement the kre.Pattern class with methods that call kre functions 
        rather than re functions.

    Improve compile implemention. It should depend on kre.Pattern, as it
        should return a kre.Pattern object rather than a re.Pattern 
        object

    Implement the error exception; may want to add kre-specific 
        exceptions

    finditer should return callable_iterator rather than list_iterator
        (this may depend on the implementation of KRE_Match)

    Allow syllable-final consonant clusters to be split.

"""


import re, KO

class KRE_Match:
    """
    The KRE_Match class is intended to mimic the _sre.SRE_Match object,
    but to provide results based on the positions of the Match objects
    in the original input rather than the linearized input which is fed
    to the re module functions. In essence, it converts a _sre.SRE_Match
    object into a new one by replacing the positional arguments of
    letters to their corresponding index positions in the unlinearized
    text.
    A few additional methods are defined to allow the user to obtain data on
    both the original and modified strings created by kre.

    TODO: this is not yet fully implemented. See todos at top.
    """
    def __init__(self, endpos = None, lastgroup = None, 
            lastindex = None, pos = 0, re = None, regs = None, 
            string = None, kre = None, kre_pos = 0, kre_endpos = None, 
            index_mapping = None, kre_string = None):
       
        self.endpos =  endpos # int; last index pos==len(self.string)
        self.lastgroup = lastgroup
        self.lastindex = lastindex
        self.pos = pos #int
        self.re = re #SRE_Pattern
        self.regs = regs #tuple
        self.string = string
   
        #Supplemental in KRE; SHOULD WE ALSO DOUBLE ENDPOS, ETC?
        self.kre = kre #modified KRE_Pattern
        self.kre_endpos = kre_endpos
        self.kre_pos = kre_pos
        self.kre_string = kre_string
        self.index_mapping = index_mapping

    def __repr__(self):
        return "<kre.KRE_Match object; span=%s, match='%s'>" % (
                self.span(), self.string[self.span()[0]:self.span()[1]])

    def end(self):
        """
        end([group=0]) -> int.
        Return index of the end of the substring matched by group.
        """
        return self.regs[0][1]

    def expand():
        """
        expand(template) -> str.
        Return the string obtained by doing backslash substitution
        on the string template, as done by the sub() method.
        """
        pass
    
    def group(self):
        """
        group([group1, ...]) -> str or tuple.
        Return subgroup(s) of the match by indices or names.
        For 0 returns the entire match.
        """
        pass

    def groupdict(self):
        """
        groupdict([default=None]) -> dict.
        Return a dictionary containing all the named subgroups of the 
        match, keyed by the subgroup name. The default argument is used
        for groups that did not participate in the match
        """
        pass

    def groups(self):
        """
        groups([default=None]) -> tuple.
        Return a tuple containing all the subgroups of the match, from
        1. The default argument is used for groups that did not 
        participate in the match
        """
        pass

    def span(self):
        """
        span([group]) -> tuple.
        For MatchObject m, return the 2-tuple (m.start(group),
        m.end(group)).
        """
        return self.regs[0]       

    def start(self):
        """
        start([group=0]) -> int.
        Return index of the start of the substring matched by group.
        """
        return self.regs[0][0]



### Public interface

def kre_pattern_string(func):
    """
    Decorator for re module which adds additional search options for the
    Korean language

    Args:
        funct: a re function

        Note that the wrapper function accepts keyword arguments not
        present in the re module. These keywords are passed in with the 
        function itselt, but they are removed from kwargs prior to 
        passing kwargs on to the re function.

    Returns:
        kre_object or None: a kre_object containing the search result,
            or None if no result was found
    """

    def wrapper(*args, **kwargs):
        # Set default values of extra kwargs
        kre_kwargs = {'boundaries': False,
                'boundary_marker': ';',
                }

        # Pop kwargs specific to kre
        for key, value in kre_kwargs.items():
            if key in kwargs:
                value = kwargs.pop(key)
       
        # Linearize the pattern and string
        kre_pattern = _linearize(args[0])[0]
        kre_string = _linearize(args[1], 
                boundaries=kre_kwargs['boundaries'],
                boundary_marker=kre_kwargs['boundary_marker'],
                    )[0]

        # Run the re function on the linearized pattern and string
        response = func(kre_pattern, kre_string, **kwargs)

        # If a re.Match object was returned, construct and a KRE_Match 
        # object and return the KRE_Match object
        if response:
            return _make_match_object(args[0], args[1], response,
                    boundaries=kre_kwargs['boundaries'],
                    boundary_marker=kre_kwargs['boundary_marker'],
                    )

        else:
            return response
    return wrapper

@kre_pattern_string
def search(*args, **kwargs):
    return re.search(*args, **kwargs)

@kre_pattern_string
def match(*args, **kwargs):
    return re.match(*args, **kwargs)

@kre_pattern_string
def fullmatch(*args, **kwargs):
    return re.fullmatch(*args, **kwargs)


def sub(pattern, repl, string, count=0, flags=0, boundaries=False, 
        boundary_marker=';'):
    """
    kre modification: source string and pattern are linearized prior to 
    calling re.sub()
    """
    pass

def subn(pattern, repl, string, count=0, flags=0, boundaries=False, 
        boundary_marker=';'):
    """
    kre modification: source string and pattern are linearized prior to 
    calling re.subn()
    """
    pass

def split(pattern, string, maxsplit=0, flags=0, boundaries=False, 
        boundary_marker=';'):
    """
    kre modification: source string and pattern are linearized prior to 
    calling re.split()"""
    pass

def findall(pattern, string, flags=0, boundaries=False, 
        boundary_marker=';'):
    """
    kre modification: source string and pattern are linearized prior to 
    calling re.findall()"""

    # Run re function on linearized pattern and linearized string
    match = re.findall(_linearize(pattern)[0], 
            _linearize(string, boundaries, boundary_marker)[0], flags)

    # For all patterns found, find their position in the original text
    # and return the syllable(s) they are part of
    if match:
        regex = compile(_linearize(pattern)[0])
        linearized_string, index_mapping = _linearize(string, 
                boundaries, boundary_marker)
        pos = 0 
        match_list = []
        for item in match:
            sub_match = regex.search(linearized_string, pos)
            source_string_span = _get_span(sub_match, index_mapping)
            match_list.append(
                    string[source_string_span[0]:source_string_span[1]]
                    )
            pos = sub_match.span()[1]
        return match_list
    else:
        return None

def finditer(pattern, string, flags=0, boundaries=False, 
        boundary_marker=';'):
    """
    kre modifications: 
        source string and pattern are linearized prior to calling 
        re.finditer()

        returns list_iterator rather than callable iterator (see TODOs)
    """

    #Implementation differs from re.finditer

    # Run re function on linearized pattern and linearized string
    match = re.findall(_linearize(pattern)[0], _linearize(string, 
        boundaries, boundary_marker)[0], flags)

    # For all re.Match objects in 
    if match:
        regex = compile(_linearize(pattern)[0])
        linearized_string, index_mapping = _linearize(string, 
                boundaries, boundary_marker)
        pos = 0 
        match_list = []
        for item in match:
            sub_match = regex.search(linearized_string, pos)
            match_list.append(_make_match_object(pattern, string, 
                sub_match))
            pos = sub_match.span()[1]
        return iter(match_list)
    else:
        return None

def compile(pattern, flags=0):
    """
    kre modification: source string and pattern are linearized prior to
    calling re.compile()

    note that this may change in the future; see TODOs
    """
    return re.compile(_linearize(pattern)[0], flags)

def purge():
    """
    kre modification: none; note that this will purge all regular 
    expression caches, not just those created through kre
    """
    re.purge()

def escape(pattern):
    """
    kre modification: none
    """
    re.escape(pattern)

### Private interface


def _linearize(string, boundaries=False, boundary_marker=';'):
    """
    Linearizes input string by splitting up Korean syllables into 
    individual Korean letters.

    Args:
        string (str): input string containing one or more Korean
        characters

    Outputs:
        linear (str): linearized version of input string
        index_list (lst): letter position mapping as a pair containing
            [position_in_output_string, position_in_input_string]
    """

    letter_by_letter = ''
    index_list = []
    real_index = 0
    new_index = 0
    for word in string:
        for symbol in word:
            if KO.isSyllable(symbol) == True:
                for letter in KO.split(symbol):
                    if letter != '':
                        letter_by_letter = letter_by_letter + letter
                        index_list.append([new_index, real_index])
                        new_index += 1
                if boundaries==True:
                    letter_by_letter = letter_by_letter + \
                            boundary_marker
                    index_list.append([new_index, real_index])
                    new_index += 1
            else:
                letter_by_letter = letter_by_letter + symbol
                index_list.append([new_index, real_index])
                new_index += 1

        real_index += 1
 
    return (letter_by_letter, index_list)

def _get_span(match, index_mapping):
    """
    Map the index positions of the match to their corresponding 
    positions in the source text

    Args:
        match: re.Match object carried out over the linearized text
        index_mapping: index_list returned from _linearize function

    Returns:
        list: a list containing the corresponding span positions in the
            original (non-linearized) text
    """

    span_index = list(match.span())
    return (index_mapping[span_index[0]][1], 
            index_mapping[span_index[1]-1][1] + 1)

def _make_match_object(pattern, string, match, boundaries=False, 
        boundary_marker=';'):
    """
    Instantiates a KRE_Match object

    Args:
        pattern: original (unlinearized) pattern
        string: original (unlinearized) string
        match: re.Match object

    Returns:
        KRE.Match object
    """
    
    linearized_string, index_mapping = _linearize(string, boundaries, 
            boundary_marker)
    match_obj = KRE_Match(
            kre = re.compile(_linearize(pattern)[0]), 
            re = re.compile(pattern), 
            string = string, 
            kre_string = linearized_string, 
            regs = (_get_span(match, index_mapping),), 
            index_mapping = index_mapping
            )
    return match_obj 
