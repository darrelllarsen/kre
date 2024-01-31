import pytest, re
import kre.kre as kre

arirang = "아리랑 아리랑 아라리요. 아리랑 고개로 넘어간다. 나를 버리고 가시는 님은 십리도 못가서 발병 난다."

news = '월간<산>은 무명명산들을 독자들의 도움을 통해 하나씩 찾아나간다. 국립, 군립, 도립공원 및 100대 명산에 해당하지 않는 산이면서 또 산행하는 것이 불법이 아닌 산이 대상이다. 직접 제보한 독자와 함께 오른다. 제보는 blackhouse@chosun.com 찬란했다. 분명히 빛나고 있었다. 햇빛이 들지 않는 깊은 산골인데도 눈이 부셨다. 구불거리는 계곡을 따라 흘러온 티 없이 투명한 물이 바위에 부딪쳐 맑게 부서지며 빛의 파편을 흩뿌린다. 그 광경에 눈이 멀 것 같아 잠시 이끼 낀 바위에 눈을 얹혀놓고 쉬어본다. 그러자 이번엔 계곡이 산의 정수리부터 꼭 잡아 끌고 내려온 냉기를 온 몸에 퍼붓는다. 살짝 솟았던 땀이 꼼짝없이 얼어붙는다. 귀를 앵앵거리는 날벌레도, 시끄러운 트로트 소리도 없는, 고요한 오지계곡의 호사다. 충북 제천 십자봉(983m)은 완전히 알려지지 않은 산은 아니다. 최근 등산을 시작한 이들에게는 깜깜할지 몰라도 약 30~40년 전부터 꾸준히 산악인들이 찾아온 바 있다. 십자봉을 제보해 준 독자 박노원씨는 "십자봉이 있는 제천시 백운면은 내 고향 시골"이라며 "현재 내 나이가 50대 후반인데 고등학교 무렵부터 산악인들이 찾기 시작했던 것으로 기억한다"고 전했다. 특히 발치에 흐르는 덕동계곡이 2000년대 이후 조용히 다녀오기 좋은 피서지로 유명세를 탔기에 이를 낀 십자봉의 존재도 덩달아 상기되곤 했다. 그래서 여름 무더위에 가기 딱 좋은 산으로 꼽힌다. 이처럼 이름값이 있지만 그래도 여전히 오지의 산임은 분명하다. 제천과 충주, 원주 사이에 있으며 서쪽에 미륵산, 북쪽에 백운산과 치악산에 둘러싸인 형세이기 때문에 개발의 손길이 거의 미치지 않았고, 등산객의 답압이 자연의 성장속도를 이기지 못해 등산로 대부분 수풀이 우거져 있다.'

nonsense = '할ㄱ으하느늘근ㅡ'

### Public Functions

def test_search():
    res = kre.search('ㅏㄴ[ㄱ-ㅣ ]+독', news)
    assert res.group() == "산들을 독"
    res = kre.search('ㅏㄴ[ㄱ-ㅣ >]+독', news)
    assert res.group() == "산>은 무명명산들을 독"
    res = kre.search('(ㄹ).*(ㄴ)', arirang)
    assert res.regs == ((1, 54), (1, 2), (53, 54))

def test_match():
    res = kre.match('ㅏㄴ[ㄱ-ㅣ ]+독', news)
    assert res == None
    res = kre.match('.ㅝ[^ㅎ]*', news)
    assert res.group() == "월간<산>은 무명명산들을 독자들의 도움을 통"
    assert res.span() == (0,24)
    assert res.start() == 0
    assert res.end() == 24
    res = kre.match(r"ㅎ", "한글") # 1st letter of 1st syllable
    assert res.span() == (0,1)
    res = kre.match(r"ㅏ", "한글") # 2nd letter of 1st syllable
    assert res == None

def test_fullmatch():
    pass

def test_sub():
    res = kre.sub('ㄴ다', 'ㄹ 거예요', arirang, syllabify="extended")
    assert res == "아리랑 아리랑 아라리요. 아리랑 고개로 넘어갈 거예요. 나를 버리고 가시는 님은 십리도 못가서 발병 날 거예요."


