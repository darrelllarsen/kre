#KO: Basic Tools for Working with Korean Text
#Version 0.5.1
#Author: Darrell Larsen
#
#Distributed under GNU General Public License v3.0


"""Section: Conversion between Korean syllables (as Unicode object strings) and their component sounds.

For simple conversion of a Korean syllable to its ordinal value, or conversion from an ordinal value to a Korean syllable, use Python's built-in ord() and chr() functions.
"""
# Key:(ord_value, Yale_romanization)
initials = {'ㄱ':(0,'k'),'ㄲ':(1,'kk'),'ㄴ':(2,'n'),'ㄷ':(3,'t'),'ㄸ':(4,'tt'),
'ㄹ':(5, 'l'),'ㅁ':(6,'m'),'ㅂ':(7,'p'),'ㅃ':(8,'pp'),'ㅅ':(9,'s'),'ㅆ':(10,'ss'),
'ㅇ':(11,''),'ㅈ':(12,'c'),'ㅉ':(13,'cc'),'ㅊ':(14,'ch'),'ㅋ':(15,'kh'),'ㅌ':(16,'th'),
'ㅍ':(17,'ph'),'ㅎ':(18,'h')}
medials = {'ㅏ':(0,'a'),'ㅐ':(1,'ay'),'ㅑ':(2,'ya'),'ㅒ':(3,'yay'),'ㅓ':(4,'e'),
'ㅔ':(5,'ey'),'ㅕ':(6,'ye'),'ㅖ':(7,'yey'),'ㅗ':(8,'o'),'ㅘ':(9,'wa'),'ㅙ':(10,'way'),
'ㅚ':(11,'oy'), 'ㅛ':(12,'yo'),'ㅜ':(13,'wu'),'ㅝ':(14,'we'),'ㅞ':(15,'wey'),'ㅟ':(16,'wi'),
'ㅠ':(17,'yu'),'ㅡ':(18,'u'),'ㅢ':(19,'uy'),'ㅣ':(20,'i')}
finals = {'':(0,''),'ㄱ':(1,'k'),'ㄲ':(2,'kk'),'ㄳ':(3,'ks'),'ㄴ':(4,'n'),
'ㄵ':(5,'nc'),'ㄶ':(6,'nh'),'ㄷ':(7,'t'),'ㄹ':(8,'l'),'ㄺ':(9,'lk'),'ㄻ':(10,'lm'),
'ㄼ':(11,'lp'),'ㄽ':(12,'ls'),'ㄾ':(13,'lth'),'ㄻ':(14,'lm'),'ㅀ':(15,'lh'),'ㅁ':(16,'m'),
'ㅂ':(17,'p'),'ㅄ':(18,'ps'),'ㅅ':(19,'s'),'ㅆ':(20,'ss'),'ㅇ':(21,'ng'),'ㅈ':(22,'c'),
'ㅊ':(23,'ch'),'ㅋ':(24,'kh'),'ㅌ':(25,'th'),'ㅍ':(26,'ph'),'ㅎ':(27,'h')}

"""Yale Patterns - Unnecessary
Yale_initial_letters = {'ㄱ':'k','ㄲ':'kk','ㄴ':'n','ㄷ':'t','ㄸ':'tt','ㄹ':'l','ㅁ':'m',
'ㅂ':'p','ㅃ':'pp','ㅅ':'s','ㅆ':'ss','ㅇ':'','ㅈ':'c','ㅉ':'cc','ㅊ':'ch','ㅋ':'kh',
'ㅌ':'th','ㅍ':'ph','ㅎ':'h'}
Yale_medial_letters = {'ㅏ':'a','ㅐ':'ay','ㅑ':'ya','ㅒ':'yay','ㅓ':'e','ㅔ':'ey','ㅕ':'ye',
'ㅖ':'yey','ㅗ':'o','ㅘ':'wa','ㅙ':'way','ㅚ':'oy','ㅛ':'yo','ㅜ':'wu','ㅝ':'we','ㅞ':'wey',
'ㅟ':'wi','ㅠ':'yu','ㅡ':'u','ㅢ':'uy','ㅣ':'i'}
Yale_final_letters = {'':'','ㄱ':'k','ㄲ':'kk','ㄳ':'ks','ㄴ':'n','ㄵ':'nc','ㄶ':'nh',
'ㄷ':'t','ㄹ':'l','ㄺ':'lk','ㄻ':'lm','ㄼ':'lp','ㄽ':'ls','ㄾ':'lth','ㄻ':'lm','ㅀ':'lh',
'ㅁ':'m','ㅂ':'p','ㅄ':'ps','ㅅ':'s','ㅆ':'ss','ㅇ':'ng','ㅈ':'c','ㅊ':'ch','ㅋ':'kh',
'ㅌ':'th','ㅍ':'ph','ㅎ':'h'}

"""

