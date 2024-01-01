#KRE: Support for Korean regular expression searches.
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
delimiter=new_symbol.


TODO:

    Improve documentation.

    Complete and improve implementation of KRE_Match class. One
    significant consideration is whether to implement the re.Match
    object within the KRE_Match object, or to return the original
    re.Match object on the linearized data along with the KRE_Match
    objects on the unlinearized data.

    Implement the kre.Pattern class with methods that call kre functions 
        rather than re functions.

    Implement the error exception; may want to add kre-specific 
        exceptions

    finditer should return callable_iterator rather than list_iterator
        (this may depend on the implementation of KRE_Match)

"""

import re
from . import KO

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
            string = None, kre = None, lin2syl_map = None, 
            linear = None, Match=None):
       
        self.endpos =  endpos # int; last index pos==len(self.string)
        self.lastgroup = lastgroup
        self.lastindex = lastindex
        self.pos = pos #int
        self.re = re #SRE_Pattern
        self.regs = regs #tuple
        self.string = string

        # underlying re.Match object 
        # contains same attributes as above but for linearized string
        self.Match = Match 
   
        #Supplemental in KRE; SHOULD WE ALSO DOUBLE ENDPOS, ETC?
        self.kre = kre #modified KRE_Pattern
        self.linear = linear

        # Following maps linear indices to original string indices
        self.lin2syl_map = lin2syl_map

    def __repr__(self):
        return "<kre.KRE_Match object; span=%s, match='%s'>" % (
                self.span(), self.string[self.span()[0]:self.span()[1]])

    def end(self, *args):
        """
        end([group=0]) -> int.
        Return index of the end of the substring matched by group.
        """
        if not args:
            args = [0,]
        return self.regs[args[0]][1]

    def expand():
        """
        expand(template) -> str.
        Return the string obtained by doing backslash substitution
        on the string template, as done by the sub() method.

        NOTE: not well documented. Example use:
        number = re.match(r"(\d+)\.(\d+)", "24.1632")
        print(number.expand(r"Whole: \1 | Fractional: \2"))
        (output) 'Whole: 24 | Fractional: 1632'

        TODO: When implementing, will need to add argument for degrees 
        of syllabification, as with sub() function.
        
        TODO: Will need to treat linearization of pattern different from
        string. Need to maintain identifiers of named groups such as  
        (?P<숫자>\d+) 
        """
        pass
    
    def group(self, *args):
        """
        group([group1, ...]) -> str or tuple.
        Return subgroup(s) of the match by indices or names.
        For 0 returns the entire match.
        """
        if not args:
            args = [0,]
        res = [self.string[self.span(arg)[0]:self.span(arg)[1]] or None 
                    for arg in args]
        if len(res) == 1:
            return res[0]
        else:
            return tuple(res)

    def groupdict(self):
        """
        groupdict([default=None]) -> dict.
        Return a dictionary containing all the named subgroups of the 
        match, keyed by the subgroup name. The default argument is used
        for groups that did not participate in the match
        """
        inv_map = {value: key for key, value in
                self.re.groupindex.items()}
        return {inv_map[n]: self.group(n) for n in range(1, 
                len(inv_map)+1)}

    def groups(self, default=None):
        """
        groups([default=None]) -> tuple.
        Return a tuple containing all the subgroups of the match, from
        1. The default argument is used for groups that did not 
        participate in the match
        """
        g = []
        for n in range(1, len(self.Match.groups())+1):
            if self.span(n) == (-1, -1):
                g.append(default)
            else:
                g.append(self.string[self.span(n)[0]:self.span(n)[1]])
        return tuple(g)

    def span(self, *args):
        """
        span([group]) -> tuple.
        For MatchObject m, return the 2-tuple (m.start(group),
        m.end(group)).
        """
        if not args:
            args = [0,]
        return self.regs[args[0]]

    def start(self, *args):
        """
        start([group=0]) -> int.
        Return index of the start of the substring matched by group.
        """
        if not args:
            args = [0,]
        return self.regs[args[0]][0]

### Public interface


def search(pattern, string, flags=0, boundaries=False, delimiter=';'):
    return compile(pattern, flags).search(string, 
            boundaries=boundaries,
            delimiter=delimiter)

def match(pattern, string, flags=0, boundaries=False, delimiter=';'):
    return compile(pattern, flags).match(string, 
            boundaries=boundaries,
            delimiter=delimiter)

def fullmatch(pattern, string, flags=0, boundaries=False, delimiter=';'):
    return compile(pattern, flags).fullmatch(string, 
            boundaries=boundaries,
            delimiter=delimiter)

def sub(pattern, repl, string, count=0, flags=0, boundaries=False, 
        delimiter=';', syllabify='extended'):
    """
    Returns unsubstituted characters in the same format as input (i.e.,
    as syllable characters or individual letters) except as affected by 
    the syllabify options.

    syllabify options: 
        'full' (linearize + syllabify entire string)
        'none' (affected characters are output without syllabification)
        'minimal' (affected characters are syllabified prior to output)
        'extended' (will attempt to combine affected characters with
            preceding/following characters to create syllables)
    """
    return compile(pattern, flags).sub(repl, string, count=count,
            boundaries=boundaries, 
            delimiter=delimiter, 
            syllabify=syllabify)

def subn(pattern, repl, string, count=0, flags=0, boundaries=False, 
        delimiter=';', syllabify='extended'):
    """
    Similar to sub(), but returns tuple with count as second element.
    """
    return compile(pattern, flags).subn(repl, string, count=count, 
            boundaries=boundaries,
            delimiter=delimiter, 
            syllabify=syllabify)

def split(pattern, string, maxsplit=0, flags=0, boundaries=False, 
        delimiter=';'):
    return compile(pattern, flags).split(string, maxsplit=maxsplit, 
            boundaries=boundaries, delimiter=delimiter)

def findall(pattern, string, flags=0, boundaries=False, delimiter=';'):
    """
    kre modification: source string and pattern are linearized prior to 
    calling re.findall()
    """
    return compile(pattern, flags).findall(string, 
            boundaries=boundaries,
            delimiter=delimiter)

def finditer(pattern, string, flags=0, boundaries=False, delimiter=';'):
    """
    kre modifications: 
        source string and pattern are linearized prior to calling 
        re.finditer()

        returns list_iterator rather than callable iterator (see TODOs)
    """
    return compile(pattern, flags).finditer(string, 
            boundaries=boundaries,
            delimiter=delimiter)

def compile(pattern, flags=0):
    """
    kre modification: source string and pattern are linearized prior to
    calling re.compile()

    note that this may change in the future; see TODOs
    """
    return _compile(pattern, flags)

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
    return re.escape(pattern)

### Private interface

def _compile(pattern, flags):
    return KRE_Pattern(pattern, flags)

class KRE_Pattern:
    def __init__(self, pattern, flags):
        self.pattern = pattern #original Korean, unlinearized
        self.flags = flags
        self.linear = _Linear(pattern).linear #linear input to compile
        self.Pattern = re.compile(self.linear, flags) # re.Pattern obj
        self.groups = self.Pattern.groups
        self.groupindex = self.Pattern.groupindex

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "kre.compile(%s)" % repr(self.pattern)

    def search(self, string, *args, boundaries=False, delimiter=';'):
        ls = _Linear(string, boundaries=boundaries, delimiter=delimiter)
        match_ = self.Pattern.search(ls.linear, *args)
        if match_:
            return _make_match_object(self.pattern, string, match_,
                    *args,
                    boundaries=boundaries,
                    delimiter=delimiter,
                    )
        else:
            return match_

    def match(self, string, *args, boundaries=False, delimiter=';'):
        ls = _Linear(string, boundaries=boundaries, delimiter=delimiter)
        match_ = self.Pattern.match(ls.linear, *args)
        if match_:
            return _make_match_object(self.pattern, string, match_,
                    *args,
                    boundaries=boundaries,
                    delimiter=delimiter,
                    )
        else:
            return match_
        return re.match(*args, **kwargs)

    def fullmatch(self, string, *args, boundaries=False, delimiter=';'):
        ls = _Linear(string, boundaries=boundaries, delimiter=delimiter)
        match_ = self.Pattern.fullmatch(ls.linear, *args)
        if match_:
            return _make_match_object(self.pattern, string, match_,
                    *args,
                    boundaries=boundaries,
                    delimiter=delimiter,
                    )
        else:
            return match_

    def sub(self, repl, string, count=0, boundaries=False, 
            delimiter=';', syllabify='extended'):
        """
        TODO: limit number of substitions to count
        kre modification: source string and pattern are linearized prior to 
        calling re.subn()

        Returns unsubstituted characters in the same format as input (i.e.,
        as syllable characters or individual letters) except as affected by 
        the syllabify options.

        syllabify options: 
            'full' (linearize + syllabify entire string)
            'none' (affected characters are output without syllabification)
            'minimal' (affected characters are syllabified prior to output)
            'extended' (will attempt to combine affected characters with
                preceding/following characters to create syllables)
        """
        # Linearize string
        ls = _Linear(string, 
                boundaries=boundaries,
                delimiter=delimiter,
                    )
        
        # Find the spans where substitutions will occur.
        matches = self.finditer(ls.linear,
                boundaries=boundaries, delimiter=delimiter)

        # Iterate over matches to extract subbed spans from original string
        subs = dict()
        i = 0 # number non-overlapping sub spans (no increment for shared syllable)
        for n, match_ in enumerate(matches):
            # limit matches to number indicated by count (0=no limit)
            if 0 < count <= n:
                break
            span = match_.span()
            start = ls.lin2syl_map[span[0]]
            end = ls.lin2syl_map[span[1]-1]+1
            if i > 0 and subs[i-1]['original_span'][1] > start:
                subs[i-1]['num_subs'] += 1
                subs[i-1]['original_span'] = (
                        subs[i-1]['original_span'][0], end)
                subs[i-1]['linear_span'] = (
                        subs[i-1]['linear_span'][0], span[1])
            else:
                subs[i] = dict()
                sub = subs[i]
                sub['num_subs'] = 1
                sub['original_span'] = (start, end)
                sub['linear_span'] = span
                i += 1

        # Keep track of extra letters in the subbed syllables which
        # preceded/followed the actual substitution
        for n in range(len(subs)):
            sub = subs[n]
            start = sub['linear_span'][0]
            end = sub['linear_span'][1]
            extra_start = start - ls.get_syl_start(start)
            extra_end = ls.get_syl_end(end-1) - end
            pre_sub_letters = ls.linear[start - extra_start:start]
            post_sub_letters = ls.linear[end:end + extra_end]
            sub['extra_letters'] = (pre_sub_letters,post_sub_letters)

        # Extract the text from the unchanged indices so we can return them
        # without change. (If we use KO.syllabify to reconstruct the entire
        # string, inputs like 가ㅎ (linearized to ㄱㅏㅎ) would be returned 
        # as 갛 even if they weren't matches for substitution. We want to 
        # avoid this.) 
        safe_text = []
        for n in range(len(subs) + 1):
            start = 0 if n == 0 else subs[n-1]['original_span'][1]
            end = len(string) if n == len(subs) else subs[n]['original_span'][0]
            safe_text.append(string[start:end])

        # Carry out substitutions one by one to identify the indices of each 
        # changed section. 
        extra = 0
        prev_string = ls.linear
        num_subs = 0
        for n in range(len(subs)):
            sub = subs[n]
            num_subs = num_subs + sub['num_subs']
            subbed_string = self.Pattern.sub(repl, ls.linear,
                    count=num_subs)

            # Calculate the start and end indices of the inserted substitution
            sub_start = sub['linear_span'][0] + extra
            extra += len(subbed_string) - len(prev_string)
            sub_end = sub['linear_span'][1] + extra

            # Combine the substitution with the extra letters
            syl_text = sub['extra_letters'][0]
            syl_text += subbed_string[sub_start:sub_end]
            syl_text += sub['extra_letters'][1]
            subs[n]['subbed_syl'] = syl_text

            prev_string = subbed_string

        # Attempt to construct Hangul characters to the desired degree of 
        # syllabification.
        output = ''
        for n in range(len(safe_text)):
            output += safe_text[n]
            if n < len(subs):
                new_text = subs[n]['subbed_syl']
                if syllabify == 'minimal': 
                    output += KO.syllabify(new_text)
                elif syllabify == 'extended':
                    new_text = _Linear(new_text).linear
                    if safe_text[n+1]:
                        post = safe_text[n+1][0]
                        safe_text[n+1] = safe_text[n+1][1:]
                        if KO.isSyllable(post):
                            post = ''.join(KO.split(post))
                        new_text += post
                    if output:
                        pre = output[-1]
                        output = output[:-1]
                        if KO.isSyllable(pre):
                            pre = ''.join(KO.split(pre))
                        new_text = pre + new_text
                    output += KO.syllabify(new_text)
                else:
                    output += new_text
        if syllabify == 'full':
            output = KO.syllabify(_Linear(output).linear)
        if syllabify == 'none':
            pass

        return output

    def subn(self, repl, string, count=0, boundaries=False, 
            delimiter=';', syllabify='extended'):
        """
        kre modification: source string and pattern are linearized prior to 
        calling re.subn()
        """
        
        # Must limit substitutions to max of count if != 0
        sub_count = len(self.findall(string,
            boundaries=boundaries, delimiter=delimiter))
        if 0 < count < sub_count:
            sub_count = count

        return (self.sub(repl, string, count=count, 
            boundaries=boundaries, delimiter=delimiter, 
            syllabify=syllabify), sub_count)


    def split(self, string, maxsplit=0, boundaries=False, 
            delimiter=';'):
        """
        kre modification: source string and pattern are linearized prior to 
        calling re.split()"""
        raise NotImplementedError 

    def findall(self, string, *args, boundaries=False, delimiter=';'):
        # Run re function on linearized pattern and linearized string
        ls = _Linear(string, boundaries=boundaries,
                delimiter=delimiter)
        
        match_ = self.Pattern.findall(ls.linear, *args)

        # For all patterns found, find their position in the original text
        # and return the syllable(s) they are part of
        if match_:
            pos = 0 
            match_list = []
            for item in match_:
                sub_match = self.search(ls.linear, pos,
                        boundaries=boundaries, delimiter=delimiter)
                source_string_span = _get_regs(sub_match, 
                        ls.lin2syl_map, boundaries, delimiter)[0]
                match_list.append(
                        string[source_string_span[0]:source_string_span[1]]
                        )
                pos = sub_match.span()[1]
            return match_list
        else:
            return None

    def finditer(self, string, *args, boundaries=False, delimiter=';'):
        """
        kre modifications: 
            source string and pattern are linearized prior to calling 
            re.finditer()

            returns list_iterator rather than callable iterator (see TODOs)
        """

        #Implementation differs from re.finditer
        ls = _Linear(string, boundaries=boundaries, 
                delimiter=delimiter)

        match_ = self.Pattern.finditer(ls.linear, *args)

        # For all re.Match objects in match_
        if match_:
            pos = 0 
            match_list = []
            for item in match_:
                sub_match = self.search(ls.linear, pos)
                match_list.append(_make_match_object(self.pattern, string, 
                    sub_match, *args, boundaries=boundaries,
                    delimiter=delimiter))
                pos = sub_match.span()[1]
            return iter(match_list)
        else:
            return None

class _Linear:
    def __init__(self, string, boundaries=False, delimiter=';'):
        self.boundaries = boundaries
        self.delimiter = delimiter
        self.original = string
        self.linear, self.lin2syl_map = self._linearize()
        self.syl_span_map = self._get_syl_span_map()

    def _linearize(self):
        """
        Linearizes input string by splitting up Korean syllables into 
        individual Korean letters.

        Args:
            string (str): input string containing one or more Korean
            characters

        Outputs:
            linearized_str (str): linearized version of input string
            lin2syl_mapping (lst): index of character positions in input string
                ex. given input 한국:
                    linearized_str -> ㅎㅏㄴㄱㅜㄱ
                    lin2syl_mapping[4] -> 1 (ㅜ in index 1 in input)
        """
        

        linearized_str = ''
        lin2syl_mapping = []
        linear_index = 0
        just_saw_boundary = False

        for char_ in self.original:
            if KO.isSyllable(char_):
                
                # add boundary symbol in front of Korean syllable
                if self.boundaries==True and not just_saw_boundary:
                    linearized_str += self.delimiter
                    lin2syl_mapping.append(linear_index)

                # append the linearized string
                for letter in ''.join(KO.split(char_, split_coda=True)):
                    linearized_str += letter
                    lin2syl_mapping.append(linear_index)

                # add boundary symbol at end of Korean syllable
                if self.boundaries==True:
                    linearized_str += self.delimiter
                    lin2syl_mapping.append(linear_index)
                
                linear_index += 1

            else:
                linearized_str += char_
                lin2syl_mapping.append(linear_index)
                linear_index += 1
            just_saw_boundary = (linearized_str[-1] == self.delimiter)
        return (linearized_str, lin2syl_mapping)

    def _get_syl_span_map(self):
        # Note: to get syllable span (start and end indices) for any given
        # linearized Korean letter, use syl_span_map[lin_to_syl_map[idx]]
        syl_span_map = []
        start = 0
        mapped_idx = 0
        for n in range(len(self.lin2syl_map)+1):
            if n == len(self.lin2syl_map):
                syl_span_map.append((start, n))
            elif self.lin2syl_map[n] == mapped_idx:
                n += 1
            else:
                syl_span_map.append((start, n))
                start = n
                mapped_idx += 1
        return syl_span_map

    def _show_alignment(self):
        for n, pair in enumerate(self.syl_span_map):
            print(n, self.original[n], '\t-> ', pair, self.linear[pair[0]:pair[1]])

    def get_syl_span(self, idx):
        return self.syl_span_map[self.lin2syl_map[idx]]

    def get_syl_start(self, idx):
        return self.get_syl_span(idx)[0]

    def get_syl_end(self, idx):
        return self.get_syl_span(idx)[1]

def _make_match_object(pattern, string, Match, *args, boundaries=False, 
        delimiter=';'):
    """
    Instantiates a KRE_Match object

    Args:
        pattern: original (unlinearized) pattern
        string: original (unlinearized) string
        Match: re.Match object

    Returns:
        KRE_Match object
    """

    # Extract pos, endpos args, if provided
    pos_args = [0, len(string)] # re defaults
    if args:
        for n, arg in enumerate(args):
            pos_args[n] = arg

    ls = _Linear(string, boundaries, delimiter)
    lp = _Linear(pattern)
    match_obj = KRE_Match(
            kre = re.compile(lp.linear), 
            re = re.compile(pattern), 
            string = string, 
            linear = ls.linear,
            pos = pos_args[0],
            endpos = pos_args[1],
            regs = _get_regs(Match, ls.lin2syl_map, boundaries,
                delimiter),
            lin2syl_map = ls.lin2syl_map,
            Match = Match,
            )
    return match_obj 

def _get_regs(Match, lin2syl_mapping, boundaries=False, delimiter=';'):
    # TODO: update doc
    """
    Map the index positions of the match to their corresponding 
    positions in the source text

    Args:
        Match: re.Match object carried out over the linearized text
        lin2syl_mapping: index_list returned from _linearize function

    Returns:
        list: a list containing the corresponding span positions in the
            original (non-linearized) text
    """
    regs = []
    for n in range(len(Match.groups())+1):
        span = Match.span(n)
        # (-1, -1) used for groups that did not contibute to the match
        if span == (-1, -1):
            regs.append(span)
            continue
        elif boundaries == True and Match.group(n)[0] == delimiter:
            span_start = lin2syl_mapping[span[0]+1]
        else:
            span_start = lin2syl_mapping[span[0]]

        # re.MATCH object's span end is index *after* final character,
        # so, we need to subtract one to get the index of the character 
        # to map back to the original, then add one to the result to 
        # get the index after this character
        if boundaries == True and Match.group(n)[-1] == delimiter:
            span_end = lin2syl_mapping[span[1]-2] + 1
        else:
            span_end = lin2syl_mapping[span[1]-1] + 1

        regs.append((span_start, span_end))
    
    return tuple(regs)
