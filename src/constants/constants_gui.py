import customtkinter as ctk
import ast
import numpy as np

# Import your constants (make sure constants.py is in the same directory)
import constants


def format_literal(val):
    """
    Recursively formats a Python literal as a string.
    For NumPy arrays, returns 'np.array([...])'.
    """
    if isinstance(val, np.ndarray):
        # Convert the array to a list and then format it recursively.
        return f"np.array({format_literal(val.tolist())})"
    elif isinstance(val, list):
        return "[" + ", ".join(format_literal(item) for item in val) + "]"
    elif isinstance(val, dict):
        items = []
        for key, value in val.items():
            items.append(f"{format_literal(key)}: {format_literal(value)}")
        return "{" + ", ".join(items) + "}"
    else:
        return repr(val)


class ConstantsEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Constants Editor")
        self.geometry("800x600")

        # Create a tab view with a tab for each constants class
        self.tabview = ctk.CTkTabview(self, width=780, height=500)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        # Create tabs for each group
        self.tabs = {}
        for tab in [
            "Constants",
            "NetworkTableConstants",
            "ObjectDetectionConstants",
            "DisplayConstants",
            "CameraConstants",
        ]:
            self.tabview.add(tab)
            self.tabs[tab] = self.tabview.tab(tab)

        # Create a dict to store widget references
        self.widgets = {}

        # Create the widgets for each constants group
        self.create_constants_tab()
        self.create_network_table_tab()
        self.create_object_detection_tab()
        self.create_display_tab()
        self.create_camera_tab()

        # Save button to write changes back to constants.py
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_constants)
        self.save_button.pack(pady=(0, 10))

    def create_constants_tab(self):
        frame = self.tabs["Constants"]
        self.widgets["Constants"] = {}
        row = 0
        # Edit booleans: log, print_terminal, detection_logging
        for field in ["log", "print_terminal", "detection_logging"]:
            value = getattr(constants.Constants, field)
            label = ctk.CTkLabel(frame, text=field)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            # Using a checkbox for booleans
            var = ctk.BooleanVar(value=value)
            checkbox = ctk.CTkCheckBox(frame, variable=var, text="")
            checkbox.var = var  # keep a reference for later retrieval
            checkbox.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.widgets["Constants"][field] = checkbox
            row += 1

    def create_network_table_tab(self):
        frame = self.tabs["NetworkTableConstants"]
        self.widgets["NetworkTableConstants"] = {}
        row = 0
        # Edit strings: server_address, robot_position_key, robot_rotation_key
        for field in ["server_address", "robot_position_key", "robot_rotation_key"]:
            value = getattr(constants.NetworkTableConstants, field)
            label = ctk.CTkLabel(frame, text=field)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(frame)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.widgets["NetworkTableConstants"][field] = entry
            row += 1

    def create_object_detection_tab(self):
        frame = self.tabs["ObjectDetectionConstants"]
        self.widgets["ObjectDetectionConstants"] = {}
        row = 0
        # Edit input_size (int)
        field = "input_size"
        value = getattr(constants.ObjectDetectionConstants, field)
        label = ctk.CTkLabel(frame, text=field)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(value))
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        self.widgets["ObjectDetectionConstants"][field] = entry
        row += 1

        # Edit confidence_threshold (float)
        field = "confidence_threshold"
        value = getattr(constants.ObjectDetectionConstants, field)
        label = ctk.CTkLabel(frame, text=field)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(value))
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        self.widgets["ObjectDetectionConstants"][field] = entry
        row += 1

        # Edit note_combined_threshold (int)
        field = "note_combined_threshold"
        value = getattr(constants.ObjectDetectionConstants, field)
        label = ctk.CTkLabel(frame, text=field)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(value))
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        self.widgets["ObjectDetectionConstants"][field] = entry

    def create_display_tab(self):
        frame = self.tabs["DisplayConstants"]
        self.widgets["DisplayConstants"] = {}
        row = 0
        # Edit run_web_server (bool)
        field = "run_web_server"
        value = getattr(constants.DisplayConstants, field)
        label = ctk.CTkLabel(frame, text=field)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        var = ctk.BooleanVar(value=value)
        checkbox = ctk.CTkCheckBox(frame, variable=var, text="")
        checkbox.var = var
        checkbox.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        self.widgets["DisplayConstants"][field] = checkbox

    def create_camera_tab(self):
        frame = self.tabs["CameraConstants"]
        self.widgets["CameraConstants"] = {}
        row = 0
        # Edit camera_list (list of dictionaries)
        field = "camera_list"
        value = getattr(constants.CameraConstants, field)
        label = ctk.CTkLabel(frame, text=field)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="nw")
        textbox = ctk.CTkTextbox(frame, width=600, height=200)
        # Insert the Python literal representation into the textbox
        textbox.insert("0.0", repr(value))
        textbox.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        self.widgets["CameraConstants"][field] = textbox

    def save_constants(self):
        """
        Collects the data from all widgets and writes a new constants.py file.
        Uses format_literal() to ensure NumPy arrays are saved as np.array([...]).
        (The formatting is fixed; comments from the original file are not preserved.)
        """
        lines = []
        lines.append("import numpy as np")
        lines.append("array = np.array")
        lines.append("")

        # --- Constants ---
        lines.append("class Constants:")
        for field in ["log", "print_terminal", "detection_logging"]:
            widget = self.widgets["Constants"][field]
            val = widget.var.get()  # get the boolean value
            lines.append(f"    {field} = {format_literal(val)}")
        lines.append("")

        # --- NetworkTableConstants ---
        lines.append("class NetworkTableConstants:")
        for field in ["server_address", "robot_position_key", "robot_rotation_key"]:
            entry = self.widgets["NetworkTableConstants"][field]
            val = entry.get()
            # Use format_literal to ensure the string is properly quoted.
            lines.append(f"    {field} = {format_literal(val)}")
        lines.append("")

        # --- ObjectDetectionConstants ---
        lines.append("class ObjectDetectionConstants:")
        # input_size (int)
        entry = self.widgets["ObjectDetectionConstants"]["input_size"]
        try:
            input_size = int(entry.get())
        except ValueError:
            input_size = entry.get()
        lines.append(f"    input_size = {format_literal(input_size)}")
        # confidence_threshold (float)
        entry = self.widgets["ObjectDetectionConstants"]["confidence_threshold"]
        try:
            confidence_threshold = float(entry.get())
        except ValueError:
            confidence_threshold = entry.get()
        lines.append(f"    confidence_threshold = {format_literal(confidence_threshold)}")
        # note_combined_threshold (int)
        entry = self.widgets["ObjectDetectionConstants"]["note_combined_threshold"]
        try:
            note_combined_threshold = int(entry.get())
        except ValueError:
            note_combined_threshold = entry.get()
        lines.append(f"    note_combined_threshold = {format_literal(note_combined_threshold)}")
        lines.append("")

        # --- DisplayConstants ---
        lines.append("class DisplayConstants:")
        widget = self.widgets["DisplayConstants"]["run_web_server"]
        val = widget.var.get()
        lines.append(f"    run_web_server = {format_literal(val)}")
        lines.append("")

        # --- CameraConstants ---
        lines.append("class CameraConstants:")
        textbox = self.widgets["CameraConstants"]["camera_list"]
        text_value = textbox.get("0.0", "end").strip()
        # Try to safely evaluate the text so we store a proper Python literal
        try:
            camera_list = ast.literal_eval(text_value)
            lines.append(f"    camera_list = {format_literal(camera_list)}")
        except Exception as e:
            # If there is an error in the input, save the raw text
            lines.append(f"    camera_list = {text_value}")
        lines.append("")

        # Write all lines to constants.py
        try:
            with open("constants.py", "w") as f:
                f.write("\n".join(lines))
            print("Constants saved to constants.py")
        except Exception as e:
            print("Error writing to constants.py:", e)


if __name__ == "__main__":
    # Optionally set appearance and theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    app = ConstantsEditor()
    app.mainloop()
