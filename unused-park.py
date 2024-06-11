import pandas as pd
import re
import os
from datetime import datetime, timedelta
import calendar


# Функция для фильтрации данных по заданному периоду
def filter_data_by_period(df, start_date, end_date):
    df['Дата_постановки_ожидание'] = pd.to_datetime(df['Дата_постановки_ожидание'])
    df['Дата_выхода_из_ремонта'] = pd.to_datetime(df['Дата_выхода_из_ремонта'])
    mask = ((df['Дата_постановки_ожидание'] >= start_date) & (df['Дата_постановки_ожидание'] <= end_date)) | (
                (df['Дата_выхода_из_ремонта'].isnull()) & (df['Дата_постановки_ожидание'] <= end_date))
    return df[mask]


# Функция для определения виновного предприятия и вычисления времени простоя на НР
def calculate_downtime(row):
    if row['Вид_НЭП'] == 'НР':
        if pd.isna(row['Виновное_предприятие']):
            row['Время_простоя_НР_исполнителя'] = row['Общее_время_простоя']
        elif any(re.search(re.escape(word), row['Виновное_предприятие'], re.IGNORECASE) for word in
                 виновные_по_заказчику):
            row['Время_простоя_НР_заказчика'] = row['Общее_время_простоя']
        elif any(re.search(re.escape(word), row['Виновное_предприятие'], re.IGNORECASE) for word in
                 виновные_по_исполнителю):
            row['Время_простоя_НР_исполнителя'] = row['Общее_время_простоя']
    return row

# Функция для расчета общего времени передислокации с учетом start_date
def calculate_total_relocation_time(row):
    if pd.notnull(start_date) and row['Дата_постановки_ремонт'] < start_date:
        return (row['Дата_выхода_из_ремонта'] - start_date).total_seconds() / 3600
    else:
        return (row['Дата_выхода_из_ремонта'] - row['Дата_постановки_ремонт']).total_seconds() / 3600



# Текущая дата
current_date = datetime.now()

# Создание end_date, которое равно вчерашнему дню в 18:00
end_date = current_date.replace(hour=18, minute=0, second=0, microsecond=0) - timedelta(days=1)

# Определение последнего дня прошлого месяца
first_day_of_current_month = current_date.replace(day=1)
last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

# Создание start_date, которое равно последнему дню прошлого месяца в 18:00
start_date = last_day_of_previous_month.replace(hour=18, minute=0, second=0, microsecond=0)

start_date = start_date.strftime("%d.%m.%Y %H:%M")
end_date = end_date.strftime("%d.%m.%Y %H:%M")

# # Получаем от пользователя даты начала и конца отчетного периода
# start_date = "31.05.2024 18:00"
# end_date = "06.06.2024 18:00"

# выгрузка дополнительной таблицы с депо приписки локомотива
path = "/Users/user/Desktop/dlya_analiz/Расследование_НР.xlsx"
df1 = pd.read_excel(path, header=3)
df1 = df1.rename(columns={'Депо приписки': 'Депо', '№': 'Номер',
                          'Ожидание': 'Дата_постановки_ожидание',
                          'Начало': 'Дата_постановки_ремонт',
                          'Окончание': 'Дата_выхода_из_ремонта',
                          'Ответственное предприятие за проведение НР': 'Виновное_предприятие'})
df1 = df1[['Депо', 'Серия', 'Номер', 'Вид', 'Дата_постановки_ожидание', 'Дата_постановки_ремонт',
           'Дата_выхода_из_ремонта', 'Виновное_предприятие']]
df1 = df1.query('Вид == "НЕПЛ. РЕМ" or Вид == "РЕКЛАМАЦИЯ"')

# выгрузка дополнительной таблицы с депо приписки локомотива
path_2 = "/Users/user/Desktop/dlya_analiz/РаспределениеОЖ.xlsx"
df2 = pd.read_excel(path_2, header=3)
df2 = df2.rename(columns={'2': 'Депо', '3': 'Серия', '4': 'Номер',
                          '8': 'Дата_постановки_ожидание',
                          '9': 'Дата_постановки_ремонт',
                          '10': 'Дата_выхода_из_ремонта', '6': 'Вид'})

# df2['Дата_время_постановки_оперативного_графика'] = ''
df2['Виновное_предприятие'] = ''

df2['Депо'] = df2['Депо'].fillna('0')
df2['x'] = df2['11'].astype(str).apply(lambda x: x.split(' ')[1])

# Словарь с ключевыми словами для каждой категории
ключевые_слова = {
    'ТЧЭ-12 Спб-Фин': ['ТЧЭ - 12'],
    'ТЧЭ-28 Мурманск': ['ТЧЭ - 28'],
    'ТЧЭ-26 Кемь': ['ТЧЭ - 26'],
    'ТЧЭ-21 Волховстрой': ['ТЧЭ - 21'],
    'ТЧЭ-11 Выборг': ['ТЧЭ - 11'],
    'ТЧЭ-14 Спб-Варшавский ': ['ТЧЭ - 14'],
    'ТЧЭ-31 Великие Луки': ['ТЧЭ - 31'],
    'ТЧЭ-8 Спб-Пасс-Мск': ['ТЧЭ - 08'],
    'ТЧЭ-18 Дно': ['ТЧЭ - 18'],
    'ТЧЭ-5 Кандалакша': ['ТЧЭ - 05'],
    'ТЧЭ-4 Бологовское': ['ТЧЭ - 04'],
    'ТЧЭ-30 Суоярви': ['ТЧЭ - 30'],
    'ТЧЭ-22 Бабаево': ['ТЧЭ - 22']
}

