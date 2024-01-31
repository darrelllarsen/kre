import pytest
import kre.tools._tools as tools

### Test hidden functions
def test_get_split_values():
    assert tools._get_split_values("흙") == (18,18,9)
    assert tools._get_split_values("다") == (3,0,0)
    with pytest.raises(ValueError) as e_info:
        x = tools._get_split_values("ㅋ")

def test_get_letters():
    assert tools._get_letters((18,18,9)) == ('ㅎ','ㅡ','ㄺ')
    assert tools._get_letters((3,0,0)) == ('ㄷ','ㅏ','')

def test_get_combined_value():
    assert tools._get_combined_value('ㄷ','ㅏ','ㄺ') == 45805
    assert tools._get_combined_value('ㄷ','ㅏ', '') == 45796
    assert tools._get_combined_value('ㄷ','ㅏ') == 45796

def test_values_to_letter():
    assert tools._values_to_letter(('ㅇ','ㅘ','ㅇ')) == '왕'
    assert tools._values_to_letter(['ㅇ','ㅘ','ㅇ']) == '왕'
    assert tools._values_to_letter(('ㅇ','ㅘ','')) == '와'
    assert tools._values_to_letter(('ㅇ','ㅘ')) == '와'

def test_combine_value_list():
    assert tools._combine_value_list((18,18,9)) == '흙'
    assert tools._combine_value_list((3,0,0)) == '다'

def test_split_coda():
    assert tools.split_coda('ㄺ') == 'ㄹㄱ'
    assert tools.split_coda('닭') == '닭'

def test_combine_coda():
    assert tools._combine_coda('ㄹㄱ') == 'ㄺ'
    assert tools._combine_coda('ㄹㅓ') == 'ㄹㅓ'
    assert tools._combine_coda('ㅎㅡㄹㄱ') == 'ㅎㅡㄹㄱ'

### Test external functions
def test_combine():
    assert tools.combine('ㄷㅏㄺ') == '닭'
    assert tools.combine('ㄷㅏㄹㄱ') == '닭'
    assert tools.combine(('ㄷ', 'ㅏ', 'ㄺ')) == '닭' 
    assert tools.combine(('ㄷ', 'ㅏ', 'ㄹㄱ')) == '닭' 
    assert tools.combine(('ㄷ', 'ㅏ', 'ㄹ','ㄱ')) == '닭' 

def test_split():
    assert tools.split('닭', fill_finals = True) == ['ㄷ', 'ㅏ', 'ㄺ']
    assert tools.split('닭', fill_finals = False) == ['ㄷ', 'ㅏ', 'ㄺ']
    assert tools.split('다', fill_finals = False) == ['ㄷ', 'ㅏ']
    assert tools.split('다', fill_finals = True) == ['ㄷ', 'ㅏ', '']
    assert tools.split('닭', split_codas = True) == ['ㄷ', 'ㅏ', 'ㄹㄱ']
    assert tools.split('닭', fill_finals = True, split_codas = True) == ['ㄷ', 'ㅏ', 'ㄹㄱ']

def test_isSyllable():
    assert tools.isSyllable('닭') == True
    assert tools.isSyllable('w') == False
    assert tools.isSyllable('ㅈ') == False
    assert tools.isSyllable('달걀') == False

def test_isComplexCoda():
    assert tools.isComplexCoda('ㄹ') == False
    assert tools.isComplexCoda('ㄺ') == True
    assert tools.isComplexCoda('ㄹㄱ') == False
    assert tools.isComplexCoda('ㄺ다') == False
    
def test_isComplexOnset():
    assert tools.isComplexOnset('ㄴ') == False
    assert tools.isComplexOnset('ᄓ') == True
    assert tools.isComplexOnset('ㄴㄱ') == False

def test_isJamo():
    assert tools.isJamo('ㄱ') == True
    assert tools.isJamo('ㅣ') == True
    assert tools.isJamo('ㄺ') == True
    assert tools.isJamo('ㄹㄱ') == False

def test_isLetter():
    assert tools.isLetter('ㄱ') == True
    assert tools.isLetter('ㅣ') == True
    assert tools.isLetter('ㄺ') == False
    assert tools.isLetter('ㄺ', include_complex=True) == True
    assert tools.isLetter('ㄹㄱ') == False

def test_isHangul():
    assert tools.isHangul('ㄱ') == True
    assert tools.isHangul('ㄺ') == True
    assert tools.isHangul('닭') == True
    assert tools.isHangul('a') == False
    assert tools.isHangul('.') == False

def test_hasHangul():
    assert tools.hasHangul('ㄱ') == True
    assert tools.hasHangul('ㄺ') == True
    assert tools.hasHangul('닭') == True
    assert tools.hasHangul('a') == False
    assert tools.hasHangul('.') == False
    assert tools.hasHangul('A sentence with 한글.') == True
