# 校驗羅馬字數據準確性

import pandas as pd
from thokit import ThoKit
import re
import os
from unicodedata import normalize

def normalizePoj(text: str):
	text_ascii = ThoKit().pojUnicode2Ascii(text, standard='campbell')
	try:
		text_ascii = re.sub(
				"([a-zA-Z]+[ptkh]n?n?)2", r'\g<1>8', text_ascii
		)
	except Exception as e:
		print(f"{text_ascii}, {e}")
		exit(-1)
	return ThoKit().pojAscii2Unicode(text_ascii, standard='campbell')


def pojCheck(text: str):
	if '[' not in text:
		text = normalizePoj(text)
	else:
		typo_matches = list(re.finditer('\[[^\|\]]+\|', text))
		if not typo_matches:
			text =  normalizePoj(text)
		else:
			# 原冊筆誤毋參與校驗：設字符串 "a[b|c]d"，不處理 b
			parts = []
			last_pos = 0
			for match in typo_matches:
				if match.start() > last_pos:
					normal_text = text[last_pos:match.start()]
					processed_normal = normalizePoj(normal_text)
					parts.append(processed_normal)
				parts.append(match.group())
				last_pos = match.end()
			
			if last_pos < len(text):
				normal_text = text[last_pos:]
				processed_normal = normalizePoj(normal_text)
				parts.append(processed_normal)
			
			text = ''.join(parts)
	return normalize("NFC", text)
	
# print(pojCheck("[chúi-tsóaⁿ|chiú-tsóaⁿ], niû mi̍h ê khì-kū, tsū-chi̍p, siúⁿ-sù, tí-tng, tāng-tāng."))
# print(pojCheck("[chúi-tsóaⁿ|chiú-tsóaⁿ], niû [mih8|mi̍h] ê khì-kū, tsū-chi̍p, siúⁿ-sù, tí-tng, tāng-tāng."))

if not os.path.exists('main-old.csv'):
	os.rename('main.csv', 'main-old.csv')

df = pd.read_csv('main-old.csv')

df.to_csv('main.csv', index=False)


df['poj_unicode'] = df['poj_unicode'].apply(lambda x: pojCheck(x))

df['poj_bunim_unicode'] = df['poj_bunim_unicode'].fillna('')
df['poj_bunim_unicode'] = df['poj_bunim_unicode'].apply(lambda x: pojCheck(x))

df['comment'] = df['comment'].apply(lambda x: pojCheck(x))

df['hanlo_comment'] = df['hanlo_comment'].apply(lambda x: pojCheck(x))

df['tailo'] = df['poj_unicode'].apply(lambda x: ThoKit().tailoUnicode2Ascii(ThoKit().pojUnicode2TailoUnicode(x, poj_standard='campbell')))

df.to_csv('main.csv', index=False)

# ids_char_list = '⿰⿲⿱⿳⿸⿺⿹⿽⿵⿷⿶⿼⿴⿻⿾⿿㇯'



# df3['word'] = df3['word'].apply(lambda x: ThoKit().pojAscii2Unicode(x, standard='campbell', support_N=True))
# df3['bunim'] = df3['bunim'].apply(lambda x: ThoKit().pojAscii2Unicode(x, standard='campbell', support_N=True))
# df3['exp'] = df3['exp'].apply(lambda x: ThoKit().pojAscii2Unicode(ThoKit().pojUnicode2Ascii(x), standard='campbell', support_N=True).replace('\r\n', ' ').replace('  ', ' '))
# df3['example'] = df3['example'].apply(lambda x: ThoKit().pojAscii2Unicode(ThoKit().pojUnicode2Ascii(x), standard='campbell', support_N=True).replace('\r\n', ' ').replace('  ', ' '))
# # df3['tailo'] = df3['word'].apply(lambda x: ThoKit().pojAscii2TailoAscii(ThoKit().pojUnicode2Ascii(x.lower(), standard='campbell')))
# df3['tailo'] = df3['word'].apply(lambda x: ThoKit().tailoUnicode2Ascii(ThoKit().pojUnicode2TailoUnicode(x.lower(), poj_standard='campbell')))

# df3 = df3.set_index('id')
