from datetime import datetime, timedelta
from function.util import get_project_root
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


def calculate_time_spent(service, calendar_list, from_date_dt, to_date_dt):
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


def plot_time_spent(time_spent, calendar_list, title):
    calendar_map = {entry['id']: (entry['summary'], entry['backgroundColor']) for entry in calendar_list}
    # Prepare data for sorting
    label_size_color = [(calendar_map[calendar_id][0], time_spent[calendar_id], calendar_map[calendar_id][1]) for
                        calendar_id in time_spent]

    # Sort the data alphabetically by label
    label_size_color.sort(key=lambda x: x[0])

    # Unzip the sorted data
    labels, sizes, colors = zip(*label_size_color)

    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('equal')  # Equal aspect ratio ensures that the pie chart is circular.
    plt.title(title)

    plt.savefig(f"{get_project_root()}/reports/{title}.png")
    plt.show()


def main():
    try:
        start_date_input = input("Enter the start date (YYYY-MM-DD), default to today: ")
        end_date_input = input("Enter the end date (YYYY-MM-DD), default to today(inclusive): ")

        shanghai_tz = pytz.timezone('Asia/Shanghai')
        today = datetime.now(shanghai_tz).date()

        start_date = start_date_input if start_date_input else today.strftime("%Y-%m-%d")
        end_date = end_date_input if end_date_input else today.strftime("%Y-%m-%d")

        # Convert from_date and to_date to datetime objects in Shanghai timezone
        from_date_dt = shanghai_tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))

        # Need to add one day as time is exclusive per doc https://developers.google.com/calendar/api/v3/reference/events/list
        end_date_dt = shanghai_tz.localize(datetime.strptime(end_date, "%Y-%m-%d")) + timedelta(days=1)

        service = build("calendar",
                        "v3",
                        credentials=get_creds())
        print("======== retrieving calendar data ========")
        calendar_list = get_calendar_list(service)
        print("======== calculating time spend ========")
        time_spent = calculate_time_spent(service, calendar_list, from_date_dt, end_date_dt)
        print("======== plotting graph ========")
        plot_time_spent(time_spent, calendar_list, f"{from_date_dt.date()} to {end_date_dt.date()}")
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
