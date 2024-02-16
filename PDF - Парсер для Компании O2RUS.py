import sqlite3
from PyPDF2 import PdfReader
from translate import Translator

def parse_pdf(pdf_file, pgn_id, parameter_name, search_paragraph):
    global text
    pdf = PdfReader(pdf_file)
    matching_text = []

    for page in pdf.pages:
        text = page.extract_text()

        if pgn_id and pgn_id in text:
            matching_text.append(text)
            break  # Останавливаем поиск при первом найденном совпадении

        if parameter_name and parameter_name in text:
            matching_text.append(text)
            break  # Останавливаем поиск при первом найденном совпадении

        if search_paragraph and search_paragraph in text:
            matching_text.append(text)
            break  # Останавливаем поиск при первом найденном совпадении

    return matching_text

def extract_info_from_paragraph(search_paragraph):
    info_keys = ["ID", "Data_length", "Length", "Name", "RusName", "Scaling", "Range", "SPN"]
    info_values = {}

    lines = search_paragraph.split("\n")

    for line in lines:
        for key in info_keys:
            if key in line:
                if key == "Name":
                    value = line.replace(key, "").strip()
                    translator = Translator(to_lang='ru')
                    translat = Translator(to_lang='en')
                    rusname = translator.translate(value)
                    name = translat.translate(value)
                    info_values["RusName"] = rusname
                    info_values['Name'] = name
                else:
                    value = line.replace(key, "").strip()
                    info_values[key] = value
                break

    return info_values


def save_text_to_db(text, db_name):
    info = extract_info_from_paragraph(text)

    # Подключение к базе данных
    conn = sqlite3.connect(db_name)

    # Создание таблицы, если она не существует
    conn.execute("""
        CREATE TABLE IF NOT EXISTS extracted_text (
            ID INTEGER,
            Data_length TEXT,
            Length TEXT,
            Name TEXT,
            RusName TEXT,
            Scaling REAL,
            Range TEXT,
            SPN INTEGER
        )
    """)

    # Вставка извлеченного текста в базу данных
    conn.execute("""
        INSERT INTO extracted_text (
            ID,
            Data_length,
            Length,
            Name,
            RusName,
            Scaling,
            Range,
            SPN
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (info.get("ID"), info.get("Data_length"), info.get("Length"), info.get("Name"), info.get("RusName"), info.get("Scaling"), info.get("Range"), info.get("SPN")))

    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_name = "datapars.db"
    pdf_file = "SAE J1939-71.pdf"

    pgn_id = input('Введите PGN ID: ')
    parameter_name = input('Введите Parameter Name: ')
    search_paragraph = input('Введите Параграф документа: ')

    pgn_id = str(pgn_id)
    parameter_name = str(parameter_name)
    search_paragraph = str(search_paragraph)

    parse_pdf(pdf_file, pgn_id, parameter_name, search_paragraph)
    extract_info_from_paragraph(search_paragraph)
    save_text_to_db(text, db_name)