def test_subn():
    assert kre.subn('a', 'b', 'c') == ('c', 0)

    res = kre.subn('느', '나가', nonsense, syllabify="extended")
    assert res == ('할ㄱ으하나가나갈그나가', 3)

    res = kre.subn('ㅏ','ㅗ',nonsense, syllabify="extended")
    assert res == ('홁으호느늘근ㅡ', 2)

    res = kre.subn('ㅡ','ㅓ', nonsense, syllabify='none')
    assert res ==  ('할ㄱㅇㅓ하ㄴㅓㄴㅓㄹㄱㅓㄴㅓ', 5)

    # Test limiting substitutions with 'count' variable
    res = kre.subn('ㅡ','ㅓ', nonsense, count=2, syllabify='none')
    assert res ==  ('할ㄱㅇㅓ하ㄴㅓ늘근ㅡ', 2)
    
    # Substitution count != 'count' variable if fewer matches 
    res = kre.subn('ㅡ','ㅓ', nonsense, count=6, syllabify='none')
    assert res ==  ('할ㄱㅇㅓ하ㄴㅓㄴㅓㄹㄱㅓㄴㅓ', 5)

    res = kre.subn('ㅡ','ㅓ', nonsense, syllabify='minimal')
    assert res == ('할ㄱ어하너널건ㅓ', 5)

    res = kre.subn('ㅡ','ㅓ', nonsense, syllabify='extended')
    assert res == ('할ㄱ어하너널거너', 5)

    res = kre.subn('ㅡ','ㅓ', nonsense, syllabify='full')
    assert res == ('핡어하너널거너', 5)

    # Test multiple substitutions affecting same syllable
    res = kre.subn('ㅇ','ㄱ', '앙', syllabify="extended")
    assert res == ('각', 2) # former error: "강악"

    res = kre.subn('[ㅇ|ㅏ]','ㄱ', '앙', syllabify="extended")
    assert res == ('ㄱㄱㄱ', 3)

def test_empty_strings():
    res = kre.sub('a?', 'b', nonsense)
    assert res == ('bㅎbㅏbㄹbㄱbㅇbㅡbㅎbㅏbㄴbㅡbㄴbㅡbㄹbㄱbㅡbㄴbㅡb')

def test_split():
    pass

def test_findall():
    results = kre.findall('ㅏㄹ', arirang)
    assert results == ['아리', '아리', '아라', '라리', '아리', '나를', '발']

    res = kre.findall('ㄹ;', arirang, boundaries=True)
    assert res == ['를', '발']

    res = kre.findall(';ㄹ', arirang, boundaries=True)
    assert res == ['리', '랑', '리', '랑', '라', '리', '리', '랑', '로', '를', '리', '리']

    res = kre.findall('ㄹ.ㄹ', arirang)
    assert res == ['리랑', '리랑', '라리', '리랑', '를']

    res = kre.findall('ㄹ.ㄹ', arirang, boundaries=True)
    assert res == ['를']

    res = kre.findall('ㄹ;ㄹ', arirang, boundaries=True)
    assert res == None

    res = kre.findall('ㄹ.;ㄹ', arirang, boundaries=True)
    assert res == ['리랑', '리랑', '라리', '리랑']

    res = kre.findall(';ㄹ.ㄹ;', arirang, boundaries=True)
    assert res == ['를']

    res = kre.findall('ㄹ%', arirang, boundaries=True, delimiter='%')
    assert res == ['를', '발']


def test_finditer():
    pass

def test_compile():
    pass

def test_purge():
    pass

def test_escape():
    pass

### KRE_Pattern Method Calls
def test_kre_pattern_search():
    m = kre.compile('ㅏㄴ[ㄱ-ㅣ ]+독')
    res = m.search(news)
    assert res.group() == "산들을 독"
    m = kre.compile('ㅏㄴ[ㄱ-ㅣ >]+독')
    res = m.search(news)
    assert res.group() == "산>은 무명명산들을 독"

def test_kre_pattern_match():
    m = kre.compile('ㅏㄴ[ㄱ-ㅣ ]+독')
    res = m.match(news)
    assert res == None
    m = kre.compile('.ㅝ[^ㅎ]*')
    res = m.match(news)
    assert res.group() == "월간<산>은 무명명산들을 독자들의 도움을 통"
    assert res.span() == (0,24)
    assert res.start() == 0
    assert res.end() == 24

def test_kre_pattern_match_with_pos():
    p = kre.compile(r'ㅏ')
    assert p.match("한글") == None
    assert p.match("한글", 0).span() == (0,1)
    assert p.match("한글", 1) == None

