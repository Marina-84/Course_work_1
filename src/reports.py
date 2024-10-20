import datetime
import json
import logging
import os
from typing import Optional
import pandas as pd


logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "reports.log"),
    filemode="w",
    format="%(asctime)s: %(name)s: %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "report.json")


def report(filename=PATH):
    """Decorator create report file."""

    def my_decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            json_data = json.dumps(result)
            with open(filename, "w") as file:
                json.dump(json_data, file)
            return result

        return wrapper

    return my_decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Function get sum of spending by category."""

    logger.info(f"Запуск функции {spending_by_category.__name__}")
    if date:
        date_obj = datetime.datetime.strptime(date, "%d.%m.%Y")
    else:
        date_obj = datetime.datetime.now().date()
    end_date = date_obj.strftime("%Y.%m.%d")
    transactions["Дата"] = transactions["Дата платежа"].map(
        lambda x: datetime.datetime.strptime(str(x), "%d.%m.%Y").strftime("%Y.%m.%d")
    )
    begin_date = (date_obj - datetime.timedelta(days=90)).strftime("%Y.%m.%d")
    tr_by_cat = transactions.loc[transactions.loc[:, "Категория"] == category]
    tr_by_cat_period = tr_by_cat[(tr_by_cat["Дата"] >= begin_date) & (tr_by_cat["Дата"] <= end_date)]
    logger.info(f"Успешное завершение работы функции {spending_by_category.__name__}")
    return tr_by_cat_period.iloc[:, :-1]
