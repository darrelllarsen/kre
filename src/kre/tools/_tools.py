#KO: Basic Tools for Working with Korean Text
#Version 0.5.2
#Author: Darrell Larsen
#
#Distributed under GNU General Public License v3.0
from collections.abc import Sequence
from ._constants import (_COMBINED_FINALS, _FINALS, _INITIALS, _MEDIALS,
        _SPLIT_FINALS)

"""Section: Conversion between Korean syllables (as Unicode object 
strings) and their component sounds.

For simple conversion of a Korean syllable to its ordinal value, or 
conversion from an ordinal value to a Korean syllable, use Python's
built-in ord() and chr() functions.
"""

# TODO: implement exceptions throughout

def _get_split_values(char) -> tuple[int, int, int]:
    """
    Convert a one-character Korean syllable 3-tuple of dictionary
    look-up values

    Args:
        char (str): a one-character Korean syllable input

    Returns:
        tuple(int, int, int): tuple of look-up values of the initial,
            medial, and final letters of the syllable

    Example:
        '닭' --> (3, 0, 9)
    """

    if not isSyllable(char):
        raise ValueError(
                f"Korean syllable character expected, got '{char}'")

    # Get the Unicode value of the input string
    value_char = ord(char)

    # Convert value_a into the look-up values of the letters it 
    # represents
    fin = ((value_char-44032) % 588) % 28
    mid = (((value_char - 44032) % 588) - fin) / 28
    init = ((value_char -44032) - mid*28 - fin) / 588

    return (int(init), int(mid), int(fin))

def _get_letters(value_set: Sequence[int, int, int]) -> tuple[str,str,str]:
    """
    Convert a sequence of look-up values into a one-character syllable

    Args:
        value_set -- a list or tuple containing look-up values to the 
            initial, medial and final Korean letters

    Returns:
        tuple(str, str, str): a 3-tuple of Korean letters
    
    Example:
        (3, 0, 9) --> ('ㄷ', 'ㅏ', 'ㄺ')
    """

    for key in _INITIALS:
        if _INITIALS[key][0] == value_set[0]:
            init = key
    for key in _MEDIALS:
        if _MEDIALS[key][0] == value_set[1]:
            mid = key
    for key in _FINALS:
        if _FINALS[key][0] == value_set[2]:
            fin = key
    return (init, mid, fin)

def _get_combined_value(
        initial: str, medial: str, final: str = None) -> int:
    """
    Convert a sequence of Korean letters into the Unicode value of the
    syllable they constitute

    Args:
        initial (str): an initial Korean letter
        medial (str): a medial Korean letter
        final (str): a final Korean letter (default is None)

    Returns:
        int: Unicode value of the syllable comprised of init, med, fin

    Example:
        'ㄷ', 'ㅏ', 'ㄺ' --> 45805 
    """
    output = 44032 + _INITIALS[initial][0]*588 + _MEDIALS[medial][0]*28
    
    if final:
        output += _FINALS[final][0]

    return output

def _values_to_letter(char_seq: Sequence[str, str, (str)]) -> str:
    """
    Convert a sequence of Korean letters into their one-character
    syllable representation

    Arguments:
        char_seq (list): a sequence of two or three Korean letters

    Returns:
        str: a one-character syllable

    Example:
        ('ㄷ', 'ㅏ', 'ㄺ') --> '닭' 
    """
    if len(char_seq) == 2:
        char_seq = list(char_seq)[:] + ['']

    return chr(_get_combined_value(char_seq[0],char_seq[1],char_seq[2]))
   
def _combine_value_list(int_seq: Sequence[int,int,int]) -> str:
    """
    Convert a list of look-up values into a one-character syllable

    Args:
        int_seq (list): a sequence of look-up values

    Returns:
        str: one-character syllable

    Example:
        (3, 0, 9) --> '닭'
    """

    return _values_to_letter(_get_letters(int_seq))

def split_coda(final: str) -> str:
    """
    Splits a complex coda/final into separate letters.

    Args:
        final: a Korean letter

    Returns:
        a string containing the split letters or the input if not a 
        complex coda
    """
    if final in _COMBINED_FINALS.keys():
        final = _COMBINED_FINALS[final]

    return final

def _combine_coda(final: str) -> str:
    """
    Combines letters of a complex coda/final into a single character.

    Args:
        final (str): a Korean letter

    Returns:
        the character represent the complex coda/final or the input if
        not a complex coda
    """
    if final in _SPLIT_FINALS.keys():
        final = _SPLIT_FINALS[final]

    return final


#### External Functions ####