# Используйте метод apply и лямбда-функцию для создания нового столбца
df2['Депо'] = df2['Депо'].apply(lambda x: next(
    (категория for категория, ключевые_слова_категории in ключевые_слова.items() if
     any(слово in x for слово in ключевые_слова_категории)), ''))

df2 = df2.query('Депо != ""')

df2['месяц'] = (df2['Дата_постановки_ожидание'].astype(str).apply(
    lambda x: x.split('.')[1] if len(x.split('.')) > 1 else None)).astype(str).apply(
    lambda x: x.split(' ')[0] if len(x.split(' ')) > 1 else None)
df2['месяц'] = df2['месяц'].astype(int)
df2 = df2.reset_index(drop=True)

# Создаем новый столбец "год_постановки_локомотива"
df2['год_постановки_локомотива'] = None

current_year = 2024

for i in range(len(df2) - 1, -1, -1):
    if i != 0 and df2.at[i, 'месяц'] < df2.at[i - 1, 'месяц']:
        current_year -= 1
    df2.at[i, 'год_постановки_локомотива'] = current_year

df2['x2'] = df2['Дата_постановки_ожидание'].astype(str).apply(lambda x: x.split(' ')[0])
df2['x3'] = df2['Дата_постановки_ожидание'].astype(str).apply(
    lambda x: x.split(' ')[1] if len(x.split(' ')) > 1 else None)
df2['Дата_постановки_ожидание'] = df2['x2'].astype(str) + '.' + df2['год_постановки_локомотива'].astype(str) + ' ' + \
                                  df2['x3'].astype(str)

df2['x2'] = df2['Дата_постановки_ремонт'].astype(str).apply(lambda x: x.split(' ')[0])
df2['x3'] = df2['Дата_постановки_ремонт'].astype(str).apply(
    lambda x: x.split(' ')[1] if len(x.split(' ')) > 1 else None)
df2['Дата_постановки_ремонт'] = df2['x2'] + '.' + df2['год_постановки_локомотива'].astype(str) + ' ' + df2['x3']

df2['x2'] = df2['Дата_выхода_из_ремонта'].astype(str).apply(lambda x: x.split(' ')[0])
df2['x3'] = df2['Дата_выхода_из_ремонта'].astype(str).apply(
    lambda x: x.split(' ')[1] if len(x.split(' ')) > 1 else None)
df2['Дата_выхода_из_ремонта'] = df2['x2'] + '.' + df2['x'] + ' ' + df2['x3']

# #ДОПОЛНИТЕЛЬНО

df2 = df2[['Депо', 'Серия', 'Номер', 'Вид', 'Дата_постановки_ожидание', 'Дата_постановки_ремонт',
           'Дата_выхода_из_ремонта']]

# выгрузка дополнительной таблицы с депо приписки локомотива
path_3 = "/Users/user/Desktop/dlya_analiz/оперативный.xlsx"
df3 = pd.read_excel(path_3, header=0)

# Добавляем столбец для обозначения вида НЭП
df1['Вид_НЭП'] = 'НР'  # Неплановый ремонт
df2['Вид_НЭП'] = 'ДР'  # Плановый ремонт

# Словарь для сопоставления серии с общей серией
common_series = {
    '1/3М62у': 'М62 ви',
    'ТЭП70бс': 'ТЭП70 ви',
    '2ТЭ116у': '2ТЭ116 ви',
    '2ТЭ25КМ': '2ТЭ25КМ',
    'ТЭП70': 'ТЭП70 ви',
    '1/2М62у': 'М62 ви',
    '2ТЭ116': '2ТЭ116 ви',
    '2ТЭ116к': '2ТЭ116 ви',
    'ТЭМ2': 'ТЭМ2 ви',
    '3ЭС4К': '3ЭС4К',
    '2ЭС4К': '2ЭС4К',
    'ЧС6': 'ЧС6',
    'ЭП2К': 'ЭП2К',
    'ЧС2Т': 'ЧС2Т',
    '2/3М62у': 'М62 ви',
    'ТЭМ2Ум': 'ТЭМ2 ви',
    'ТЭМ18ДМ': 'ТЭМ18 ви',
    'ДМ62': 'М62 ви',
    '3М62у': 'М62 ви',
    'ТЭМ7а': 'ТЭМ7 ви',
    'ТЭМ2а': 'ТЭМ2 ви',
    'ЭП1': 'ЭП1',
    '2ЭС5К': '2ЭС5К',
    '3ЭС5К': '3ЭС5К',
    'ВЛ10у': 'ВЛ10 ви',
    'ТЭМ18Д': 'ТЭМ18 ви',
    'ТЭМ2УМТ': 'ТЭМ2 ви',
    'ВЛ15': 'ВЛ15 ви',
    'ВЛ10': 'ВЛ10 ви',
    'ТЭМ18В': 'ТЭМ18 ви',
    'ТЭМ31М': 'ТЭМ31М',
    'ЧМЭ3': 'ЧМЭ3 ви',
    'ЧМЭ3т': 'ЧМЭ3 ви',
    'ЧМЭ3э': 'ЧМЭ3 ви',
    '2хТЭМ18ДМ': 'ТЭМ18 ви',
    '3ЭС8': '3ЭС8',
    '2ЭС7': '2ЭС7',
    '2ЭС6': '2ЭС6',
    'ВЛ15С': 'ВЛ15 ви',
    'ТЭМ7': 'ТЭМ7 ви',
    'ВЛ15с': 'ВЛ15 ви',
    'М62': 'М62 ви'
}