def test_kre_pattern_match_with_pos_and_boundaries():
    # Test if pos expands to include preceding boundary
    # No boundaries in pattern
    p = kre.compile(r"ㄱ")
    p.match("한글", 0, boundaries=True) == None
    p.match("한글", 1, boundaries=True).span() == (1,2)
    
    # Preceding boundary in pattern
    p = kre.compile(r";ㄱ")
    p.match("한글", 1, boundaries=True).span() == (1,2)
    
    # Following boundary in pattern
    p = kre.compile(r"ㄱ;")
    p.match("한글", 1, boundaries=True) == None
    p = kre.compile(r"ㄹ;")
    p.match("한글", 1, boundaries=True).span() == (1,2)

def test_kre_pattern_fullmatch():
    pass

def test_kre_pattern_fullmatch_with_pos_and_boundaries():
    p = kre.compile(r"ㅡㄹ")
    p.match("한글", 1, boundaries=True) == None
    p = kre.compile(r"ㅡㄹ;")
    p.match("한글", 1, boundaries=True).span == (1,2)


def test_kre_pattern_sub():
    m = kre.compile('ㄴ다')
    res = m.sub('ㄹ 거예요', arirang, syllabify="extended")
    assert res == "아리랑 아리랑 아라리요. 아리랑 고개로 넘어갈 거예요. 나를 버리고 가시는 님은 십리도 못가서 발병 날 거예요."

def test_kre_pattern_subn():
    m = kre.compile('느')
    res = m.subn('나가', nonsense, syllabify="extended")
    assert res == ('할ㄱ으하나가나갈그나가', 3)

    m = kre.compile(';느')
    res = m.subn(';나가', nonsense, boundaries=True, syllabify="extended")
    assert res == ('할ㄱ으하나가나갈근ㅡ', 2)

    # syllable-final boundary in pattern and sub
    m = kre.compile('[ㄱ|ㄴ];')
    res = m.subn('ㅁ;',nonsense, boundaries=True, syllabify="extended")
    assert res == ('할ㅁ으하느늘금ㅡ', 2)

    # syllable-final boundary in pattern but not sub
    m = kre.compile('[ㄱ|ㄴ];')
    res = m.subn('ㅁ',nonsense, boundaries=True, syllabify="extended")
    assert res == ('할ㅁ으하느늘그므', 2)

    m = kre.compile('ㅏ')
    res = m.subn('ㅗ',nonsense, syllabify="extended")
    assert res == ('홁으호느늘근ㅡ', 2)

    ### Boundaries True/False pairs
    m = kre.compile(r'ㅡ')
    m2 = kre.compile(r'ㅡㄴ')
    res = m.subn('ㅓ', nonsense, syllabify='none')
    assert res ==  ('할ㄱㅇㅓ하ㄴㅓㄴㅓㄹㄱㅓㄴㅓ', 5)

    m = kre.compile('ㅡ')
    res = m.subn('ㅓ', nonsense, boundaries=True, syllabify='none')
    assert res ==  ('할ㄱㅇㅓ하ㄴㅓㄴㅓㄹㄱㅓㄴㅓ', 5)

    # syllabify='minimal': result may differ for patterns that cross
    # syllables
    # same
    res = m.subn('ㅓ', nonsense, syllabify='minimal')
    assert res == ('할ㄱ어하너널건ㅓ', 5)

    res = m.subn('ㅓ', nonsense, boundaries=True, syllabify='minimal')
    assert res == ('할ㄱ어하너널건ㅓ', 5)

    # different
    res = m2.subn(r'ㅓㄴ', nonsense, syllabify="minimal")
    assert res == ('할ㄱ으하너늘건ㅡ', 2)

    res = m2.subn(r'ㅓㄴ', nonsense, boundaries=True, syllabify="minimal")
    assert res == ('할ㄱ으하느늘건ㅡ', 1)

    # syllabify='extended': result may differ for patterns that cross
    # syllables
    # same
    res = m.subn('ㅓ', nonsense, syllabify='extended')
    assert res == ('할ㄱ어하너널거너', 5)

    res = m.subn('ㅓ', nonsense, boundaries=True, syllabify='extended')
    assert res == ('할ㄱ어하너널건ㅓ', 5)

    # different
    res = m2.subn(r'ㅓㄴ', nonsense, syllabify="extended")
    assert res == ('할ㄱ으하너늘거느', 2)

    res = m2.subn(r'ㅓㄴ', nonsense, boundaries=True, syllabify="extended")
    assert res == ('할ㄱ으하느늘건ㅡ', 1)

    # syllabify='full'
    # same
    res = m.subn('ㅓ', nonsense, syllabify='full')
    assert res == ('핡어하너널거너', 5)

    res = m.subn('ㅓ', nonsense, boundaries=True, syllabify='full')
    assert res == ('핡어하너널거너', 5)

    # different
    res = m2.subn('ㅓㄴ', nonsense, syllabify='full')
    assert res == ('핡으하너늘거느', 2)

    res = m2.subn('ㅓㄴ', nonsense, boundaries=True, syllabify='full')
    assert res == ('핡으하느늘거느', 1)

    # With boundaries=True, 'minimal' and 'extended' differ only when
    # boundary from pattern is removed from repl argumenta
    m3 = kre.compile(r'ㅡㄴ;')
    m4 = kre.compile(r';ㅡ')
    
    res = m3.subn(r'ㅓㄴ', nonsense, boundaries=True, syllabify="minimal")
    assert res == ('할ㄱ으하느늘건ㅡ', 1)

    res = m3.subn(r'ㅓㄴ', nonsense, boundaries=True, syllabify="extended")
    assert res == ('할ㄱ으하느늘거느', 1)

    res = m4.subn(r'ㅓ', nonsense, boundaries=True, syllabify="minimal")
    assert res == ('할ㄱ으하느늘근ㅓ', 1)

    res = m4.subn(r'ㅓ', nonsense, boundaries=True, syllabify="extended")
    assert res == ('할ㄱ으하느늘그너', 1)

