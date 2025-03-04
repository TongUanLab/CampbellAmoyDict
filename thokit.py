import re
import unicodedata


class ThoKit:
    def __init__(self) -> None:
        """
        愛注意，傳統白話字本身無定義陽上調、高升調符
        """
        self.tailoAccentMarks = [
            "",
            "",
            "\u0301",
            "\u0300",
            "",
            "\u0302",
            "\u030C",
            "\u0304",
            "\u030D",
            "\u030B",
        ]
        self.pojAccentMarks = [
            "",
            "",
            "\u0301",
            "\u0300",
            "",
            "\u0302",
            "\u030C",
            "\u0304",
            "\u030D",
            "\u0306",
        ]

    def addToneNumber(self, s:str) -> str:
        return s+'4' if s[-1] in 'ptkhPTKH' else s+'1'

    def tailoUnicode2Ascii(self, s: str, output_style_list=[]):
        s = unicodedata.normalize("NFD", s)
        for accent in self.tailoAccentMarks:
            if accent == '': continue
            if accent in s:
                s = s.replace(accent, str(self.tailoAccentMarks.index(accent)))
        s = re.sub('(\d)([a-z]+)([^a-z]|$)', r'\2\1\3', s, flags=re.IGNORECASE)
        s = re.sub("([a-zA-Z]+)([^\da-zA-Z])", lambda x: self.addToneNumber(x.group(0)[:-1])+x.group(0)[-1], s)
        s = re.sub("([a-zA-Z]+)$", lambda x: self.addToneNumber(x.group(0)), s)
        return s

    def pojUnicode2Ascii(self, s: str, standard='', output_style_list=[]):
        if standard: assert standard in ['kjt']
        if standard == 'kjt':
            s = s.replace('hⁿ', 'ⁿh')
            ...
        s = unicodedata.normalize("NFD", s)
        s = s.replace('ⁿ', 'nn')
        if s.upper() == s: s = s.replace('nn', 'NN')
        else: s = s.replace('nn', 'nn')
        # if s.lower() == s: s = s.replace('\u0358', 'o')
        if s.upper() == s: s = s.replace('\u0358', 'O')
        else: s = s.replace('\u0358', 'o')

        for accent in self.pojAccentMarks:
            if accent == '': continue
            if accent in s:
                s = s.replace(accent, str(self.pojAccentMarks.index(accent)))
        s = re.sub('(\d)([a-z]+)([^a-z]|$)', r'\2\1\3', s, flags=re.IGNORECASE)
        s = re.sub("([a-zA-Z]+)([^\da-zA-Z])", lambda x: self.addToneNumber(x.group(0)[:-1])+x.group(0)[-1], s)
        s = re.sub("([a-zA-Z]+)$", lambda x: self.addToneNumber(x.group(0)), s)
        s = s.replace('oonn', 'onn')
        return s

    def movePojToneNumber(self, s: str) -> str:
        """
        POJ 數字標調徙位
        無處理 oo
        """
        if "a" in s or "e" in s or "A" in s or "E" in s:
            return re.sub(
                "([ae])([a-z]*)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE
            )
        elif "o" in s or "O" in s:
            return re.sub("(o)([a-z]*)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        elif "u" in s or "U" in s:
            return re.sub("(u)([a-z]*)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        elif "i" in s or "I" in s:
            return re.sub("(i)([a-z]*)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        s = re.sub("(n)(gh?)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        s = re.sub("(m)(h?)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)

        return s

    def moveTailoToneNumber(self, s: str) -> str:
        """
        臺羅數字標調徙位
        """
        s = re.sub(
            "([aeiou])(r?m?n*h?g?p?t?k?)(\d)",
            r"\1\3\2",
            s,
            count=1,
            flags=re.IGNORECASE,
        )
        s = re.sub("([aeo])([iueo])(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        s = re.sub("(n)(gh?)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        s = re.sub("(m)(h?)(\d)", r"\1\3\2", s, count=1, flags=re.IGNORECASE)
        return s

    def tailoAscii2Unicode(self, s: str, output_style_list=[]):
        s = re.sub("([a-zA-Z]+\d)", lambda x: self.moveTailoToneNumber(x.group(0)), s)
        s = re.sub(
            "([aeioumn])(\d)",
            lambda x: x.group(0)[0] + self.tailoAccentMarks[int(x.group(0)[-1])],
            s,
            flags=re.IGNORECASE,
        )
        if "nfd" not in output_style_list:
            s = unicodedata.normalize("NFC", s)
        return s

    def pojAscii2Unicode(self, s: str, standard:str = None,
                         output_style_list=[]):
        if standard: assert standard in ['kjt']
        if standard == 'kjt':
            s = s.replace('ou', 'oo').replace('Ou', 'Oo').replace('OU', 'OO')
            s = re.sub('([aeioug])N', r'\1nn', s) # 此拼式全大寫 -nn 與 -n 有衝突
            s = re.sub('([^o])onn', '\\1oonn', s)
            s = re.sub('ch([^eéèêēiíìîīh])', r'ts\1', s)
            s = re.sub('Ch([^eéèêēiíìîīh])', r'Ts\1', s)
            s = re.sub('CH([^EÉÈÊĒIÍÌÎĪH])', r'TS\1', s)
            s = re.sub('ts([eéèêēiíìîīh])', r'ch\1', s)
            s = re.sub('Ts([eéèêēiíìîīh])', r'Ch\1', s)
            s = re.sub('TS([EÉÈÊĒIÍÌÎĪH])', r'CH\1', s)
            # .replace('N', 'nn')
        # s = s.replace('ch', 'ts')
        # s = s.replace('oa', 'ua').replace('oe', 'oe').replace('eng', 'ing').replace('ek', 'ik')
        s = re.sub("([a-zA-Z]+\d)", lambda x: self.movePojToneNumber(x.group(0)), s)

        s = re.sub("(o)([ae])(\d)([^a-z]|$)", r"\1\3\2\4", s, flags=re.IGNORECASE)
        s = re.sub("(o)([ae])(\d)(nn)([^h]|$)", r"\1\3\2\4\5", s, flags=re.IGNORECASE)

        s = re.sub(
            "([aeioumn])(\d)",
            lambda x: x.group(0)[0] + self.pojAccentMarks[int(x.group(0)[-1])],
            s,
            flags=re.IGNORECASE,
        )

        s = re.sub(
            "(o)([\u0301\u0300\u0302\u030C\u0304\u030D\u0306])(o)",
            "\\1\\2\u0358",
            s,
            flags=re.IGNORECASE,
        )
        s = re.sub("(o)o", "\\1\u0358", s, flags=re.IGNORECASE)

        s = re.sub(
            "nn(h?)([^g\u0301\u0300\u0302\u030C\u0304\u030D\u0306]|$)",
            r"ⁿ\1\2",
            s,
            flags=re.IGNORECASE,
        )

        if "nfd" not in output_style_list:
            s = unicodedata.normalize("NFC", s)
        if standard == 'kjt':
            s = s.replace('ⁿh', 'hⁿ')
        return s
    
    def pojUnicode2TailoUnicode(self, s: str, poj_standard=''):
        s = self.pojUnicode2Ascii(s, standard=poj_standard)
        s = s.replace('ch', 'ts').replace('oa', 'ua').replace('oe', 'ue').replace('eng', 'ing').replace('ek', 'ik')
        return self.tailoAscii2Unicode(s)

    def Hanji2Tailo(self, s: str) -> str:
        pass