# Добавляем столбец "Общая серия" на основе словаря
df1['Общая_серия'] = df1['Серия'].map(common_series)
df2['Общая_серия'] = df2['Серия'].map(common_series)

# # # Преобразование столбца 'Номер' в строковый тип данных в таблице df3
df2['Дата_время_постановки_оперативного_графика'] = ''

df2['Дата_постановки_ожидание'] = df2['Дата_постановки_ожидание'].astype(str)
df2['Дата_постановки_ремонт'] = df2['Дата_постановки_ремонт'].astype(str)
df2['Дата_выхода_из_ремонта'] = df2['Дата_выхода_из_ремонта'].astype(str)

# Объединяем оба DataFrame в один
merged_df = pd.concat([df1, df2], ignore_index=True)

# выгрузка дополнительной таблицы с депо приписки локомотива
path_4 = "/Users/user/Desktop/dlya_analiz/Локомотивы_на_сервисе.xlsx"
df4 = pd.read_excel(path_4, header=2)

df4 = df4[['Серия', 'Номер', 'Приписка', 'Сервисная компания']]
df4['Номер'] = df4['Номер'].astype(str)
df4 = df4.rename(columns={'Сервисная компания': 'Сервисная_компания'})

# Объединение таблиц df2 и df3 по столбцам 'Депо', 'Серия' и 'Номер'
merged_df = merged_df.merge(df4[['Серия', 'Номер', 'Сервисная_компания']], on=['Серия', 'Номер'], how='left')

# Преобразование в формат datetime
merged_df['Дата_постановки_ожидание'] = pd.to_datetime(merged_df['Дата_постановки_ожидание'], dayfirst=True)
merged_df['Дата_постановки_ремонт'] = pd.to_datetime(merged_df['Дата_постановки_ремонт'], dayfirst=True)
merged_df['Дата_выхода_из_ремонта'] = pd.to_datetime(merged_df['Дата_выхода_из_ремонта'], dayfirst=True)

start_date = pd.to_datetime(start_date).strftime('%d.%m.%Y %H:%M')
end_date = pd.to_datetime(end_date).strftime('%d.%m.%Y %H:%M')

# Фильтруем данные по заданному периоду
merged_df_filtered = filter_data_by_period(merged_df, start_date, end_date)

# Преобразуем столбцы с датами к типу datetime
date_columns = ['Дата_постановки_ожидание',
                'Дата_постановки_ремонт',
                'Дата_выхода_из_ремонта',
                'Дата_время_постановки_оперативного_графика']

for col in date_columns:
    merged_df_filtered = merged_df_filtered.copy()  # Создание явной копии DataFrame
    merged_df_filtered[col] = pd.to_datetime(merged_df_filtered[col])

# Вычисляем общее время простоя
merged_df_filtered['Общее_время_простоя'] = (merged_df_filtered['Дата_выхода_из_ремонта'] - merged_df_filtered[
    'Дата_постановки_ожидание']).dt.total_seconds() / 3600

# Алгоритм для вычисления времени простоя согласно заданному условию
for index, row in merged_df_filtered.iterrows():
    if row['Дата_постановки_ожидание'] < pd.to_datetime(start_date):
        row['Дата_постановки_ожидание'] = pd.to_datetime(start_date)
    if pd.isnull(row['Дата_выхода_из_ремонта']) or row['Дата_выхода_из_ремонта'] > pd.to_datetime(end_date):
        row['Дата_выхода_из_ремонта'] = pd.to_datetime(end_date)
    if row['Дата_постановки_ожидание'] > pd.to_datetime(start_date):
        row['Дата_постановки_ожидание'] = row['Дата_постановки_ожидание']
    merged_df_filtered.loc[index, 'Общее_время_простоя'] = (row['Дата_выхода_из_ремонта'] - row[
        'Дата_постановки_ожидание']).total_seconds() / 3600

# Вычисляем время по вине заказчика и исполнителя для плановых видов ремонта
mask = merged_df_filtered['Вид_НЭП'] == 'ДР'
merged_df_filtered.loc[mask, 'Время_заказчика'] = ((merged_df_filtered['Дата_время_постановки_оперативного_графика'] -
                                                    merged_df_filtered[
                                                        'Дата_постановки_ожидание']).dt.total_seconds() / 3600)
