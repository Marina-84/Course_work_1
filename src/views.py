import datetime
import json
import logging
import os


from src.utils import (filter_by_date, get_currency_rates, get_data_about_cards, get_data_from_excel, get_greeting,
                       get_stock_rates, get_top_transactions)

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "views.log"),
    filemode="w",
    format="%(asctime)s: %(name)s: %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_settings.json")


def main_page(date: str) -> str:
    """Function get info for main page."""

    logger.info("Запуск функции-генератора JSON-ответа для главной страницы")
    df = get_data_from_excel(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx"))
    date_for_stock = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S").strftime("%Y-%m-%d")
    with open(PATH) as f:
        data = json.load(f)
    filtered_df = filter_by_date(date, df)
    currency_list = data["user_currencies"]
    stock_list = data["user_stocks"]
    greeting = get_greeting(date)
    cards_info = get_data_about_cards(filtered_df)
    top_transactions = get_top_transactions(filtered_df)
    currency_rates = get_currency_rates(currency_list)
    stock_rates = get_stock_rates(stock_list, date_for_stock)
    main_page_info = json.dumps(
        {
            "greeting": greeting,
            "cards": cards_info,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_rates,
        },
        ensure_ascii=False,
    )
    logger.info("Завершение генерации JSON-ответа для главной страницы")
    return main_page_info
