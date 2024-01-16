﻿#KO: Basic Tools for Working with Korean Text
#Version 0.5.2
#Author: Darrell Larsen
#
#Distributed under GNU General Public License v3.0

### Conversion dictionaries
### Format: korean_letter : (decomposed_value, yale_romanization)
INITIALS = {'ㄱ':(0,'k'),'ㄲ':(1,'kk'),'ㄴ':(2,'n'),'ㄷ':(3,'t'),'ㄸ':(4,'tt'),
'ㄹ':(5, 'l'),'ㅁ':(6,'m'),'ㅂ':(7,'p'),'ㅃ':(8,'pp'),'ㅅ':(9,'s'),'ㅆ':(10,'ss'),
'ㅇ':(11,''),'ㅈ':(12,'c'),'ㅉ':(13,'cc'),'ㅊ':(14,'ch'),'ㅋ':(15,'kh'),'ㅌ':(16,'th'),
'ㅍ':(17,'ph'),'ㅎ':(18,'h')}

MEDIALS = {'ㅏ':(0,'a'),'ㅐ':(1,'ay'),'ㅑ':(2,'ya'),'ㅒ':(3,'yay'),'ㅓ':(4,'e'),
'ㅔ':(5,'ey'),'ㅕ':(6,'ye'),'ㅖ':(7,'yey'),'ㅗ':(8,'o'),'ㅘ':(9,'wa'),'ㅙ':(10,'way'),
'ㅚ':(11,'oy'), 'ㅛ':(12,'yo'),'ㅜ':(13,'wu'),'ㅝ':(14,'we'),'ㅞ':(15,'wey'),'ㅟ':(16,'wi'),
'ㅠ':(17,'yu'),'ㅡ':(18,'u'),'ㅢ':(19,'uy'),'ㅣ':(20,'i')}

FINALS = {'':(0,''),'ㄱ':(1,'k'),'ㄲ':(2,'kk'),'ㄳ':(3,'ks'),'ㄴ':(4,'n'),
'ㄵ':(5,'nc'),'ㄶ':(6,'nh'),'ㄷ':(7,'t'),'ㄹ':(8,'l'),'ㄺ':(9,'lk'),'ㄻ':(10,'lm'),
'ㄼ':(11,'lp'),'ㄽ':(12,'ls'),'ㄾ':(13,'lth'),'ㄻ':(14,'lm'),'ㅀ':(15,'lh'),'ㅁ':(16,'m'),
'ㅂ':(17,'p'),'ㅄ':(18,'ps'),'ㅅ':(19,'s'),'ㅆ':(20,'ss'),'ㅇ':(21,'ng'),'ㅈ':(22,'c'),
'ㅊ':(23,'ch'),'ㅋ':(24,'kh'),'ㅌ':(25,'th'),'ㅍ':(26,'ph'),'ㅎ':(27,'h')}

COMBINED_FINALS = {'ㄳ':'ㄱㅅ', 'ㄵ':'ㄴㅈ','ㄶ':'ㄴㅎ','ㄺ':'ㄹㄱ','ㄻ':'ㄹㅁ',
'ㄼ':'ㄹㅂ','ㄽ':'ㄹㅅ','ㄾ':'ㄹㅌ','ㄻ':'ㄹㅁ','ㅀ':'ㄹㅎ','ㅄ':'ㅂㅅ'}

SPLIT_FINALS = {val:key for key, val in COMBINED_FINALS.items()}

### Section: Constants
DIPTHONGS = '(ㅑㅒㅖㅛㅠㅘㅙㅚㅝㅞㅟㅢ)'
TRAD_DIPTHONGS = '(ㅑㅒㅖㅛㅠㅘㅙㅝㅞㅟ)' # excludes ㅚ and ㅢ
