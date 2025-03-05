import pandas as pd
from thokit import ThoKit
import re
import os
from collections import defaultdict
from tqdm import tqdm

df = pd.read_csv('dict-new.csv')

hanji_ascii_list = []
poj_ascii_dict = defaultdict()

for i, row in tqdm(df.iterrows()):
	poj_unicode, hanji, comment = row['poj_unicode'], row['ji'], row['comment']
	poj_unicode = re.sub('\[[^\]]*\]', '', poj_unicode)
	hanji = re.sub('\[[^\]]*\]', '', hanji)
	poj_ascii = ThoKit().pojUnicode2Ascii(poj_unicode, standard='campbell')
	if (poj_unicode, poj_ascii) not in poj_ascii_dict:
		poj_ascii_dict[(poj_unicode, poj_ascii)] = 1
	else:
		poj_ascii_dict[(poj_unicode, poj_ascii)] += 1
	if (poj_unicode.lower(), poj_ascii.lower()) not in poj_ascii_dict:
		poj_ascii_dict[(poj_unicode.lower(), poj_ascii.lower())] = 1
	else:
		poj_ascii_dict[(poj_unicode.lower(), poj_ascii.lower())] += 1
	if hanji not in ['●', '—'] and (poj_unicode, hanji) not in hanji_ascii_list:
		hanji_ascii_list.append((hanji, poj_ascii))
	comment = re.sub('\[[^\]]*\]', '', comment)
	for res_unicode in re.findall('[a-z\-áàâāa̍éèêēe̍íìîīi̍úùûūu̍o͘óòôōo̍ńǹn̂n̄n̍ⁿ]+', comment, flags=re.IGNORECASE):
		if res_unicode.startswith('-') or res_unicode.endswith('-'):
			continue
		res_ascii = ThoKit().pojUnicode2Ascii(res_unicode, standard='campbell')
		if (res_unicode, res_ascii) not in poj_ascii_dict:
			poj_ascii_dict[(res_unicode, res_ascii)] = 1
		else:
			poj_ascii_dict[(res_unicode, res_ascii)] += 1
		if (res_unicode.lower(), res_ascii.lower()) not in poj_ascii_dict:
			poj_ascii_dict[(res_unicode.lower(), res_ascii.lower())] = 1
		else:
			poj_ascii_dict[(res_unicode.lower(), res_ascii.lower())] += 1

if not os.path.exists('rime'): os.makedirs('rime')

with open('rime/kamjitian.hanji.dict.yaml', 'w', encoding='utf-8') as f:
	hanji_yaml_prefix = '''# Rime dictionary
# encoding: utf-8
#
# KamJiTian -- HÀN-JĪ
#
# 廈門音新字典（甘字典）・漢字
#
# 碼表取自信望愛提供、東苑實驗室校增的
# 甘為霖《廈門音新字典》(Kam Ûi-lîm ê "Ē-mn̄g Im ê Jī-tián")
# (William Campbell, "A Dictionary of the Amoy Vernacular")
---
name: kamjitian.hanji
version: "2025.3.5"
sort: by_weight
use_preset_vocabulary: false
...
'''
	f.write(hanji_yaml_prefix)
	for tup in hanji_ascii_list:
		f.write(tup[0]+'\t'+tup[1]+'\n')

with open('rime/kamjitian.poj.dict.yaml', 'w', encoding='utf-8') as f:
	poj_yaml_prefix = '''# Rime dictionary
# encoding: utf-8
#
# KamJiTian -- PE̍H-OĒ-JĪ
#
# 廈門音新字典（甘字典）・白話字
#
# 碼表取自信望愛提供、東苑實驗室校增的
# 甘為霖《廈門音新字典》(Kam Ûi-lîm ê "Ē-mn̄g Im ê Jī-tián")
# (William Campbell, "A Dictionary of the Amoy Vernacular")
---
name: kamjitian.poj
version: "2025.3.5"
sort: by_weight
use_preset_vocabulary: false
...
-	-	100%
'''
	f.write(poj_yaml_prefix)
	for tup, freq in poj_ascii_dict.items():
		f.write(f'{tup[0]}\t{tup[1]}\t{freq}\n')