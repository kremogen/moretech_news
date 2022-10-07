import csv

try:
    with open('forbes_data.csv', mode='w', encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=';', lineterminator='\r')
        file_writer.writerow(['Article', 'Body', 'Date'])
except Exception as e:
    print('Файл уже существует, начинаю сохранять данные:\n')

    with open('forbes_data.csv', mode='w', encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=';', lineterminator='\r')
        file_writer.writerow(['Article', 'Body', 'Date'])

