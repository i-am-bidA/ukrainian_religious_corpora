import pandas as pd

# Завантаження аркушів з повними словами
pcu_words = pd.read_excel("26_05.xlsx", sheet_name="ПЦУ_Слова")
upc_words = pd.read_excel("26_05.xlsx", sheet_name="УПЦ_Слова")

# Додаємо стовпець джерела
pcu_words["Джерело"] = "ПЦУ"
upc_words["Джерело"] = "УПЦ"

# Об'єднуємо таблиці
all_words = pd.concat([pcu_words, upc_words], ignore_index=True)

# Підрахунок частот за частинами мови та джерелом
pos_freq = all_words.groupby(["Частина мови", "Джерело"])["Частота"].sum().unstack(fill_value=0)
pos_freq["Загальна частота"] = pos_freq.sum(axis=1)
pos_freq = pos_freq.sort_values(by="Загальна частота", ascending=False)
pos_freq.reset_index(inplace=True)

# Збереження результату в окремий файл
output_path = "частини_мови.xlsx"
pos_freq.to_excel(output_path, index=False)

output_path
