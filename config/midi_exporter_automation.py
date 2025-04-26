import pyautogui
import time
import json
from pynput import mouse, keyboard
from tkinter import Tk, Button, Label
import pyperclip

# ----------------------------------------------
# Global click capture until 'C' is pressed
# ----------------------------------------------
clicks = []
recording = False

def on_click(x, y, button, pressed):
    if recording and pressed:
        clicks.append((x, y))
        print(f"Recorded click at {(x, y)}")

# Keyboard handler to stop recording on 'c'
def on_key_press(key):
    global recording
    try:
        if key.char.lower() == 'c' and recording:
            recording = False
            print("'C' pressed: stopping click recording")
            return False
    except AttributeError:
        pass

# ----------------------------------------------
# GUI for calibrating multiple channel clicks
# ----------------------------------------------
class Calibrator:
    def __init__(self):
        self.root = Tk()
        self.root.title("FL Studio Channel Rack Calibrator")

        self.instructions = Label(
            self.root,
            text="Click 'Start Calibration' then click channel positions; press 'C' to end recording.")
        self.instructions.pack(pady=10)

        self.start_button = Button(self.root, text="Start Calibration", command=self.start_calibration)
        self.start_button.pack(pady=5)

        self.save_button = Button(self.root, text="Save Calibration", command=self.save, state="disabled")
        self.save_button.pack(pady=5)

        self.root.mainloop()

    def start_calibration(self):
        global recording
        self.instructions.config(text="Recording clicks in 2 seconds... Move to FL and prepare.")
        self.start_button.config(state="disabled")
        time.sleep(2)
        recording = True
        # start mouse listener
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()
        # listen keyboard
        with keyboard.Listener(on_press=on_key_press) as key_listener:
            key_listener.join()
        mouse_listener.stop()

        print(f"Collected {len(clicks)} channel positions")
        self.instructions.config(text=f"{len(clicks)} clicks recorded. Click 'Save Calibration'.")
        self.save_button.config(state="normal")

    def save(self):
        if not clicks:
            print("Error: No clicks recorded.")
            return
        cal_data = {'channels': clicks}
        with open('calibration.json', 'w') as f:
            json.dump(cal_data, f)
        print("Calibration saved to calibration.json")
        self.root.destroy()

# ----------------------------------------------
# Export selected channels using GUI actions
# ----------------------------------------------
def load_calibration():
    with open('calibration.json', 'r') as f:
        return json.load(f)

def export_clicked_channels(cal, export_path):
    for idx, (cx, cy) in enumerate(cal['channels']):
        # Focus channel
        pyautogui.moveTo(cx, cy)
        pyautogui.click(button='left')
        time.sleep(3)

        # Close the sampler popup
        pyautogui.press('escape')
        time.sleep(1)

        # Right-click to open context menu
        pyautogui.click(button='right')
        time.sleep(1)
        # Navigate to 'Rename, color and icon...' option (3 downs)
        pyautogui.press('down', presses=3, interval=0.1)
        pyautogui.press('enter')
        time.sleep(1)
        # Copy channel name
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)
        name = pyperclip.paste().strip()
        # Close rename dialog
        pyautogui.press('escape')
        time.sleep(1)
        if not name:
            print(f"Skipping channel at {(cx, cy)}: name copy failed")
            continue
        safe = name.replace(' ', '_')
        print(f"Exporting channel '{name}' as {safe}.mid")

        # Open Piano Roll
        pyautogui.hotkey('fn', 'f7')
        time.sleep(1)
        # Open Save MIDI dialog
        pyautogui.hotkey('shift', 'ctrl', 'm')
        time.sleep(2)
        # Type filename and save
        pyautogui.write(f"{safe}.mid")
        pyautogui.press('enter')
        time.sleep(1)
        # Return to Channel Rack
        pyautogui.hotkey('fn', 'f6')
        time.sleep(1)

# ----------------------------------------------
# Main Execution
# ----------------------------------------------
def main():
    # Launch calibrator GUI
    Calibrator()
    # Load recorded channel coords
    cal = load_calibration()
    # Ask user for export folder
    export_path = pyautogui.prompt(text='Enter export folder path', title='Export Path', default='C:/MidiExports')
    # Export only clicked channels
    export_clicked_channels(cal, export_path)
    print("All selected channels exported. Exiting.")

if __name__ == '__main__':
    main()