def combine(*args: str or Sequence[str]) -> str:
    """
    Combines 2-4 Korean letters into a single syllable

    Args:
        str or letter-separated (list or tuple)

    Returns:
        str: a one-character syllable

    Example:
        'ㄷㅏㄺ' --> '닭'
        'ㄷㅏㄹㄱ' --> '닭'
        ('ㄷ', 'ㅏ', 'ㄺ') --> '닭' 
        ('ㄷ', 'ㅏ', 'ㄹㄱ') --> '닭' 
        ('ㄷ', 'ㅏ', 'ㄹ','ㄱ') --> '닭' 

    """

    # If length one, should be str, list, or tuple
    # Sets args = list, tuple, or list(str)
    if len(args) == 1:
        args = args[0]
        if type(args) is str:
            args = list(args)

    if 1 < len(args) < 5:
        # combine two-letter complex finals, if any
        final = _combine_coda(''.join(args[2:]))

        # construct and return syllable
        return chr(_get_combined_value(args[0], args[1], final))

    elif len(args) > 4:
        raise Exception("Too many characters")
    else:
        raise Exception("Insufficient characters")
        
def syllabify(text, linearize_first=True) -> str:
    """
    Combines a string of Korean letters into syllables.

    Args:
        text (str): a string which presumably contains at least some
            Korean letters
        linearize_first (bool): if True, any Korean syllables or complex 
            coda characters in the input will be linearized first, then
            syllabified 

            ex. True: 가ㄹ -> ㄱㅏㄹ -> 갈
            ex. False: 가ㄹ -> 가ㄹ -> 가ㄹ

    Returns:
        str: a string of in which any linear sequences of possible 
        Korean syllables have been replaced with Korean syllables
    """

    buffer = ''
    output = ''

    if linearize_first == True:
        text = linearize(text, split_codas=True)

    for char in text:
        if not isLetter(char, include_complex=True):
            if len(buffer) > 1:
                output += combine(buffer)
            else:
                output += buffer
            output += char
            buffer = ''
            continue

        elif not buffer:
            # only accept an onset letter
            if char not in _INITIALS.keys():
                output += char
            else:
                buffer = char
            continue

        elif len(buffer) == 1:
            if char in _MEDIALS.keys():
                buffer += char
            else:
                output += buffer
                if char in _INITIALS.keys():
                    buffer = char
                else:
                    buffer = ''
            continue

        elif len(buffer) == 2:
            if char in _COMBINED_FINALS.keys():
                output += combine(buffer + char)
                buffer = ''
            elif char in _FINALS.keys():
                buffer += char
            else:
                output += combine(buffer)
                if char in _INITIALS.keys():
                    buffer = char
                else:
                    output += char
                    buffer = ''
            continue

        elif len(buffer) == 3: 
            if (buffer[-1] + char) in _SPLIT_FINALS.keys():
                buffer += char
            elif char in _INITIALS.keys():
                output += combine(buffer)
                buffer = char
            elif char in _MEDIALS.keys():
                output += combine(buffer[:-1])
                buffer = buffer[-1] + char
            else:
                output += combine(buffer) + char
                buffer = ''
            continue
        
        elif len(buffer) == 4:
            if char in _INITIALS.keys():
                output += combine(buffer)
                buffer = char
            elif char in _MEDIALS.keys():
                output += combine(buffer[:-1])
                buffer = buffer[-1] + char
            else:
                output += combine(buffer) + char
                buffer = ''
            continue

        else:
            raise Exception("This shouldn't happen")

    if len(buffer) > 1:
        output += combine(buffer)
    else:
        output += buffer

    return output

def split(char, 
        fill_finals=False, split_codas=False) -> list[str, str, (str)]:
    """
    Converts a Korean syllable character into a sequence of letters

    Args:
        char (str): a Korean syllable character
        fill_finals (bool): return an empty string in finals position
            if no final is provided in the input (default is False)

    Returns:
        list(str, str(, str)): a list of Korean letters, optionally
            includes an empty string to occupy empty final letter
            position

    Examples:
        '닭' --> ['ㄷ', 'ㅏ', 'ㄺ']     (fill_finals=True or False)
        '다' --> ['ㄷ', 'ㅏ']           (fill_finals=False)
        '다' --> ['ㄷ', 'ㅏ', '']       (fill_finals=True)
        '닭' --> ['ㄷ', 'ㅏ', 'ㄹㄱ']   (split_codas=True
    """

    output = list(_get_letters(_get_split_values(char)))
    if split_codas:
        output[-1] = split_coda(output[-1])

    # Remove empty strings in finals position if fill_finals is False
    if output[-1] == '' and not fill_finals:
        output = output[:-1]

    return output

def linearize(text, split_codas=True) -> str:
    output = ''
    for char in text:
        if isSyllable(char):
            output += ''.join(split(char, fill_finals=False, 
                    split_codas=split_codas))
        elif char in _COMBINED_FINALS.keys() and split_codas == True:
            output += ''.join(split_coda(char))
        else:
            output += char
    return output

