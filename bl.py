from datetime import datetime, timedelta
class UserManager:
    def __init__(self,dal):
        self.dal = dal

    def validate_user(self,username, password):
        user = self.dal.get_user(username, password)
        return user

class BookingManager:
    def __init__(self, dal):
        self.dal = dal  
    def get_current_week_dates(self):
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
        return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    def get_rooms(self):
        return self.dal.get_rooms()
    
    def get_bookings(self, room_id):
        return self.dal.get_bookings(room_id)
    
    def add_booking(self, user_id, room_id, date, start, end):
        self.dal.add_booking(user_id, room_id, date, start, end)
    
    def is_room_occupied(self, room_id):
        now = datetime.now()
        bookings = self.dal.get_bookings(room_id)
        for booking in bookings:
            start_dt = datetime.combine(booking['date'], datetime.strptime(str(booking["start"]), "%H:%M:%S").time())
            end_dt = datetime.combine(booking['date'], datetime.strptime(str(booking["end"]), "%H:%M:%S").time())
            if start_dt <= now <= end_dt:
                return True
        return False