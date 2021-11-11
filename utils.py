from dotenv import load_dotenv
import os


def get_config() -> dict:
    load_dotenv("config.env")
    keys = [
        "ID",
        "PASSWORD",
        "ID_XPATH",
        "PASSWORD_XPATH",
        "LOGIN_BUTTON_XPATH",
        "SEARCH_BAR_XPATH",
        "TOTAL_IMG_NUM_XPATH",
        "POP_IMG_XPATH",
        "RECENT_IMG_XPATH",
    ]
    config_dict = {key: value for key, value in os.environ.items() if key in keys}
    return config_dict