merged_df_filtered.loc[mask, 'Время_исполнителя'] = ((merged_df_filtered['Дата_выхода_из_ремонта'] - merged_df_filtered[
    'Дата_время_постановки_оперативного_графика']).dt.total_seconds() / 3600)

# Если локомотив встал в ожидание планового ремонта позже оперативного графика,
# всё время от начала времени ожидания и начала постановки на плановый вид ремонта относится за заказчиком
mask2 = (merged_df_filtered['Вид_НЭП'] == 'ДР') & (merged_df_filtered['Дата_постановки_ожидание'] > merged_df_filtered[
    'Дата_время_постановки_оперативного_графика'])
merged_df_filtered.loc[mask2, 'Время_заказчика'] = merged_df_filtered['Общее_время_простоя']

# Вычисляем время простоя на неплановом ремонте по вине заказчика и исполнителя
merged_df_filtered['Время_простоя_НР_заказчика'] = 0  # Время простоя на НР по вине заказчика
merged_df_filtered['Время_простоя_НР_исполнителя'] = 0  # Время простоя на НР по вине исполнителя

# Новые списки ключевых фраз для определения виновного предприятия
виновные_по_заказчику = ['ОКТ', 'ТЧЭ', 'АО "НИИАС" МОСКВА',
                         'НТЭ МОСК', 'Галичская', 'Т МОСК', 'ТЭ ОАО "РЖД"', 'НТЭ МОСК', 'ТЧЭ-30 СУОЯРВИ',
                         'ТЧЭ-15 ИСАКОГОРКА', 'ТЧЭ-31 ВЕЛИКИЕ ЛУКИ', 'ТЧЭ-25 МЕДВЕЖЬЯ ГОРА',
                         'ТЧЭ-12 СПБ-ФИНЛЯНДСКИЙ', 'ТЧЭ-5 КАНДАЛАКША', 'ТЧЭ-14 СПБ ВАРШАВСКИЙ',
                         'ТЧЭ-18 ДНО', 'ТЧЭ-4 БОЛОГОВСКОЕ', 'ТЧЭ-21 ВОЛХОВСТРОЙ', 'Т ОКТ', 'ТЧЭ-26 КЕМЬ',
                         'ТЧЭ-11 ВЫБОРГ','АО "НИИАС" МОСКВА', 'ТЧЭ-11 ЛОСТА', 'ТЧЭ-9 ЛЯНГАСОВО', 'ТЧЭ-28 МУРМАНСК',
                         'ДС СУККОЗЕРО ОКТ', 'Т МОСК', 'ТЧЭ-10 ЧЕРЕПОВЕЦ', 'ТЧЭ-46 БРЯНСК-2', 'ТЧЭ-13 НЯНДОМА',
                         'ТЧЭ-22 БАБАЕВО', 'ТЭ ОАО "РЖД"', 'СПб-Московская', 'Бологовская', 'ТЧ-99 ЖДРС ПОДМОСКОВНАЯ',
                         'ТЧЭ-38 РЫБНОЕ-СОРТ.', 'ОАО "НКВЗ"', 'ТЧЭ-6 БУЙ', 'НТЭ СЕВ', 'Дновская', 'ТЧЭ-1 МОСКОВСКОЕ',
                         'ТЧЭ-12 КИНЕЛЬ', 'ТЧЭ-5 РУЗАЕВКА','ТЧ-45 ЖДРС ТРОИЦК', 'ТЧЭ-1 ЗЛАТОУСТ', 'ТЧЭ-5 ИВАНОВО-СОРТ.', 'Петрозаводская',
                         'ТЧЭ-32 РЖЕВСКОЕ','Московско-Курский', 'ТЧЭ-1 ЯРОСЛАВЛЬ-ГЛ.', 'ТЧЭ-23 БЕКАСОВО-СОРТ.', 'Волховстроевский',
                         'СПб-Финляндская', 'ТЧЭ-8 СПБ-ПАСС.-МОСК.', 'Мгинская', 'СОРТАВАЛЬСКАЯ',
                         'Новосокольническая', 'НТЭ ГОРЬК', 'ЮЖНАЯ', 'ТЧЭ-10 САМАРА', 'Тихвинская',
                         'Галичская']  # Добавляем "ТЧЭ" к списку ключевых фраз

