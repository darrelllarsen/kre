# kre
Subcharacter-level regular expressions with Korean text.

kre is a wrapper for `re` from the Python Standard Library which allows users to apply the full functionality of `re` at the subcharacter level for Korean text.

## Documentation

Most functionality is documented in the [re documentation](https://docs.python.org/3/library/re.html).

Documentation on the unique features of kre is available in the [wiki](https://github.com/darrelllarsen/kre/wiki), where you will also find discussion of inherent differences between `re` (character-level regular expressions) and `kre` (subcharacter-level regular expressions) and how kre addresses them. *It is strongly recommended that users familiarize themselves with these differences.*

## Example Features
In the simple case of search functions, matches are mapped back to their original position. 
```
> re.search(r"ㅡ", "한글") # no match
> kre.search(r"ㅡ", "한글")
<kre.KRE_Match object; span=(1, 2), match='글'>
```

In the case of subcharacter-level substitutions, kre can recombine any newly created sequences into standard Korean characters, provided the input used standard (syllable) characters.
``` 
> kre.sub(r"ㅏ", r"ㅗ", "핳ㅏ하ㅎㅏ하핳")
'홓ㅗ호ㅎㅗ호홓'
```

If you prefer, kre can also attempt to merge non-standard input with substitutions.
```
> kre.sub(r"ㅏ", r"ㅗ", "핳ㅏ하ㅎㅏ하핳", syllabify="extended")
'호호호호호홓'
```

Although linearizing a Korean string normally results in the loss of information about syllable boundaries, kre makes it possible to make use of syllable boundaries in regular expression patterns through the use of (customizable) syllable delimiters (';' by default).
```
> kre.search(r"ㅇ", "생일 축하해~")
<kre.KRE_Match object; span=(0, 1), match='생'>
> kre.search(r";ㅇ", "생일 축하해~", boundaries=True)
<kre.KRE_Match object; span=(1, 2), match='일'>
```

As a more interesting, complicated, and perhaps useless example of what kre can do, the following swaps every sequential pair of final consonant(s) (받침) in the input string. 
```
> sun_and_moon = "옛날 옛적 깊은 산 속에 가난하지만 사이좋은 오누이와 그 홀어머니 가족이 살고 있었다."
> kre.sub(r"([ㅏ-ㅣ])([ㄱ-ㅎ]{1,2};)(.*?)([ㅏ-ㅣ])([ㄱ-ㅎ]{1,2};)", r"\1\5\3\4\2", sun_and_moon, boundaries=True)
'옐낫 옉젓 긴읖 삭 손에 가난하지만 사이존읗 오누이와 그 혹어머니 가졸이 샀고 일었다.'
```
