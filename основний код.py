import os
import re
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path
from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer(lang='uk')

# Шлях до стоп-слів
with open("stop_words.txt", encoding="utf-8") as f:
    stop_words = set(line.strip().lower() for line in f if line.strip() and len(line.strip().split()) == 1)

# files = [
#     "1C-and-S_1.txt", "1C-and-S_2.txt", "1C-and-S_3.txt", "1C-and-S_4.txt", "1C-and-S_5.txt",
#     "1trudy_22_2022.txt", "1trudy_24_2024.txt", "1trudy_23_2023.txt", "1пцу_новини_проповіді.txt"
# ]

files = [
    "2KDA38.txt", "2KDA39.txt", "2KDA40.txt", "2KDA41.txt", "2упц новини.txt", "2упц проповіді онуфрій.txt"]

# stop_words = {"в", "у", "і", "та", "не", "що", "до", "з", "на", "за", "із", "й", "як", "але", "теж", "аби"}

abbreviation_expansion = {
    "ап.": "апостол", "апп.": "апостоли", "архієп.": "архієпископ", "архім.": "архимандрит", 
    "безср.": "безсрібник", "блгв.": "благовірний", "блж.": "блаженний", "вмц.": "великомучениця",
    "вмч.": "великомученик", "дияк.": "диякон", "єп.": "єпископ", "ігум.": "ігумен", "спов.": "сповідник",
    "кн.": "князь", "митр.": "митрополит", "мц.": "мучениця", "мцц.": "мучениць", "мч.": "мученик",
    "мчч.": "мучеників", "патр.": "патріарх", "прав.": "праведний", "прп.": "преподобний", "прпп.": "преподобні",
    "прпмц.": "преподобномучениця", "прпмч.": "преподобномученик", "пресвіт.": "пресвітер", "прор.": "пророк",
    "св.": "святий", "свв.": "святі", "свт.": "святитель", "свтт.": "святителі", "сщмч.": "священномученик",
    "сщмчн.": "священномучениця", "сщч.": "священнослужитель", "вч.": "вчитель", "ввеч.": "вечірня", "с.": "сторінка",
    "ран.": "рання", "літ.": "літургія", "євангеліє: мф.": "від матфея", "мк.": "від марка", "лк.": "від луки",
    "ін.": "від іоана", "діян.": "діяння святих апостолів", "послання апостолів: як.": "якова", "1 пет.": "1-ше петра",
    "2 пет.": "2-ге петра", "1 ін.": "1-ше іоана", "2 ін.": "2-ге іоана", "3 ін.": "3-тє іоана", "іуд.": "іуда",
    "послання апостола павла: рим.": "до римлян", "1 кор.": "1-ше до коринфян", "2 кор.": "2-ге до коринфян",
    "гал.": "до галатів", "еф.": "до ефесян", "флп.": "до филип’ян", "кол.": "до колосян", "прот.": "протоієрей",
    "1 сол.": "1-ше до солунян", "2 сол.": "2-ге до солунян", "1 тим.": "1-ше до тимофія", "об.": "об’явлення", 
    "2 тим.": "2-ге до тимофія", "тит.": "до тита", "флм.": "до филимона", "євр.": "до євреїв", "свящ.": "священник",
    "бут.": "буття", "вих.": "вихід", "іс.": "ісая", "іоїл.": "йоїль", "зах.": "захарія", "притч.": "притчі соломона"
}

roman_re = re.compile(r"^(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", re.IGNORECASE)

global_counter = Counter()
source_counters = defaultdict(Counter)
file_tracker = defaultdict(set)
abbreviations = defaultdict(int)
latin_words = defaultdict(int)
all_tokens = []

