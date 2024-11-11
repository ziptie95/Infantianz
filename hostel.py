import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.clock import Clock
from kivy.core.window import Window
import random

kivy.require('2.1.0')  # Replace with the version you have installed

# Room, Floor, Building, and Hostel Management System
class Room:
    def __init__(self, room_number, room_type, is_occupied=False):
        self.room_number = room_number
        self.room_type = room_type
        self.is_occupied = is_occupied

    def allocate(self):
        if not self.is_occupied:
            self.is_occupied = True
            return True
        return False

    def deallocate(self):
        self.is_occupied = False

class Floor:
    def __init__(self, floor_number):
        self.floor_number = floor_number
        self.rooms = []

    def add_room(self, room):
        self.rooms.append(room)

class Building:
    def __init__(self, building_name):
        self.building_name = building_name
        self.floors = []

    def add_floor(self, floor):
        self.floors.append(floor)

class Hostel:
    def __init__(self):
        self.buildings = []

    def add_building(self, building):
        self.buildings.append(building)

    def allocate_room(self, preferred_type):
        for building in self.buildings:
            for floor in building.floors:
                for room in floor.rooms:
                    if room.room_type == preferred_type and not room.is_occupied:
                        room.allocate()
                        return room
        return None

    def get_room_report(self):
        report = []
        for building in self.buildings:
            for floor in building.floors:
                for room in floor.rooms:
                    status = "Occupied" if room.is_occupied else "Empty"
                    report.append({
                        'Room Number': room.room_number,
                        'Room Type': room.room_type,
                        'Status': status
                    })
        return report

    def generate_dashboard(self):
        total_rooms = 0
        occupied_rooms = 0
        empty_rooms = 0
        for building in self.buildings:
            for floor in building.floors:
                for room in floor.rooms:
                    total_rooms += 1
                    if room.is_occupied:
                        occupied_rooms += 1
                    else:
                        empty_rooms += 1
        return {
            'Total Rooms': total_rooms,
            'Occupied Rooms': occupied_rooms,
            'Empty Rooms': empty_rooms
        }

# RecycleView to display room data
class RoomDataView(RecycleDataViewBehavior, Label):
    pass

class RoomListView(RecycleView):
    def __init__(self, **kwargs):
        super(RoomListView, self).__init__(**kwargs)
        self.viewclass = RoomDataView
        self.data = []

    def update_data(self, report):
        self.data = [{'text': f"Room {entry['Room Number']} ({entry['Room Type']}) - {entry['Status']}"} for entry in report]

# Main App using Kivy
class HostelApp(App):
    def build(self):
        self.hostel = Hostel()
        
        # Building and Floor setup
        building = Building("Building A")
        floor1 = Floor(1)
        floor2 = Floor(2)

        # Add rooms for testing
        for i in range(1, 51):
            floor1.add_room(Room(i, "AC" if i % 2 == 0 else "NON-AC"))
            floor2.add_room(Room(i + 50, "AC" if i % 2 != 0 else "NON-AC"))

        building.add_floor(floor1)
        building.add_floor(floor2)

        self.hostel.add_building(building)

        # Create main layout
        layout = BoxLayout(orientation="vertical", padding=10)

        # Title Label
        title_label = Label(text="Hostel Management System", font_size='24sp', size_hint=(1, None), height=50)
        layout.add_widget(title_label)

        # Student name input
        name_layout = BoxLayout(size_hint_y=None, height=50)
        name_label = Label(text="Student Name:", font_size='18sp', size_hint=(0.3, 1))
        self.name_input = TextInput(font_size='18sp', size_hint=(0.7, 1))
        name_layout.add_widget(name_label)
        name_layout.add_widget(self.name_input)
        layout.add_widget(name_layout)

        # Room Type input
        room_layout = BoxLayout(size_hint_y=None, height=50)
        room_label = Label(text="Room Type (AC or NON-AC):", font_size='18sp', size_hint=(0.3, 1))
        self.room_input = TextInput(font_size='18sp', size_hint=(0.7, 1))
        room_layout.add_widget(room_label)
        room_layout.add_widget(self.room_input)
        layout.add_widget(room_layout)

        # Allocate Room Button
        allocate_button = Button(text="Allocate Room", size_hint_y=None, height=50, font_size='18sp')
        allocate_button.bind(on_press=self.allocate_room)
        layout.add_widget(allocate_button)

        # Reallocate Room Button
        reallocate_button = Button(text="Reallocate Room", size_hint_y=None, height=50, font_size='18sp')
        reallocate_button.bind(on_press=self.reallocate_room)
        layout.add_widget(reallocate_button)

        # Report Button
        report_button = Button(text="Generate Room Report", size_hint_y=None, height=50, font_size='18sp')
        report_button.bind(on_press=self.show_report)
        layout.add_widget(report_button)

        # Dashboard Button
        dashboard_button = Button(text="Show Dashboard", size_hint_y=None, height=50, font_size='18sp')
        dashboard_button.bind(on_press=self.show_dashboard)
        layout.add_widget(dashboard_button)

        # Scrollable list for displaying room status
        self.room_list_view = RoomListView(size_hint=(1, 1), height=Window.height - 300)
        layout.add_widget(self.room_list_view)

        return layout

    def allocate_room(self, instance):
        student_name = self.name_input.text
        room_type = self.room_input.text
        if not student_name or not room_type:
            self.show_popup("Input Error", "Please enter both Student Name and Room Type.")
            return

        room = self.hostel.allocate_room(room_type)
        if room:
            self.show_popup("Room Allocated", f"Room {room.room_number} ({room.room_type}) allocated to {student_name}.")
        else:
            self.show_popup("No Room Available", "No rooms of the preferred type are available.")

    def reallocate_room(self, instance):
        student_name = self.name_input.text
        room_type = self.room_input.text
        if not student_name or not room_type:
            self.show_popup("Input Error", "Please enter both Student Name and Room Type.")
            return

        room = self.hostel.allocate_room(room_type)
        if room:
            self.show_popup("Room Reallocated", f"Room {room.room_number} ({room.room_type}) reallocated to {student_name}.")
        else:
            self.show_popup("No Room Available", "No rooms of the preferred type are available.")

    def show_report(self, instance):
        report = self.hostel.get_room_report()
        self.room_list_view.update_data(report)

    def show_dashboard(self, instance):
        dashboard = self.hostel.generate_dashboard()
        report = [
            {'Room Number': 'Total Rooms', 'Room Type': str(dashboard['Total Rooms']), 'Status': ''},
            {'Room Number': 'Occupied Rooms', 'Room Type': str(dashboard['Occupied Rooms']), 'Status': ''},
            {'Room Number': 'Empty Rooms', 'Room Type': str(dashboard['Empty Rooms']), 'Status': ''},
        ]
        self.room_list_view.update_data(report)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message, font_size='18sp'), size_hint=(0.6, 0.3))
        popup.open()

# Main Application
if __name__ == "__main__":
    HostelApp().run()
