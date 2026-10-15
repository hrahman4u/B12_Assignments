import pyautogui
import pyperclip
import time
import re
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

pyautogui.PAUSE = 1

now = datetime.now()

date_string = now.strftime("%Y-%m-%d")
time_string = now.strftime("%H:%M:%S")

excel_filename = f"daily_report_{date_string}.xlsx"
screenshot_filename = f"daily_report_{date_string}.png"

# Save files to the current folder
current_folder = os.getcwd()

excel_path = os.path.join(current_folder, excel_filename)
screenshot_path = os.path.join(current_folder, screenshot_filename)

print("Starting automated daily report...")
print("-----------------------------------")


# --------------------------------------------------
# STEP 1 - OPEN GOOGLE CHROME
# --------------------------------------------------

print("1. Opening Chrome...")

pyautogui.hotkey("win", "r")
time.sleep(1)

pyautogui.write("chrome", interval=0.05)
pyautogui.press("enter")

time.sleep(5)


# --------------------------------------------------
# STEP 2 - SEARCH FOR PERTH WEATHER
# --------------------------------------------------

print("2. Searching for Perth weather...")

pyautogui.hotkey("ctrl", "l")

pyautogui.write(
    "https://www.google.com/search?q=weather+Perth+Western+Australia",
    interval=0.01
)

pyautogui.press("enter")

time.sleep(6)


# --------------------------------------------------
# STEP 3 - COPY THE WEBPAGE TEXT
# --------------------------------------------------

print("3. Reading weather information...")

pyautogui.hotkey("ctrl", "a")
pyautogui.hotkey("ctrl", "c")

time.sleep(2)

page_text = pyperclip.paste()

print("Webpage text copied.")


# --------------------------------------------------
# STEP 4 - FIND TEMPERATURE
# --------------------------------------------------

print("4. Extracting temperature...")

# Look for values such as:
# 24°C
# 24 °C
# 24°
# 24 C

temperature_pattern = r"(-?\d{1,3})\s*°?\s*C"

temperatures = re.findall(
    temperature_pattern,
    page_text,
    re.IGNORECASE
)


if temperatures:

    # Use the first temperature found
    temperature = temperatures[0]

    fetched_data = f"{temperature}°C"

    print(f"Temperature found: {fetched_data}")

else:

    print("Could not automatically find the temperature.")

    # Backup value so the program doesn't crash
    fetched_data = "Temperature not detected"


# --------------------------------------------------
# STEP 5 - CREATE AUTOMATIC COMMENT
# --------------------------------------------------

if temperatures:

    temp_value = int(temperature)

    if temp_value >= 30:
        comment = "Hot day – stay hydrated."

    elif temp_value >= 20:
        comment = "Good conditions for outdoor activities."

    elif temp_value >= 10:
        comment = "Mild weather – suitable for outdoor activities."

    else:
        comment = "Cool weather – consider warmer clothing."

else:

    comment = "Weather information could not be automatically detected."


print(f"Comment: {comment}")


# --------------------------------------------------
# STEP 6 - OPEN MICROSOFT EXCEL
# --------------------------------------------------

print("5. Opening Microsoft Excel...")

pyautogui.hotkey("win", "r")

time.sleep(1)

pyautogui.write("excel", interval=0.05)

pyautogui.press("enter")

time.sleep(6)


# --------------------------------------------------
# STEP 7 - CREATE A NEW EXCEL WORKBOOK
# --------------------------------------------------

print("6. Creating Excel report...")

# Press Enter to select the default Blank Workbook
pyautogui.press("enter")

time.sleep(4)


# --------------------------------------------------
# STEP 8 - ENTER THE DATA
# --------------------------------------------------

# We use PyAutoGUI to enter the spreadsheet content.

# Header row

pyautogui.write("Date & Time")
pyautogui.press("tab")

pyautogui.write("Fetched Data")
pyautogui.press("tab")

pyautogui.write("Comment")

# Move to next row

pyautogui.press("home")
pyautogui.press("down")

# Date and time

pyautogui.write(
    f"{date_string} {time_string}"
)

pyautogui.press("tab")

# Weather data

pyautogui.write(fetched_data)

pyautogui.press("tab")

# Comment

pyautogui.write(comment)

time.sleep(2)



# --------------------------------------------------
# STEP 10 - SAVE EXCEL FILE
# --------------------------------------------------

print("8. Saving Excel file...")

pyautogui.hotkey("F12")  # Press F12 to open the Save As dialog

time.sleep(3)

# Type full path into Save As dialog
pyautogui.hotkey("ctrl", "a")

pyautogui.write(
    excel_path,
    interval=0.01
)

pyautogui.press("enter")

time.sleep(5)

# Handle possible format confirmation
pyautogui.press("enter")

time.sleep(3)


# --------------------------------------------------
# STEP 11 - TAKE SCREENSHOT
# --------------------------------------------------

print("9. Taking screenshot...")

# Make sure Excel is visible
#pyautogui.hotkey("alt", "tab")

#time.sleep(2)

screenshot = pyautogui.screenshot()

screenshot.save(screenshot_path)


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print("-----------------------------------")
print("AUTOMATION COMPLETED")
print("-----------------------------------")

print(f"Excel file:")
print(excel_path)

print()

print(f"Screenshot:")
print(screenshot_path)

print()

print(f"Date & Time: {date_string} {time_string}")
print(f"Fetched Data: {fetched_data}")
print(f"Comment: {comment}")