for file in files:
    path = Path(file)
    if not path.exists():
        continue

    with open(path, "r", encoding="utf-8") as f:
        text = f.read().lower()

    text = text.replace("’", "'").replace("ʼ", "'").replace("\u00AD", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    for word in re.findall(r"\b[a-zA-Z]{2,}\b", text):
        if not roman_re.fullmatch(word):
            latin_words[word] += 1
            file_tracker[f"LATIN::{word}"].add(file)

    abbrs = re.findall(r"\b[а-щґєіїьюя]{1,4}\.", text)
    for abbr in abbrs:
        if abbr in abbreviation_expansion:
            abbreviations[abbr] += 1
            file_tracker[f"ABBR::{abbr}"].add(file)

    raw_tokens = re.findall(r"\b[а-щґєіїьюя]+(?:[-'][а-щґєіїьюя]+)*\.?\b", text)

    i = 0
    tokens = []
    while i < len(raw_tokens):
        w1 = raw_tokens[i]
        if i + 1 < len(raw_tokens):
            w2 = raw_tokens[i + 1]
            combined = w1 + w2
            if (not morph.word_is_known(w1) or not morph.word_is_known(w2)) and morph.word_is_known(combined):
                tokens.append(combined)
                file_tracker[combined].update(file_tracker[w1])
                file_tracker[combined].update(file_tracker[w2])
                i += 2
                continue
        tokens.append(w1)
        i += 1

    for t in tokens:
        file_tracker[t].add(file)
    source_counters[file].update(tokens)
    global_counter.update(tokens)
    all_tokens.extend(tokens)

main_rows = []
lemma_pos_dict = {}
for word, freq in global_counter.items():
    parse = morph.parse(word)[0]
    lemma = parse.normal_form
    pos = parse.tag.POS or "-"
    file_list = ", ".join(file_tracker[word])
    main_rows.append((word, lemma, pos, freq, file_list))
    lemma_pos_dict[word] = (lemma, pos)

main_df = pd.DataFrame(main_rows, columns=["Слово", "Лема", "Частина мови", "Частота", "Файли"])

top20_rows = []
top20_content = []
for file, counter in source_counters.items():
    for word, freq in counter.most_common(25):
        top20_rows.append((file, word, freq))
    filtered = [(w, c) for w, c in counter.items()
                if w not in stop_words and lemma_pos_dict.get(w, ("", ""))[1] in {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}]
    for word, freq in sorted(filtered, key=lambda x: -x[1])[:20]:
        top20_content.append((file, word, freq))

top20_df = pd.DataFrame(top20_rows, columns=["Файл", "Слово", "Частота"])
top20_content_df = pd.DataFrame(top20_content, columns=["Файл", "Слово", "Частота"])

latin_df = pd.DataFrame([
    (word, count, ", ".join(file_tracker[f"LATIN::{word}"])) for word, count in latin_words.items()
], columns=["Слово (латиниця)", "Частота", "Файли"])

abbrev_df = pd.DataFrame([
    (abbr, count, abbreviation_expansion.get(abbr, "-"), ", ".join(file_tracker[f"ABBR::{abbr}"]))
    for abbr, count in abbreviations.items()
], columns=["Скорочення", "Частота", "Розшифрування", "Файли"])

#the beginning of new things
bigram_counter = Counter()
trigram_counter = Counter()
bigram_sources = defaultdict(set)
trigram_sources = defaultdict(set)

for i in range(len(all_tokens) - 1):
    bg = all_tokens[i] + " " + all_tokens[i + 1]
    bigram_counter[bg] += 1
    bigram_sources[bg].update(file_tracker[all_tokens[i]])

for i in range(len(all_tokens) - 2):
    tg = all_tokens[i] + " " + all_tokens[i + 1] + " " + all_tokens[i + 2]
    trigram_counter[tg] += 1
    trigram_sources[tg].update(file_tracker[all_tokens[i]])

bigrams_df = pd.DataFrame([
    (k, v, ", ".join(bigram_sources[k])) for k, v in bigram_counter.items() if v > 5
], columns=["2-грам", "Частота", "Файли"])

trigrams_df = pd.DataFrame([
    (k, v, ", ".join(trigram_sources[k])) for k, v in trigram_counter.items() if v > 5
], columns=["3-грам", "Частота", "Файли"])
#the end of new

# Топ-20 по всьому корпусу
top20_global = pd.DataFrame(
    global_counter.most_common(20),
    columns=["Слово", "Частота"]
)

# Топ-20 повнозначних по всьому корпусу
content_words = [
    (w, c) for w, c in global_counter.items()
    if w not in stop_words and lemma_pos_dict.get(w, ("", ""))[1] in {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
]
top20_content_global = pd.DataFrame(
    sorted(content_words, key=lambda x: -x[1])[:25],
    columns=["Слово", "Частота"]
)

output_path = "ОСТАТОЧНО упц.xlsx"
with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    main_df.sort_values(by="Частота", ascending=False).to_excel(writer, sheet_name="Лема + Частота", index=False)
    top20_df.to_excel(writer, sheet_name="Топ-20", index=False)
    top20_content_df.to_excel(writer, sheet_name="Топ-20 повнозначні", index=False)
    top20_global.sort_values(by="Частота", ascending=False).to_excel(writer, sheet_name="Топ-20 по всьому", index=False)
    top20_content_global.sort_values(by="Частота", ascending=False).to_excel(writer, sheet_name="Топ-20 повнозначні всі", index=False)   
    # latin_df.to_excel(writer, sheet_name="Латинські слова", index=False)
    abbrev_df.sort_values(by="Частота", ascending=False).to_excel(writer, sheet_name="Скорочення", index=False)
    bigrams_df.sort_values(by="Частота", ascending=False).to_excel(writer, sheet_name="2-грами", index=False)
    trigrams_df.sort_values(by="Частота", ascending=False).to_excel(writer, sheet_name="3-грами", index=False)

print("Загальна кількість токенів:", len(all_tokens))
print("Унікальних токенів:", len(set(all_tokens)))
print("Унікальних у частотнику:", len(global_counter))

for tok in set(all_tokens):
    if tok not in global_counter:
        print("Пропущено:", tok)