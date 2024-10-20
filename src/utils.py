import datetime
import logging
import os
from collections import Counter
import pandas as pd
import requests
from pandas import DataFrame


logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "utils.log"),
    filemode="w",
    format="%(asctime)s: %(name)s: %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


PATH_TO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")


def get_data_from_excel(excel_path: str) -> DataFrame:
    """ Функция получает данные из файла excel """

    logger.info(f"Запуск функции {get_data_from_excel.__name__}")
    if excel_path == "":
        excel_data = pd.DataFrame(
            {
                "Дата операции": [],
                "Дата платежа": [],
                "Номер карты": [],
                "Статус": [],
                "Сумма операции": [],
                "Валюта операции": [],
                "Сумма платежа": [],
                "Валюта платежа": [],
                "Кэшбэк": [],
                "Категория": [],
                "МСС": [],
                "Описание": [],
                "Бонусы (включая кэшбэк)": [],
                "Округление на инвесткопилку": [],
                "Сумма операции с округлением": [],
            }
        )
        return excel_data
    try:
        excel_data = pd.read_excel(excel_path)
        excel_data_no_nan = excel_data.loc[excel_data["Номер карты"].notnull()]
    except Exception as e:
        logger.error(f"Функция {get_data_from_excel.__name__} завершилась с ошибкой {e}")
        excel_data = pd.DataFrame()
        return excel_data
    logger.info(f"Успешное завершение работы функции {get_data_from_excel.__name__}")
    return excel_data_no_nan


def get_currency_rates(currencies_list: list[str]) -> list[dict]:
    """ Функция получает данные о курсе валют через API """

    logger.info(f"Запуск функции {get_currency_rates.__name__}")
    currency_rates = []
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    courses = response.json()
    for currency in currencies_list:
        currency_rates.append({"currency": currency, "price": courses["Valute"][currency]["Value"]})
    logger.info(f"Успешное завершение работы функции {get_currency_rates.__name__}")
    return currency_rates


def get_stock_rates(stocks: list[str], date="2024-08-08") -> list[dict]:
    """ Функция получает данные о стоимости акций через API """

    stock_rates = []
    for stock in stocks:
        try:
            j = requests.get(f"https://iss.moex.com/iss/securities/{stock}/aggregates.json?date={date}").json()
            data = [{k: r[i] for i, k in enumerate(j["aggregates"]["columns"])} for r in j["aggregates"]["data"]]
            df_data = pd.DataFrame(data)
            price = round(float((df_data.loc[0, "value"] / df_data.loc[0, "volume"])), 2)
        except Exception:
            price = f"{date} торгов по {stock} не было"
        stock_rates.append({"stock": stock, "price": price})
    return stock_rates


def get_greeting(date_str: str) -> str:
    """ Функция генерирует приветствие для пользователя в зависимости от времени суток """

    time_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
    if 6 <= time_obj.hour < 11:
        greeting = "Доброе утро"
    elif 11 <= time_obj.hour < 18:
        greeting = "Добрый день"
    elif 18 <= time_obj.hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    return greeting


def get_data_about_cards(df_data: DataFrame) -> list[dict]:
    """ Функция генерирует данные о банковских картах пользователя """

    cards_list = list(Counter(df_data.loc[:, "Номер карты"]))
    cards_data = []
    for card in cards_list:
        j_df_data = df_data.loc[df_data.loc[:, "Номер карты"] == card]
        total_spent = abs(sum(j for j in j_df_data.loc[:, "Сумма операции"] if j < 0))
        cashback = round(total_spent / 100, 2)
        cards_data.append({"last digits": card, "total_spent": total_spent, "cashback": cashback})
    return cards_data


def get_top_transactions(df_data: DataFrame, top_number=5) -> list[dict]:
    """ Функция генерирует данные о топ-5 транзакциях за текущий месяц """

    top_transactions_list = []
    df = df_data.loc[::]
    df["amount"] = df.loc[:, "Сумма платежа"].map(float).map(abs)
    sorted_df_data = df.sort_values(by="amount", ascending=False, ignore_index=True)
    for i in range(top_number):
        date = sorted_df_data.loc[i, "Дата платежа"]
        amount = float(sorted_df_data.loc[i, "amount"])
        category = sorted_df_data.loc[i, "Категория"]
        description = sorted_df_data.loc[i, "Описание"]
        top_transactions_list.append(
            {"date": date, "amount": amount, "category": category, "description": description}
        )
    return top_transactions_list


def filter_by_date(current_date: str, df: DataFrame) -> DataFrame:
    """ Функция фильтрует DataFrame, оставляя операции только за текущий месяц """

    end_date = datetime.datetime.strptime(current_date, "%d.%m.%Y %H:%M:%S")
    start_date = datetime.datetime.strptime(f"01.{end_date.month}.{end_date.year} 00:00:00", "%d.%m.%Y %H:%M:%S")
    df["Дата"] = df["Дата операции"].map(lambda x: datetime.datetime.strptime(str(x), "%d.%m.%Y %H:%M:%S"))
    filtered_df = df[(df["Дата"] >= start_date) & (df["Дата"] <= end_date)]
    return filtered_df.iloc[:, :-1]