виновные_по_исполнителю = ['СЛД', 'Спорный случай', 'АО "ТМХ-ЛОКОМОТИВЫ"', 'ЛВРЗ', 'ТРПУ', 'ТРЗ', 'АО "ТМХ-ЛОКОМОТИВЫ"',
                           'УЛАН-УДЭНСКИЙ ЛВРЗ', 'УРАЛЬСКИЕ ЛОКОМОТИВЫ', 'ЧЕЛЯБИНСКИЙ ЭРЗ', 'ОРЕНБУРГСКИЙ',
                           'ЗАО УПРАВЛЯЮЩАЯ КОМПАНИЯ "БМЗ"', 'УССУРИЙСКИЙ', 'АСТРАХАНСКИЙ', 'ЯРОСЛАВСКИЙ',
                           'МИЧУРИНСКИЙ','РОСТОВСКИЙ', 'ВОРОНЕЖСКИЙ ТРЗ', 'СЛД-16 ВОЛХОВ', 'ТРПУ-2 САНКТ-ПЕТЕРБУРГ',
                           'СЛД-17 ДНО-ПСКОВСКОЕ','СЛД-2 САНКТ-ПЕТЕРБУРГ', 'СЛД-29 КЕМСКОЕ', 'СЛД-32 КИНЕЛЬ', 'ЗАО УПРАВЛЯЮЩАЯ КОМПАНИЯ "БМЗ"',
                           'СЛД-33 ВЕЛИКОЛУКСКОЕ','СЛД-9 СПБ-СОРТ-ВИТЕБ', 'ЧЕЛЯБИНСКИЙ ЭРЗ', 'СЛД-27 КАНДАЛАКША', 'ОРЕНБУРГСКИЙ',
                           'СЛД-22 ЮЖНЫЙ УРАЛ','СЛД-24 ПЕТРОЗАВОДСК', 'СЛД-18 ДЕМА', 'СЛД-36 СОЛЬВЫЧЕГОДСК',
                           'УССУРИЙСКИЙ', 'СЛД-21 ЕЛЕЦ', 'МИЧУРИНСКИЙ', 'СЛД-49 УНЕЧА', 'СЛД-7 СПБ-СОРТ-МОСК',
                           'ТРПУ-16 ВОЛХОВ','СЛД-35 НЯНДОМА-СЕВ', 'СЛД-61 БЕКАСОВО', 'СЛД-31 ИВАНОВО', 'ВОРОНЕЖСКИЙ ТРЗ',
                           'УРАЛЬСКИЕ ЛОКОМОТИВЫ','Спорный случай', 'СЛД-23 ХВОЙНАЯ', 'УЛАН-УДЭНСКИЙ ЛВРЗ', 'АСТРАХАНСКИЙ',
                           'СЛД-60 ОРЕХОВО', 'СЛД-21 ТАГАНАЙ', 'СЛД-3 ТВЕРЬ', 'СЛД-16  САРАТОВ', 'СЛД-17 БЕЛОВО',
                           'СЛД-5 САРЕПТА', 'СЛД-2 КАЛИНИНГРАД', 'АО "ТМХ-ЛОКОМОТИВЫ"',
                           'ЯРОСЛАВСКИЙ', 'ТРПУ-24 ПЕТРОЗАВОДСК', 'СЛД-33 ПЕНЗА', 'СЛД-40 ВЯЗЬМА', 'ТРПУ-37 РЫБНОЕ',
                           'СЛД-15 ТУАПСЕ-ПАСС','СЛД-13 ДЕРБЕНТ-МАХАЧК', 'СЛД-37 РЫБНОЕ', 'НОВОЧЕРКАССКИЙ', 'ТРПУ-47 БРЯНСК-ЛЬГОВ',
                           'СЛД-33 ШАРЬЯ','СЛД-34 ВОЛОГДА', 'СЛД-30 ЛЯНГАСОВО-ЗАП', 'ТРПУ-32 КИНЕЛЬ-ГРУЗОВОЙ',
                           'СЛД-9 ПОВОРИНО', 'СЛД-28 МУРОМ-ВОСТ', 'ТРПУ-9 СПБ-СОРТ.-ВИТЕБСКИЙ', 'СЛД-16 МОСКВА-СОРТ',
                           'СЛД-30 ЯРОСЛАВЛЬ', 'СЛД-47 БРЯНСК-ЛЬГОВ', 'СЛД-36  БУГУЛЬМА', 'Московско-Курский',
                           'СЛД-10 ЕРШОВСКОЕ', 'СЛД-28 ОРЕЛ', 'РОСТОВСКИЙ', 'СЛД-23 ЗИМИНСКОЕ', 'ТРПУ-29 КЛУБ',
                           'ТРПУ-27 КАНДАЛАКША', 'КОЛОМЕНСКИЙ','СЛД-28 КРАСНОДАР', 'ТРПУ-28 ОРЕЛ', 'СЛД-1 БЕЛГОРОД', 'СЛД-30 САМАРА ', 'СЛД-35 ТЮМЕНЬ',
                           'ТРПУ-3 ТВЕРЬ']  # Добавляем "ТЧЭ" к списку ключевых фраз

# Применяем функцию к каждой строке DataFrame
merged_df_filtered = merged_df_filtered.apply(calculate_downtime, axis=1)

merged_df_filtered = merged_df_filtered[['Депо', 'Серия', 'Номер', 'Вид_НЭП', 'Дата_постановки_ожидание',
                                         'Дата_постановки_ремонт', 'Дата_выхода_из_ремонта', 'Общее_время_простоя',
                                         'Время_заказчика',
                                         'Время_исполнителя', 'Дата_время_постановки_оперативного_графика',
                                         'Время_простоя_НР_заказчика',
                                         'Время_простоя_НР_исполнителя', 'Общая_серия', 'Сервисная_компания']]

