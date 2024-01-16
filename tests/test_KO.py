import pytest
import kre.KO as KO

### Test hidden functions
def test_get_split_values():
    assert KO._get_split_values("흙") == (18,18,9)
    assert KO._get_split_values("다") == (3,0,0)
    with pytest.raises(ValueError) as e_info:
        x = KO._get_split_values("ㅋ")

def test_get_letters():
    assert KO._get_letters((18,18,9)) == ('ㅎ','ㅡ','ㄺ')
    assert KO._get_letters((3,0,0)) == ('ㄷ','ㅏ','')

def test_get_combined_value():
    assert KO._get_combined_value('ㄷ','ㅏ','ㄺ') == 45805
    assert KO._get_combined_value('ㄷ','ㅏ', '') == 45796
    assert KO._get_combined_value('ㄷ','ㅏ') == 45796

def test_values_to_letter():
    assert KO._values_to_letter(('ㅇ','ㅘ','ㅇ')) == '왕'
    assert KO._values_to_letter(['ㅇ','ㅘ','ㅇ']) == '왕'
    assert KO._values_to_letter(('ㅇ','ㅘ','')) == '와'
    assert KO._values_to_letter(('ㅇ','ㅘ')) == '와'

def test_combine_value_list():
    assert KO._combine_value_list((18,18,9)) == '흙'
    assert KO._combine_value_list((3,0,0)) == '다'

def test_split_coda():
    assert KO._split_coda('ㄺ') == 'ㄹㄱ'
    assert KO._split_coda('닭') == '닭'

def test_combine_coda():
    assert KO._combine_coda('ㄹㄱ') == 'ㄺ'
    assert KO._combine_coda('ㄹㅓ') == 'ㄹㅓ'
    assert KO._combine_coda('ㅎㅡㄹㄱ') == 'ㅎㅡㄹㄱ'

### Test external functions
def test_combine():
    assert KO.combine('ㄷㅏㄺ') == '닭'
    assert KO.combine('ㄷㅏㄹㄱ') == '닭'
    assert KO.combine(('ㄷ', 'ㅏ', 'ㄺ')) == '닭' 
    assert KO.combine(('ㄷ', 'ㅏ', 'ㄹㄱ')) == '닭' 
    assert KO.combine(('ㄷ', 'ㅏ', 'ㄹ','ㄱ')) == '닭' 

def test_split():
    assert KO.split('닭', fill_finals = True) == ['ㄷ', 'ㅏ', 'ㄺ']
    assert KO.split('닭', fill_finals = False) == ['ㄷ', 'ㅏ', 'ㄺ']
    assert KO.split('다', fill_finals = False) == ['ㄷ', 'ㅏ']
    assert KO.split('다', fill_finals = True) == ['ㄷ', 'ㅏ', '']
    assert KO.split('닭', split_coda = True) == ['ㄷ', 'ㅏ', 'ㄹㄱ']
    assert KO.split('닭', fill_finals = True, split_coda = True) == ['ㄷ', 'ㅏ', 'ㄹㄱ']

def test_isSyllable():
    assert KO.isSyllable('닭') == True
    assert KO.isSyllable('w') == False
    assert KO.isSyllable('ㅈ') == False
    assert KO.isSyllable('달걀') == False

def test_isComplexCoda():
    assert KO.isComplexCoda('ㄹ') == False
    assert KO.isComplexCoda('ㄺ') == True
    assert KO.isComplexCoda('ㄹㄱ') == False
    assert KO.isComplexCoda('ㄺ다') == False
    
def test_isComplexOnset():
    assert KO.isComplexOnset('ㄴ') == False
    assert KO.isComplexOnset('ᄓ') == True
    assert KO.isComplexOnset('ㄴㄱ') == False

def test_isJamo():
    assert KO.isJamo('ㄱ') == True
    assert KO.isJamo('ㅣ') == True
    assert KO.isJamo('ㄺ') == True
    assert KO.isJamo('ㄹㄱ') == False

def test_isLetter():
    assert KO.isLetter('ㄱ') == True
    assert KO.isLetter('ㅣ') == True
    assert KO.isLetter('ㄺ') == False
    assert KO.isLetter('ㄺ', include_complex=True) == True
    assert KO.isLetter('ㄹㄱ') == False

def test_isHangul():
    assert KO.isHangul('ㄱ') == True
    assert KO.isHangul('ㄺ') == True
    assert KO.isHangul('닭') == True
    assert KO.isHangul('a') == False
    assert KO.isHangul('.') == False

def test_hasHangul():
    assert KO.hasHangul('ㄱ') == True
    assert KO.hasHangul('ㄺ') == True
    assert KO.hasHangul('닭') == True
    assert KO.hasHangul('a') == False
    assert KO.hasHangul('.') == False
    assert KO.hasHangul('A sentence with 한글.') == True