"""Section: Tests for Korean input."""

def isSyllable(text) -> bool:
    """
    Test whether an input string is a Korean syllable or not

    Args:
        text (str): the string to test

    Returns:
        bool: True if the input string is of length one and is a Korean
            syllable (i.e., is located within the Unicode range
            specified below). False otherwise.

    TODO: implement other Unicode ranges containing Korean syllables;
    currently only returns true for modern Korean syllables using the
    default unicode space
    """

    if len(text) == 1 and 44032 <= ord(text) <= 55203:
        return True
    else:
        return False

def isComplexCoda(char) -> bool:
    """
    Test whether the character is a coda character containing two 
    letters (i.e., a consonant cluser).

    Ssangjaeum (doubled consonants) are *not* treated as consonant
    clusters by this algorithm.

    Args:
        char (char): a single character

    Returns:
        bool: True if the character represents two adjacent coda 
        consonants, False otherwise
    """

    coda_ccs = []

    # add coda clusters in U1100 set (4520-4607)
    coda_ccs += [4522, 4524, 4525, 4528, 4529, 4530, 4531, 4532, 4533,
            4534, 4537, 4547, 4748, 4549, 4550, 4551, 4552, 4553, 4554,
            4555, 4556, 4557, 4558, 4559, 4560, 4561, 4562, 4563, 4564,
            4565, 4566, 4567, 4568, 4569, 4570, 4571, 4572, 4573, 4574,
            4575, 4576, 4577, 4579, 4580, 4581, 4583, 4584, 4585, 4586,
            4588, 4589, 4590, 4591, 4593, 4594, 4595, 4597, 4598, 4599,
            4600, 4602, 4603, 4604, 4605, 4606]

    #add coda clusters in U3130 set (12593-12686)
    coda_ccs += [12595, 12597, 12598, 12602, 12603, 12604, 12605,12606,
            12607,12608,12612, 12647, 12648, 12649, 12650, 12651, 
            12652, 12653, 12655, 12656]

    # add coda clusters in UD7B0 set (55216-55291)
    # note that this set excludes initial consonants (see corresponding
    # set UA960)
    coda_ccs += [55243, 55243, 55244, 55246, 55247, 55248, 55249, 55250,
            55251, 55252, 55253, 55254, 55255, 55256, 55257, 55258, 
            55259, 55260, 55262, 55263, 55265, 55266, 55267, 55268, 
            55269, 55271, 55272, 55273, 55274, 55275, 55276, 55277, 
            55278, 55279, 55280, 55281, 55282, 55283, 55284, 55285, 
            55286, 55287, 55288, 55290]


    if len(char) == 1 and ord(char) in coda_ccs:
        return True
    else:
        return False

def isComplexOnset(char) -> bool:
    """
    Test whether the character is an onset character containing two 
    letters (i.e., a consonant cluser). Note that this does not occur in
    modern Korean writing.
    
    Ssangjaeum (doubled consonants) are *not* treated as consonant
    clusters by this algorithm.


    Args:
        char (char): a single character

    Returns:
        bool: True if the character represents two adjacent onset 
        consonants, False otherwise
    """

    onset_ccs = []

    #check in U1100 set (4371-4446)
    onset_ccs += [4371, 4373, 4374, 4375, 4376, 4378, 4380, 4382, 4383,
            4384, 4385, 4386, 4387, 4388, 4389, 4390, 4391, 4392, 4393,
            4394, 4397, 4398, 4399, 4400, 4401, 4402, 4403, 4404, 4405,
            4406, 4407, 4408, 4409, 4410, 4411, 4417, 4418, 4419, 4420,
            4421, 4422, 4424, 4425, 4426, 4427, 4429, 4434, 4435, 4438,
            4442, 4443, 4444, 4445, 4446]

    #check in U3130
    onset_ccs += [12646, 12654, 12658, 12659, 12660, 12661, 12662, 
            12663, 12666, 12667, 12668, 12669, 12670, 12674, 12675]

    # add onset clusters in UA960 set (43360-43388)
    # note that set UA960 exclusively contains old initial consonants
    onset_ccs += [x for x in range(43360, 44385)]
    onset_ccs += [43386, 43387]

    if len(char) == 1 and ord(char) in onset_ccs:
        return True
    else:
        return False

def isJamo(char) -> bool:
    """
    Test whether the character is Jamo (Korean letter, including
    complex letters) rather than a syllable.

    Args:
        char (char)

    Returns:
        bool: True if char is a Korean Jamo, otherwise False
    """

    return isLetter(char, include_complex=True)

