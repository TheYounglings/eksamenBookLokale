import tkinter as tk
from tkinter import messagebox, Canvas
from datetime import datetime

from bl import BookingManager
from bl import UserManager
from db import DataAccessLayer

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lokalebooker")
        self.user = None
        
        # Create the Business Logic Layer instance
        self.booking_manager = BookingManager(DataAccessLayer())
        self.user_manager = UserManager(DataAccessLayer())
        
        # UI Elements setup (Headers, Buttons, Forms, etc.)
        self.rooms = self.booking_manager.get_rooms()

        self.setup_ui()

        

    def setup_ui(self):
        
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

        separator = tk.Frame(root, height=2, bg="black")  # Thin black line
        separator.pack(fill="x")

        title_label = tk.Label(header, text="Lokalebooker", bg="gray", fg="black", font=("Helvetica", 16, "bold"))
        title_label.pack(side="left", padx=10, pady=10)

        login_border = tk.Frame(header, bg="black")
        login_border.pack(side="right", padx=10, pady=10)

        self.login_btn = tk.Button(
            login_border,
            text="Log ind",
            bg="gray",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            command=self.show_login_screen
        )
        self.login_btn.pack(padx=1, pady=1)


        self.login_frame = tk.Frame(root, bg="white")
        tk.Label(self.login_frame, text="Log ind", font=("Helvetica", 16, "bold"), bg="white").pack(pady=(10, 20))

        tk.Label(self.login_frame, text="Brugernavn:", bg="white").pack(anchor="w")
        self.username_entry = tk.Entry(self.login_frame, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Kodeord:", bg="white").pack(anchor="w")
        self.password_entry = tk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.login_frame, 
                  text="Log ind", 
                  width=15, 
                  command=self.handle_login,    
                  ).pack(pady=10)


        # Add a Return Button
        tk.Button(self.login_frame, text="Return", width=15, command=self.handle_return).pack(pady=5)


        self.error_label = tk.Label(self.login_frame, text="", bg="white", font=("Helvetica", 10))
        self.error_label.pack()

        self.main_frame = tk.Frame(root, bg="white")
        tk.Label(self.main_frame, text="Lokaler:", font=("Helvetica", 14, "bold"), bg="white").pack(anchor="w", pady=(0, 10))

        # Buttons for sorting
        sort_frame = tk.Frame(self.main_frame, bg="white")
        sort_frame.pack(pady=10)

        sort_name_btn = tk.Button(sort_frame, text="Sorter alfabetisk", command=self.sort_rooms_by_name)
        sort_name_btn.pack(side="left", padx=5)

        sort_building_floor_btn = tk.Button(sort_frame, text="Sorter efter bygning/floor", command=self.sort_rooms_by_building_floor)
        sort_building_floor_btn.pack(side="left", padx=5)

        sort_availability_btn = tk.Button(sort_frame, text="Sorter efter tilgængelighed", command=self.sort_rooms_by_availability)
        sort_availability_btn.pack(side="left", padx=5)

        self.room_buttons = {}
        for room in self.rooms:
            
            btn = tk.Button(self.main_frame, text=f"{room['name']} - Ledigt", font=("Helvetica", 12), width=30,
                            fg="green", anchor="w", command=lambda r=room['name']: self.handle_room_click(r))
            btn.pack(pady=5, anchor="w")
            self.room_buttons[room['name']] = btn

        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.update_room_buttons()


        
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.user = self.user_manager.validate_user(username, password)
        
        if self.user:
            messagebox.showinfo("Login Success", "You are now logged in.")
            self.login_btn.config(text="Log ud", command=self.handle_logout)
            self.handle_return()
            self.error_label.config(text="")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_logout(self):
        self.current_user = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()

    def handle_return(self):
        # Hide the login screen and show the main screen (or any other screen)
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.update_room_buttons()
            
    def handle_room_click(self, room_name):
        room = next(room for room in self.rooms if room['name'] == room_name)
        room_id = room['id']  # Find the room dictionary from the list
        if self.user == None:
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
        self.draw_calendar(calendar_canvas, room['id'])

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
                allowed_dates = self.booking_manager.get_current_week_dates()
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

            for booking in self.booking_manager.get_bookings(room['id']):
                if str(booking["date"]) != str(date):
                    continue
                existing_start = datetime.strptime(f"{booking['date']} {booking['start']}", "%Y-%m-%d %H:%M:%S")

                existing_end = datetime.strptime(f"{booking['date']} {booking['end']}", "%Y-%m-%d %H:%M:%S")
                if start_dt < existing_end and end_dt > existing_start:
                    messagebox.showerror("Tidskonflikt", f"Konflikt med booking {booking['start']}-{booking['end']}")
                    return



            self.booking_manager.add_booking(self.user[0], room_id, date, start, end)

            popup.destroy()
            self.update_room_buttons()
        tk.Button(form_frame, text="Book", command=confirm_booking).grid(row=3, column=0, columnspan=2, pady=10)

        # Adjust row and column weight to make sure the popup resizes properly
        popup.grid_rowconfigure(0, weight=1)  # Calendar takes up most space
        popup.grid_rowconfigure(1, weight=0)  # Form Frame doesn't need to expand
        popup.grid_columnconfigure(0, weight=1)  # Expand across width
        popup.grid_columnconfigure(1, weight=1)  # Expand across width

    def update_room_buttons(self):
        for room in self.rooms:
            room_name = room['name']
            room_id = room['id']
            button = self.room_buttons.get(room_name)
            if self.booking_manager.is_room_occupied(room_id):
                button.config(fg="red", text=f"{room_name} - Optaget", state="normal")
            else:
                button.config(fg="green", text=f"{room_name} - Ledigt", state="normal")

    def draw_calendar(self,canvas, room_id):
        canvas.delete("all")
        hour_height = 40
        day_width = 120
        start_hour = 8
        end_hour = 18

        week_dates = self.booking_manager.get_current_week_dates()
        hours = list(range(start_hour, end_hour + 1))

        for i, date in enumerate(week_dates):
            x = i * day_width + 60
            canvas.create_line(x, 0, x, (end_hour - start_hour) * hour_height + 30, fill="gray")
            canvas.create_text(x + day_width // 2, 10, text=date, font=("Helvetica", 9, "bold"))

        for h in hours:
            y = (h - start_hour) * hour_height + 30
            canvas.create_line(60, y, 60 + len(week_dates) * day_width, y, fill="lightgray")
            canvas.create_text(50, y, text=f"{h:02}:00", anchor="e", font=("Helvetica", 8))

        bookings = self.booking_manager.get_bookings(room_id)
        for booking in bookings:

            try:
                

                col = week_dates.index(str(booking["date"]))


                
                start_time = datetime.strptime(str(booking["start"]), "%H:%M:%S")
                end_time = datetime.strptime(str(booking["end"]), "%H:%M:%S")

                start = start_time.strftime("%H:%M")
                end = end_time.strftime("%H:%M")

                start_minutes = start_time.hour * 60 + start_time.minute
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

    def sort_rooms_by_name(self):
        sorted_rooms = sorted(self.rooms, key=lambda x: x['name'])
        self.update_room_buttons_sorted(sorted_rooms)

    def sort_rooms_by_building_floor(self):
        sorted_rooms = sorted(self.rooms, key=lambda x: (x['building'], x['floor']))
        self.update_room_buttons_sorted(sorted_rooms)

    def sort_rooms_by_availability(self):
        sorted_rooms = sorted(self.rooms, key=lambda x: self.booking_manager.is_room_occupied(x['id']))
        self.update_room_buttons_sorted(sorted_rooms)

    def update_room_buttons_sorted(self, sorted_rooms):
        # Remove all current buttons
        for button in self.room_buttons.values():
            button.destroy()  # Actually removes them from memory

        self.room_buttons.clear()  # Reset the dictionary

        # Recreate buttons in sorted order
        for room in sorted_rooms:
            status = "Optaget" if self.booking_manager.is_room_occupied(room['id']) else "Ledigt"
            color = "red" if status == "Optaget" else "green"

            button = tk.Button(
                self.main_frame,
                text=f"{room['name']} - {status}",
                font=("Helvetica", 12),
                width=30,
                fg=color,
                anchor="w",
                command=lambda r=room['name']: self.handle_room_click(r)
            )
            button.pack(pady=5, anchor="w")
            self.room_buttons[room['name']] = button


    def show_login_screen(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)
# Start Tkinter Application
root = tk.Tk()
app = GUI(root)
root.mainloop()
