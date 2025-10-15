from datetime import datetime


def format_datetime_1(datetime_str):
    """
    Ex: FROM: "2024-08-23 09:46:41" 
        TO:   "23th Aug 24, 9:46 am"
    """

    # dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    dt = datetime_str
    formatted_dt = dt.strftime("%d{suffix} %b %y, %-I:%M %p").lower()

    def __get_day_suffix(day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            return "th"
        else:
            return ["st", "nd", "rd"][day % 10 - 1]

    day_with_suffix = dt.strftime("%d").lstrip("0") + __get_day_suffix(int(dt.strftime("%d")))
    formatted_dt = dt.strftime(f"{day_with_suffix} %b %y, %-I:%M %p").lower()

    return formatted_dt
