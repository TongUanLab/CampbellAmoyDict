import pandas as pd
from thokit import ThoKit
import re

df = pd.read_csv('dict.csv')

df['page'] = df['page'].astype('string').fillna('')
df['page'] = df['page'].apply(lambda x: str(int(float(x))) if x else x)

df['word'] = df['word'].apply(lambda x: x.strip())
df['chinese'] = df['chinese'].apply(lambda x: x.strip())
df['exp'] = df['exp'].apply(lambda x: x.strip())
df['example'] = df['example'].astype('string').fillna('')
df['example'] = df['example'].apply(lambda x: x.strip())

df2 = df[['id', 'word', 'chinese', 'exp', 'example', 'page']]

df2['ji'] = df2['chinese'].apply(lambda x: ''.join(re.findall(r'[^a-zA-Z\(\)\[\]\d]+', x)).strip())
df2['bunim'] = df2['chinese'].apply(lambda x: ''.join(re.findall(r'[a-zA-Z\[\]]+\d?', x)).strip())
df2['bunim'] = df2['bunim'].apply(lambda x: x if not x else x[0].upper()+x[1:])

df3 = df2[['id', 'word', 'ji', 'bunim', 'exp', 'example', 'page']]

df3['word'] = df3['word'].apply(lambda x: ThoKit().pojAscii2Unicode(x, standard='campbell', support_N=True))
df3['bunim'] = df3['bunim'].apply(lambda x: ThoKit().pojAscii2Unicode(x, standard='campbell', support_N=True))
df3['exp'] = df3['exp'].apply(lambda x: ThoKit().pojAscii2Unicode(ThoKit().pojUnicode2Ascii(x), standard='campbell', support_N=True).replace('\r\n', ' ').replace('  ', ' '))
df3['example'] = df3['example'].apply(lambda x: ThoKit().pojAscii2Unicode(ThoKit().pojUnicode2Ascii(x), standard='campbell', support_N=True).replace('\r\n', ' ').replace('  ', ' '))
df3['tailo'] = df3['word'].apply(lambda x: ThoKit().tailoUnicode2Ascii(ThoKit().pojUnicode2TailoUnicode(x.lower(), poj_standard='campbell')))

df3 = df3[['id', 'word', 'ji', 'bunim', 'exp', 'example', 'tailo', 'page']]

df3 = df3.rename(columns={'word': 'poj_unicode', 'bunim': 'poj_bunim_unicode', 'exp': 'comment', 'example': 'hanlo_comment', 'page': 'page_number'})

df3 = df3.set_index('id')


'''
統一格式[TODO]：

1. 訂[原]
2. 原[[訂]]
3. `增`

'''

ji_tuple_list = [
	(6552, '㕼'),
	(7438, '圯[圮]'),
	(9349, '假'),
	(10696, '綰'),
	(15130, '玫[玟]'),
	(16498, '䀣'),
	(16499, '箅'),
	(16500, '䪐'),
	(16501, '𢲾'),
	(17435, '礟'),
	(21855, '朵[呆]'),
	(24780, '圩[𱖇]'),
	(24785, '盱[盰]'),
]

poj_unicode_tuple_list = [
	(3646, 'Chhù'),
	(19812, 'soaihⁿ'),
	(24243, 'tsoàn'),
	(24270, 'Tsoat'),
]

poj_bunim_unicode_tuple_list = [
	(1251, 'Tsoa̍t'),
	(7438, ''),
	(9060, 'Te̍k[Tek]'),
	(9349, 'Kà[Ká]'),
	(15130, ''),
	(16499, ''),
	(17436, ''),
	(21855, ''),
	(24780, ''),
]

