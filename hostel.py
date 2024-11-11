import tkinter as tk
from tkinter import messagebox

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

    def reallocate_room(self, student, new_room_type):
        current_room = student.current_room
        current_room.deallocate()

        new_room = self.allocate_room(new_room_type)
        if new_room:
            student.current_room = new_room
            return new_room
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

# GUI Interface Using Tkinter
class HostelGUI:
    def __init__(self, root, hostel):
        self.root = root
        self.root.title("Hostel Management System")
        self.hostel = hostel
        self.student_name = ""
        self.current_room = None
        
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="Hostel Management System", font=("Arial", 20))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Student name input
        name_label = tk.Label(self.root, text="Student Name:")
        name_label.grid(row=1, column=0, padx=10)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=1, column=1)

        # Room Type selection
        room_label = tk.Label(self.root, text="Room Type (AC or NON-AC):")
        room_label.grid(row=2, column=0, padx=10)
        self.room_type_entry = tk.Entry(self.root)
        self.room_type_entry.grid(row=2, column=1)

        # Allocate Room Button
        allocate_button = tk.Button(self.root, text="Allocate Room", command=self.allocate_room)
        allocate_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Reallocate Room Button
        reallocate_button = tk.Button(self.root, text="Reallocate Room", command=self.reallocate_room)
        reallocate_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Report Button
        report_button = tk.Button(self.root, text="Generate Room Report", command=self.show_report)
        report_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Dashboard Button
        dashboard_button = tk.Button(self.root, text="Show Dashboard", command=self.show_dashboard)
        dashboard_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Listbox to display room status
        self.room_listbox = tk.Listbox(self.root, width=50, height=10)
        self.room_listbox.grid(row=7, column=0, columnspan=2, pady=10)

    def allocate_room(self):
        self.student_name = self.name_entry.get()
        room_type = self.room_type_entry.get()
        if not self.student_name or not room_type:
            messagebox.showerror("Input Error", "Please enter both Student Name and Room Type.")
            return

        room = self.hostel.allocate_room(room_type)
        if room:
            self.current_room = room
            messagebox.showinfo("Room Allocated", f"Room {room.room_number} ({room.room_type}) allocated to {self.student_name}.")
        else:
            messagebox.showwarning("No Room Available", "No rooms of the preferred type are available.")

    def reallocate_room(self):
        if not self.current_room:
            messagebox.showerror("No Allocation", "No room allocated yet. Please allocate a room first.")
            return

        new_room_type = self.room_type_entry.get()
        if not new_room_type:
            messagebox.showerror("Input Error", "Please enter a new room type.")
            return

        room = self.hostel.reallocate_room(self, new_room_type)
        if room:
            messagebox.showinfo("Room Reallocated", f"Reallocated to Room {room.room_number} ({room.room_type}).")
        else:
            messagebox.showwarning("No Room Available", "No rooms of the preferred type are available for reallocation.")

    def show_report(self):
        report = self.hostel.get_room_report()
        self.room_listbox.delete(0, tk.END)
        for entry in report:
            self.room_listbox.insert(tk.END, f"Room {entry['Room Number']} ({entry['Room Type']}) - {entry['Status']}")

    def show_dashboard(self):
        dashboard = self.hostel.generate_dashboard()
        self.room_listbox.delete(0, tk.END)
        self.room_listbox.insert(tk.END, f"Total Rooms: {dashboard['Total Rooms']}")
        self.room_listbox.insert(tk.END, f"Occupied Rooms: {dashboard['Occupied Rooms']}")
        self.room_listbox.insert(tk.END, f"Empty Rooms: {dashboard['Empty Rooms']}")

# Login Screen
class LoginScreen:
    def __init__(self, root, hostel, users):
        self.root = root
        self.hostel = hostel
        self.users = users
        self.root.title("Login / Create Account")
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="Login or Create Account", font=("Arial", 20))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Username input
        username_label = tk.Label(self.root, text="Username:")
        username_label.grid(row=1, column=0, padx=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=1, column=1)

        # Password input
        password_label = tk.Label(self.root, text="Password:")
        password_label.grid(row=2, column=0, padx=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=2, column=1)

        # Buttons
        login_button = tk.Button(self.root, text="Login", command=self.login)
        login_button.grid(row=3, column=0, pady=10)

        create_account_button = tk.Button(self.root, text="Create Account", command=self.create_account)
        create_account_button.grid(row=3, column=1, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if user exists and password matches
        if username in self.users and self.users[username] == password:
            self.root.destroy()  # Close the login window
            self.open_hostel_management()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Input Error", "Both username and password are required.")
            return

        if username in self.users:
            messagebox.showerror("Account Exists", "This username already exists. Please choose another one.")
            return

        # Create new account
        self.users[username] = password
        messagebox.showinfo("Account Created", f"Account created successfully for {username}. Please log in now.")
    
    def open_hostel_management(self):
        # Open the main hostel management window
        root = tk.Tk()
        hostel_gui = HostelGUI(root, self.hostel)
        root.mainloop()

# Main Application
def main():
    # Create Hostel with some data
    hostel = Hostel()

    building = Building("Building A")
    floor1 = Floor(1)
    floor2 = Floor(2)

    floor1.add_room(Room(101, "AC"))
    floor1.add_room(Room(102, "NON-AC"))
    floor2.add_room(Room(201, "AC"))
    floor2.add_room(Room(202, "NON-AC"))

    building.add_floor(floor1)
    building.add_floor(floor2)

    hostel.add_building(building)

    # Initialize users dictionary for login
    users = {}

    # Setup Login Screen
    root = tk.Tk()
    login_screen = LoginScreen(root, hostel, users)
    root.mainloop()

if __name__ == "__main__":
    main()
