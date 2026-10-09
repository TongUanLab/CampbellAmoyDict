"""检查 main.csv 中 comment 与 hanlo_comment 的逐字对齐情况。

comment 是白话字释义，hanlo_comment 是对应的汉罗释义。脚本将白话字
音节数与汉罗中的汉字数进行比较；修订标记 ``[原|訂]`` 和
``[原|=等價項]`` 只采用竖线右侧内容。
"""

from __future__ import annotations

import argparse
import csv
import re
import regex
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Optional

from thokit import ThoKit

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# Campbell 白話字音節；連字符分隔音節，故不放入匹配式。
POJ_SYLLABLE = regex.compile(
    "(?i)([\p{Latin}\u0300-\u030f\u0358\u207f]+)"
)
# 合法性检查先保留带连字符的完整 POJ 串，转换数字调后再拆分音节。
POJ_WORD = regex.compile(
    "(?i)([\p{Latin}\u0300-\u030f\u0358\u207f']+(?:-[\p{Latin}\u0300-\u030f\u0358\u207f']+)*)"
)
HANLO_CHAR = regex.compile("\p{Han}")
UNIT = regex.compile(
    rf"(?P<han>\p{{Han}}|[ㄅ-ㆿ])|(?P<poj>{POJ_SYLLABLE.pattern})"
)
THO_KIT = ThoKit()
EXTRA_POJ_FILE = Path(__file__).with_name("extra_poj_syllables.txt")
NUMERIC_POJ_SYLLABLE = re.compile(r"^[a-z]+[1-8]$")


def revised(text: str) -> str:
    """将每个 [旧|新] 替换为新；支持新值以 = 开头的等价项标记。"""
    def replace(match: re.Match[str]) -> str:
        value = match.group(1).split("|", 1)[1]
        return value[1:] if value.startswith("=") else value

    return re.sub(r"\[([^\[\]|]*\|[^\[\]]*)\]", replace, text or "")


def normalize_layout(text: str) -> str:
    """统一标点及等价项标记周边空格，不改动实际释义内容。"""
    # 引号及 {} 是释义标记，前面通常保留空格：kap "á"、kap {暋Bín}。
    text = regex.sub(r"\s+(?=\p{P})(?![\{\[\}\(\"'“”‘’（【《「『])", "", text or "")
    # { 在释义中是特殊标记的左边界，保留其前面的空格：kap {暋Bín}。
    text = regex.sub(r"(?<=[(\[（【《「『])\s+", "", text)
    text = regex.sub(r"(?<=[,.;:!?，。；：！？])(?=\[)", " ", text)
    text = regex.sub(r"([\.,;])([\p{sc=Latin}])", r"\1 \2", text)
    text = text.replace("= ", " =")
    return re.sub("\s+", " ", text).strip()


def space_words(text: str) -> list[str]:
    """替换修订标记后，再按空格分词；统计不把旧值算进去。"""
    return normalize_layout(revised(text)).split()


def count_units(text: str) -> int:
    """計算可參與逐字對齊的單位：白話字音節、漢字。"""
    return len(list_units(text))


def list_units(text: str) -> list[tuple[str, str]]:
    text = revised(text)
    return [(match.lastgroup, match.group()) for match in UNIT.finditer(text)]


def numbered_poj_syllables(text: str) -> list[tuple[str, Optional[str]]]:
    """先将每个 POJ 串转数字调，再返回其逐音节的原文及数字调形式。"""
    output: list[tuple[str, Optional[str]]] = []
    for match in POJ_WORD.finditer(revised(text)):
        raw_word = match.group()
        numeric_word = poj_number(raw_word)
        raw_syllables = raw_word.split("-")
        numeric_syllables = numeric_word.split("-") if numeric_word else []
        if len(raw_syllables) == len(numeric_syllables):
            output.extend(zip(raw_syllables, numeric_syllables))
        else:
            output.extend((syllable, None) for syllable in raw_syllables)
    return output


def poj_number(value: str) -> Optional[str]:
    """将 Campbell Unicode 白话字音节转为小写数字调形式。"""
    try:
        return THO_KIT.pojUnicode2Ascii(
            unicodedata.normalize("NFC", value), standard="campbell"
        ).lower()
    except Exception:
        return None


def headword_poj_forms(rows: list[dict[str, str]]) -> set[str]:
    """建立字头合法 POJ 数字调组合：修订取右、转小写、去重后再转换。"""
    unicode_forms = {
        unicodedata.normalize("NFC", revised(row.get("poj_unicode") or "").strip()).lower()
        for row in rows
        if revised(row.get("poj_unicode") or "").strip()
    }
    return {number for value in unicode_forms if (number := poj_number(value))}


