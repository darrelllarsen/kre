# korean
Tools for working with Korean language text

kre.py:
kre.py supplements re.py from the Python Standard Library by allowing the user to perform regular expression searches on Korean text at the level of individual letters by breaking up the standard syllable-based font mapping to a letter-based mapping prior to carrying out the search. It returns a KRE_Match object, a sort of extended RE_Match object which allows the user to obtain match indices based on either the original syllable-structured text or the letter-based text. Function implementation is designed to match that of re.py wherever possible.

kre.py depends on KO.py

More detailed information is available in the kre.py file itself.


KO.py:
KO.py contains basic tools for detecting Korean language text, splitting Korean syllables up into individual Korean letters, combining Korean letters into Korean syllables, and Romanizing Korean text using Yale Romanization.  Additional Romanization types may be implemented in the future.
