import tkinter as tk
from tkinter import messagebox, Canvas
from datetime import datetime, timedelta
from db import *
DB = DataAcessLayer()

def get_current_week_dates():
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


logged_in = {"status": False, "user": None}


# Define rooms with additional attributes
rooms = DB.get_rooms()

def show_login_screen():
    main_frame.pack_forget()
    login_frame.pack(fill="both", expand=True, padx=20, pady=20)

def show_main_screen():
    login_frame.pack_forget()
    main_frame.pack(padx=20, anchor="w", pady=20,expand=True)
    update_room_buttons()

def handle_login():
    username = username_entry.get()
    password = password_entry.get()
    user = DB.validate_user(username, password)
    if user:
        logged_in["status"] = True
        logged_in["user"] = username
        logged_in["user_id"] = user[0]  # user[0] is ID from DB
        login_btn.config(text="Log ud", command=handle_logout)
        show_main_screen()
        error_label.config(text="")
    else:
        error_label.config(text="Forkert brugernavn eller kodeord!", fg="red")

def handle_logout():
    logged_in["status"] = False
    logged_in["user"] = None
    login_btn.config(text="Log ind", command=show_login_screen)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    error_label.config(text="")
    show_login_screen()

def draw_calendar(canvas, room_id):
    canvas.delete("all")
    hour_height = 40
    day_width = 120
    start_hour = 8
    end_hour = 18

    week_dates = get_current_week_dates()
    hours = list(range(start_hour, end_hour + 1))

    for i, date in enumerate(week_dates):
        x = i * day_width + 60
        canvas.create_line(x, 0, x, (end_hour - start_hour) * hour_height + 30, fill="gray")
        canvas.create_text(x + day_width // 2, 10, text=date, font=("Helvetica", 9, "bold"))

    for h in hours:
        y = (h - start_hour) * hour_height + 30
        canvas.create_line(60, y, 60 + len(week_dates) * day_width, y, fill="lightgray")
        canvas.create_text(50, y, text=f"{h:02}:00", anchor="e", font=("Helvetica", 8))

    bookings = DB.get_bookings(room_id)
    for booking in bookings:

        try:
            

            col = week_dates.index(str(booking["date"]))


            
            print(booking["start"])
            start_time = datetime.strptime(str(booking["start"]), "%H:%M:%S")
            print(start_time)
            end_time = datetime.strptime(str(booking["end"]), "%H:%M:%S")

            start = start_time.strftime("%H:%M")
            end = end_time.strftime("%H:%M")

            start_minutes = start_time.hour * 60 + start_time.minute
            print(start_minutes)
            end_minutes = end_time.hour * 60 + end_time.minute
            y1 = ((start_minutes - start_hour * 60) / 60) * hour_height + 30
            y2 = ((end_minutes - start_hour * 60) / 60) * hour_height + 30
            x1 = col * day_width + 62
            x2 = x1 + day_width - 4

            canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="blue")
            canvas.create_text((x1 + x2)//2, (y1 + y2)//2, 
                               text=f"{start}-{end}", 
                               font=("Helvetica", 8), justify="center")
        except:
            continue

