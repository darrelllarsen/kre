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
- Supplemental in KRE_Match objects: `Match` (the underlying re.Match object resulting from applying a `re` function to the linearized input string); `lin2syl_mapping`

### Limitations
kre works for modern Korean using the current Unicode default for Korean syllables ([Ac00-D7AF](https://www.unicode.org/charts/PDF/UAC00.pdf)). This will not work with other Korean unicode blocks (i.e., syllable characters from those blocks will not be converted to sequences of letters) or older Korean varieties (which contain different characters and allow different combinations).

## KO.py:

KO.py contains basic tools for detecting Korean language text, splitting Korean syllables up into individual Korean letters, combining Korean letters into Korean syllables, and Romanizing Korean text using Yale Romanization.  Additional Romanization types may be implemented in the future.

## constants.py

constants.py contains constants used by KO

## Dependencies
kre depends on re (standard library), KO (this package)
KO depends on constants (this package)