def load_extra_poj_numbers(path: Path = EXTRA_POJ_FILE) -> set[str]:
    """读取字头外合法音节白名单；仅接受小写数字调单音节。"""
    if not path.exists():
        return set()
    output: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = line.partition("#")[0].strip().lower()
        if not value:
            continue
        if not NUMERIC_POJ_SYLLABLE.fullmatch(value):
            print(
                f"WARNING: {path.name} 第 {line_number} 行不是小写数字调单音节：{value}",
                file=sys.stderr,
            )
            continue
        output.add(value)
    return output


def headword_poj_numbers(
    rows: list[dict[str, str]], extra_numbers: Optional[set[str]] = None
) -> set[str]:
    """由合法字头数字调组合派生逐音节集合，供 comment/hanlo_comment 检查。"""
    output = {
        syllable
        for form in headword_poj_forms(rows)
        for syllable in form.split("-")
        if syllable
    }
    output.update(load_extra_poj_numbers() if extra_numbers is None else extra_numbers)
    return output


def invalid_poj_units(
    text: str, headword_numbers: set[str]
) -> list[tuple[str, Optional[str]]]:
    """返回文字中不在字头白话字数字调列表内的数字调音节。"""
    output: list[tuple[str, Optional[str]]] = []
    for value, number in numbered_poj_syllables(text):
        if number is None or number not in headword_numbers:
            output.append((value, number))
    return output


def print_rough_alignment(comment: str, hanlo: str) -> None:
    """按空格分词，以 index 输出两列的粗略对应关系。"""
    left, right = space_words(comment), space_words(hanlo)
    for index in range(max(len(left), len(right))):
        left_value = left[index] if index < len(left) else "<缺>"
        right_value = right[index] if index < len(right) else "<缺>"
        print(f"    [{index}] {left_value}  |  {right_value}")


def unit_mismatch_count(comment: str, hanlo: str) -> int:
    return sum(a[0] == b[0] and a[1] != b[1]
               for a, b in zip(list_units(comment), list_units(hanlo)))


def refine_hanlo_spaces(comment: str, hanlo: str) -> Optional[str]:
    """只增删 hanlo 空格，使各空格分段的单位数对应 comment。"""
    comment_words = space_words(comment)
    hanlo_text = normalize_layout(revised(hanlo))
    if (len(comment_words) == len(space_words(hanlo))
            and len(list_units(comment)) == len(list_units(hanlo))):
        return None
    # 汉罗侧的白话字连字符有时落在错误的分词边界；先把它视为可调整的空格。
    hanlo_text = regex.sub(
        r"(?<=[\p{Latin}\u0300-\u030f\u0358])-(?=[\p{Latin}\u0300-\u030f\u0358])",
        " ",
        hanlo_text,
    )
    targets = [len(list_units(word)) for word in comment_words]
    matches = list(UNIT.finditer(hanlo_text))
    if sum(targets) != len(matches):
        return None
    boundaries, cursor = [], 0
    for count in targets[:-1]:
        cursor += count
        boundaries.append(matches[cursor - 1].end())
    starts, ends = [0] + boundaries, boundaries + [len(hanlo_text)]

    def format_part(part: str, equal_after: Optional[list[int]] = None) -> str:
        """按该目标分组的 unit 类型重建内部空格/连字符。"""
        matches = list(UNIT.finditer(part))
        if not matches:
            return part.strip()
        equal_after = equal_after or []
        output, last = [part[:matches[0].start()]], matches[0].end()
        previous = matches[0]
        output.append(previous.group())
        for unit_index, current in enumerate(matches[1:], start=1):
            if unit_index in equal_after:
                output.append("=")
            gap = part[last:current.start()]
            if previous.lastgroup == current.lastgroup == "poj":
                separator = "-"
            elif previous.lastgroup == current.lastgroup == "han":
                # 汉字之间通常直接相连，如「過暝」「五穀」。
                separator = ""
            elif previous.lastgroup != current.lastgroup:
                # 同一目标分组内汉字与白话字直接相连，如「魚á-kiáⁿ」「m̄見」。
                separator = ""
            elif regex.search(r"\p{P}", gap):
                separator = regex.sub(r"\s+", "", gap)
            else:
                separator = " "
            output.extend([separator, current.group()])
            previous, last = current, current.end()
        output.append(part[last:])
        return "".join(output).strip()

    parts = []
    for word, (start, end) in zip(comment_words, zip(starts, ends)):
        equal_after = []
        if "=" in word:
            equal_after = [len(list_units(side)) for side in word.split("=")[:-1]]
        parts.append(format_part(hanlo_text[start:end], equal_after))
    refined = " ".join(parts)
    # 标点不是独立对齐单位；避免生成「柱 ,」「像 。」等空格。
    refined = regex.sub(r"\s+(?=\p{P})(?![\{\[\}\(\"'“”‘’（【《「『])", "", refined)
    refined = regex.sub(r"(?<=[(\[（【《「『])\s+", "", refined)
    refined = regex.sub(r"(?<=[,.;:!?，。；：！？])(?=\[)", " ", refined)
    refined = regex.sub(r"([\.,;])([\p{sc=Latin}])", r"\1 \2", refined)
    # 等價項分隔符後不可帶音節連字符：ùi=-tùi / ùi=-tùi -> ùi=tùi。
    refined = regex.sub(r"=\s*-", "=", refined)
    refined = refined.replace("= ", " =")
    refined = re.sub("\s+", " ", refined).strip()
    if unit_mismatch_count(comment, refined) > unit_mismatch_count(comment, hanlo):
        return None
    return refined