# ПЕРЕСЫЛКА

print('НАЧАЛО КОДА ПО ПЕРЕСЫЛКАМ МАй')

folder_path = "/Users/user/Desktop/NEP/NEP_mai"

# Список файлов Excel в папке
excel_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# Инициализация списка для хранения датафреймов
dfs = []

# Чтение и объединение данных из каждого файла Excel
for file in excel_files:
    df = pd.read_excel(file, header=2)
    df = df.rename(columns={df.columns[1]: '1 Серия'})[['1 Серия', 'Номер', 'Дата', 'Состояние', 'Дислокация','№ поезда']]
    df['Состояние'] = df['Состояние'].astype(str)
    dfs.append(df)
# Объединение всех датафреймов в один
merged_df = pd.concat(dfs, ignore_index=True)

# ________________________________________________________________________#
print('НАЧАЛО КОДА ПО ПЕРЕСЫЛКАМ июнь')

# Путь к папке с файлами Excel
folder_path = "/Users/user/Desktop/NEP/NEP_june"

# Список файлов Excel в папке
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# Инициализация списка для хранения датафреймов
dfs = []

# Чтение и объединение данных из каждого файла Excel
for file in excel_files:
    df = pd.read_excel(os.path.join(folder_path, file), header=2)
    current_column_name = df.columns[1]
    df = df.rename(columns={current_column_name: '1 Серия'})
    df = df[['1 Серия', 'Номер', 'Дата', 'Состояние', 'Дислокация','№ поезда']]
    df['Состояние'] = df['Состояние'].astype(str)
    dfs.append(df)

# Объединение всех датафреймов в один
merged_df_1 = pd.concat(dfs, ignore_index=True)

print('Окончание КОДА ПО ПЕРЕСЫЛКАМ июнь')

merged_df_1['Дата'] = merged_df_1['Дата'].str.replace('-', '.')
merged_df_1['Дата'] = pd.to_datetime(merged_df_1['Дата'], dayfirst=True)

# Объединение двух датафреймов
merged_df = pd.concat([merged_df, merged_df_1], ignore_index=True)

# Сортировка по нескольким столбцам
merged_df = merged_df.sort_values(by=['1 Серия', 'Номер', 'Дата'])

# __________________________________________________________________________#
# Загрузка данных из Excel файла
df5 = merged_df
df5['Состояние'] = df5['Состояние'].astype(str)

# Инициализация списка для хранения данных о пересылках
shipments = []

# Инициализация переменных для хранения данных о текущей пересылке
current_series = None
current_number = None
start_date_1 = None
end_date = None
ozh_date = None
nep_rem_date = None
ship_1 = None
ship_2 = None

# Номера поездов, которые мы рассматриваем
train_numbers = list(range(8901, 8918))
spisok = ['ОЖ. ТО-2', 'ТО-2', 'ТО-3', 'ОЖ.PEM.CEK', 'СР-Д', 'ЭКИПИРОВКА', 'TO-2 БP.', 'ТР-1', 'РЕКЛАМАЦИЯ',
          'ТР-2', 'ОЖ.ОТП.ЗР', 'ТР-2 + ТО-4', 'ТР-3', 'ТР-1 + ТО-4', 'ТО-5б', 'ТО-4', 'ТО-5в', 'Консервация',
          'ТО-5а(Р)', 'Резерв ОАО «РЖД»', 'ТО-5г(Р)', 'ТО-5А(КОНС)', 'КР', 'ОЖ ТО-5а(Р)', 'ОЖ РЕМ ЗАВ',
          'СР ЗАВОД', 'ТО-2 ХОЛ', 'ТО-5д', 'ТО-3 + ТО-4', 'МОД-Д', 'ТО-5г(КОНС)', 'РЕКЛАМАЦИЯ ДЕПО', 'ОЖ ТО-5г (Р)',
          'ТО.3']

