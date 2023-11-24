# korean
Tools for working with Korean language text.

## kre.py:

kre.py supplements re.py from the Python Standard Library by allowing the user to perform regular expression searches on Korean text at the level of individual letters by breaking up the standard syllable-based font mapping to a letter-based mapping prior to carrying out the search. It returns a KRE_Match object, a sort of extended RE_Match object which allows the user to obtain match indices based on either the original syllable-structured text or the letter-based text. Function/method and attribute implementation is designed to match that of re.py wherever possible. 

### Functions
With the exception of `split`, all public re functions (`search`, `match`, `fullmatch`, `sub`, `subn`, `findall`, `finditer`, `compile`, `purge`, `escape`) have been implemented as stand-alone functions. They are not yet callable from a compiled Pattern object.

- Supplemental for search/match/find functions are the keyword arguments `boundaries` and `boundary_marker`. These have not yet been implemented with the `sub/subn` functions.
- Supplemental for the `sub/subn` functions is the keyword argument `syllabify`.

### Objects
The most essential methods and attributes of Match objects have been implemented in the KRE_Match object, along with some supplementary attributes.
- Currently implemented for KRE_Match objects: `re`, `regs`, `string`, `end`, `group`, `groupdict`, `groups`, `span`, `start`, `__repr__`
- To be implemented: `endpos`, `pos`, `lastgroup`, `lastindex`, `expand`
- Supplemental in KRE_Match objects: `Match` (the underlying re.Match object resulting from applying a `re` function to the linearized input string)

