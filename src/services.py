import datetime
import logging
import os
from typing import Any

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "services.log"),
    filemode="w",
    format="%(asctime)s: %(name)s: %(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int = 50) -> float:
    """Function get salary by investment_bank."""

    logger.info(f"Запуск функции {investment_bank.__name__}.")
    target_date_obj = datetime.datetime.strptime(month, "%Y-%m")
    savings: float = 0.00
    try:
        for transaction in transactions:
            print(transaction)
            date_obj = datetime.datetime.strptime(transaction["Дата операции"], "%Y-%m-%d")
            if target_date_obj.year == date_obj.year and target_date_obj.month == date_obj.month:
                round_up = limit - transaction["Сумма операции"] % limit
                savings += round_up
        logger.info(f"Успешное завершение работы функции {investment_bank.__name__}.")
        return savings
    except Exception as e:
        logger.error(f"Завершение функции {investment_bank.__name__} с ошибкой {e}.")
        return savings
