#import sys # added!
#sys.path.append("..") # added!

from api.client import APIClient
from app_config import AppConfig
from manager.mod import ModManager
from manager.file import FileManager
from manager.profile import ProfileManager
import tkinter
import customtkinter

# client = APIClient(AppConfig)
# file_manager = FileManager(AppConfig)

# mod_manager = ModManager(AppConfig, client, file_manager)

# mod_manager.update_cache()
# profile_manager = ProfileManager(AppConfig, client, mod_manager, file_manager)
# profile_manager.add_mod_to_profile("Default", 219, "1.0.2-rc.1")
# # profile_manager.remove_mod_from_profile("Default", 219, "1.0.2-rc.1")
# profile_manager.deploy_profile("Default")
# profile_manager.undeploy_profile("Default")



customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("400x240")

def button_function():
    print("button pressed")

# Use CTkButton instead of tkinter Button
button = customtkinter.CTkButton(master=app, text="Im a mod manager", command=button_function)
button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

app.mainloop()