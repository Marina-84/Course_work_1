import os
from unittest.mock import patch

from src.views import main_page


@patch("src.views.get_stock_rates")
@patch("src.views.get_currency_rates")
@patch("src.views.get_top_transactions")
@patch("src.views.get_data_about_cards")
@patch("src.views.json.load")
@patch("src.views.open")
def test_main_page(
    mock_open,
    mock_json,
    mock_get_data_about_cards,
    mock_get_top_transactions,
    mock_get_currency_rates,
    mock_get_stock_rates,
    json_response,
):
    mock_json.return_value = {"user_currencies": ["USD"], "user_stocks": ["MOEX"]}
    mock_get_data_about_cards.return_value = [{"last digits": "*7777", "total_spent": 88888.01, "cashback": 88.88}]
    mock_get_top_transactions.return_value = [
        {
            "date": "2024.05.02 05:02:00",
            "amount": 17000,
            "category": "Супермаркеты",
            "description": "Выброшенные на ветер деньги",
        }
    ]
    mock_get_currency_rates.return_value = [{"currency": "USD", "price": 22}]
    mock_get_stock_rates.return_value = [{"stock": "MOEX", "price": 111.11}]
    assert main_page("01.02.2020 01:02:03") == json_response
    mock_open.assert_called_once_with(os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_settings.json"))
