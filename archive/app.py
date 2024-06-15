from flask import Flask, request, render_template_string
import requests
import time
import threading
import sched
import random

app = Flask(__name__)
scheduler = sched.scheduler(time.time, time.sleep)
scheduler_thread = None
stop_event = threading.Event()
interval_range = (30, 60)

def visit_website():
    try:
        response = requests.get("https://www.google.com")
        print(f"Visited at {time.strftime('%Y-%m-%d %H:%M:%S')}: {response.status_code}")
    except Exception as e:
        print(f"Error visiting site at {time.strftime('%Y-%m-%d %H:%M:%S')}: {e}")

def schedule_visits(action, actionargs=()):
    if not stop_event.is_set():
        interval = random.randint(*interval_range)
        scheduler.enter(interval, 1, schedule_visits, (action, actionargs))
        action(*actionargs)

def start_scheduler():
    stop_event.clear()
    schedule_visits(visit_website)
    scheduler.run()

def start_scheduler_thread():
    global scheduler_thread
    if not scheduler_thread or not scheduler_thread.is_alive():
        scheduler_thread = threading.Thread(target=start_scheduler)
        scheduler_thread.start()

@app.route('/')
def home():
    return "Website visitor is running in the background with random intervals!"

@app.route('/start')
def start():
    start_scheduler_thread()
    start_message = "Scheduler started!"
    print(start_message)
    return start_message

@app.route('/stop')
def stop():
    stop_event.set()
    # Clear the scheduler queue to stop any pending tasks
    for event in list(scheduler.queue):
        scheduler.cancel(event)
    stop_message = "Scheduler stopped!"
    print(stop_message)
    return stop_message

@app.route('/set_interval', methods=['GET', 'POST'])
def set_interval():
    if request.method == 'POST':
        try:
            min_interval = int(request.form['min_interval'])
            max_interval = int(request.form['max_interval'])
            global interval_range
            interval_range = (min_interval, max_interval)
            message = f"Interval range updated to {min_interval} - {max_interval} seconds."
            print(message)
            return message
        except ValueError:
            return "Invalid input. Please enter integer values."
    
    return '''
    <form method="post">
        Minimum Interval (seconds): <input type="text" name="min_interval"><br>
        Maximum Interval (seconds): <input type="text" name="max_interval"><br>
        <input type="submit" value="Submit">
    </form>
    '''

if __name__ != '__main__':
    start_scheduler_thread()