### Additional Limitations
kre works for modern Korean using the current Unicode default for Korean syllables ([Ac00-D7AF](https://www.unicode.org/charts/PDF/UAC00.pdf)). This will not work with other Korean unicode blocks (i.e., syllable characters from those blocks will not be converted to sequences of letters) or older Korean varieties (which contain different characters and allow different combinations).

### Examples
As kre is intended to mimic re in most aspects, refer to the [re documentation](https://docs.python.org/3/library/re.html#regular-expression-objects) for usage. The following examples highlight the useful of kre for Korean-language data.

```
import kre

arirang = "아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 임은 십 리도 못가서 발병 난다."
```
Find all sequences in which the vowel ㅏ is immediately followed by ㄹ, within or across syllables

```
kre.findall('ㅏㄹ', arirang)
> ['아리', '아리', '아라', '라리', '아리', '나를', '발']
```
Although text is linearized prior to calling the corresponding `re` function, calling the `span()` method on the returned object returns spans based on the input string.
```
zipped = [f'{n}:{char}' for n, char in enumerate(arirang)]
print('Indexation:\n' + ' | '.join(zipped) + '\n')
print('Matched spans:\n' + '  |  '.join([' '.join([str(res.span()), arirang[res.span()[0]:res.span()[1]]]) for res in kre.finditer('ㅏㄹ', arirang)]))
> Indexation:
> 0:아 | 1:리 | 2:랑 | 3:  | 4:아 | 5:리 | 6:랑 | 7:  | 8:아 | 9:라 |
  10:리 | 11:요 | 12:. | 13:  | 14:아 | 15:리 | 16:랑 | 17:  | 18:고 |
  19:개 | 20:로 | 21:  | 22:넘 | 23:어 | 24:간 | 25:다 | 26:. | 27:  | 
  28:나 | 29:를 | 30:  | 31:버 | 32:리 | 33:고 | 34:  | 35:가 | 36:시 |
  37:는 | 38:  | 39:임 | 40:은 | 41:  | 42:십 | 43:  | 44:리 | 45:도 | 
  46:  | 47:못 | 48:가 | 49:서 | 50:  | 51:발 | 52:병 | 53:  | 54:난 | 55:다 | 56:.
>
> Matched spans:
> (0, 2) 아리  |  (4, 6) 아리  |  (8, 10) 아라  |  (9, 11) 라리  |  (14, 16) 아리  |  (28, 30) 나를  |  (51, 52) 발
```
KRE_Match implements the same methods and attributes as re's Match, with values adjusted to align with the input string. You can also directly access the underlying Match object provided by re, which took the linearized string as input. (Some methods/attributed remain to the implemented.)
```
res = kre.search('이.+?ㅁ', arirang)
print('KRE_Match object:')
print(f'Input string: {res.string}')
print(f'Matched span: {res.span()}')
print('\nre Match object:')
print(f'Input string: {res.Match.string}')
print(f'Matched span: {res.Match.span()}')
> KRE_Match object:
> Input string: 아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 임은 십 리도 못가서 발병 난다.
> Matched span: (39, 48)
>
> re Match object:
> Input string: ㅇㅏㄹㅣㄹㅏㅇ ㅇㅏㄹㅣㄹㅏㅇ ㅇㅏㄹㅏㄹㅣㅇㅛ. ㅇㅏㄹㅣㄹㅏㅇ ㄱㅗㄱㅐㄹㅗ ㄴㅓㅁㅇㅓㄱㅏㄴㄷㅏ. ㄴㅏㄹㅡㄹ ㅂㅓㄹㅣㄱㅗ ㄱㅏㅅㅣㄴㅡㄴ ㅇㅣㅁㅇㅡㄴ ㅅㅣㅂ ㄹㅣㄷㅗ ㅁㅗㅅㄱㅏㅅㅓ ㅂㅏㄹㅂㅕㅇ ㄴㅏㄴㄷㅏ.
> Matched span: (74, 91)
```
Note that Korean letters entered in syllable format in the *search* pattern can match across syllables. In the example below, '신' matches with 시는 (**ㅅㅣㄴ**ㅡㄴ). To avoid this behavior, set `boundaries=True` (see below).
```
print(kre.findall('신', arirang))
print(kre.search('신', arirang).span())
print(kre.findall('신', arirang, boundaries=True))
> ['시는']
> (36, 38)
> None
```
Just as ranges can be used for Latin letters (e.g., [a-zA-Z]), ranges can be used for Korean characters: [ㄱ-ㅎ] for all consonant (자음) letters, [ㅏ-ㅣ] for all vowel (모음) letters, and [ㄱ-ㅣ] for all Korean letters.
```
print(f"All consonants C in sequence ㅏCㅣ: {kre.findall('ㅏ[ㄱ-ㅎ]ㅣ', arirang)}")
> All consonants C in sequence ㅏCㅣ: ['아리', '아리', '라리', '아리', '가시']

print(f"All vowels between two ㄹ (within/across syllables): {kre.findall('ㄹ[ㅏ-ㅣ]ㄹ', arirang)}")
> All vowels between two ㄹ (within/across syllables): ['리랑', '리랑', '라리', '리랑', '를']

print(f"All uninterrupted sequences of Korean: {kre.findall('[ㄱ-ㅣ]+', 'not Korean' + arirang + 'not Korean')}")
> All uninterrupted sequences of Korean: ['아리랑', '아리랑', '아라리요', '아리랑', '고개로', '넘어간다', '나를',
  '버리고', '가시는', '임은', '십', '리도', '못가서', '발병', '난다']
```

#### Substitutions
Let's change the verb endings from the narrative forms to a type of future tense.
```
print(f"Original: {arirang}")
print(f"Revised:  {kre.sub('ㄴ다', 'ㄹ 거예요', arirang)}")
> Original: 아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 임은 십 리도 못가서 발병 난다.
> Revised:  아리랑 아리랑 아라리요. 아리랑 고개로 넘어갈 거예요. 나를 버리고 가시는 임은 십 리도 못가서 발병 날 거예요.
```
When carrying out substitutions in Korean, there is no guarantee that the result will be a sequence that can form a syllable block. There is also no requirement that the input contain only syllable blocks. When performing substitutions, kre allows the user to decide the extent to which kre should attempt to create syllables from the sequences through the keyword argument `syllabify` (options: 'none', 'minimal', 'extended' (default), 'full'). Except for 'full', any non-captured syllable blocks remain unaffected.

*"Affected character"* refers to captured letters/characters and any other letters belonging to the same syllable in the input.
- 'none': affected characters are ouput without syllabification. Unaffected characters are returned as they appeared in input.
- 'minimal': affected characters are syllabified prior to output
- 'extended': as in minimal, except attempts to combine affected characters with preceding/following character to create syllables
- 'full': linearizes and resyllabifies the entire string, including all non-captured characters
```
nonsense = '할ㄱ으하느늘근ㅡ'
kre.subn('느', '나가', nonsense)
> ('할ㄱ으하나가나갈그나가', 3)

kre.subn('ㅏ','ㅗ',nonsense)
> ('홁으호느늘근ㅡ', 2)

kre.subn('ㅡ','ㅓ', nonsense, syllabify='none')
> ('할ㄱㅇㅓ하ㄴㅓㄴㅓㄹㄱㅓㄴㅓ', 5)

kre.subn('ㅡ','ㅓ', nonsense, syllabify='minimal')
> ('할ㄱ어하너널건ㅓ', 5)

kre.subn('ㅡ','ㅓ', nonsense, syllabify='extended')
> ('할ㄱ어하너널거너', 5)

kre.subn('ㅡ','ㅓ', nonsense, syllabify='full')
> ('핡어하너널거너', 5)
```
#### Re Extension: Syllable Boundaries
Like syllabaries, Korean script encodes information not encoded in alphabetic writing systems: syllable boundaries (to some extent). We lose this information when linearizing the script, and although we could use a somewhat complex regular expression to capture the concept of a syllable boundary in Korean, kre makes it easy to capture syllable boundaries in regular expressions patterns.

To do this, we include the argument `boundaries=True` (default is False) and then place a semi-colon `;` in the search pattern where we want to indicate a syllable boundary. There is no need to manually include semi-colons in the input string. (Note that `boundaries` is not currently implemented for the `sub/subn` functions.)
```
# Look for all ㄹ at the end of the syllable
print(f"Syllable-final ㄹ: {kre.findall('ㄹ;', arirang, boundaries=True)}")
> Syllable-final ㄹ: ['를', '발']

# Look for all ㄹ at the beginning of the syllable
print(f"Syllable-initial ㄹ: {kre.findall(';ㄹ', arirang, boundaries=True)}")
> Syllable-initial ㄹ: ['리', '랑', '리', '랑', '라', '리', '리', '랑', '로', '를', '리', '리']

print(f"ㄹ.ㄹ sequences (boundaries=False): {kre.findall('ㄹ.ㄹ', arirang)}")
> ㄹ.ㄹ sequences (boundaries=False): ['리랑', '리랑', '라리', '리랑', '를']

print(f"ㄹ.ㄹ sequences (boundaries=True): {kre.findall('ㄹ.ㄹ', arirang, boundaries=True)}")
> ㄹ.ㄹ sequences (boundaries=True): ['를']

print(f"ㄹ;ㄹ sequences (boundaries=True): {kre.findall('ㄹ;ㄹ', arirang, boundaries=True)}")
> ㄹ;ㄹ sequences (boundaries=True): None

print(f"ㄹ.;ㄹ sequences (boundaries=True): {kre.findall('ㄹ.;ㄹ', arirang, boundaries=True)}")
> ㄹ.;ㄹ sequences (boundaries=True): ['리랑', '리랑', '라리', '리랑']

print(f";ㄹ.ㄹ; sequences (boundaries=True): {kre.findall(';ㄹ.ㄹ;', arirang, boundaries=True)}")
> ;ㄹ.ㄹ; sequences (boundaries=True): ['를']
```
The semi-colon was chosen as the default boundary marker because it appears on Korean keyboards (thus is easy to type) yet is not commonly used in Korean writing, and it is not a special character in regular expression. Nonetheless, the boundary marker can be set to any other character by setting `delimiter` to a different character. (Using special regular expression characters is not recommended.)
```
print(f"Syllable-final ㄹ: {kre.findall('ㄹ%', arirang, boundaries=True, delimiter='%')}")
> Syllable-final ㄹ: ['를', '발']
```

## KO.py:

KO.py contains basic tools for detecting Korean language text, splitting Korean syllables up into individual Korean letters, combining Korean letters into Korean syllables, and Romanizing Korean text using Yale Romanization.  Additional Romanization types may be implemented in the future.

## constants.py

constants.py contains constants used by KO

## Dependencies
kre depends on re (standard library), KO (this package)
KO depends on constants (this package)
