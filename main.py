from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
from function.credentials import get_creds
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'https://127.0.0.1:7890'

def get_calendar_list(service):
    """Get list of calendars from the Google Calendar API."""
    return service.calendarList().list().execute().get("items")


def get_events(service, calendar_id, time_min, time_max):
    """Retrieve events for a specific calendar."""
    return service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()


def calculate_time_spent(service, calendar_list, from_date, to_date):
    shanghai_tz = pytz.timezone('Asia/Shanghai')

    # Convert from_date and to_date to datetime objects in Shanghai timezone
    from_date_dt = shanghai_tz.localize(datetime.strptime(from_date, "%Y-%m-%d"))
    to_date_dt = shanghai_tz.localize(datetime.strptime(to_date, "%Y-%m-%d"))

    time_spent = {}

    for entry in calendar_list:
        calendar_id = entry['id']
        events = get_events(service, calendar_id, from_date_dt.isoformat(), to_date_dt.isoformat()).get("items")
        for event in events:
            start = datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.fromisoformat(event['end']['dateTime'])
            duration = (end - start).total_seconds() / 3600  # Convert to hours
            time_spent[calendar_id] = time_spent.get(calendar_id, 0) + duration

    return time_spent


def plot_time_spent(time_spent, calendar_map):
    """Plot the time spent on each calendar."""
    time_spent_summary = {calendar_map[calendar_id]: time for calendar_id, time in time_spent.items()}
    labels = time_spent_summary.keys()
    sizes = time_spent_summary.values()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.axis('equal')  # Equal aspect ratio ensures that the pie chart is circular.
    plt.show()


def main():
    try:
        service = build("calendar",
                        "v3",
                        credentials=get_creds())
        calendar_list = get_calendar_list(service)
        calendar_map = {entry['id']: entry['summary'] for entry in calendar_list}
        time_spent = calculate_time_spent(service, calendar_list, "2024-01-01", "2024-01-07")
        plot_time_spent(time_spent, calendar_map)
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
