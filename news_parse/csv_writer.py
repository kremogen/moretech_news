import csv


def write(filename: str, article: str, body: str, date: str):
    try:
        with open(filename, mode='w', encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=';', lineterminator='\r')
            file_writer.writerow(['Article', 'Body', 'Date'])
    except Exception:
        print('Файл уже существует, начинаю сохранять данные:\n')

        with open(filename, mode='a', encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=';', lineterminator='\r')
            file_writer.writerow([article, body, date])
