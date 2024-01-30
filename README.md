# kre
Subcharacter-level regular expressions with Korean text.

kre supplements re from the Python Standard Library by allowing the user to perform regular expression searches and substitutions on Korean text at the level of individual letters. It does so by mapping the standard syllable-based characters to a letter-based mapping prior to carrying out the search or substitution. A successful search returns a KRE_Match object, a sort of extended RE_Match object which allows the user to obtain match indices based on the original syllable-structured text. Substitutions automatically resyllabify the text to produce standard syllable-based output (where possible), with various levels of resyllabification possible. Function/method and attribute implementation is designed to match that of re.py wherever possible.

kre supplements re by adding an option to reference syllable boundaries in search patterns. 

### Functions
With the exception of `split`, all public re functions (`search`, `match`, `fullmatch`, `sub`, `subn`, `findall`, `finditer`, `compile`, `purge`, `escape`) and Pattern class methods (`search`, `match`, `fullmatch`, `sub`, `subn`, `findall`, `finditer`) have been implemented.

- Supplemental for search/match/find functions are the keyword arguments `boundaries` and `boundary_marker`.
- Supplemental for the `sub/subn` functions is the keyword argument `syllabify`.

### KRE_Match Objects
With the exception of `expand`, all public methods and attributes of Match objects have been implemented in the KRE_Match object, along with some supplementary attributes.
- Currently implemented for KRE_Match objects: `re`, `regs`, `string`, `end`, `group`, `groupdict`, `groups`, `span`, `start`, `endpos`, `pos`, `lastgroup`, `lastindex`, `__repr__`, `__getitem__`

### Flags
All `re` flags (e.g., DOTALL) are made directly available when importing the kre module.

```
import kre

> kre.search(r'^ㄱ', '한\n국') # no match
> kre.search(r'^ㄱ', '한\n국', kre.MULTILINE)
<kre.KRE_Match object; span=(2, 3), match='국'>
```

