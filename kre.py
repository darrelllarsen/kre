#KRE: Support for Korean regular expression searches.
#Version 0.5.1
#Author: Darrell Larsen
#
#Distributed under GNU General Public License v3.0

"""IMPLEMENTED: COMPILE, FINDALL, FINDITER, FULLMATCH, MATCH, SEARCH
MOSTLY IMPLEMENTED: KRE.Match OBJECTS

This module is built on top of re.  See re documentation for information
on special characters, etc, not affected by this module.

This module provides support for conducting regular expression searches
over Unicode strings containing Korean text.  This is designed for users
wishing to search for Korean text at the sub-syllable level; those wishing 
to conducted re searches using full Korean syllables can do so using the 
standard re module.  This module breaks Korean syllables up 
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

[ㄱ-ㅎ] : matches all Korean consonants, also includes null ㅇ in initial position
[ㅏ-ㅣ] : matches all Korean vowels
[ㄱ-ㅣ] : matches all Korean letters

By default, syllable-final jamo are NOT split (i.e. ㅄ is treated as a 
single character; it is not split into ㅂㅅ), though the option to split 
these up may be implemented later.  Likewise, vowels such as ㅖ and ㅢ are
treated as single characters by default.

By default, kre does NOT track boundaries between syllable characters, even if 
the search string is entered as a syllabary (e.g. 일 rather than ㅇㅣㄹ).  Thus, 
a search for 'ㅣㄹ' will match both '일' and '이라'.  To track boundaries, set 
boundaries=True.  The default boundary symbol is the semicolon <;> and may be 
changed using boundary_symbol=new_symbol."""

import re, KO

"""Section: Constants"""
trad_dipthongs = '[ㅑㅒㅖㅛㅠㅘㅙㅝㅞㅟ]'
dipthongs = '[ㅑㅒㅖㅛㅠㅘㅙㅚㅝㅞㅟㅢ]'

"""Section: kre_MatchObject
This mimics the _sre.SRE_Match object whenever possible.  A few additional 
methods are defined to allow the user to obtain data on both the original
and modified strings created by kre."""

class KRE_Match:
    def __init__(self, endpos = None, lastgroup = None, lastindex = None, pos = 0, re = None, regs = None, string = None, kre = None, kre_pos = 0, kre_endpos = None, index_mapping = None, kre_string = None):
       
        self.endpos =  endpos #will be int; last index position==len(self.string)
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
        """end([group=0]) -> int.
        Return index of the end of the substring matched by group."""#VERIFIED?
        return self.regs[0][1]

    def expand():
        """expand(template) -> str.
        Return the string obtained by doing backslash substitution
        on the string template, as done by the sub() method."""#VERIFIED?
        pass
    
    def group(self):
        """group([group1, ...]) -> str or tuple.
        Return subgroup(s) of the match by indices or names.
        For 0 returns the entire match."""#VERIFIED?
        pass

    def groupdict(self):
        """groupdict([default=None]) -> dict.
        Return a dictionary containing all the named subgroups of the match,
        keyed by the subgroup name. The default argument is used for groups
        that did not participate in the match"""
        pass

    def groups(self):
        """groups([default=None]) -> tuple.
        Return a tuple containing all the subgroups of the match, from 1.
        The default argument is used for groups
        that did not participate in the match"""
        pass

    def span(self):
        """span([group]) -> tuple.
        For MatchObject m, return the 2-tuple (m.start(group), m.end(group))."""
        return self.regs[0]       

    def start(self):
        """start([group=0]) -> int.
        Return index of the start of the substring matched by group."""
        return self.regs[0][0]

# --------------------------------------------------------------------
# public interface

def match(pattern, string, flags=0, boundaries=False, boundary_marker=';'):
    """Try to apply the pattern at the start of the linearized string, returning
    a kre_match object, or None if no match was found.

    kre modification: source string and pattern are linearized prior to 
    calling re.match"""
    match = re.match(_linearize(pattern)[0], _linearize(string, boundaries, boundary_marker)[0], flags)

    if match:
        return _make_match_object(pattern, string, match, boundaries, boundary_marker) 
    else:
        return None

def fullmatch(pattern, string, flags=0, boundaries=False, boundary_marker=';'):
    """Try to apply the pattern to all of the string, returning
    a match object, or None if no match was found.
    
    kre modification: source string and pattern are linearized prior to 
    calling re.fullmatch"""
    match = re.fullmatch(_linearize(pattern)[0], _linearize(string, boundaries, boundary_marker)[0], flags)

    if match:
        return _make_match_object(pattern, string, match, boundaries, boundary_marker) 
    else:
        return None

def search(pattern, string, flags=0, boundaries=False, boundary_marker=';'):
    """Scan through string looking for a match to the pattern, returning
    a match object, or None if no match was found.
    
    kre modification: source string and pattern are linearized prior to 
    calling re.search"""
    match = re.search(_linearize(pattern)[0], _linearize(string, boundaries, boundary_marker)[0], flags)

    if match:
        return _make_match_object(pattern, string, match, boundaries, boundary_marker) 
    else:
        return None

