import ast
import numpy as np
import constants  # Make sure constants.py is in the same directory

# Define the groups and their fields.
GROUPS = {
    "Constants": ["log", "print_terminal", "detection_logging"],
    "NetworkTableConstants": ["server_address", "robot_position_key", "robot_rotation_key"],
    "ObjectDetectionConstants": ["input_size", "confidence_threshold", "note_combined_threshold"],
    "DisplayConstants": ["run_web_server"],
    "CameraConstants": ["camera_list"]
}


def format_literal(val):
    """
    Recursively formats a Python literal as a string.
    For NumPy arrays, it returns 'np.array([...])'.
    """
    if isinstance(val, np.ndarray):
        # Convert the array to a list and then format it recursively.
        return f"np.array({format_literal(val.tolist())})"
    elif isinstance(val, list):
        return "[" + ", ".join(format_literal(item) for item in val) + "]"
    elif isinstance(val, dict):
        items = []
        for key, value in val.items():
            # Assume keys are strings or other literals.
            items.append(f"{format_literal(key)}: {format_literal(value)}")
        return "{" + ", ".join(items) + "}"
    else:
        # For other types (str, int, bool, etc.), use repr.
        return repr(val)


def convert_input(current_value, new_input):
    """
    Convert the input string to the same type as current_value.
    If conversion fails, returns None.
    """
    if isinstance(current_value, bool):
        # Interpret various boolean inputs.
        if new_input.lower() in ['true', 't', '1']:
            return True
        elif new_input.lower() in ['false', 'f', '0']:
            return False
        else:
            print("Invalid boolean input.")
            return None
    elif isinstance(current_value, int):
        try:
            return int(new_input)
        except ValueError:
            print("Invalid integer.")
            return None
    elif isinstance(current_value, float):
        try:
            return float(new_input)
        except ValueError:
            print("Invalid float.")
            return None
    elif isinstance(current_value, str):
        return new_input
    elif isinstance(current_value, (list, dict)):
        try:
            return ast.literal_eval(new_input)
        except Exception as e:
            print("Error parsing list/dict:", e)
            return None
    elif isinstance(current_value, np.ndarray):
        try:
            parsed = ast.literal_eval(new_input)
            return np.array(parsed)
        except Exception as e:
            print("Error parsing numpy array:", e)
            return None
    else:
        # Fallback: try literal_eval
        try:
            return ast.literal_eval(new_input)
        except Exception as e:
            print("Error parsing input:", e)
            return None


def get_current_constants():
    """
    Build a dictionary holding the current values from the constants module.
    """
    current = {}
    for group, fields in GROUPS.items():
        current[group] = {}
        group_cls = getattr(constants, group)
        for field in fields:
            current[group][field] = getattr(group_cls, field)
    return current


def edit_field(group, field, current_value):
    """
    Prompt the user to enter a new value for the given field.
    If the user enters nothing, the original value is kept.
    Returns the updated (or original) value.
    """
    print(f"\nEditing {group}.{field}")
    print(f"Current value: {current_value}")
    new_input = input("Enter new value (or press Enter to keep current): ").strip()
    if new_input == "":
        return current_value

    new_value = convert_input(current_value, new_input)
    if new_value is None:
        print("Keeping original value.")
        return current_value
    else:
        return new_value


def save_constants(updated):
    """
    Writes the updated constants to constants.py.
    Uses `format_literal` to ensure NumPy arrays are saved as np.array([...]).
    (This version does not preserve original comments.)
    """
    lines = []
    lines.append("import numpy as np")
    lines.append("array = np.array")
    lines.append("")
    for group, fields in GROUPS.items():
        lines.append(f"class {group}:")
        for field in fields:
            val = updated[group][field]
            # Use format_literal to convert the value to a proper Python literal string.
            line_val = format_literal(val)
            lines.append(f"    {field} = {line_val}")
        lines.append("")
    try:
        with open("constants.py", "w") as f:
            f.write("\n".join(lines))
        print("\nconstants.py has been updated successfully.")
    except Exception as e:
        print("Error writing to constants.py:", e)


def show_tree_menu(updated):
    """
    Display the tree menu to choose which group and field to edit.
    """
    while True:
        print("\n=== Constants Editor Menu ===")
        print("Groups:")
        groups_list = list(GROUPS.keys())
        for i, group in enumerate(groups_list, 1):
            print(f"  {i}. {group}")
        print("  s. Save changes and exit")
        print("  q. Quit without saving")
        choice = input("Select a group (number) or action: ").strip().lower()

        if choice == "q":
            print("Exiting without saving changes.")
            return False  # indicate no save
        elif choice == "s":
            # Save and exit
            save_constants(updated)
            return True
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(groups_list):
                    group = groups_list[idx]
                    edit_group(updated, group)
                else:
                    print("Invalid group number.")
            except ValueError:
                print("Please enter a valid number, 's' to save, or 'q' to quit.")


def edit_group(updated, group):
    """
    Displays the fields for the given group and lets the user choose one to edit.
    """
    fields = GROUPS[group]
    while True:
        print(f"\n--- Editing Group: {group} ---")
        for i, field in enumerate(fields, 1):
            print(f"  {i}. {field} (current: {updated[group][field]})")
        print("  b. Back to main menu")
        choice = input("Select a field to edit (number) or 'b' to go back: ").strip().lower()
        if choice == "b":
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(fields):
                    field = fields[idx]
                    curr_val = updated[group][field]
                    new_val = edit_field(group, field, curr_val)
                    updated[group][field] = new_val
                else:
                    print("Invalid field number.")
            except ValueError:
                print("Please enter a valid number or 'b'.")


def main():
    print("=== Terminal Constants Editor ===")
    updated = get_current_constants()
    saved = show_tree_menu(updated)
    if not saved:
        print("No changes were saved.")


if __name__ == "__main__":
    main()
