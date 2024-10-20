from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (
    filter_by_date,
    get_currency_rates,
    get_data_about_cards,
    get_data_from_excel,
    get_greeting,
    get_stock_rates,
    get_top_transactions,
)


@patch("src.utils.pd.read_excel")
def test_get_data_from_excel(mock_read_excel, empty_df):
    mock_read_excel.return_value = empty_df
    assert get_data_from_excel("test.xlsx").equals(empty_df)
    mock_read_excel.assert_called_once_with("test.xlsx")


@patch("requests.get")
def test_get_currency_rates(mock_get):
    mock_get.return_value.json.return_value = {"Valute": {"EUR": {"Value": 95.1844}}}
    assert get_currency_rates(["EUR"]) == [{"currency": "EUR", "price": 95.1844}]
    mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")


@patch("requests.get")
def test_get_stock_rates(mock_get, moex_response):
    mock_get.return_value.json.return_value = moex_response
    assert get_stock_rates(["YDEX"]) == [{"stock": "YDEX", "price": 4.0}]
    mock_get.assert_called_once_with("https://iss.moex.com/iss/securities/YDEX/aggregates.json?date=2024-08-08")


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ("01.01.2023 06:05:04", "Доброе утро"),
        ("01.01.2023 13:05:04", "Добрый день"),
        ("01.01.2023 20:05:04", "Добрый вечер"),
        ("01.01.2023 01:05:04", "Доброй ночи"),
    ],
)
def test_get_greeting(input_data, expected):
    assert get_greeting(input_data) == expected


def test_get_data_about_cards(test_operations):
    assert get_data_about_cards(test_operations) == [{"last digits": "*7197", "total_spent": 224.89, "cashback": 2.25}]


def test_get_top_transactions(top_5):
    assert get_top_transactions(top_5, 2) == [
        {"date": "31.12.2019", "amount": 17000, "category": "Услуги банка", "description": "Колхоз"},
        {"date": "31.12.2020", "amount": 4575.45, "category": "Фастфуд", "description": "Колхоз"},
    ]


def test_filter_by_date(transactions_df_test_1):
    df = pd.DataFrame(
        {
            "Дата операции": ["01.08.2024 18:00:00"],
            "Сумма операции": ["-160.89"],
            "Категория": ["Супермаркеты"],
        }
    )
    assert filter_by_date("07.08.2024 18:00:05", transactions_df_test_1).equals(df)