def _get_split_values(a):
    """get_split_values(str) -> tuple (int, int, int).

    Split a one-character syllable input up into letters. Returns a tuple containing the 
    conversion values for the letters (initial letter, medial letter, final letter)"""
    
    value_a = ord(a)
    fin = ((value_a-44032) % 588) % 28
    mid = (((value_a - 44032) % 588) - fin) / 28
    init = ((value_a -44032) - mid*28 - fin) / 588
    return (int(init), int(mid), int(fin))

#Given three Korean letters (onset, nucleus, coda), returns a tuple containing their conversion values.
def _get_letters(value_set):
    #Argument must be ordered set of 3 or 2 (if no final letter is present)
    for key in initials:
        if initials[key][0] == value_set[0]:
            init = key
    for key in medials:
        if medials[key][0] == value_set[1]:
            mid = key
    for key in finals:
        if finals[key][0] == value_set[2]:
            fin = key
    return (init, mid, fin)

#Find the ordinal value of a Korean syllable containing the three letters passed in as arguments.
def _get_combined_value(a,b,c):
    return initials[a][0]*588 + medials[b][0]*28 + finals[c][0] + 44032

def _values_to_letter(a):
    return chr(_get_combined_value(a[0],a[1],a[2]))
   
def _combine_value_list(a):
    return _values_to_letter(_get_letters(a))

#Given three ordered conversion values, return a Korean syllable.
def combine(a,b,c):
    return chr(_get_combined_value(a,b,c))

def split(a):
    return _get_letters(_get_split_values(a))



"""Section: Tests for Korean input."""

def isSyllable(text):
    #returns true if input text is a single Korean syllable; input must be a string
    #1-character strings evaluated as KO syllables or not; 2-character strings all return False
    #currently only returns true for modern Korean syllables
    if len(text) == 1 and 44032 <= ord(text) <= 55203:
        return True
    else:
        return False


def isMultigraph(letter):
    #Check for clusters found in coda positions
    
    #check in U3130 set (12593-12686)
    if ord(letter) in {12595,12597,12598,12602,12603,12604,12605,12606,12607,12608,12612}:
        return True
    else:
        return False
	
    #check in U1100 set (4342-4469)
    #check in UA960 set (43360-43388)
    #check in UD7B0 set (55216-55291)



def isLetter(letter):
    value = ord(letter)
    #check in U3130 set (12593-12686)
    if value >= 12593 and value <= 12686:
        return True
	
    #check in U1100 set (4342-4469)
    elif value >= 4352 and value <= 4607:
        return True

    #check in UA960 set (43360-43388)
    elif value >= 43360 and value <= 43388:
        return True

    #check in UD7B0 set (55216-55291), and exclude empty values
    elif value >= 55216 and value <= 55291 and not (value >= 55239 and value <= 55242):
        return True

    else:
        return False

def isHangul(text):
    if isSyllable(text) or isLetter(text):
        return True
    else:
        return False





""""Romanization"""
def toYale(text, syllable=None, WO=False, U=False, strict=False):
    """Options: 
    syllable = max (will place a dot between all syllables in a word)
    syllable = min (limits dots to official Yale rules, with a few extra)
    syllable = none (no syllables boundaries marked)
    WO = True (will use <wo> instead of <o> for ㅗ.  Useful for some time periods)
    U = True (will use <u> after labial consonants)
    strict = True (follows Yale Romanization rules as closely as possible, without
    phonological knowledge; currently, this sets WO and U to true, and syllable to min, 
    regardless what the user entered"""
    
    output = ''
    prev_letters = None
    if strict == True:
        WO = True
        U = True
        syllable = 'min'
   
    for char in text:
        if isHangul(char) and isSyllable(char):
            letters = split(char)
            onset = initials[letters[0]][1]
            nucleus = medials[letters[1]][1]
            coda = finals[letters[2]][1]

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
 