### Limitations
kre works for modern Korean using the current Unicode default for Korean syllables ([Ac00-D7AF](https://www.unicode.org/charts/PDF/UAC00.pdf)). This will not work with other Korean unicode blocks (i.e., syllable characters from those blocks will not be converted to sequences of letters) or older Korean varieties (which contain different characters and allow different combinations).


### Examples
As kre is intended to mimic re in most aspects, refer to the [re documentation](https://docs.python.org/3/library/re.html) for usage. The following examples highlight the useful of kre for Korean-language data.

```
> import kre

> arirang = "아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 님은 십리도 못가서 발병 난다."
```
Find all sequences in which the vowel ㅏ is immediately followed by ㄹ, within or across syllables

```
> kre.findall('ㅏㄹ', arirang)
['아리', '아리', '아라', '라리', '아리', '나를', '발']
```
Although text is linearized prior to calling the corresponding `re` function, calling the `span()` method on the returned object returns spans based on the input string.
```
> zipped = [f'{n}:{char}' for n, char in enumerate(arirang)]
> print('Indexation:\n' + ' | '.join(zipped) + '\n')
> print('Matched spans:\n' + '  |  '.join([' '.join([str(res.span()), arirang[res.span()[0]:res.span()[1]]]) for res in kre.finditer('ㅏㄹ', arirang)]))
Indexation:
0:아 | 1:리 | 2:랑 | 3:  | 4:아 | 5:리 | 6:랑 | 7:  | 8:아 | 9:라 |
  10:리 | 11:요 | 12:. | 13:  | 14:아 | 15:리 | 16:랑 | 17:  | 18:고 |
  19:개 | 20:로 | 21:  | 22:넘 | 23:어 | 24:간 | 25:다 | 26:. | 27:  | 
  28:나 | 29:를 | 30:  | 31:버 | 32:리 | 33:고 | 34:  | 35:가 | 36:시 |
  37:는 | 38:  | 39:님 | 40:은 | 41:  | 42:십 | 43:리  | 44:도 | 45:  | 
  46:못 | 47:가 | 48:서 | 49:  | 50:발 | 51:병 | 52:  | 53:난 | 54:다 | 55:.

Matched spans:
(0, 2) 아리  |  (4, 6) 아리  |  (8, 10) 아라  |  (9, 11) 라리  |  (14, 16) 아리  |  (28, 30) 나를  |  (50, 51) 발
```
KRE_Match implements the same methods and attributes as re's Match, with values adjusted to align with the input string. You can also directly access the underlying Match object provided by re, which took the linearized string as input. (Some methods/attributed remain to the implemented.)
```
> res = kre.search('니.+?ㅁ', arirang)
> print('KRE_Match object:')
> print(f'Input string: {res.string}')
> print(f'Matched span: {res.span()}')
> print('\nre Match object:')
> print(f'Input string: {res.Match.string}')
> print(f'Matched span: {res.Match.span()}')
KRE_Match object:
Input string: 아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 님은 십리도 못가서 발병 난다.
Matched span: (39, 47)

re Match object:
Input string: ㅇㅏㄹㅣㄹㅏㅇ ㅇㅏㄹㅣㄹㅏㅇ ㅇㅏㄹㅏㄹㅣㅇㅛ. ㅇㅏㄹㅣㄹㅏㅇ ㄱㅗㄱㅐㄹㅗ ㄴㅓㅁㅇㅓㄱㅏㄴㄷㅏ. ㄴㅏㄹㅡㄹ ㅂㅓㄹㅣㄱㅗ ㄱㅏㅅㅣㄴㅡㄴ ㄴㅣㅁㅇㅡㄴ ㅅㅣㅂㄹㅣㄷㅗ ㅁㅗㅅㄱㅏㅅㅓ ㅂㅏㄹㅂㅕㅇ ㄴㅏㄴㄷㅏ.
Matched span: (74, 90)
```
Note that Korean letters entered in syllable format in the *search* pattern can match across syllables. In the example below, '신' matches with 시는 (**ㅅㅣㄴ**ㅡㄴ). To avoid this behavior, set `boundaries=True` (see below).
```
> print(kre.findall('신', arirang))
> print(kre.search('신', arirang).span())
> print(kre.findall('신', arirang, boundaries=True))
['시는']
(36, 38)
None
```
Just as ranges can be used for Latin letters (e.g., [a-zA-Z]), ranges can be used for Korean characters: [ㄱ-ㅎ] for all consonant (자음) letters, [ㅏ-ㅣ] for all vowel (모음) letters, and [ㄱ-ㅣ] for all Korean letters.
```
> print(f"All consonants C in sequence ㅏCㅣ: {kre.findall('ㅏ[ㄱ-ㅎ]ㅣ', arirang)}")
All consonants C in sequence ㅏCㅣ: ['아리', '아리', '라리', '아리', '가시']

> print(f"All vowels between two ㄹ (within/across syllables): {kre.findall('ㄹ[ㅏ-ㅣ]ㄹ', arirang)}")
All vowels between two ㄹ (within/across syllables): ['리랑', '리랑', '라리', '리랑', '를']

> print(f"All uninterrupted sequences of Korean: {kre.findall('[ㄱ-ㅣ]+', 'not Korean' + arirang + 'not Korean')}")
All uninterrupted sequences of Korean: ['아리랑', '아리랑', '아라리요', '아리랑', '고개로', '넘어간다', '나를',
  '버리고', '가시는', '님은', '십리도', '못가서', '발병', '난다']
```
#### `re` Extension: Syllable Boundaries
Like syllabaries, Korean script encodes information not encoded in alphabetic writing systems: syllable boundaries (to some extent). We lose this information when linearizing the script, and although we could use a somewhat complex regular expression to capture the concept of a syllable boundary in Korean, kre makes it easy to capture syllable boundaries in regular expressions patterns.

To do this, we include the argument `boundaries=True` (default is False) and then place a delimiter (by default, the semi-colon `;`) in the search pattern where we want to indicate a syllable boundary. There is no need to manually include semi-colons in the input string. When using the `sub` or `subn` functions/methods, delimiters must be manually entered in the replacement *repl* argument, if desired.
```
# Look for all ㄹ at the end of the syllable
> print(f"Syllable-final ㄹ: {kre.findall('ㄹ;', arirang, boundaries=True)}")
Syllable-final ㄹ: ['를', '발']

# Look for all ㄹ at the beginning of the syllable
> print(f"Syllable-initial ㄹ: {kre.findall(';ㄹ', arirang, boundaries=True)}")
Syllable-initial ㄹ: ['리', '랑', '리', '랑', '라', '리', '리', '랑', '로', '를', '리', '리']

> print(f"ㄹ.ㄹ sequences (boundaries=False): {kre.findall('ㄹ.ㄹ', arirang)}")
ㄹ.ㄹ sequences (boundaries=False): ['리랑', '리랑', '라리', '리랑', '를']

> print(f"ㄹ.ㄹ sequences (boundaries=True): {kre.findall('ㄹ.ㄹ', arirang, boundaries=True)}")
ㄹ.ㄹ sequences (boundaries=True): ['를']

> print(f"ㄹ;ㄹ sequences (boundaries=True): {kre.findall('ㄹ;ㄹ', arirang, boundaries=True)}")
ㄹ;ㄹ sequences (boundaries=True): None

> print(f"ㄹ.;ㄹ sequences (boundaries=True): {kre.findall('ㄹ.;ㄹ', arirang, boundaries=True)}")
ㄹ.;ㄹ sequences (boundaries=True): ['리랑', '리랑', '라리', '리랑']

> print(f";ㄹ.ㄹ; sequences (boundaries=True): {kre.findall(';ㄹ.ㄹ;', arirang, boundaries=True)}")
;ㄹ.ㄹ; sequences (boundaries=True): ['를']
```
The semi-colon was chosen as the default boundary marker because it appears on Korean keyboards (thus is easy to type) yet is not commonly used in Korean writing, and it is not a special character in regular expressions. Nonetheless, the boundary marker can be set to any other character by setting `delimiter` to a different character. (Using special regular expression characters is not recommended.)
```
> print(f"Syllable-final ㄹ: {kre.findall('ㄹ%', arirang, boundaries=True, delimiter='%')}")
Syllable-final ㄹ: ['를', '발']
```
#### Substitutions
Let's change the verb endings from the narrative forms to a type of future tense.
```
> print(f"Original: {arirang}")
> print(f"Revised:  {kre.sub('ㄴ다', 'ㄹ 거예요', arirang)}")
Original: 아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 님은 십리도 못가서 발병 난다.
Revised:  아리랑 아리랑 아라리요. 아리랑 고개로 넘어갈 거예요. 나를 버리고 가시는 님은 십리도 못가서 발병 날 거예요.
```
When carrying out substitutions in Korean, there is no guarantee that the result will be a sequence that can form a syllable block. There is also no requirement that the input contain only syllable blocks. When performing substitutions, kre allows the user to decide the extent to which kre should attempt to create syllables from the sequences through the keyword argument `syllabify` (options: 'none', 'minimal (default)', 'extended', 'full'). Except when using the 'full' option, any non-captured syllable blocks remain unaffected.

*"Affected character"* refers to captured letters/characters and any other letters belonging to the same syllable in the input.
- 'none': affected characters are ouput without syllabification. Unaffected characters are returned as they appeared in input.
- 'minimal': affected characters are syllabified prior to output
- 'extended': as in minimal, except attempts to combine affected characters with immediately preceding/following characters to create syllables when it reduces the number of stand-alone letters
- 'full': linearizes and resyllabifies the entire string, including all non-captured characters
```
> nonsense = '할ㄱ으하느늘근ㅡ'
> kre.subn('ㅏ','ㅗ',nonsense)
('홀ㄱ으호느늘근ㅡ', 2)

> kre.subn('ㅡ','ㅓ', nonsense, syllabify='none')
('할ㄱㅇㅓ하ㄴㅓㄴㅓㄹㄱㅓㄴㅓ', 5)

> kre.subn('ㅡ','ㅓ', nonsense, syllabify='minimal')
('할ㄱ어하너널건ㅓ', 5)

> kre.subn('ㅡ','ㅓ', nonsense, syllabify='extended')
('할ㄱ어하너널거너', 5)

> kre.subn('ㅡ','ㅓ', nonsense, syllabify='full')
('핡어하너널거너', 5)
```
As noted above, the 'extended' option will attempt to reduce the number of stand-alone letters (seen above), but it will not combine eligible characters if doing so would increase the number of stand-alone letters. Below, ㅏ matches with the syllable 하, and the 'extended' setting makes the following letter, ㅇ, a potential candidate for combining together with 하. This would create 항ㅜ, increasing the number of stand-alone letters, thus ㅇ is not combined with 하.
```
> kre.subn(r'ㅏ', 'ㅗ', '하우', syllabify="extended")
('호우', 1)
```
In contrast, if ㅇ and ㅜ were already separated in the input string, the combination would be allowed, since they map to different input characters.
```
> kre.subn(r'ㅏ', r'ㅗ', '하ㅇㅜ', syllabify="extended")
('홍ㅜ', 1)
```
However, if ㅇ is also an affected character, ㅜ will belong to the extended domain, resulting in 호우.
```
> kre.subn(r'ㅏㅇ', r'ㅗㅇ', '하ㅇㅜ', syllabify="extended")
('호우', 1)
```
Note that some consonant sequences are available as single characters, and these behave different from the same sequence entered as separate letters for the reason explained above.
```
> kre.subn(r"가", r"다", "가ㄹㄱ", syllabify="extended")
('달ㄱ', 1)

> kre.subn(r"가", r"다", "가ㄺ", syllabify="extended")
('닭', 1)
```
##### Substitutions with Boundaries
When boundaries==True, delimiters are also subject to substitution (they can be added or deleted). These interact with the various syllabify options and thus produce different results than similar substitutions without the use of boundaries. Specifically, when boundaries==True, "extended" will only result in resyllabification when patterns include boundary symbols that are removed in the *repl* argument.
```
# Before or after boundary symbol, merging is not possible
> kre.subn('ㄱ', 'ㄴ', 'ㄱㅗ', boundaries=True, syllabify="extended")
('ㄴㅗ', 1)
> kre.subn('ㅗ', 'ㅏ', 'ㄱㅗ', boundaries=True, syllabify="extended")
('ㄱㅏ', 1)
> kre.subn(';ㅗ', ';ㅏ', 'ㄱㅗ', boundaries=True, syllabify="extended")
('ㄱㅏ', 1)

#  Including (and deleting) boundary symbol enables merging, because letter preceding the boundary is now accessible
> kre.subn(';ㅗ', 'ㅏ', 'ㄱㅗ', boundaries=True, syllabify="extended")
('가', 1)
> kre.subn(';', '', 'ㄱㅗ', boundaries=True, syllabify="extended")
('고', 1)
```
In the case of "full" syllabification, boundaries are deleted prior to syllabification, as it would otherwise have no effect.

### Special Considerations (Differences from `re`)
This section discusses a few cases where the mapping process is not straightforward, and we must choose among multiple possible solutions. Users should be aware of these cases and how this module addresses them.

#### `regs` and empty string matches

The Match.regs attribute is undocumented in the official docs. Here 
is an explanation of its use, followed by discussion of a problem kre
runs regarding regs (and groups) into when empty string matches occur.

regs is a tuple of tuples of indices, where the first tuple contains
the span of the complete match, and each subsequent tuple represents 
the spans of the subgroups of the pattern. When the Match.span method
is called with an integer argument n, it returns regs[n]. When called
without an argument, Match.span returns regs[0]. Note that Match.span 
also accepts string arguments for named groups, thus it is not merely 
a redundant function for accessing the subelements of regs.

Some matches can consist of an empty string, such as the following
patterns and resulting Match object attributes:
```
re.search(r".*?", "한글"): regs -> ((0,0),) | groups -> ()
re.search(r"..*?", "한글"): regs -> ((0,1),) | groups -> ()
re.search(r"한.*?", "한글"): regs -> ((0,1),) | groups -> ()
re.search(r"글.*?", "한글"): regs -> ((1,2),) | groups -> ()
re.search(r"(p?).*?", "한글"): regs -> ((0,1, (0,0)) | groups -> ('',)
re.search(r".(p?)", "한글"): regs -> ((0,1), (1,1)) | groups -> ('',)
re.search(r"..(p?)", "한글"): regs -> ((0,2), (2,2)) | groups -> ('',)
```
Note that while empty string matches return an empty string in groups, 
optional groups that don't participate in a match return None and are 
assigned the indices (-1,-1).
```
re.search(r".(p?)", "한글"): regs -> ((0,1), (1,1)) | groups -> ('',)
re.search(r".(p)?", "한글"): regs -> ((0,1), (-1,-1)) | groups -> (None,)
```

The problem:
In the original implementation, re.Match.group(n) method presumably 
returns the substring corresponding to the pair of indices stored at 
re.Match.regs[n]. More specifically, for match m and integer n:                        
`m.group(n) == m.string[slice(*m.regs[n])]`

This isn't as simple for kre, because empty string matches can occur
*between* mapped indices, not just *at* indices. Thus, the following
is expected. (Note: 한글 (length 2) linearizes to ㅎㅏㄴㄱㅡㄹ (length 6))

```
# RE:
re.search(r".(p?)", "한글"): regs -> ((0,1), (1,1)) | groups -> ('',)
re.search(r"..(p?)", "한글"): regs -> ((0,2), (2,2)) | groups -> ('',)
# KRE: NOT ACTUAL IMPLEMENTATION!
# kre.search(r"(p?)", "한글"): regs -> ((0,0), (0,0)) | groups -> ('',)
kre.search(r".(p?)", "한글"): regs -> ((0,1), (0,1)) | groups -> ('한',) # -> ('',) in actual implementation
kre.search(r"..(p?)", "한글"): regs -> ((0,1), (0,1)) | groups -> ('한',) # -> ('',) in actual implementation

kre.search(r"...(p?)", "한글"): regs -> ((0,1), (1,1)) | groups -> ('',)
kre.search(r"....(p?)", "한글"): regs -> ((0,2), (1,2)) | groups -> ('글',) # -> ('',) in actual implementation

```

On the one hand, the span is correct in each case (empty string
matches between syllables should have same start and end indices,
while the end indices for matches within syllables should be 1 greater
than the start indices). On the other hand, the groups method returns
a non-empty string for syllable-internal empty-string matches. This
latter fact may be desired (after all, kre is designed to return
full syllable matches for sub-syllabic matches), but for many cases
users will likely want to treat empty string matches different from
other matches (e.g., ignoring empty string matches). There are at least
two possible workarounds:

1. Whenever a tuple in re.Match.regs contains identical start and end
indices, we can force them to map onto a single index. We then run into 
the question of whether to use the start or end index; for example,
the following search has two possible solutions:
ex. `kre.search(r"(ㅎ)(p?).(ㄴ)", "한글")`: 
option 1: regs -> ((0,1), (0,1), (0,0), (0,1))
option 2: regs -> ((0,1), (0,1), (1,1), (0,1))

2. Leave the indices as is, but add a condition to the groups
method to return an empty string for any group in the linearized
string that returned an empty string.

The present implementation adopts method (2). 

#### `pos` \ `endpos`

The `pos` and `endpos` are optional (non-keyword) arguments for several methods of compiles (i.e., Pattern) objects. They allow users to restrict the regular expression search to a subset of an input string delimited by the specified start (`pos`) and end (`endpos`) indices.

The problem that arises is that in the case of the `match` method, which only returns matches that begin with the pattern. When not using `pos` or `endpos`, there is no problem, because the expectation is clear that the first character---or the first letter it maps to---must be part of the matched pattern. The following exemplifies this.

```
# RE:
> re.match(r"한", "한글")
<re.Match object; span=(0, 1), match='한'>
> re.match(r"글", "한글") # no match
# KRE:
> kre.match(r"한", "한글")
<kre.KRE_Match object; span=(0, 1), match='한'>
> kre.match(r"ㅎ", "한글") # initial letter of initial character
<kre.KRE_Match object; span=(0, 1), match='한'>
> kre.match(r"ㅏ", "한글") # second letter of initial character -> no match
```

`pos` and `endpos`, only available on compiled (Pattern) object methods, are intended to allow the user to shift these boundaries, allowing `match` to return a match even when the string-initial character is not part of the match.

```
> p = re.compile(r"글")
> p.match("한글") # no match
> p.match("한글", 1)
<re.Match object; span=(1, 2), match='글'>
```

One issue that arises in kre is that users might want `pos` to refer to a letter in the middle of a syllable---for example, to ㅏ in 한글. However, if we apply the same mapping methodology to `pos` and `endpos` as elsewhere, 0 would map to the span (0, 3) (i.e., ㅎㅏㄴ), and 1 would map to (3, 6) (i.e., ㄱㅡㄹ). Since ㅏ is not at the beginning of either span, there is no clear way to *map* `pos` to syllable-internal letters.

Three solutions are possible:
1. Apply the same mapping methodology as elsewhere, and accept that `pos` and `endpos` cannot map to syllable-internal indices.
2. `pos` and `endpos` must be entered based on the linearized string position. This would require users to linearize the string in advance to determine this position, which would be rather burdensome and largely defeat the purpose and appeal of kre.
3. Map `pos` to spans, and run the underlying `match` method multiple times, incrementing `pos` each time until a match is returned or all (start) indices of the span have been tested. This compromise would mean that `match` would successfully match patterns in which the first character matches any letter of the start syllable indicated by `pos`. If no `pos` argument is entered, the first letter of the initial syllable must be part of the pattern match for a positive result to be returned. 

I have chosen to adopt method (3) in the module. When more specificity is required, users can use boundaries to further restrict the start/end points of positive matches. The examples below demonstrate how `pos` can be used with `match`.

```
# Function call (requires initial letter to be part of pattern)
> kre.match(r"ㅎ", "한글") # initial letter of initial character
<kre.KRE_Match object; span=(0, 1), match='한'>
> kre.match(r"ㅏ", "한글") # second letter of initial character -> no match
# Method call
> p = kre.compile(r"ㅏ")
> p.match("한글") # no pos -> no match
> p.match("한글", 0)
<kre.KRE_Match object; span=(0, 1), match='한'>
> p.match("한글", 1) # no match

```

Other than `match`, for all methods of compiled (Pattern) objects that accept `pos` and `endpos` arguments, `pos` and `endpos` are simply mapped to the initial or final index of the span of the relevant syllable. When boundaries is True, `pos` and `endpos` expand to include the boundary immediately preceding/following the relevant syllable. In this case, the `match` method will also look for matches starting with the syllable boundary before the syllable referenced by `pos`.

```
> p = kre.compile(r"ㄱ")
> p.match("한글", 0, boundaries=True) # no match
> p.match("한글", 1, boundaries=True)
<kre.KRE_Match object; span=(1, 2), match='글'>
> p = kre.compile(r";ㄱ")
> p.match("한글", 1, boundaries=True) # search space expands to include boundary preceding 글
<kre.KRE_Match object; span=(1, 2), match='글'>
> p = kre.compile(r"ㄱ;")
> p.match("한글", 1, boundaries=True) # no match
```

## tools.py:

tools.py contains basic tools for detecting Korean language text, splitting Korean syllables up into individual Korean letters, combining Korean letters into Korean syllables, and Romanizing Korean text using Yale Romanization.  Additional Romanization types may be implemented in the future.

## constants.py

constants.py contains constants used by tools.py
