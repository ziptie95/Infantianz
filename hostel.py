import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import sqlite3
import os


# Database Handling for Room Data Persistence
class RoomDatabase:
    def __init__(self, db_name="hostel.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.initialize_db()

    def initialize_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                                id INTEGER PRIMARY KEY,
                                room_number INTEGER,
                                room_type TEXT,
                                is_occupied INTEGER)''')
        self.connection.commit()
        
        # Add rooms only if they don't already exist in the database
        if not self.get_rooms():
            for i in range(1, 51):  # Example: 50 rooms, alternating types
                room_type = "AC" if i % 2 == 0 else "NON-AC"
                self.add_room(i, room_type)

    def add_room(self, room_number, room_type):
        self.cursor.execute("INSERT INTO rooms (room_number, room_type, is_occupied) VALUES (?, ?, ?)", 
                            (room_number, room_type, 0))
        self.connection.commit()

    def allocate_room(self, room_type):
        self.cursor.execute("SELECT * FROM rooms WHERE room_type = ? AND is_occupied = 0 LIMIT 1", 
                            (room_type,))
        room = self.cursor.fetchone()
        if room:
            self.cursor.execute("UPDATE rooms SET is_occupied = 1 WHERE id = ?", (room[0],))
            self.connection.commit()
        return room

    def deallocate_room(self, room_number):
        self.cursor.execute("UPDATE rooms SET is_occupied = 0 WHERE room_number = ?", (room_number,))
        self.connection.commit()

    def get_rooms(self, status_filter=None):
        if status_filter == "Occupied":
            self.cursor.execute("SELECT * FROM rooms WHERE is_occupied = 1")
        elif status_filter == "Empty":
            self.cursor.execute("SELECT * FROM rooms WHERE is_occupied = 0")
        else:
            self.cursor.execute("SELECT * FROM rooms")
        return self.cursor.fetchall()

    def get_dashboard(self):
        self.cursor.execute("SELECT COUNT(*) FROM rooms")
        total_rooms = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM rooms WHERE is_occupied = 1")
        occupied_rooms = self.cursor.fetchone()[0]
        empty_rooms = total_rooms - occupied_rooms
        return total_rooms, occupied_rooms, empty_rooms

    def close(self):
        self.connection.close()


# Main Hostel Management Application
class HostelApp(App):
    def build(self):
        self.db = RoomDatabase()

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Title
        title_label = Label(text="Hostel Management System", font_size='24sp', size_hint=(1, None), height=50)
        layout.add_widget(title_label)

        # Student Name Input
        self.name_input = TextInput(hint_text="Enter Student Name", font_size='18sp', size_hint_y=None, height=40)
        layout.add_widget(self.name_input)

        # Room Type Selection with DropDown
        room_type_layout = BoxLayout(size_hint_y=None, height=50)
        room_type_label = Label(text="Room Type:", font_size='18sp', size_hint=(0.3, 1))
        self.room_type_dropdown = DropDown()
        
        for room_type in ["AC", "NON-AC"]:
            btn = Button(text=room_type, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.room_type_dropdown.select(btn.text))
            self.room_type_dropdown.add_widget(btn)

        self.room_type_button = Button(text="Select Room Type", size_hint=(0.7, 1))
        self.room_type_button.bind(on_release=self.room_type_dropdown.open)
        self.room_type_dropdown.bind(on_select=lambda instance, x: setattr(self.room_type_button, 'text', x))
        room_type_layout.add_widget(room_type_label)
        room_type_layout.add_widget(self.room_type_button)
        layout.add_widget(room_type_layout)

        # Allocate and Deallocate Room Buttons
        allocate_button = Button(text="Allocate Room", size_hint_y=None, height=50)
        allocate_button.bind(on_press=self.allocate_room)
        layout.add_widget(allocate_button)

        # Room Number Input for Deallocation
        self.room_number_input = TextInput(hint_text="Enter Room Number to Deallocate", font_size='18sp', size_hint_y=None, height=40)
        layout.add_widget(self.room_number_input)

        deallocate_button = Button(text="Deallocate Room", size_hint_y=None, height=50)
        deallocate_button.bind(on_press=self.deallocate_room)
        layout.add_widget(deallocate_button)

        # Generate Report Button
        report_button = Button(text="Generate Room Report", size_hint_y=None, height=50)
        report_button.bind(on_press=self.show_report)
        layout.add_widget(report_button)

        # Show Dashboard Button
        dashboard_button = Button(text="Show Dashboard", size_hint_y=None, height=50)
        dashboard_button.bind(on_press=self.show_dashboard)
        layout.add_widget(dashboard_button)

        # Scrollable Report Display
        self.report_display = ScrollView(size_hint=(1, None), size=(Window.width, Window.height / 3))
        layout.add_widget(self.report_display)

        return layout

    def allocate_room(self, instance):
        student_name = self.name_input.text.strip()
        room_type = self.room_type_button.text.strip()
        if student_name and room_type in ["AC", "NON-AC"]:
            room = self.db.allocate_room(room_type)
            if room:
                self.show_popup("Room Allocated", f"Room {room[1]} ({room_type}) allocated to {student_name}.")
            else:
                self.show_popup("No Room Available", f"No available rooms of type {room_type}.")
        else:
            self.show_popup("Input Error", "Please enter a valid Student Name and select Room Type.")

    def deallocate_room(self, instance):
        room_number_text = self.room_number_input.text.strip()
        if room_number_text.isdigit():
            room_number = int(room_number_text)
            self.db.deallocate_room(room_number)
            self.show_popup("Room Deallocated", f"Room {room_number} has been deallocated.")
        else:
            self.show_popup("Input Error", "Please enter a valid Room Number to deallocate.")

    def show_report(self, instance):
        rooms = self.db.get_rooms()
        report = '\n'.join([f"Room {room[1]} - {room[2]} - {'Occupied' if room[3] else 'Empty'}" for room in rooms])
        report_label = Label(text=report, font_size='16sp', size_hint_y=None)
        report_label.bind(
            width=lambda *x: report_label.setter('text_size')(report_label, (report_label.width, None))
        )
        report_label.texture_update()
        report_label.height = report_label.texture_size[1]
        self.report_display.clear_widgets()
        self.report_display.add_widget(report_label)

    def show_dashboard(self, instance):
        total, occupied, empty = self.db.get_dashboard()
        dashboard_text = f"Total Rooms: {total}\nOccupied Rooms: {occupied}\nEmpty Rooms: {empty}"
        self.show_popup("Dashboard", dashboard_text)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

    def on_stop(self):
        self.db.close()


# Run the Application
if __name__ == "__main__":
    HostelApp().run()
