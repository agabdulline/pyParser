import datetime

import requests
import os
import re
import json
import fitz  # импортируем PyMuPDF
import time
from database import get_event_by_id, get_all_events, delete_all_events, delete_event, add_event, update_record, create_connection, add_sport, get_sport_by_id, get_all_sports
from parsing import parseLink

data = []
events = {}



def download_pdf(url):
    # Получаем имя файла из URL
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4282.88 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            # Записываем файл по частям
            with open('downloaded_file.pdf', 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    downloaded_size += len(data)

                    # Выводим прогресс
                    done = int(50 * downloaded_size / total_size)
                    print(
                        f"\r[{'█' * done}{'.' * (50 - done)}] {downloaded_size / 1024:.2f} KB / {total_size / 1024:.2f} KB",
                        end='')

            print("\nСкачивание завершено.")
            return 'downloaded_file.pdf'
        else:
            print(f"Ошибка при скачивании файла: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка: {e}")
        return None
    # URL для скачивания файла


def pdf_parse (pdf_path, connection):
    with fitz.open(pdf_path) as pdf:
        sost = ""
        cat = ""
        all_ids = get_all_events(connection)
        print(all_ids)
        sport_ids = get_all_sports(connection)
        print(sport_ids)
        added_ids = []
        deleted_ids = []
        for page_num in range(len(pdf)):
            # print(page_num)
            page = pdf.load_page(page_num)
            lines = page.get_text().split('\n')
            if page_num == 0:
                lines = lines[19:]
            stage = 0
            curline = ""


            eve = {}
            eve['category'] = ""
            eve['category_id'] = 0
            eve['id'] = ""
            eve['sostav'] = ""
            eve['title'] = ""
            eve['gender'] = ""
            eve['dop_info'] = ""
            eve['date_start'] = ""
            eve['date_end'] = ""
            eve['country'] = ""
            eve['participants'] = 0

            for line in lines:
                if len(line) >= 16 and line[:16].isdigit():
                    eve['id'] = line[0:16]
                    eve['category_id'] = int(line[0:4])
                    events[line] = {}
                    curline += ',' + line[17:]
                    stage = 3
                    continue
                if line.isupper() and (stage == 0 or stage == 1):
                    eve['category'] = line
                    cat=line
                    stage = 1
                    continue

                if "состав" in line and stage == 1:
                    eve['sostav'] = line
                    sost=line
                    stage = 2
                    continue

                if stage == 3 and not bool(re.match(r'^[\d\.]{10}$', line)):
                    curline += ',' + line
                    continue
                if stage == 3 and bool(re.match(r'^[\d\.]{10}$', line)):
                    stage = 4
                    inff = curline.split(',')
                    stage2=0
                    curlinee2=""
                    for i in range(2, len(inff)):
                        if stage2==0 and inff[i].isupper():
                            curlinee2+=inff[i]

                            continue
                        if stage2==0 and not inff[i].isupper():
                            eve['title'] = curlinee2
                            eve['gender'] += inff[i]
                            curlinee2=""
                            stage2 = 1
                            continue
                        if stage2==1 and not inff[i].isupper():
                            eve['gender'] += "," + inff[i]
                            continue
                        if (stage2==1 or stage2 ==2):
                            stage2 = 2
                            eve['dop_info'] += inff[i]
                            continue
                    stage2 = 0
                    curlinee2 = ""
                    curline = ""
                    eve['date_start'] = line
                    continue
                if stage == 4 and bool(re.match(r'^[\d\.]{10}$', line)):
                    stage = 5
                    eve['date_end'] = line
                    continue
                if stage == 5 and line.isupper():
                    eve['country'] = line
                    stage = 6
                    continue
                if stage == 6 and not line.isdigit():
                    stage = 7
                    eve['country'] += ", " + line
                    continue
                if stage == 7 and line.isdigit():

                    eve['participants'] = int(line)
                    if not eve['category']:
                        eve['category'] = cat
                    if not eve['sostav']:
                        eve['sostav'] = sost
                    stage = 1
                    # print(eve)
                    events[eve['id']] = eve.copy()
                    ret = database_manipulation(connection, eve, all_ids, added_ids, sport_ids)
                    all_ids = ret[0]
                    added_ids = ret[1]
                    sport_ids = ret[2]
                    # print(events[eve['id']])
                    # print(eve['id'])
                    eve['category'] = ""
                    eve['category_id'] = 0
                    eve['id'] = ""
                    eve['sostav'] = ""
                    eve['title'] = ""
                    eve['gender'] = ""
                    eve['dop_info'] = ""
                    eve['date_start'] = ""
                    eve['date_end'] = ""
                    eve['country'] = ""
                    eve['participants'] = 0
                    continue
        if len(all_ids):
            for i in all_ids:
                delete_event(connection, i)
                deleted_ids.append(i)
        return [added_ids, deleted_ids]


def database_manipulation (connection, eve, all_ids, added_ids, sport_ids):
    if int(eve['id']) in all_ids:
        all_ids.remove(int(eve['id']))
    else:
        if not eve['category_id'] in sport_ids:
            print(get_sport_by_id(connection, eve['category_id']))
            add_sport(connection, eve['category_id'], eve['category'])
            sport_ids = get_all_sports(connection)
        add_event(connection, int(eve['id']), eve['category_id'], eve['title'], eve['gender'], eve['dop_info'], eve['sostav'], eve['date_start'], eve['date_end'], eve['country'], eve['participants'])
        added_ids.append(int(eve['id']))
    return [all_ids, added_ids, sport_ids]





# pdf_url = 'https://storage.minsport.gov.ru/cms-uploads/cms/II_chast_EKP_2024_14_11_24_65c6deea36.pdf'
# our_server_url = 'http://127.0.0.1:8000/post'
# filename = 's1-1-20.pdf'
# filename = download_pdf(pdf_url)

# парсинг и запоковка в json

# jsonname = 'data.json'
# with open(jsonname, 'w', encoding='utf-8') as json_file:
#     # Сохраняем объект в файл в формате JSON
#     json.dump(events, json_file, indent=4, ensure_ascii=False)


# единоразовый парсинг и обработка

def testMain():
    try:
        pdf_url = parseLink()
    except:
        pdf_url = 'https://storage.minsport.gov.ru/cms-uploads/cms/II_chast_EKP_2024_14_11_24_65c6deea36.pdf'

    try:
        filename = download_pdf(pdf_url)
    except:
        filename = 'downloaded_file.pdf'
    connection = create_connection("127.0.0.1", "root", "", "app_db")
    [added_ids, deleted_ids] = pdf_parse(filename, connection)
    print(added_ids)
    print(deleted_ids)
    connection.close()
    jsonname = 'data.json'
    with open(jsonname, 'w', encoding='utf-8') as json_file:
        # Сохраняем объект в файл в формате JSON
        json.dump(events, json_file, indent=4, ensure_ascii=False)

testMain()


# бесконечный цикл для автоматического обновления данных

# def main():
#
#     pdf_url = 'https://storage.minsport.gov.ru/cms-uploads/cms/II_chast_EKP_2024_14_11_24_65c6deea36.pdf'
#     url_to_parse = 'http://127.0.0.1:8000/post'
#     filename = 's1-1-20.pdf'
#
#     while True:
#         try:
#             pdf_url = parseLink()
#         except:
#             pdf_url = 'https://storage.minsport.gov.ru/cms-uploads/cms/II_chast_EKP_2024_14_11_24_65c6deea36.pdf'
#
#         try:
#             filename = download_pdf(pdf_url)
#         except:
#             filename = 'downloaded_file.pdf'
#         connection = create_connection("127.0.0.1", "root", "", "app_db")
#         [added_ids, deleted_ids] = pdf_parse(filename, connection)
#         connection.close()
#         time.sleep(43200)
#
# if __name__ == '__main__':
#     main()