def sub(pattern, repl, string, count=0, flags=0, boundaries=False, boundary_marker=';'):
    """Return the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern in string by the
    replacement repl.  repl can be either a string or a callable;
    if a string, backslash escapes in it are processed.  If it is
    a callable, it's passed the match object and must return
    a replacement string to be used.
    
    kre modification: source string and pattern are linearized prior to 
    calling re.sub()"""
    pass

def subn(pattern, repl, string, count=0, flags=0, boundaries=False, boundary_marker=';'):
    """Return a 2-tuple containing (new_string, number).
    new_string is the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern in the source
    string by the replacement repl.  number is the number of
    substitutions that were made. repl can be either a string or a
    callable; if a string, backslash escapes in it are processed.
    If it is a callable, it's passed the match object and must
    return a replacement string to be used.

    kre modification: source string and pattern are linearized prior to 
    calling re.subn()"""
    pass

def split(pattern, string, maxsplit=0, flags=0, boundaries=False, boundary_marker=';'):
    """Split the source string by the occurrences of the pattern,
    returning a list containing the resulting substrings.  If
    capturing parentheses are used in pattern, then the text of all
    groups in the pattern are also returned as part of the resulting
    list.  If maxsplit is nonzero, at most maxsplit splits occur,
    and the remainder of the string is returned as the final element
    of the list.
    
    kre modification: source string and pattern are linearized prior to 
    calling re.split()"""
    pass

def findall(pattern, string, flags=0, boundaries=False, boundary_marker=';'):
    """Return a list of all non-overlapping matches in the string.

    If one or more capturing groups are present in the pattern, return
    a list of groups; this will be a list of tuples if the pattern
    has more than one group.

    Empty matches are included in the result.

    kre modification: source string and pattern are linearized prior to 
    calling re.findall()"""
    match = re.findall(_linearize(pattern)[0], _linearize(string, boundaries, boundary_marker)[0], flags)

    if match:
        regex = compile(_linearize(pattern)[0])
        linearized_string, index_mapping = _linearize(string, boundaries, boundary_marker)
        pos = 0 
        match_list = []
        for item in match:
            sub_match = regex.search(linearized_string, pos)
            source_string_span = _get_span(sub_match, index_mapping)
            match_list.append(string[source_string_span[0]:source_string_span[1]])
            pos = sub_match.span()[1]
        return match_list
    else:
        return None

def finditer(pattern, string, flags=0, boundaries=False, boundary_marker=';'):
    """Return an iterator over all non-overlapping matches in the
    string.  For each match, the iterator returns a match object.

    Empty matches are included in the result.
     
    kre modifications: source string and pattern are linearized prior to 
    calling re.finditer()
    returns list_iterator rather than callable_iterator"""

    #Implementation differs from re.finditer
    match = re.findall(_linearize(pattern)[0], _linearize(string, boundaries, boundary_marker)[0], flags)

    if match:
        regex = compile(_linearize(pattern)[0])
        linearized_string, index_mapping = _linearize(string, boundaries, boundary_marker)
        pos = 0 
        match_list = []
        for item in match:
            sub_match = regex.search(linearized_string, pos)
            match_list.append(_make_match_object(pattern, string, sub_match))
            pos = sub_match.span()[1]
        return iter(match_list)
    else:
        return None


def compile(pattern, flags=0):
    """Compile a regular expression pattern, returning a pattern object.

    kre modification: source string and pattern are linearized prior to 
    calling re.compile()"""
    return re.compile(_linearize(pattern)[0], flags)
    

def purge():
    """Compile a regular expression pattern, returning a pattern object.

    kre modification: none"""
    re.purge()

def template(pattern, flags=0):    
    """Compile a regular expression pattern, returning a pattern object.

    kre modification: source string and pattern are linearized prior to 
    calling re.template()"""
    pass

def escape(pattern):
    """
    Escape all the characters in pattern except ASCII letters, numbers and '_'.

    kre modification: source string and pattern are linearized prior to 
    calling re.escape()"""   
    pass

# --------------------------------------------------------------------
# internals

#Prepare the text, including re expression, by splitting up Korean syllables into individual Korean letters.  By default, syllable boundaries are unmarked, though I intend to implement an optional argument in the future to allow for syllable boundary marking.  (For the time being, one can already distinguish between onsets and codas using a somewhat cumbersome regex syntax).

def _linearize(string, boundaries=False, boundary_marker=';'):
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
                    letter_by_letter = letter_by_letter + boundary_marker
                    index_list.append([new_index, real_index])
                    new_index += 1
            else:
                letter_by_letter = letter_by_letter + symbol
                index_list.append([new_index, real_index])
                new_index += 1

        real_index += 1
 
    return (letter_by_letter, index_list)

def _get_span(match, index_mapping):
    '''Map the index positions of the match to their corresponding positions in the source text''' 
    span_index = list(match.span())
    return (index_mapping[span_index[0]][1], index_mapping[span_index[1]-1][1] + 1)

def _make_match_object(pattern, string, match, boundaries=False, boundary_marker=';'):
    
    linearized_string, index_mapping = _linearize(string, boundaries, boundary_marker)
    match_obj = KRE_Match(
            kre = re.compile(_linearize(pattern)[0]), 
            re = re.compile(pattern), 
            string = string, 
            kre_string = linearized_string, 
            regs = (_get_span(match, index_mapping),), 
            index_mapping = index_mapping
            )
    return match_obj 