def test_kre_pattern_split():
    pass

def test_kre_pattern_findall():
    m = kre.compile('ㅏㄹ')
    results = m.findall(arirang)
    assert results == ['아리', '아리', '아라', '라리', '아리', '나를', '발']

    m = kre.compile('ㄹ;')
    res = m.findall(arirang, boundaries=True)
    assert res == ['를', '발']

    m = kre.compile(';ㄹ')
    res = m.findall(arirang, boundaries=True)
    assert res == ['리', '랑', '리', '랑', '라', '리', '리', '랑', '로', '를', '리', '리']

    m = kre.compile('ㄹ.ㄹ')
    res = m.findall(arirang)
    assert res == ['리랑', '리랑', '라리', '리랑', '를']

    m = kre.compile('ㄹ.ㄹ')
    res = m.findall(arirang, boundaries=True)
    assert res == ['를']

    m = kre.compile('ㄹ;ㄹ')
    res = m.findall(arirang, boundaries=True)
    assert res == None

    m = kre.compile('ㄹ.;ㄹ')
    res = m.findall(arirang, boundaries=True)
    assert res == ['리랑', '리랑', '라리', '리랑']

    m = kre.compile(';ㄹ.ㄹ;')
    res = m.findall(arirang, boundaries=True)
    assert res == ['를']

    m = kre.compile('ㄹ%')
    res = m.findall(arirang, boundaries=True, delimiter='%')
    assert res == ['를', '발']

def test_kre_pattern_finditer():
    pass


### KRE_Match object attributes and functions

def test_kre_match_special_cases():
    # The following includes a named group, unmatched capturing group,
    # and empty string matching group.
    p = kre.compile(r"a(?P<f>f)(p)?(.*?)")
    m = p.search('sdaflkj')
    re_p = re.compile(r"a(?P<f>f)(p)?(.*?)")
    re_m = re_p.search('sdaflkj')
    assert m.regs == re_m.regs
    assert m.groups() == re_m.groups()
    for n in range(len(m.regs)):
        assert m.group(n) == re_m.group(n)


    # Test case: matches of empty strings, but at syllable boundaries
    # and within syllables. For such cases, re module returns span of
    # length 0 (pos==endpos), whereas kre returns length 1 when empty
    # string is syllable-internal.