def handle_room_click(room_name):
    room = next(room for room in rooms if room['name'] == room_name)
    room_id = room['id']  # Find the room dictionary from the list
    if not logged_in["status"]:
        messagebox.showinfo("Login krævet", "Du skal være logget ind for at booke et lokale.")
        return

    popup = tk.Toplevel(root)
    popup.title(f"Book {room_name}")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    popup_width = min(800, screen_width - 100)
    popup_height = min(600, screen_height - 100)

    popup.geometry(f"{popup_width}x{popup_height}")

    # Calendar Canvas
    calendar_canvas = Canvas(popup, bg="white")
    calendar_canvas.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    draw_calendar(calendar_canvas, room['id'])

    # Form Frame
    form_frame = tk.Frame(popup)
    form_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")

    tk.Label(form_frame, text="Dato (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
    date_entry = tk.Entry(form_frame, width=30)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    date_entry.grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Starttid (HH:MM):").grid(row=1, column=0, sticky="w")
    start_entry = tk.Entry(form_frame, width=30)
    start_entry.grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="Sluttid (HH:MM):").grid(row=2, column=0, sticky="w")
    end_entry = tk.Entry(form_frame, width=30)
    end_entry.grid(row=2, column=1, pady=5)

    def confirm_booking():
        date = date_entry.get()
        start = start_entry.get()
        end = end_entry.get()

        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            allowed_dates = get_current_week_dates()
            if date not in allowed_dates:
                messagebox.showerror("Ugyldig dato", "Du kan kun booke for indeværende uge.")
                return
            start_dt = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M")
            if start_dt >= end_dt:
                raise ValueError("Starttid skal være før sluttid.")
        except ValueError as ve:
            messagebox.showerror("Ugyldig input", str(ve))
            return

        for booking in DB.get_bookings(room['id']):
            if booking["date"] != date:
                continue
            existing_start = datetime.strptime(f"{booking['date']} {booking['start']}", "%Y-%m-%d %H:%M")
            existing_end = datetime.strptime(f"{booking['date']} {booking['end']}", "%Y-%m-%d %H:%M")
            if start_dt < existing_end and end_dt > existing_start:
                messagebox.showerror("Tidskonflikt", f"Konflikt med booking {booking['start']}-{booking['end']} af {booking['user']}")
                return



        DB.add_booking(logged_in["user_id"], room_id, date, start, end)

        popup.destroy()
        update_room_buttons()


    tk.Button(form_frame, text="Book", command=confirm_booking).grid(row=3, column=0, columnspan=2, pady=10)

    # Adjust row and column weight to make sure the popup resizes properly
    popup.grid_rowconfigure(0, weight=1)  # Calendar takes up most space
    popup.grid_rowconfigure(1, weight=0)  # Form Frame doesn't need to expand
    popup.grid_columnconfigure(0, weight=1)  # Expand across width
    popup.grid_columnconfigure(1, weight=1)  # Expand across width

def is_room_occupied(room_id):
    now = datetime.now()
    bookings = DB.get_bookings(room_id)
    for booking in bookings:
        # Check if booking['date'] is a string or already a datetime.date
        if isinstance(booking['date'], str):
            # If the date is a string, parse it into a datetime.date object
            date_obj = datetime.strptime(booking['date'], "%Y-%m-%d").date()
        else:
            # If it's already a date, use it directly
            date_obj = booking['date']
        
        # Handle 'start' and 'end' if they are timedelta objects
        if isinstance(booking['start'], timedelta):
            # If 'start' is a timedelta, convert it to a string in "HH:MM:SS" format
            start_time_str = str(booking['start'])
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
        else:
            # If 'start' is already a string, parse it
            start_time = datetime.strptime(booking['start'], "%H:%M:%S").time()

        if isinstance(booking['end'], timedelta):
            # If 'end' is a timedelta, convert it to a string in "HH:MM:SS" format
            end_time_str = str(booking['end'])
            end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
        else:
            # If 'end' is already a string, parse it
            end_time = datetime.strptime(booking['end'], "%H:%M:%S").time()

        # Combine date and time to get start_dt and end_dt
        start_dt = datetime.combine(date_obj, start_time)
        end_dt = datetime.combine(date_obj, end_time)

        # Check if the room is occupied at the current time
        if start_dt <= now <= end_dt:
            return True
    return False

def update_room_buttons():
    for room in rooms:
        room_name = room['name']
        room_id = room['id']
        button = room_buttons.get(room_name)
        if is_room_occupied(room_id):
            button.config(fg="red", text=f"{room_name} - Optaget", state="normal")
        else:
            button.config(fg="green", text=f"{room_name} - Ledigt", state="normal")


def sort_rooms_by_name():
    sorted_rooms = sorted(rooms, key=lambda x: x['name'])
    update_room_buttons_sorted(sorted_rooms)

def sort_rooms_by_building_floor():
    sorted_rooms = sorted(rooms, key=lambda x: (x['building'], x['floor']))
    update_room_buttons_sorted(sorted_rooms)

