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
    Implement exceptions; may want to add kre-specific exceptions

NOTE:
    re.finditer returns class 'callable_iterator', where kre returns
    'list_iterator'. Unclear whether there is any practical difference.
"""

import re

# Make flags from re library accessible 
from re import (A, ASCII, DEBUG, DOTALL, I, IGNORECASE, L, LOCALE, M,
        MULTILINE, T, TEMPLATE, U, UNICODE, VERBOSE, X)
from .tools import _tools
from .tools._constants import _COMBINED_FINALS

_settings = {"boundaries": False,
        "delimiter": ";",
        "syllabify": "minimal",
        "empty_es": True,
        "es_idx": "accurate",
        }

def set_defaults(dictionary):
    OPTIONS = {"boundaries": [True, False],
            "empty_es": [True, False],
            "syllabify": ["none", "minimal", "extended", "full"],
            "es_idx": ["accurate", "start", "end"],
            }
    for key, val in dictionary.items():
        if key not in _settings.keys():
            raise ValueError(f"{key} is not an available setting")
        elif key in OPTIONS.keys():
            if val in OPTIONS[key]:
                _settings[key] = val
            else:
                raise ValueError(
                        f"{val} is not a valid option for '{key}'")
        else:
            _settings[key] = val


### Public interface

def search(pattern, string, flags=0, **kwargs):
    return compile(pattern, flags, **kwargs).search(string, 
            **kwargs)

def match(pattern, string, flags=0, **kwargs):
    return compile(pattern, flags, **kwargs).match(string, 
            **kwargs)

def fullmatch(pattern, string, flags=0, **kwargs):
    return compile(pattern, flags, **kwargs).fullmatch(string, 
            **kwargs)

def sub(pattern, repl, string, count=0, flags=0, **kwargs):
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
    return compile(pattern, flags, **kwargs).sub(repl, string, 
            count=count, **kwargs)

def subn(pattern, repl, string, count=0, flags=0, **kwargs):
    """
    Similar to sub(), but returns tuple with count as second element.
    """
    return compile(pattern, flags, **kwargs).subn(repl, string, count=count, 
            **kwargs)

def split(pattern, string, maxsplit=0, flags=0, **kwargs):
    return compile(pattern, flags, **kwargs).split(string, maxsplit=maxsplit, 
            **kwargs)

def findall(pattern, string, flags=0, **kwargs):
    return compile(pattern, flags, **kwargs).findall(string, **kwargs)

def finditer(pattern, string, flags=0, **kwargs):
    return compile(pattern, flags, **kwargs).finditer(string,**kwargs)

def compile(pattern, flags=0, **kwargs):
    return KRE_Pattern(pattern, flags, **kwargs)

def purge():
    # note that this will purge all regular expression caches, 
    # not just those created through kre
    re.purge()

def escape(pattern):
    return re.escape(pattern)

### Private interface

class KRE_Pattern:
    def __init__(self, pattern, flags, **kwargs):
        self.pattern = pattern #original Korean, unlinearized
        self.flags = flags
        self.boundaries = kwargs.pop("boundaries",
                _settings["boundaries"])
        self.delimiter = kwargs.pop("delimiter",
                _settings["delimiter"])
        self.mapping = Mapping(pattern, boundaries=False)
        self.linear = self.mapping.linear #linear input to compile
        self.Pattern = re.compile(self.linear, flags) # re.Pattern obj
        self.groups = self.Pattern.groups

        # Extract from compiled non-linearized string so access format
        # can match input format
        self._re = re.compile(self.pattern)
        self.groupindex = self._re.groupindex

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "kre.compile(%s)" % repr(self.pattern)

    def search(self, string, *args, **kwargs):
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)
        return self._search(sm, *args, **kwargs)

    def _search(self, string_mapping, *args, **kwargs):
        sm = string_mapping
        pos_args, iter_span = self._process_pos_args(sm, *args)
        match_ = self.Pattern.search(sm.linear, *pos_args)
        if match_:
            return KRE_Match(self, sm, match_, *args, **kwargs)
        else:
            return match_

    def match(self, string, *args, **kwargs):
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)
        pos_args, iter_span = self._process_pos_args(sm, *args)
       
        for span in iter_span:
            match_ = self.Pattern.match(sm.linear, *span)
            if match_:
                return KRE_Match(self, sm, match_, *args, 
                        **kwargs)
        else:
            return match_

    def fullmatch(self, string, *args, **kwargs):
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)
        pos_args, iter_span = self._process_pos_args(sm, *args)

        for span in iter_span:
            match_ = self.Pattern.fullmatch(sm.linear, *span)
            if match_:
                return KRE_Match(self, sm, match_, *args, 
                        **kwargs)
        else:
            return match_

    def sub(self, repl, string, count=0, **kwargs):
        """
        Returns unsubstituted characters in the same format as input (i.e.,
        as syllable characters or individual letters) except as affected by 
        the syllabify options.

        syllabify options: 
            'none' (affected characters are output without syllabification)
            'minimal' (affected characters are syllabified prior to output)
            'extended' (will attempt to combine affected characters with
                the immediately preceding/following characters to create 
                syllables when it minimizes stand-alone Korean letters)
            'full' (linearize + syllabify entire string; deletes
                    boundaries prior to syllabifying string)
        """
        # Linearize string
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)

        return self._sub(repl, sm, count=count, **kwargs)

    def _sub(self, repl, string_mapping, count=0, **kwargs):
        sm = string_mapping
        subs = dict()
        matches = self._finditer(sm)
        syllabify = kwargs.pop("syllabify", _settings["syllabify"])

        def compute_spans():
            i = 0 # number non-overlapping sub spans (no increment for shared syllable)
            for n, match_ in enumerate(matches):
                # limit matches to number indicated by count (0=no limit)
                if 0 < count <= n:
                    break

                lin_span = match_.Match.span()
                del_span = match_._del_span

                i = add_spans(subs, i, lin_span, del_span)

        def add_spans(subs, i, lin_span, del_span):
            # CASE: multiple subs from same syllable
            if i > 0 and subs[i-1]['del_span'][1] > del_span[0]:
                prev = subs[i-1]
                prev['num_subs'] += 1

                # update endpos
                prev['del_span'] = (prev['del_span'][0], del_span[1])
                prev['lin_span'] = (prev['lin_span'][0], lin_span[1])

            # DEFAULT CASE:
            else:
                subs[i] = dict()
                sub = subs[i]
                sub['num_subs'] = 1
                sub['del_span'] = del_span
                sub['lin_span'] = lin_span
                i += 1
            return i

        def get_outlying_chars():
            # Keep track of extra letters in the subbed syllables which
            # preceded/followed the actual substitution
            for sub in subs.values():
                sub_start, sub_end = sub['lin_span']

                # Case: string-final empty string match
                if sub_start == len(sm.linear):
                    syl_start = len(sm.linear)
                # Normal case
                else:
                    syl_start = sm._get_syl_start(sub_start)
                syl_end = sm._get_syl_end(sub_end-1)

                pre_sub_letters = sm.linear[syl_start:sub_start]
                post_sub_letters = sm.linear[sub_end:syl_end]

                sub['extra_letters'] = (pre_sub_letters,post_sub_letters)
           
        def extract_unchanged_spans():
            # Extract the text from the unchanged indices so we can return them
            # without change. (If we use tools.syllabify to reconstruct the entire
            # string, inputs like 가ㅎ (linearized to ㄱㅏㅎ) would be returned 
            # as 갛 even if they weren't matches for substitution. We want to 
            # avoid this.) 
            unchanged_text = []
            for n in range(len(subs) + 1):
                start = 0 if n == 0 else subs[n-1]['del_span'][1]
                end = len(sm.delimited) if n == len(subs) else subs[n]['del_span'][0]
                unchanged_text.append(sm.delimited[start:end])
            return unchanged_text

        def make_substitutions():
            # Carry out substitutions one by one* to identify the indices of each 
            # changed section. *Multiple subs affecting same syllable are
            # carried out at same time.
            extra = 0 # Tracks added/substracted number of letters after sub
            prev_string = sm.linear
            num_subs = 0 # For carrying out subs incrementally
            for sub in subs.values():
                # Carry out next substitution(s)
                num_subs = num_subs + sub['num_subs']
                subbed_string = self.Pattern.sub(repl, sm.linear,
                        count=num_subs)

                # Calculate the start and end indices of the inserted substitution
                sub_start = sub['lin_span'][0] + extra
                extra += len(subbed_string) - len(prev_string)
                sub_end = sub['lin_span'][1] + extra

                # Combine the substitution(s) with the extra letters from
                # affected syllables
                syl_text = sub['extra_letters'][0]
                syl_text += subbed_string[sub_start:sub_end]
                syl_text += sub['extra_letters'][1]
                sub['subbed_syl'] = syl_text

                prev_string = subbed_string

        def reconstruct():
            # Attempt to construct Hangul characters to the desired degree of 
            # syllabification.
            output = ''
            for n in range(len(unchanged_text)):
                output += unchanged_text[n]
                if n < len(subs):
                    new_text = subs[n]['subbed_syl']
                    if syllabify == 'minimal': 
                        output += _tools.syllabify(new_text)
                    elif syllabify == 'extended':
                        # Remove one character from the unchanged text
                        # that follows the current substitution. The 
                        # character will be in original (nonlinearized)
                        # form
                        if unchanged_text[n+1] != '':
                            post = unchanged_text[n+1][0]
                            unchanged_text[n+1] = unchanged_text[n+1][1:]
                            if _tools.isSyllable(post):
                                post = ''.join(_tools.split(post))
                            new_text += post
                        # Remove the character immediately preceding the
                        # current substitutions. The character will have
                        # been syllabified in the previous loop.
                        if output:
                            pre = output[-1]
                            output = output[:-1]
                            if _tools.isSyllable(pre):
                                pre = ''.join(_tools.split(pre))
                            new_text = pre + new_text
                        output += _tools.syllabify(new_text,
                                linearize_first=True)
                    else:
                        output += new_text

            # Remove the delimiter from the output
            # This should precede 'full' syllabify option
            if sm.boundaries == True:
                output = output.replace(sm.delimiter, '')

            if syllabify == 'full':
                output = _tools.syllabify(Mapping(output).linear)

            if syllabify == 'none':
                pass
            return output

        ### MAIN
        compute_spans()
        get_outlying_chars()
        unchanged_text = extract_unchanged_spans()
        make_substitutions()
        output = reconstruct()

        return output

    def subn(self, repl, string, count=0, **kwargs):
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)
        
        # Limit substitutions to max of count if != 0
        res = self._findall(sm, **kwargs)
        if res:
            sub_count = len(res)
        else:
            sub_count = 0
        if 0 < count < sub_count:
            sub_count = count

        return (self._sub(repl, sm, count=count, **kwargs), sub_count)

    def split(self, string, maxsplit=0, **kwargs):
        raise NotImplementedError 

    def findall(self, string, *args, **kwargs):
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)
        return self._findall(sm, *args, **kwargs)

    def _findall(self, string_mapping, *args, **kwargs):
        matches = self._finditer(string_mapping, *args,
                **kwargs)
        return [match_.group() for match_ in matches] or None

    def finditer(self, string, *args, **kwargs):
        sm = Mapping(string, boundaries=self.boundaries, delimiter=self.delimiter)
        return self._finditer(sm, *args, **kwargs)

    def _finditer(self, string_mapping, *args, **kwargs):
        sm = string_mapping
        pos_args, _ = self._process_pos_args(sm, *args)

        match_ = self.Pattern.finditer(sm.linear, *pos_args)

        # For all re.Match objects in match_
        match_list = []
        for item in match_:
            cur_match = item
            match_list.append(KRE_Match(self, sm, 
                cur_match, *args, **kwargs))
        return iter(match_list)

    def _process_pos_args(self, _linear, *args):
        """
        Map the pos and endpos args to their corresponding linear positions.

        When boundaries == True, pos and endpos expand to include boundaries

        Returns:
            tuple: pos and endpos, mapped to position in linear string
            iter_span (tuple of tuples): tuples of indices for `match` 
                and `fullmatch` to iterate through, if any (empty if no
                pos arg was provided)
        """
        output = []
        map_ = _linear.lin2orig
        orig_size = len(_linear.original)
        iterate = True
        iter_span = []

        ### Fill in missing args
        # No pos arg?
        if len(args) == 0:
            iterate = False
            args = [0]
        # No endpos arg? 
        if len(args) == 1:
            args = [args[0], len(map_)]

        ### Limit pos / endpos to string length
        for arg in args:
            if 0 <= arg < orig_size:
                output.append(map_.index(arg))
            # >= length of string?
            elif arg >= orig_size:
                output.append(len(map_)) 
            # Less than 0?
            else:
                output.append(0)
        
        if iterate == True:
            # which indices should be iterated through?
            for n, item in enumerate(map_[output[0]:], output[0]):
                if item == map_[output[0]]:
                    iter_span.append(tuple([n, output[1]]))
                else:
                    break
        else:
            iter_span.append(output)


        # If pos is preceded by a boundary marker, expand to include it
        # No need to do this for endpos
        if output[0] > 0:
            if map_[output[0]-1] == None:
                output[0] -= 1
                if iterate == True:
                    iter_span = [tuple(output)] + iter_span

        return tuple(output), tuple(iter_span)

class Mapping:
    """
    Contains three levels of representation of the input, maps between
    the levels, and methods for navigation, string extraction, and
    mapping representation.

    - levels:
        original: input string without alteration
        delimited: same as original if boundaries == False; otherwise, 
            input string with delimiters placed around Korean characters
            (both syllables and letters)
        linear: linearized form of delimited; i.e., Korean characters
            are all replaced with Korean letter sequences
    - maps: 
        del2orig,
            'This is ;한;글;'
        lin2del, 
        del2lin_span, 
        lin2orig
    - example
        - levels:
            original: 'This is 한글ㅋㅋ'
            delimited: 'This is ;한;글;ㅋ;ㅋ;'
            linear: 'This is ;ㅎㅏㄴ;ㄱㅡㄹ;ㅋ;ㅋ;'
        - maps:
            - Note that maps *to* original level map delimiters to None.
            del2orig: (0,1,2,3,4,5,6,7,None,8,None,9,None,10,None,11,None)
                       T,h,i,s, ,i,s, ,;...,한,;...,글,;...,ㅋ,;...,ㅋ,;...
            lin2del: (0,1,2,3,4,5,6,7,8,9,9,9,10,11,11,11,12,13,14,15,16)
                      T,h,i,s, ,i,s, ,;,ㅎ,ㅏ,ㄴ,;,ㄱ,ㅡ,ㄹ,;ㅋ,;,ㅋ,;
            lin2orig: (0,1,2,3,4,5,6,7,None,8,8,8,None,9,9,9,None,10,None,11,None)
        - span maps:
            - Note that span maps *to* original level map delimiters to
              indices of the form (n, n) (where start=end).
            del2lin_span:
                    ((0,1), #T
                    (1,2), #h
                    (2,3), #i
                    (3,4), #s
                    (4,5), # 
                    (5,6), #i
                    (6,7), #s
                    (7,8), # 
                    (8,9), #;
                    (9,12), #한 -> ㅎㅏㄴ
                    (12,13), #;
                    (13,16), #글 -> ㄱㅡㄹ
                    (16,17), #;
                    (17,18), ㅋ
                    (18,19), #;
                    (19,20), ㅋ
                    (20,21), #;


    Developer notes: 
    - new levels and their mappings should be created simultaneously
    - abbreviations: {delimiter: del; original: orig; linear: lin}
        - use abbreviations exclusively within functions
        - use full name as class attribute
    - 'forward' means from original -> delimited -> linear
    - 'backward' means from linear -> delimited -> original
    """
    def __init__(self, string, **kwargs):
        self.boundaries = kwargs.get("boundaries",
        _settings["boundaries"])
        self.delimiter = kwargs.get("delimiter",
        _settings["delimiter"])

        # levels of representation and mappings
        self.original = string
        self.delimited, self.del2orig = self._delimit()
        self.linear, self.lin2del = self._linearize()
        self.lin2orig = tuple(self.del2orig[n] for n in self.lin2del)

        # forward spans
        self.del2lin_span = self._get_forward_span('del', 'lin')
        self.orig2del_span = self._get_forward_span('orig', 'del')
        self.orig2lin_span = self._get_forward_span('orig', 'lin')

        # backward spans
        self.del2orig_span = self._get_backward_span('del', 'orig')
        self.lin2orig_span = self._get_backward_span('lin', 'orig')
        self.lin2del_span = self._get_backward_span('lin', 'del')

    def validate_delimiter(self) -> None:
        """
        When boundaries == True, checks whether choice of delimiter is
        present in string.
        
        This method should only be called on the 'string' input; it
        should not be called on the 'pattern' input.
        """
        if self.boundaries == True and self.delimiter in self.original:
            raise ValueError('Delimiter must not be present in original string')

    def _delimit(self): # returns (del_str, tuple(del2orig_))
        del_str = ''
        del2orig_ = []
        orig_idx = 0
        just_saw_delimiter = False

        for char_ in self.original:
            if _tools.isHangul(char_):
                
                # add delimiter in front of Korean syllable
                if self.boundaries==True and not just_saw_delimiter:
                    del_str += self.delimiter
                    del2orig_.append(None)

                # add the character
                del_str += char_
                del2orig_.append(orig_idx)

                # add delimiter symbol at end of Korean syllable
                if self.boundaries==True:
                    del_str += self.delimiter
                    del2orig_.append(None)

            else:
                del_str += char_
                del2orig_.append(orig_idx)

            orig_idx += 1
            just_saw_delimiter = (del_str[-1] == self.delimiter)

        return (del_str, tuple(del2orig_))

    def _linearize(self): # returns (lin_str, tuple(lin2del_))
        """
        Linearizes delimited string by splitting up Korean syllables into 
        individual Korean letters.

        Outputs:
            lin_str (str): linearized version of delimited string
            lin2del_ (tuple): index of character positions in delimited string
                ex. given input 한국:
                    lin_str -> ㅎㅏㄴㄱㅜㄱ
                    lin2del_[4] -> 1 (ㅜ in index 1 in input)
        """

        lin_str = ''
        lin2del_ = []
        lin2orig_str = []
        lin_idx = 0

        for char_ in self.delimited:
            # Case: Korean syllable character (e.g., '글')
            if _tools.isSyllable(char_):
                
                # append the linearized string
                for letter in ''.join(_tools.split(char_, split_codas=True)):
                    lin_str += letter
                    lin2del_.append(lin_idx)

                lin2orig_str.append(char_)

            # Case: complex coda character (e.g., 'ㄺ')
            elif char_ in _COMBINED_FINALS.keys():
                # append the linearized string
                for letter in ''.join(_tools.split_coda(char_)):
                    lin_str += letter
                    lin2del_.append(lin_idx)

                lin2orig_str.append(char_)

            else:
                lin_str += char_
                lin2del_.append(lin_idx)
            lin_idx += 1
        return (lin_str, tuple(lin2del_))

    def _get_forward_span(self, from_, to):
        MAP_OPTIONS = {'lin2del': self.lin2del,
                'lin2orig': self.lin2orig,
                'del2orig': self.del2orig,
                }
        SOURCE_OPTIONS = {'del': self.delimited,
                'orig': self.original,
                }

        selection = to + '2' + from_
        map_ = MAP_OPTIONS[selection]
        _pam = map_[::-1] # reverse map_
        span_map = []
        source_length = len(SOURCE_OPTIONS[from_])

        for n in range(source_length):
            start = map_.index(n)
            end = len(map_) - _pam.index(n)
            span_map.append((start, end))

        return tuple(span_map)

    def _get_backward_span(self, from_, to):
        MAP_OPTIONS = {'lin2del': self.lin2del,
                'lin2orig': self.lin2orig,
                'del2orig': self.del2orig,
                }
        selection = from_ + '2' + to
        map_ = MAP_OPTIONS[selection]
        span_map = []
        end_idx = 0

        for idx in map_:
            if idx != None:
                end_idx = idx + 1
                span_map.append((idx, end_idx))
            else:
                span_map.append((end_idx, end_idx))

        return tuple(span_map)

    def _get_syl_span(self, idx):
        return self.del2lin_span[self.lin2del[idx]]

    def _get_syl_start(self, idx):
        return self._get_syl_span(idx)[0]

    def _get_syl_end(self, idx):
        return self._get_syl_span(idx)[1]

    def show_original_alignment(self):
        print('Index\tOriginal\torig2del_span\tdel2orig\tdel2orig_span\tDelimited\tdel2lin_span\tLinear')
        for n, idx in enumerate(self.del2orig):
            orig_idx = idx if idx != None else ''
            orig_str = '' if orig_idx == '' else self.original[orig_idx]
            start, end = self.del2lin_span[n]
            print(f'{n}|{orig_idx}', '\t', orig_str, '\t\t',
                    '\t' if self.del2orig[n] == None else
                            self.orig2del_span[self.del2orig[n]], '\t',
                    self.del2orig[n], '\t\t',
                    self.del2orig_span[n], '\t', self.delimited[n],
                    '\t\t', self.del2lin_span[n], '\t',
                    self.linear[start:end])

    def show_linear_alignment(self):
        print('Index\tLinear\tlin2del\tlin2del_span\tDelimited\tlin2orig\tlin2orig_span\tOriginal')
        for n, span_ in enumerate(self.lin2orig_span):
            d2o_span = self.del2orig_span[self.lin2del[n]]
            print(n, '\t', self.linear[n], '\t', self.lin2del[n], '\t', self.lin2del_span[n],
                    '\t', self.delimited[slice(*self.lin2del_span[n])],
                    '\t\t', self.lin2orig[n], '\t\t', span_,'\t', self.original[slice(*span_)])

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
    """
    def __init__(self, pattern_obj, string_mapping, Match_obj, *args, 
            **kwargs):

        self.string_mapping = string_mapping
        # underlying re.Match object 
        # contains same attributes as above but for linearized string
        self.Match = Match_obj
        self.empty_es = kwargs.pop("empty_es", _settings["empty_es"])
        self.es_idx = kwargs.pop("es_idx", _settings["es_idx"])

        self.string = self.string_mapping.original
        self.re = pattern_obj # kre.KRE_Pattern object (kre.compile)
        self._re = self.re.Pattern # re.Pattern object (re.compile)
        self.pos, self.endpos = self._get_pos_args(*args)
        self.regs = self._get_regs() #tuple
        self.lastindex = Match_obj.lastindex
        self.lastgroup = self._get_lastgroup()
   
        self.linear = string_mapping.linear
        self._del_span = self._get_del_span()

    def __repr__(self):
        return "<kre.KRE_Match object; span=%r, match=%r>" % (
                self.span(), self.group(0))

    def __getitem__(self, group):
        return self.group(group)

    def _get_pos_args(self, *args):
        pos_args = [0, len(self.string)] # re defaults
        if args:
            for n, arg in enumerate(args):
                pos_args[n] = arg
        return pos_args

    def expand() -> str:
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
        raise NotImplementedError 
    
    def group(self, *args) -> str or tuple:
        """
        group([group1, ...]) -> str or tuple.
        Return subgroup(s) of the match by indices or names.
        For 0 returns the entire match.
        """
        res = []

        if not args:
            args = [0,]
        for arg in args:
            idx = arg
            # convert named groups to group indices
            if isinstance(idx, str):
                idx = self.re.groupindex[idx]
            # non-matching capture group?
            if self.regs[idx] == (-1, -1):
                res.append(None)
            # empty string match? (see discussion on special treatment)
            elif self.empty_es == True and self.Match.group(idx) == '':
                res.append('')
            else:
                res.append(self.string[slice(*self.regs[idx])])

        if len(res) == 1:
            return res[0]
        else:
            return tuple(res)

    def groupdict(self, default=None) -> dict:
        """
        groupdict([default=None]) -> dict.
        Return a dictionary containing all the named subgroups of the 
        match, keyed by the subgroup name. The default argument is used
        for groups that did not participate in the match
        """
        inv_map = {value: key for key, value in
                self.re.groupindex.items()}

        apply_default = lambda d: default if d == None else d

        return {inv_map[n]: apply_default(self.group(n)) for n in inv_map.keys()}

    def groups(self, default=None) -> tuple:
        """
        groups([default=None]) -> tuple.
        Return a tuple containing all the subgroups of the match, from
        1. The default argument is used for groups that did not 
        participate in the match
        """
        g = []
        for n in range(1, len(self.regs)):
            if self.group(n) == None:
                g.append(default)
            else:
                g.append(self.group(n))
        return tuple(g)

    def span(self, *args) -> tuple:
        """
        span([group]) -> tuple.
        For MatchObject m, return the 2-tuple (m.start(group),
        m.end(group)).
        """
        if args:
            idx = args[0]
            if isinstance(idx, str):
                idx = self.re.groupindex[idx]
        else:
            idx = 0
        return self.regs[idx]

    def start(self, *args) -> int:
        """
        start([group=0]) -> int.
        Return index of the start of the substring matched by group.
        """
        return self.span(*args)[0]

    def end(self, *args) -> int:
        """
        end([group=0]) -> int.
        Return index of the end of the substring matched by group.
        """
        return self.span(*args)[1]

    def _get_lastgroup(self):
        # No named capture groups? Return None
        if len(self.groupdict()) == 0:
            return None

        # Inverse map of dictionary
        inv_map = {value: key for key, value in
                self.re.groupindex.items()}
        
        # Last matched capturing group not in dictionary
        # -> not a named group.
        if self.lastindex not in inv_map.keys():
            return None

        # Return the name of the last named matched capturing group
        else:
            return inv_map[self.lastindex]

    def _get_regs(self):
        # TODO: update doc
        """
        Map the index positions of the match to their corresponding 
        positions in the source text

        Args:
            Match: re.Match object carried out over the linearized text
            linear_obj: Mapping object

        Returns:
            list: a list containing the corresponding span positions in the
                original (non-linearized) text
        """
        regs = []
        sm = self.string_mapping
        for span in self.Match.regs:
            # (-1, -1) used for groups that did not contibute to the match
            if span == (-1, -1):
                regs.append(span)
                continue

            # Did it match a string-initial empty string?
            elif span == (0, 0):
                regs.append(span)
                continue

            # Did it match a string-final empty string?
            elif span == (len(self.Match.string), len(self.Match.string)):
                idx = len(sm.original)
                regs.append((idx, idx))
                continue

            else:
                span_start = sm.lin2orig_span[span[0]][0]

                # re.MATCH object's span end is index *after* final character,
                # so, we need to subtract one to get the index of the character 
                # to map back to the original, then add one to the result to 
                # get the index after this character
                span_end = sm.lin2orig_span[span[1]-1][1]

                # Adjust idx in accordance with user's preference
                if span[0] == span[1] and self.es_idx != "accurate":
                    if self.es_idx == 'start':
                        span_end = span_start
                    elif self.es_idx == 'end':
                        span_start = span_end
                regs.append((span_start, span_end))
        
        return tuple(regs)

    def _get_del_span(self):
        """
        Returns the span corresponding to the position in the
        delimited string, which is relevant for substitutions and
        splits.                                                                        
        """
        sm = self.string_mapping
        lin_span = self.Match.span()

        # Case of empty string match at end of string
        if lin_span[0] == len(sm.linear):
            del_span = tuple([sm.lin2del[lin_span[0]-1]+1]*2)

        # Normal case
        else:
            del_span = (sm.lin2del[lin_span[0]],
                sm.lin2del[lin_span[1]-1]+1)
        return del_span
