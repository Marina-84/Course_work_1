import datetime

from src.services import investment_bank
from src.views import main_page


def main():
    """Main function."""

    date_obj = datetime.datetime.now() - datetime.timedelta(days=365 * 4)
    today = date_obj.strftime("%d.%m.%Y %H:%M:%S")
    main_page(today)


if __name__ == "__main__":
    main()
