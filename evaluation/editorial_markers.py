"""Heuristic flags for the owner's editorial defects. A flag is a pointer for review, not a verdict."""
from pathlib import Path
import json, re, sys

PATTERNS = {
    # first line narrates work instead of starting the artifact
    'process_opening': r"\A\s*(?:Я |I |Перевіри|Звіри|Завантажи|Прочитав|Проверил|Сверил|Ниже|Сначала|Спочатку я|Ось |Let me|I've|I have|I checked|I verified|Having|Next I|Now I|I'm writing|I am writing|Checked|Verified|Here is|Here's|Below is)",
    # 'what the text does not teach/prove/establish' rubric or defensive negation
    'does_not_rubric': r'(?:чого\s+(?:цей\s+)?(?:текст|вірш|уривок)[^.\n]{0,20}\s*(?:\*?не\*?)\s|не\s+(?:навчає|доводить|встановлює)|чего\s+(?:этот\s+)?(?:текст|стих|отрывок)[^.\n]{0,20}не\s|не\s+(?:учит|доказывает|устанавливает)|does not (?:teach|prove|establish)|what (?:the|this) (?:text|passage|verse) does not)',
    # estimated word count or missing counting tool
    'word_count_talk': r'(?:слів|слов|words)[^.\n]{0,80}(?:оцін|рахув|підрах|посчит|оцен|count|estimat)|(?:оцін|рахув|підрах|посчит|оцен|count|estimat)[^.\n]{0,80}(?:слів|слов|words)|інструмент\w* для підрахунку|инструмент\w* для подсчета|word[- ]count',
    # closing verification / limitations block
    'verification_block': r'^\**\s*(?:Перевірка|Обмеження|Проверка|Ограничения|Verification|Limitations|Примітк|Примечан|Notes)\b',
    'self_review_talk': r'(?:незалежн\w+ рецензуванн|самоперевір|independent review|self-review|независим\w+ рецензир|самопровер)',
}

def flags(text):
    out = {}
    for name, pat in PATTERNS.items():
        hits = [m.group(0)[:60] for m in re.finditer(pat, text, re.I | re.M)]
        if hits: out[name] = hits
    return out

if __name__ == '__main__':
    for path in sys.argv[1:]:
        print(json.dumps({'path': path, 'flags': flags(Path(path).read_text())}, ensure_ascii=False))
