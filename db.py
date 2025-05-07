import mysql.connector


class DataAccessLayer:
    def __init__(self):
        self.con = self.get_connection()


    def get_connection(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="lokalebooker"
        )

    def get_user(self, username, password):
        cursor = self.con.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        return user

    def get_rooms(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        cursor.close()
        conn.close()
        return rooms

    def get_bookings(self,room_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bookings WHERE room_id = %s", (room_id,))
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return bookings

    def add_booking(self,user_id, room_id, date, start, end):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (user_id, room_id, date, start, end)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, room_id, date, start, end))
        conn.commit()
        cursor.close()
        conn.close()