def test_kre_match_object():
    # Test case: match of search is syllable, so result should be 
    # identical to standard re search

    # Pattern includes named and unnamed groups, as well as a named
    # group with 0 matches
    p = kre.compile('(?P<첫째>ㄱ)(으)(?P<h>h)?.*(?P<둘째>근)')
    m = p.search(nonsense)
    re_p = re.compile('(?P<첫째>ㄱ)(으)(?P<h>h)?.*(?P<둘째>근)')
    re_m = re_p.search(nonsense)

    # attributes
    assert m.pos == re_m.pos
    assert m.endpos == re_m.endpos
    # assert m.re == re_m.re # WILL CHANGE
    assert m.regs == re_m.regs
    assert m.string == re_m.string
    assert m.lastgroup == re_m.lastgroup
    assert m.lastindex == re_m.lastindex

    # methods
    assert m.end() == re_m.end()
    assert m.start() == re_m.start()
    assert m.groups() == re_m.groups()
    assert m.span() == re_m.span()
    # Change default value for unmatched groups (default is None)
    assert m.groups('changed') == re_m.groups('changed')
    for n in range(len(m.groups())+1):
        assert m.end(n) == re_m.end(n)
        assert m.start(n) == re_m.start(n)
        assert m.group(n) == re_m.group(n)
        assert m.span(n) == re_m.span(n)
    assert m.groupdict() == re_m.groupdict()
    # Change default value for unmatched named groups (default is None)
    assert m.groupdict('changed') == re_m.groupdict('changed')

    # not yet implemented
    #assert m.expand() == re_m.expand()

def test_kre_match_object2():
    # Test case: match of search is subsyllable, so result should be 
    # identical to standard re search

    # Pattern includes named and unnamed groups, as well as a named
    # group with 0 matches
    # kre searches for subsyllables should have same results as re
    # searches for syllables containing said subsyllables
    p = kre.compile('(?P<첫째>ㄱ).(ㅡ)(?P<h>h)?.*(?P<둘째>그)')
    m = p.search(nonsense)
    re_p = re.compile('(?P<첫째>ㄱ)(으)(?P<h>h)?.*(?P<둘째>근)')
    re_m = re_p.search(nonsense)

    # attributes
    assert m.pos == re_m.pos
    assert m.endpos == re_m.endpos
    # assert m.re == re_m.re # WILL CHANGE
    assert m.regs == re_m.regs
    assert m.string == re_m.string
    assert m.lastgroup == re_m.lastgroup
    assert m.lastindex == re_m.lastindex

    # methods
    assert m.end() == re_m.end()
    assert m.start() == re_m.start()
    assert m.groups() == re_m.groups()
    assert m.span() == re_m.span()
    # Change default value for unmatched groups (default is None)
    assert m.groups('changed') == re_m.groups('changed')
    for n in range(len(m.groups())+1):
        assert m.end(n) == re_m.end(n)
        assert m.start(n) == re_m.start(n)
        assert m.group(n) == re_m.group(n)
        assert m.span(n) == re_m.span(n)
    assert m.groupdict() == re_m.groupdict()
    # Change default value for unmatched named groups (default is None)
    assert m.groupdict('changed') == re_m.groupdict('changed')

    # not yet implemented
    #assert m.expand() == re_m.expand()

def test_kre_match_object3():
    # Test case: match of subsyllables pattern that crosses syllables. 
    # Result should be identical to standard re search off all involved
    # syllables

    # Pattern includes named and unnamed groups, as well as a named
    # group with 0 matches
    # kre searches for subsyllables should have same results as re
    # searches for syllables containing said subsyllables
    p = kre.compile('(?P<첫째>ㄱ.ㅡ)(?P<h>h)?.*(?P<둘째>그)')
    m = p.search(nonsense)
    re_p = re.compile('(?P<첫째>ㄱ으)(?P<h>h)?.*(?P<둘째>근)')
    re_m = re_p.search(nonsense)

    # attributes
    assert m.pos == re_m.pos
    assert m.endpos == re_m.endpos
    # assert m.re == re_m.re # WILL CHANGE
    assert m.regs == re_m.regs
    assert m.string == re_m.string
    assert m.lastgroup == re_m.lastgroup
    assert m.lastindex == re_m.lastindex

    # methods
    assert m.end() == re_m.end()
    assert m.start() == re_m.start()
    assert m.groups() == re_m.groups()
    assert m.span() == re_m.span()
    # Change default value for unmatched groups (default is None)
    assert m.groups('changed') == re_m.groups('changed')
    for n in range(len(m.groups())+1):
        assert m.end(n) == re_m.end(n)
        assert m.start(n) == re_m.start(n)
        assert m.group(n) == re_m.group(n)
        assert m.span(n) == re_m.span(n)
    assert m.groupdict() == re_m.groupdict()
    # Change default value for unmatched named groups (default is None)
    assert m.groupdict('changed') == re_m.groupdict('changed')

    # not yet implemented
    #assert m.expand() == re_m.expand()