def isLetter(char, include_complex=False) -> bool:
    """
    Test whether the character is letter rather than a syllable. Onset
    and coda clusters return a value of False. (Use isJamo() to accept
    complex clusters as well.)

    Args:
        char (char)

    Returns:
        bool: True if char is a single Korean letter (optionally
        including clusters), otherwise False

    """

    if len(char) != 1:
        return False

    if include_complex == False:
        if isComplexOnset(char) or isComplexCoda(char):
            return False

    value = ord(char)

    #check in U3130 set (12593-12686), and exclude empty values
    if value >= 12593 and value <= 12686 and value != 12644:
        return True
	
    #check in U1100 set (4352-4469), and exclude empty values
    elif value >= 4352 and value <= 4607 and value not in [4447, 4448]:
        return True

    #check in UA960 set (43360-43388)
    elif value >= 43360 and value <= 43388:
        return True

    #check in UD7B0 set (55216-55291), and exclude empty values
    elif value >= 55216 and value <= 55291 and (
            value not in [55239, 55240, 55241, 55242]):
        return True
    else:
        return False

def isHangul(char) -> bool:
    """
    Checks whether input is a Korean Hangul (and not Hanja) symbol.

    Args:
        char (char)

    Returns:
        bool: True if char is a Korean Hangul symbol, including
        syllables, individual letters, and clusters. False otherwise.
    """
    if isSyllable(char) or isJamo(char):
        return True
    else:
        return False

def hasHangul(text) -> bool:
    """
    Checks whether the input string contains Korean Hangul (and not Hanja)

    Args:
        text (str)

    Returns:
        bool: True if text contains a Korean Hangul symbol, including
        syllables, individual letters, and clusters. False otherwise.
    """
    for char in text:
        if isHangul(char):
            return True

    return False

#### Romanization

def toYale(text, syllable=None, WO=False, U=False, strict=False) -> str:
    """
    Options: 
    syllable = max (will place a dot between all syllables in a word)
    syllable = min (limits dots to official Yale rules, with a few extra)
    syllable = none (no syllables boundaries marked)
    WO = True (will use <wo> instead of <o> for ㅗ.  Useful for some time periods)
    U = True (will use <u> after labial consonants)
    strict = True (follows Yale Romanization rules as closely as possible, without
    phonological knowledge; currently, this sets WO and U to true, and syllable to min, 
    regardless what the user entered
    """
    
    output = ''
    prev_letters = None
    if strict == True:
        WO = True
        U = True
        syllable = 'min'
   
    for char in text:
        if isHangul(char) and isSyllable(char):
            letters = split(char)
            onset = _INITIALS[letters[0]][1]
            nucleus = _MEDIALS[letters[1]][1]
            coda = _FINALS[letters[2]][1]

            if WO == True and nucleus == 'o':
                nucleus = 'wo'
            if U == True and nucleus == 'wu' and onset in {'p','pp','ph','m'}:
                nucleus = 'u' 

            #syllable = 'max': places dot between all syllables
            if prev_letters != None and syllable == 'max':
                output = output + '.'

            #syllable = 'min': places dot between ambiguous syllables only    
            elif prev_letters != None and syllable == 'min':
                prev_coda = prev_letters[2]
                prev_vowel = prev_letters[1]
            
                if prev_coda == '':
                    #Mark after coda-less syllables when C follows
                    if onset != '':
                        output = output + '.'

                    #Mark between adjacent vowels, when confusion of <w>/<y> 
                    #and <a>, <e>, <o>, <u> may arise
                    elif ((prev_vowel[len(prev_vowel)-1] in {'a','e','o','u'} and \
                            nucleus == 'y') \
                            or (prev_vowel[len(prev_vowel)-1] in {'y', 'w'} and \
                            nucleus in {'a','e','o','u'})):
                        output = output + '.'

                else:        
                    #Mark before onsetless syllables, unless previous coda was 
                    #null or <ng>
                    if prev_coda not in {'','ng'} and onset == '':
                        output = output + '.'
                        

                    #Mark after a consonant (final one in case of cluster) when onset 
                    #consonant is same, for those which can be doubled
                    elif prev_coda[len(prev_coda)-1] == onset and onset in \
                        {'k','p','t','c','s'} and prev_coda not in \
                        {'kk','pp','tt','cc','ss'}:
                        output = output + '.'

                    #Mark after a consonant when onset of following is <h>, when 
                    #ambiguity can arise
                    elif prev_coda[len(prev_coda)-1] in {'k','p','t','c'} and \
                            onset in {'h'}:
                        output = output + '.'

                    #Mark when <k> is followed by <kh>.  Need not do for <p,t,c>, i
                    #as their doubled variants do not occur in coda position    
                    elif prev_coda in {'k'} and onset in {'kh'}:
                        output = output + '.'

            output = (output + onset + nucleus + coda) 
            prev_letters = (onset,nucleus,coda)
 
        else:
            output = output + char
            prev_letters = None
    return output            