# Проходим по каждой строке данных
for index, row in df5.iterrows():
    if row['№ поезда'] in train_numbers:  # Если номер поезда соответствует списку
        if start_date_1 is None:  # Если дата начала пересылки не задана
            current_series = row['1 Серия']  # Сохраняем серию локомотива
            current_number = row['Номер']  # Сохраняем номер локомотива
            start_date_1 = row['Дата']  # Устанавливаем дату начала пересылки
            ship_1 = row['Дислокация'] # устанавливаем станцию дислокации
        else:
            continue
    else:  # Если номер поезда не соответствует списку
        if start_date_1 is not None:  # Если дата начала пересылки задана
            if (row['Состояние'] == 'ОЖ.НЕП.РЕМ') and (current_series == row['1 Серия']) and (
                    current_number == row['Номер']):  # Если состояние ОЖ.НЕПЛ.РЕМ
                end_date = row['Дата']  # Устанавливаем дату окончания пересылки
                ozh_date = row['Дата']  # Устанавливаем дату начала ожидания непланового ремонта
                ship_2 = row['Дислокация'] # устанавливаем станцию окончания дислокации
                shipments.append({'Серия': current_series, 'Номер': current_number,
                                  'Дата начала пересылки': start_date_1, 'Дата окончания пересылки': end_date,
                                  'Дата_постановки_ожидание': ozh_date, 'Станция_пересылки_начало': ship_1,
                                  'Станция_пересылки_окончание': ship_2,})  # Добавляем период пересылки в список
                start_date_1 = None  # Сбрасываем дату начала пересылки
                end_date = None  # Сбрасываем дату окончания пересылки
                ozh_date = None
                ship_1 = None
                ship_2 = None

            elif (row['Состояние'] in spisok) and (current_series == row['1 Серия']) and (
                    current_number == row['Номер']):
                shipments.append({'Серия': current_series, 'Номер': current_number,
                                  'Дата начала пересылки': start_date_1, 'Дата окончания пересылки': "0",
                                  'Дата_постановки_ожидание': "пересылка на плановый вид ремонта",
                                  'Станция_пересылки_начало': ship_1})  # Добавляем период пересылки в список
                start_date_1 = None  # Сбрасываем дату начала пересылки
                end_date = None  # Сбрасываем дату окончания пересылки
                ozh_date = None
                ship_1 = None
                ship_2 = None

            elif (row['Состояние'] != 'ОЖ.НЕП.РЕМ') and (current_series == row['1 Серия']) and (
                    current_number == row['Номер']):
                continue
            else:
                shipments.append({'Серия': current_series, 'Номер': current_number,
                                  'Дата начала пересылки': start_date_1, 'Дата окончания пересылки': "0",
                                  'Дата_постановки_ожидание': "пересылка не включается"})  # Добавляем период пересылки в список
                start_date_1 = None  # Сбрасываем дату начала пересылки
                end_date = None  # Сбрасываем дату окончания пересылки
                ozh_date = None
                ship_1 = None
                ship_2 = None

# Создание DataFrame для периодов пересылки
shipments_df = pd.DataFrame(shipments)

shipments_df_1 = shipments_df[shipments_df['Дата окончания пересылки'] != "0"]
shipments_df_1 = shipments_df_1.copy()  # Создаем явную копию DataFrame
shipments_df_1['Дата_постановки_ожидание'] = pd.to_datetime(shipments_df_1['Дата_постановки_ожидание'], dayfirst=True)



# В дальнейшем удалить___________________________________________________
# Функция для преобразования данных в верхний регистр
def convert_to_uppercase(data):
    return data.str.upper()
# Преобразование данных в верхний регистр в двух столбцах
shipments_df_1['Станция_пересылки_начало'] = convert_to_uppercase(shipments_df_1['Станция_пересылки_начало'])
shipments_df_1['Станция_пересылки_окончание'] = convert_to_uppercase(shipments_df_1['Станция_пересылки_окончание'])
# shipments_df_1.to_excel("__.xlsx", engine="openpyxl", index=False)


# выгрузка дополнительной таблицы с депо приписки локомотива
path_9 = "/Users/user/Desktop/dlya_analiz/Расстояние_пересылаемых_локомотивов.xlsx"
df___ = pd.read_excel(path_9, header = 1)

#соединил 2 последние таблицы через способ left
shipments_df_1 = shipments_df_1.merge(df___, on = ['Станция_пересылки_начало','Станция_пересылки_окончание'], how = 'left')
shipments_df_1.to_excel("__.xlsx", engine="openpyxl", index=False)


# Добавляем столбец для обозначения вида НЭП
shipments_df_1['Вид_НЭП'] = 'пересылка_на_НР'  # Неплановый ремонт
shipments_df_1['Номер'] = shipments_df_1['Номер'].astype(str)

# Сохранение объединенного датафрейма в файл Excel
prip = "/Users/user/Desktop/dlya_analiz/prip.xlsx"
df_prip = pd.read_excel(prip, header=3)
df_prip = df_prip.rename(columns={'Unnamed: 3': 'Номер', 'Unnamed: 2': 'Серия', 'Unnamed: 4': 'Депо'})
df_prip = df_prip[['Номер', 'Серия', 'Депо']]
df_prip['Номер'] = df_prip['Номер'].astype(str)

shipments_df_1['Номер'] = shipments_df_1['Номер'].astype(str)
shipments_df_1 = shipments_df_1.merge(df_prip, on=['Серия', 'Номер'], how='left')

shipments_df_1 = shipments_df_1.merge(merged_df_filtered[['Серия', 'Номер', 'Дата_постановки_ожидание', 'Вид_НЭП',
                                                          'Общая_серия', 'Сервисная_компания',
                                                          'Время_простоя_НР_заказчика',
                                                          'Время_простоя_НР_исполнителя']],
                                      on=['Серия', 'Номер', 'Дата_постановки_ожидание'], how='left').query(
    'Вид_НЭП_y == "НР"')

shipments_df_1 = shipments_df_1[['Депо', 'Серия', 'Номер', 'Дата начала пересылки',
                                 'Дата окончания пересылки', 'Общая_серия', 'Сервисная_компания',
                                 'Время_простоя_НР_заказчика', 'Время_простоя_НР_исполнителя',
                                 'Станция_пересылки_начало','Станция_пересылки_окончание','Расстояние']]
