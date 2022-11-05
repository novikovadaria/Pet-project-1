from bs4 import BeautifulSoup
import requests
from htmldocx import HtmlToDocx
import re
import subprocess
import json
import pathlib
import zipfile
import sys
import os

question = input("Нажми'f' для запуска программы\n")
if question.lower() == "f":

    acronym = input("Введи название папки:\n")
    start = int(input("С какой главы начнем?\n"))
    link = input("Введи ссылку без глав:\n")
    number = int(input("Введите количество глав (максимум или кратное 10):\n"))

    # Получаем API
    api_key = subprocess.run(['powershell', '-Command',
                              'yc iam create-token'], capture_output=True)
    api_key = api_key.stdout.decode('utf-8').replace("\n", "")

    IAM_TOKEN = api_key
    folder_id = 'kdjkdfslkf'
    target_language = 'ru'

    path = pathlib.Path().absolute()
    if os.path.exists(f"{acronym}") == True:  # проверяем существует ли папка
        pass
    else:  # создаём, если её нет
        acropath = pathlib.Path(f"{acronym}")
        eng_folder = pathlib.Path(f"{acronym}\CHAPTERS")
        eng_folder.mkdir(parents=True, exist_ok=True)
        eng_folder = pathlib.Path(f"{acronym}\zip")
        eng_folder.mkdir(parents=True, exist_ok=True)

    cast = start/10  # в каждой zip 10 глав
    if cast < 1:
        cast = 0
    else:
        cast = round(cast)
    chapters_in_zip = 0
    for step in range(start, number+1):
        if chapters_in_zip % 10 == 0 and chapters_in_zip != 0:
            cast += 1
        else:
            pass

        parser = HtmlToDocx()  # <--- Парсим главы

        response = requests.get(
            f"{link}{step}")
        soup = BeautifulSoup(response.text, "html.parser")

        chapterhtml = soup.find('div', 'hidden', id='chapterhidden')
        chapterhtml = str(chapterhtml)
        chapterhtml = re.sub('<img.*?/>', '', chapterhtml)
        chapterhtml = chapterhtml.replace(
            '<div class="hidden" id="chapterhidden">', "").replace('</div>', '')
        chapterhtml = chapterhtml.replace("\n", "")

        with open('tmp_eng.html', 'w', errors='ignore') as file_1:
            file_1.write(chapterhtml)
        parser.parse_html_file(
            "tmp_eng.html", f'{path}\{acronym}\CHAPTERS\{step}_eng')

        print(f"Глава {step}: записана")

        with zipfile.ZipFile(f"{acronym}\zip\{acronym} - Chapters {cast*10+1}to{cast*10+10}.zip", "a", compression=zipfile.ZIP_DEFLATED) as zipF:
            zipF.write(
                f"{acronym}\CHAPTERS\{step}_eng.docx")
            print(f"Глава {step}: на английском в архиве")

        text = chapterhtml  # <--- переводим с помощью Yandex Translate API
        body = {
            "targetLanguageCode": target_language,
            "texts": text,
            "folderId": folder_id,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(IAM_TOKEN)
        }

        response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                                 headers=headers,
                                 json=body
                                 )

        json_load = json.loads(response.text)
        if list(json_load.keys())[0] != 'translations':
            pass
        else:
            ru_text = json_load['translations'][0]['text']

        with open('tmp_ru.html', 'w', errors='ignore') as file_2:
            file_2.write(ru_text)
        parser.parse_html_file(
            "tmp_ru.html", f'{path}\{acronym}\CHAPTERS\{step}_ru')

        with zipfile.ZipFile(f"{acronym}\zip\{acronym} - Chapters {cast*10+1}to{cast*10+10}.zip", "a", compression=zipfile.ZIP_DEFLATED) as zipF:
            zipF.write(
                f"{acronym}\CHAPTERS\{step}_ru.docx")

            print(f"Глава {step}: на русском в архиве")

        print(f"Глава {step}: переведена")
        chapters_in_zip += 1
    os.remove("tmp_ru.html")
    os.remove("tmp_eng.html")
else:
    sys.exit()