def test_kre_match_object4():
    # Test case: match of subsyllables pattern that crosses syllables. 
    # Result should be identical to standard re search off all involved
    # syllables

    # Pattern includes named and unnamed groups, as well as a named
    # group with 0 matches
    # kre searches for subsyllables should have same results as re
    # searches for syllables containing said subsyllables
    p = kre.compile('(?P<첫째>ㄱ;.ㅡ)(?P<h>h)?.*(?P<둘째>그)')
    m = p.search(nonsense, boundaries=True)
    re_p = re.compile('(?P<첫째>ㄱ으)(?P<h>h)?.*(?P<둘째>근)')
    re_m = re_p.search(nonsense)

    # attributes
    assert m.pos == re_m.pos
    assert m.endpos == re_m.endpos
    # assert m.re == re_m.re # WILL CHANGE
    assert m.regs == re_m.regs
    assert m.string == re_m.string
    assert m.lastgroup == re_m.lastgroup
    assert m.lastindex == re_m.lastindex

    # methods
    assert m.end() == re_m.end()
    assert m.start() == re_m.start()
    assert m.groups() == re_m.groups()
    assert m.span() == re_m.span()
    # Change default value for unmatched groups (default is None)
    assert m.groups('changed') == re_m.groups('changed')
    for n in range(len(m.groups())+1):
        assert m.end(n) == re_m.end(n)
        assert m.start(n) == re_m.start(n)
        assert m.group(n) == re_m.group(n)
        assert m.span(n) == re_m.span(n)
    assert m.groupdict() == re_m.groupdict()
    # Change default value for unmatched named groups (default is None)
    assert m.groupdict('changed') == re_m.groupdict('changed')

    # not yet implemented
    #assert m.expand() == re_m.expand()

def test_kre_match_object5():
    # Test case: match of subsyllables pattern that crosses syllables. 
    # Result should be identical to standard re search off all involved
    # syllables

    # Pattern includes named and unnamed groups, as well as a named
    # group with 0 matches
    # kre searches for subsyllables should have same results as re
    # searches for syllables containing said subsyllables
    p = kre.compile('(?P<첫째>ㄱ)(.ㅡ).*(?P<둘째>그)(?P<h>h)?')
    m = p.search(nonsense)
    re_p = re.compile('(?P<첫째>ㄱ)(으).*(?P<둘째>근)(?P<h>h)?')
    re_m = re_p.search(nonsense)

    # attributes
    assert m.pos == re_m.pos
    assert m.endpos == re_m.endpos
    # assert m.re == re_m.re # WILL CHANGE
    assert m.regs == re_m.regs
    assert m.string == re_m.string
    assert m.lastgroup == re_m.lastgroup
    assert m.lastindex == re_m.lastindex

    # methods
    assert m.end() == re_m.end()
    assert m.start() == re_m.start()
    assert m.groups() == re_m.groups()
    assert m.span() == re_m.span()
    # Change default value for unmatched groups (default is None)
    assert m.groups('changed') == re_m.groups('changed')
    for n in range(len(m.groups())+1):
        assert m.end(n) == re_m.end(n)
        assert m.start(n) == re_m.start(n)
        assert m.group(n) == re_m.group(n)
        assert m.span(n) == re_m.span(n)
    assert m.groupdict() == re_m.groupdict()
    # Change default value for unmatched named groups (default is None)
    assert m.groupdict('changed') == re_m.groupdict('changed')

    # not yet implemented
    #assert m.expand() == re_m.expand()

### Mapping class tests 
def test_kre_mapping():
    ls = kre.Mapping('This is 한글ㅋㅋ.', boundaries=True)
    assert ls.delimited == 'This is ;한;글;ㅋ;ㅋ;.'
    assert ls.del2orig == (0, 1, 2, 3, 4, 5, 6, 7, None, 8, None, 9, 
            None, 10, None, 11, None, 12)


### KRE_Pattern Method Calls