shipments_df_1['Вид_НЭП'] = 'пересылка_на_НР'  # Неплановый ремонт
shipments_df_1['Дата_постановки_ожидание'] = 0

shipments_df_1 = shipments_df_1.rename(columns={'Дата начала пересылки': 'Дата_постановки_ремонт',
                                                'Дата окончания пересылки': 'Дата_выхода_из_ремонта'})
shipments_df_1['Время_заказчика'] = 0
shipments_df_1['Время_исполнителя'] = 0
shipments_df_1['Дата_время_постановки_оперативного_графика'] = 0
shipments_df_1['Общее_время_простоя'] = 0

# Расчет общего времени передислокации__выдает ошибку_

start_date = pd.to_datetime(start_date, dayfirst=True)

# Применяем функцию к каждой строке DataFrame
shipments_df_1['Дата_выхода_из_ремонта'] = pd.to_datetime(shipments_df_1['Дата_выхода_из_ремонта'], dayfirst=True)
shipments_df_1['Дата_постановки_ремонт'] = pd.to_datetime(shipments_df_1['Дата_постановки_ремонт'], dayfirst=True)
shipments_df_1['Общее_время_передислокации'] = shipments_df_1.apply(calculate_total_relocation_time, axis=1, result_type='reduce')


# Заменяем значения в столбце 'Общее_время_передислокации' на 0, если 'Дата_выхода_из_ремонта' меньше start_date
shipments_df_1.loc[shipments_df_1['Дата_выхода_из_ремонта'] < start_date, 'Общее_время_передислокации'] = 0

shipments_df_1['передислокация_исполнителя'] = 0
shipments_df_1['передислокация_заказчика'] = 0
shipments_df_1 = shipments_df_1[['Депо', 'Серия', 'Номер', 'Вид_НЭП', 'Дата_постановки_ожидание',
                                 'Дата_постановки_ремонт', 'Дата_выхода_из_ремонта',
                                 'Общее_время_простоя', 'Время_заказчика', 'Время_исполнителя',
                                 'Дата_время_постановки_оперативного_графика',
                                 'Время_простоя_НР_заказчика', 'Время_простоя_НР_исполнителя',
                                 'передислокация_заказчика', 'передислокация_исполнителя',
                                 'Общее_время_передислокации', 'Общая_серия', 'Сервисная_компания',
                                 'Станция_пересылки_начало','Станция_пересылки_окончание','Расстояние']]

# Условие: если 'Время_простоя_НР_заказчика' > 0 и 'Время_простоя_НР_исполнителя' = 0,
# то 'передисл_заказчика' = 'Общее_время_передислокации', иначе 'передисл_исполнителя' = 'Общее_время_передислокации'
shipments_df_1.loc[(shipments_df_1['Время_простоя_НР_заказчика'] > 0) & (
            shipments_df_1['Время_простоя_НР_исполнителя'] == 0), 'передислокация_заказчика'] = shipments_df_1[
                            'Общее_время_передислокации']
shipments_df_1.loc[(shipments_df_1['Время_простоя_НР_заказчика'] == 0) & (
            shipments_df_1['Время_простоя_НР_исполнителя'] > 0), 'передислокация_исполнителя'] = shipments_df_1[
                            'Общее_время_передислокации']
shipments_df_1['Время_простоя_НР_исполнителя'] = 0
shipments_df_1['Время_простоя_НР_заказчика'] = 0

merged_df_filtered['передислокация_заказчика'] = 0
merged_df_filtered['передислокация_исполнителя'] = 0
merged_df_filtered['Общее_время_передислокации'] = 0
merged_df_filtered = merged_df_filtered[['Депо', 'Серия', 'Номер', 'Вид_НЭП', 'Дата_постановки_ожидание',
                                         'Дата_постановки_ремонт', 'Дата_выхода_из_ремонта',
                                         'Общее_время_простоя', 'Время_заказчика', 'Время_исполнителя',
                                         'Дата_время_постановки_оперативного_графика',
                                         'Время_простоя_НР_заказчика', 'Время_простоя_НР_исполнителя',
                                         'передислокация_заказчика', 'передислокация_исполнителя',
                                         'Общее_время_передислокации', 'Общая_серия', 'Сервисная_компания']]
# Объединение двух датафреймов
merged_df_filtered = pd.concat([merged_df_filtered, shipments_df_1], ignore_index=True)

merged_df_filtered = merged_df_filtered.rename(
    columns={'Дата_постановки_ремонт': 'Дата_постановки_ремонт (начало передислокации)',
             'Дата_выхода_из_ремонта': 'Дата_выхода_из_ремонта (окончание передислокации)'})

# Сохранение результатов в отдельные файлы Excel с разделением по депо, серии локомотивов и сервисной компании
for depo, depo_data in merged_df_filtered.groupby('Депо'):
    with pd.ExcelWriter(f'{depo}.xlsx') as writer:
        for series, series_data in depo_data.groupby(['Общая_серия', 'Сервисная_компания']):
            series_name, service_company = series
            series_data.to_excel(writer, sheet_name=f'{series_name}_{service_company}', index=False)