def sort_rooms_by_availability():
    sorted_rooms = sorted(rooms, key=lambda x: is_room_occupied(x['id']))
    update_room_buttons_sorted(sorted_rooms)

def update_room_buttons_sorted(sorted_rooms):
    
    for idx, room in enumerate(sorted_rooms):
        button = room_buttons.get(room['name'])
        if button:
            button.pack_forget()
        button = tk.Button(main_frame, text=f"{room['name']} - Ledigt", font=("Helvetica", 12), width=30,
                           fg="green", anchor="w", command=lambda r=room: handle_room_click(r))
        button.pack(pady=5, anchor="w")
        room_buttons[room['name']] = button

def handle_return():
    # Hide the login screen and show the main screen (or any other screen)
    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    update_room_buttons()

def refresh_loop():
    update_room_buttons()
    root.after(10000, refresh_loop)

root = tk.Tk()
root.title("Lokalebooker")

# Start in fullscreen
root.attributes("-fullscreen", True)

# Toggle fullscreen with F11, exit with Escape
def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

def end_fullscreen(event=None):
    root.attributes("-fullscreen", False)

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", end_fullscreen)

# Dynamically set initial window geometry (optional fallback)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Background and main layout
root.configure(bg="white")

header = tk.Frame(root, bg="gray", height=50)
header.pack(fill="x")

title_label = tk.Label(header, text="Lokalebooker", bg="gray", fg="black", font=("Helvetica", 16, "bold"))
title_label.pack(side="left", padx=10, pady=10)

login_btn = tk.Button(header, text="Log ind", bg="gray", relief="flat", font=("Helvetica", 10, "bold"),
                      command=show_login_screen)
login_btn.pack(side="right", padx=10, pady=10)

login_frame = tk.Frame(root, bg="white")
tk.Label(login_frame, text="Log ind", font=("Helvetica", 16, "bold"), bg="white").pack(pady=(10, 20))

tk.Label(login_frame, text="Brugernavn:", bg="white").pack(anchor="w")
username_entry = tk.Entry(login_frame, width=30)
username_entry.pack(pady=5)

tk.Label(login_frame, text="Kodeord:", bg="white").pack(anchor="w")
password_entry = tk.Entry(login_frame, width=30, show="*")
password_entry.pack(pady=5)

tk.Button(login_frame, text="Log ind", width=15, command=handle_login).pack(pady=10)

# Add a Return Button
tk.Button(login_frame, text="Return", width=15, command=handle_return).pack(pady=5)


error_label = tk.Label(login_frame, text="", bg="white", font=("Helvetica", 10))
error_label.pack()

main_frame = tk.Frame(root, bg="white")
tk.Label(main_frame, text="Lokaler:", font=("Helvetica", 14, "bold"), bg="white").pack(anchor="w", pady=(0, 10))

# Buttons for sorting
sort_frame = tk.Frame(main_frame, bg="white")
sort_frame.pack(pady=10)

sort_name_btn = tk.Button(sort_frame, text="Sorter alfabetisk", command=sort_rooms_by_name)
sort_name_btn.pack(side="left", padx=5)

sort_building_floor_btn = tk.Button(sort_frame, text="Sorter efter bygning/floor", command=sort_rooms_by_building_floor)
sort_building_floor_btn.pack(side="left", padx=5)

sort_availability_btn = tk.Button(sort_frame, text="Sorter efter tilgængelighed", command=sort_rooms_by_availability)
sort_availability_btn.pack(side="left", padx=5)

room_buttons = {}
for room in rooms:
    
    btn = tk.Button(main_frame, text=f"{room['name']} - Ledigt", font=("Helvetica", 12), width=30,
                    fg="green", anchor="w", command=lambda r=room['name']: handle_room_click(r))
    btn.pack(pady=5, anchor="w")
    room_buttons[room['name']] = btn

main_frame.pack(fill="both", expand=True, padx=20, pady=20)
refresh_loop()
root.mainloop()