comment_tuple_list = [
	(315, 'bán-(=boán-) thian-kong, chiū-sī ū kúi-nā ki sòe-sim tūi-teh ê tông.'),
	(840, 'ka(=kā)-boa̍h-chhài, chiū-sī chhiⁿ-chhài, á-sī chhài-thâu.'),
	(1222, 'oe-khoeh, sak, ni̍h-oá, tūi-lo̍h, pâi-lia̍t, chhia-tó, chhia-sak.'),
	(1247, 'hù-sû ê oē; sih-cheh[sih-chheh]=sih chi̍t-ē sio-siāng; kiu-cheh lun-cheh=kiaⁿ ê ì-sù.'),
	(1730, 'oa̍t-tńg, sóa-ūi; àm-chīⁿ, siu-khǹg, tè i kiâⁿ, kiâⁿ bōe chìn.'),
	(2122, 'chúi[chiú]-tsóaⁿ, niû mi̍h ê khì-kū, tsū-chi̍p, siúⁿ-sù, tí-tng, tāng-tāng.'),
	(2624, 'm̄-ti̍hⁿ ê chhù; pàng-sang; chhiong-móa; chio, tōa, bô-lō͘-ēng.'),
	(4143, 'léng-gē sī léng-chhiò ê ì-sù; gē-tòaⁿ, gē-pîⁿ, tsng-gē[tosng-gē].'),
	(4881, 'chhùi kā-mi̍h, bé kā-kiuⁿ; kám-kek, niá-siúⁿ, chhùi kâm-teh, koaⁿ-hâm.'),
	(6552, 'chhut tōa-siaⁿ; oh-tit chiâⁿ kong-lô.'), # 'kap téng-bīn jī sio-siāng.',
	(8481, 'ûn-á-sio, hé-to̍h, jia̍t; ìn-hó; chhin-chhiūⁿ, àn-ni; nā-sī; gú-tsō͘-sû, sui-jiân.'),
	(8524, 'jiáuⁿ-súi, chiū-sī toh-piⁿ chhâ khek ê hoe; jiáuⁿ-súi-teng, chiū-sī thih-teng lâi tèng hit ê hoe.'),
	(9631, 'ki-ki kê-kê, chiū-sī siông-siông khê-tio̍h ê ì-sù.'),
	(10901, 'koat-tsoa̍t, chiū-sī tsoa̍t-tn̄g kap-lâng óng-lâi ê ì-sù.'),
	(10903, 'khī-koe, hé-koe[hí-koe]; tsàu-koe; koe-bú, koe-kak, koe-mn̂g, koe-nn̄g.'),
	(11067, 'chho͘-ku̍t bē kè-hé ê tâng thih, chho͘-ku̍t ê kim-ge̍k, tâng, thih.'),
	(11068, 'chho͘-ku̍t bē kè-hé ê tâng thih, chho͘-ku̍t ê kim-ge̍k, tâng, thih.'),
	(19284, 'Ûn-sio[Un-sio], siâⁿ ê miâ, chiū-sī tī Chiuⁿ-phó͘[Chiu-phó͘] kap Chiau-an ê tiong-kan.'),
	(19812, 'sihⁿ-si̍hⁿ sa̍uhⁿ-sa̍uhⁿ, sa̍uhⁿ-sa̍uhⁿ háu ê siaⁿ.'),
	(20447, 'ta-po͘, ta-po͘-kiáⁿ, ta-po͘-sun; ta-po͘-lâng, ta-po͘-hàn.'),
	(21968, 'chiū-sī bô chhiú-ńg ê saⁿ ê ì-sù.'),
	(22494, 'chháu ê miâ, hio̍h chhin-chhiūⁿ sng-chiong-hoa, sòe koh pe̍h, tiong-sim n̂g.'),
]

hanlo_comment_tuple_list = [
	(315, '滿天光, 就是 有 幾若 枝 細心 墜 teh ê 燈.'),
	(1247, '副詞 ê 話; sih-cheh=sih 一下 相像; 勼cheh, 縮cheh=驚 ê 意思.'),
	(2992, '嗤chhn̍gh哮, 嗤chhn̍gh 叫, 就是 哮 ê 聲.'),
	(3127, '藥 ê 名, 親像 石菖pô͘ⁿ, 抑是 石菖婆.'),
	(7370, '依偎[因為], 有 所靠, 偏邊, 歪; 依oá, oá靠, oá重.'),
	(10557, '鮕鮘錢, 掖鮕鮘, 用 錢 掖鮕鮘.'),
	(10903, '雉雞, 火雞; 灶雞; 雞母, 雞角, 雞毛, 雞卵.'),
	(11067, '粗掘 未 過火 ê 銅 鐵, 粗掘 ê 金玉, 銅, 鐵.'),
	(11068, '粗掘 未 過火 ê 銅 鐵, 粗掘 ê 金玉, 銅, 鐵.'),
	(11576, 'khām-tio̍h, khām-oá, 相khām, khām來 khām去.'),
	(17807, 'phn̍gh-phn̍gh哮, 就是 蛇 跳oá beh 咬 ê 聲; 人 哄頭 ê 款式.'),
	(19284, '雲霄, 城 ê 名, 就是 tī 漳浦 kap 詔安 ê 中間.'),
]

tailo_tuple_list = [
	(3646, 'tshu3'),
	(19812, 'suainnh4'),
	(24243, 'tsuan3'),
	(24270, 'tsuat4'),
]


for tup in ji_tuple_list:
	df3.loc[tup[0], 'ji'] = tup[1]

for tup in poj_unicode_tuple_list:
	df3.loc[tup[0], 'poj_unicode'] = tup[1]

for tup in poj_bunim_unicode_tuple_list:
	df3.loc[tup[0], 'poj_bunim_unicode'] = tup[1]

for tup in comment_tuple_list:
	df3.loc[tup[0], 'comment'] = tup[1]

for tup in hanlo_comment_tuple_list:
	df3.loc[tup[0], 'hanlo_comment'] = tup[1]

for tup in tailo_tuple_list:
	df3.loc[tup[0], 'tailo'] = tup[1]


df3 = df3.drop(index=[25213, 25214, 25215])

df3['comment'] = df3['comment'].apply(lambda x: re.sub('\[([\u4e00-\u9fff][^,\]]*)\]', '{\\1}', x))
df3['hanlo_comment'] = df3['hanlo_comment'].apply(lambda x: re.sub('\[([\u4e00-\u9fff][^,\]]*)\]', '{\\1}', x))

df3.to_csv('dict-new.csv')