def write_rows_atomic(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    """先写同目录临时文件，再原子替换目标 CSV，避免读写同一文件句柄。"""
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as output:
            temporary_path = Path(output.name)
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=Path(__file__).with_name("main.csv"))
    args = parser.parse_args()

    with args.csv.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        required = {"comment", "hanlo_comment"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"缺少欄位：{', '.join(sorted(missing))}")
        rows = list(reader)
        for row in rows:
            row["comment"] = normalize_layout(row.get("comment") or "")
            refined = refine_hanlo_spaces(row["comment"], row.get("hanlo_comment") or "")
            if refined is not None:
                row["hanlo_comment"] = normalize_layout(refined)

    extra_poj_numbers = load_extra_poj_numbers()
    headword_numbers = headword_poj_numbers(rows, extra_poj_numbers)
    invalid_poj_count = 0
    mismatches = 0
    for line, row in enumerate(rows, start=2):
        comment = row.get("comment") or ""
        hanlo = row.get("hanlo_comment") or ""
        comment_space_split_count = len(space_words(comment))
        hanlo_comment_space_split_count = len(space_words(hanlo))
        if comment_space_split_count != hanlo_comment_space_split_count:
            mismatches += 1
            key = row.get("id") or row.get("hanji") or "(無識別欄位)"
            page = row.get("page_number") or ""
            if page:
                print(f"第 {page} 頁 ", end="")
            print(f"第 {line} 行 [{key}] comment空格分割={comment_space_split_count} hanlo_comment空格分割={hanlo_comment_space_split_count}")
            print(f"  comment:      {comment}")
            print(f"  hanlo_comment: {hanlo}")
            print("  粗對齊（按空格 split）：")
            print_rough_alignment(comment, hanlo)

        comment_count = count_units(comment)
        hanlo_count = count_units(hanlo)
        if comment_count != hanlo_count:
            mismatches += 1
            key = row.get("id") or row.get("hanji") or "(無識別欄位)"
            page = row.get("page_number") or ""
            if page:
                print(f"第 {page} 頁 ", end="")
            print(f"第 {line} 行 [{key}] comment單位={comment_count} hanlo_comment單位={hanlo_count}")
            print(f"  comment:      {comment}")
            print(f"  hanlo_comment: {hanlo}")
            if comment_space_split_count == hanlo_comment_space_split_count:
                print("  粗對齊（按空格 split）：")
                print_rough_alignment(comment, hanlo)

        key = row.get("id") or row.get("hanji") or "(無識別欄位)"
        for field_name, field_value in (
            ("comment", comment),
            ("hanlo_comment", hanlo),
        ):
            for value, number in invalid_poj_units(field_value, headword_numbers):
                invalid_poj_count += 1
                mismatches += 1
                converted = number or "(轉換失敗)"
                print(
                    f"WARNING: 第 {line} 行 [{key}] {field_name} 白話字疑似不合法："
                    f"{value} → {converted}（不在字頭白話字數字調列表中）"
                )

        left_units, right_units = list_units(comment), list_units(hanlo)
        for position, (left, right) in enumerate(zip(left_units, right_units), start=1):
            if left[0] == right[0] and unicodedata.normalize("NFC", left[1]) != unicodedata.normalize("NFC", right[1]):
                mismatches += 1
                key = row.get("id") or row.get("hanji") or "(無識別欄位)"
                kind = "漢字/注音" if left[0] == "han" else "白話字"
                print(f"第 {line} 行 [{key}] 第 {position} 字 {kind} 不相等：{left[1]} != {right[1]}")

    # 输入文件句柄已关闭；校验完成后再原子替换原 main.csv。
    write_rows_atomic(args.csv, fieldnames, rows)

    print(f"字頭外合法白話字音節：{len(extra_poj_numbers)} 個", file=sys.stderr)
    print(f"白話字疑似不合法：{invalid_poj_count} 筆", file=sys.stderr)
    print(f"共檢查，對不齊 {mismatches} 筆。", file=sys.stderr)
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
