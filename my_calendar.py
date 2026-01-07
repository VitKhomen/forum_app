from datetime import datetime, date
from zoneinfo import ZoneInfo
import calendar


class MyCalendar(calendar.Calendar):

    def __init__(self, firstweekday=0):
        super().__init__(firstweekday)
        # date -> list[{'event_time_utc': datetime, 'description': str}]
        self.events = {}

    def show_month(self, year, month):
        """Show the month calendar with events marked"""
        month_calendar = self.monthdayscalendar(year, month)
        month_name = calendar.month_name[month]
        print(f"{month_name} {year}".center(20))
        print("Mo Tu We Th Fr Sa Su")
        for week in month_calendar:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "   "
                elif date(year, month, day) in self.events:
                    week_str += f"{day:3}*"
                else:
                    week_str += f"{day:3}"
            print(week_str)

    def add_event(self, event_date, event_time_local, description):
        """Add an event to the calendar"""
        local_tz = datetime.now().astimezone().tzinfo
        event_datetime_local = datetime.combine(
            event_date, event_time_local, tzinfo=local_tz)
        event_datetime_utc = event_datetime_local.astimezone(ZoneInfo("UTC"))

        if event_date not in self.events:
            self.events[event_date] = []
        self.events[event_date].append({
            'event_time_utc': event_datetime_utc,
            'description': description
        })

    def get_events_on_date(self, event_date):
        """Get a list of events on a specified date"""
        current_tz = datetime.now().astimezone().tzinfo
        events = self.events.get(event_date, [])
        if not events:
            print("You have free day :)")
            return
        print(f'You have some events on {event_date}')
        for n, ev in enumerate(events, 1):
            ev_with_local_time = ev['event_time_utc'].astimezone(current_tz)
            print(f'{n}. {ev_with_local_time.time()} - {ev["description"]}')


def show(my_calendar):
    try:
        year = int(input('Enter year - YYYY like 2026: '))
        month = int(input('Enter month - MM like 1-12: '))
        my_calendar.show_month(year, month)
    except:
        print('You enter something strange, so i show current month')
        today = date.today()
        my_calendar.show_month(today.year, today.month)


def add(my_calendar):
    date_str = input('Enter event date (YYYY-MM-DD): ')
    time_str = input('Enter event time (HH:MM): ')
    description = input('Enter event description: ')

    event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    event_time = datetime.strptime(time_str, '%H:%M').time()

    my_calendar.add_event(event_date, event_time, description)


def view(my_calendar):
    date_str = input('Enter event date (YYYY-MM-DD): ')
    event_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    my_calendar.get_events_on_date(event_date)


def help():
    print('''
    Okay my friend, here are some commands you can use:
    show - if you want to see a month calendar
    add - if you want add event for date to your calendar
    view - let you see events for specific date
    help, h, ?, info - show this help message
    'exit', 'quit', 'q', 'e' - exit the program
          ''')


def main():
    my_cal = MyCalendar()

    today = date.today()
    print("Hello! Here is MyCalendar!\nFirst, i show you the current month:\n")
    my_cal.show_month(today.year, today.month)

    help()

    while True:

        try:
            command = input(
                "\nI'm waiting for you commands:\n> ".strip().lower())
            if command == 'show':
                show(my_cal)
            elif command == 'add':
                add(my_cal)
            elif command == 'view':
                view(my_cal)
            elif command in ['help', 'h', '?', 'info']:
                help()
            elif command in ['exit', 'quit', 'q', 'e']:
                print("Goodbye! See you later!")
                break
            else:
                print(f"I don't understand what you mean '{command}'.\n")
        except KeyboardInterrupt:
            print("\nSee you later!")
            break
        except Exception as e:
            print(f"What's doing wrong! Error {e}. Try again.\n")


if __name__ == "__main__":
    main()
