import sys
sys.path.append("..") # added!

from api.client import APIClient
from app_config import AppConfig
from config import Configuration
from manager.mod import ModManager
from manager.file import FileManager
from manager.profile import ProfileManager
from text_stripper import TextStripper

import PySimpleGUI as sg

WWINDOW_SIZE_X = 1400
WINDOW_SIZE_Y  = 600


class App:
    #todo: add theme functionality?
    #todo: move panel logic to subclasses for easier access to specific elements.

    def __init__(self, cfg: Configuration, api: APIClient, mod_manager: ModManager, profile_manager: ProfileManager, file_manager: FileManager):
        self.cfg = cfg
        self.api = api
        self.mod_manager = mod_manager
        self.profile_manager = profile_manager
        self.file_manager = file_manager
        
        #todo: perform initialisation/load for mod_manager and profile_manager
        self.mod_manager.update_cache()

        # SG specific objects
        self.window: sg.Window = None
        self.mods_panel = []
        self.modinfo_panel = []
        self.profile_panel = []

    def run(self):
        self.make_window()
        while True:
            #todo: find a cleaner way to read and dispatch events
            event, values = self.window.read() # capture the key of the event emitter and the value sent.
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                break
            if event == "-MOD_TABLE-":
                mod_row = values["-MOD_TABLE-"][0]
                selected_mod_id = self.mod_manager.mod_cache.mods[mod_row].modid
                self.update_modinfo_panel(selected_mod_id)

    def make_window(self):
        """ Create the sg.Window object to render the App to screen. """
        theme = sg.user_settings_get_entry('-theme-')
        sg.theme(theme)
        # three column layout, center-top aligned
        three_column_layout = [[
            sg.vtop(sg.Column(self.make_mods_panel_layout(), element_justification="c")),
            sg.vtop(sg.Column(self.make_modinfo_panel_layout(), element_justification="c")),
            sg.vtop(sg.Column(self.make_profile_panel_layout(), element_justification="c")),
        ]]
        self.window = sg.Window(f"Vintage Story Mod Manager - {self.cfg.app.version}", layout=three_column_layout, size=(WWINDOW_SIZE_X, WINDOW_SIZE_Y), finalize=True)
        return self.window

    def make_mods_panel_layout(self):
        """ Builds the mods browser table layout and returns it. Also stores a reference on the app object to this layout."""
        table_headings = ["Mod Name", "Author", "Version", "Tags", "Last Updated"]
        self.mods_panel = [[
            sg.Table(
                values=[[mod.name, mod.author, "1", ", ".join(mod.tags),  mod.lastreleased] for mod in self.mod_manager.mod_cache.mods], headings=table_headings,
                auto_size_columns=True,
                display_row_numbers=False,
                justification='center',
                num_rows=30,
                alternating_row_color='lightblue',
                key='-MOD_TABLE-',
                selected_row_colors='red on yellow',
                enable_events=True,
                expand_x=True,
                expand_y=False,
                vertical_scroll_only=False,
                enable_click_events=True,           # Comment out to not enable header and other clicks
                tooltip=f"Cache Last Updated: {self.mod_manager.mod_cache.last_updated}",
                pad=(10,10)
        )]]
        return self.mods_panel

    def make_modinfo_panel_layout(self):
        """ Builds the mod info panel layout and returns it. Also stores a reference on the app object to this layout."""
        self.modinfo_panel= [
            [sg.Text("Mod Name", font="Any 16")],
            [sg.Text("Author"), sg.Text("Tags")],
            [sg.Text("Last Updated: ", justification="center")],
            [sg.HorizontalSeparator()],
            [sg.Text("Mod Information", size=(50, 30), expand_x=False)],
        ]
        return self.modinfo_panel

    def make_profile_panel_layout(self):
        """ Builds the profile selector layout and returns it. Also stores a reference on the app object to this layout."""
        self.profile_panel = [
            [sg.Text('Profiles', font='Any 20')],
            [sg.Combo([profile.name for profile in self.profile_manager.profiles], size=(60,10), readonly=True, enable_events=True)],
            [sg.Listbox(values=["Mod A", "Mod B", "Mod C"], select_mode=sg.SELECT_MODE_EXTENDED, size=(40, 20), key='-PROFILE_MOD_LIST-')],
            [sg.Button('Deploy Profile', key='Run Git Version'), sg.Button('Purge profile', key='Run Git Version'), sg.Button('Check for Mod Updates', key='Run Git Version')],
        ]
        return self.profile_panel

    def update_mods_panel(self):
        pass

    def update_modinfo_panel(self, mod_id: int):
        """ Fetch the detailed mod info from the ModDB and populate the modinfo panel elements. """
        mod_info = self.mod_manager.get_mod_info(mod_id)
        # This index logic sucks ;_;
        self.modinfo_panel[0][0].update(mod_info.name)
        self.modinfo_panel[1][0].update(mod_info.author)
        self.modinfo_panel[1][1].update(", ".join(mod_info.tags))
        self.modinfo_panel[2][0].update(f"Last Updated: Time is Relative")
        self.modinfo_panel[4][0].update(self._strip_html_from_text(mod_info.text))

    def update_profile_panel(self):
        pass


    def _strip_html_from_text(self, html_text):
        """ Returns a clean version of html_text with any HTML tags stripped from the content. """
        text_stripper = TextStripper() #todo: this is not IoC, move this to dependency injection
        text_stripper.feed(html_text)
        return text_stripper.get_data()



if __name__ == '__main__':
    icon = b'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAMAUExURQAAAB69LymqOSm6LSq2OTSrOjS2Ox28RjqdQC6qSiy3Riu3UTisRzirVDi1STq0UiuyYz6pYz62ZCjDNyjQPzTAOxrIQinARTXDRzXBVEWsP1ieZ0OrSUaqV0S0SkOzVFKnSVKrWlK0W0iqZUWmcEe0a1eoZ1apclW0Z1uzd2G8X2W8Z2i3dXStdnS/ZHW7dkXCTEnCWVnDbF3Gc1zUc2bGbGjId2fRbWjQfnLFbnTGeHfReXu6hWzFgWzRgXfGhn3Jk3bShHvWkd5HPNhYJ9RWPtRbPdxVOtlbM9xdPM5iPNRjO9VsMtNoOttiPOFVNOVUPeNZNOJbPelVPelZN+pcO/ZYPeNjPeFqPOlgNOpiPfBkO8xcR85ZUtZOUNJXQdNcQtNcTNpTRdxVT9xdQ95cSdlbUsBgR8xkRctkTc1oQ81pS8tmVMtxTsx3XtVjQdRjStRoQtNqStxiRNtjSdxpQ9toS9NkU9diWdFqUtVsW9xiU9xlXN5uVtZzWsptZ8Z3Y8p2ddBuY9duat1qY9Nvcdh3Z+VOQ+NUROJcQ+NcSutTROlcQ+pdSuhdVPJcQ/FbS/heQvZbVuFhReJjSeJpRORpTOpiRepiS+toTeVlU/RhRfJhUuZnYeBvaeR4aoPCfN+Hb9eHfNmQfeaIbOKIeOWSefaHbP+Ia/CMffCSePigeoTHhovJmIjWiYXXl5HMnpbYmY3bp4fes5PHoJnapJzUspDhnozjpo3lspnjqaLTm6HOsaPYp7XOuLbduajkqavpuLTpt7f2uKvbwbLYw7nmx7f1ybjw1tqIhtiThtiSkNasnNuimeSLhOWPkOWThuicl/mdiPKbku6fouWjl+Oinuaom+ynl+yjmuqpl+qqm/OllfOlmPSqnf6mkvqhneekoPOho8buuNPtvtbd08bpyMro1cT2ysj109XozNXo2NHzydT52M/45tvs4tj8497+8eD6y+b82+bq6Of+5+n+9fnq7f/p//b96fv7+gAAAAAAAAAAAAAAAAAAAFSfM6AAAAEAdFJOU////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wBT9wclAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAMlUlEQVR4Xu2Zf5gbRRnHtd5Fm+Z2FUQOuWQplXI+oAVqA0RrAKUlRGINlkCpei2b2EI1187eFUitBfFgc0nah5m7pFsFnvJD1FIseoDFk1/agj+wpz5gBX8geu31ODmtqb39J76zO5vb/Lzsnjw8Pt7nLpfZmcnMd99533dmc28rvMXMCJgRMCNgRsCMgP9tAQdv23jDTYm72JU9piPg5U29W8OB1O2Jl1mFHaYh4I+dS7NAbkeg8yCrsoF9AS9Ge6++Ik6k4BV9qVW/ZJXWsS3gwf4ORDAWZYQwRsqDrNoydgUc7EcwP8KEEEyQiJQh1mAVmwJeIaKI+5EoUiMggpbYVmBPwFDmk0QiWBaxjCmEoCsz9hTYE/D8J65FGIl0AegawGqQCE7YigWbS9DTK4LvYSwDhMjgiShIEnZsYNcJt9DVJ7Iowy8toQ4cxHZWwa6AAiEwM5HJdpm6AZGVDhTptaHAsoDvdr6gF76WvDqckqT1KJ3GCsnIEJNItJ4PrAoYikc3MgWbU6l+HN+AUql0HEFM2MsHFgUMZe7oiq86oF8kRImaPxtAUpdoNx9YEzCUuTIb6pNjTMHdq6Srli3PdgWxGKYxYScfWBJwMIEjIo5Eigq23JpQYitFBefAIe3lAysChhIkiNbnwsFcb2wnqwNe+OYd27YHtZiwkQ8sCBjKQKh3EEgAKEfE+1kt5bZLUdBuPmhcAKx/BHUoadKZjl8euqqXxYLG5kDKbj5oWMCDCpJgkfXNB0DdzA8oQ6uWs2rYnazlg0YFHFRg/4WtH8ysE+k03+W6LKuGPtbyQYMChjIQ4jAwmwWIJFiTxrrPsGrAWj5oTMBQZhlE2KT9gbDC2jTWrWDVOhbyQUMCaPzDmHTg4hKsSJh8oPDFHaxa62IlHzQiQIt/8D8RIr24CFev7mHNlJ1LWTWcUq3lgwYE6PFPj8B0/2fzYBRWzHe4k1XDMc1aPphaAIt/6t5wANquT4Px+juvW/cL1oXCqrHVfDClgPL4N5C7URabHbFn2aeuIElCokQM9IVCjeaDqQRUxL9BshulkC7g59rfQo8clrDYHQV3JXJOWwfIBy/qjTWZQkBl/BtQAYGM1unzLCsr35ACkQDuT8o5lDTyQWyKWKgvoEr8GyQlJDMLpAMPaO+Fu1cjyAeREJyUQQAAnw1M4Qd1BVSLfwMQkEW6BQgWmQ16yO04EMDZPv0jNB9k5cyf9cbq1BNQNf4NTALi6zsUtjt//bb77t+8ZmUoGzGeF3Aonam3CnUEVI9/gzQIwDGtI5yIyRLT+eD3PWtzESMfxHFIrqegtoAa8W8AFkihpNYzc6ccQoj5gcatX8ixfICVDrxi6aZXWUMltQWsJTiQow5QHSogpDthDCOZSOG7tQudjctYN+oHoXB6HauvpKaAAxIOk2SySgDqUAGi7gMgACfl7E3ahU5P0WkDSrQT51aad64Sagq4T1ke6I/KXWycCkwWiFILxFMbtQude4sCLsMdUnarYl6gEmoK+Bb+LFZWYwio6pRbAKVu1i50Xs6wbhi2ZUW+UrmPNVRQewlW5rCUISE2TgXlPkBKLHBAT0QUInXKOyTTMb6U2k741Y4QrGxdAcwCsAQ4SSKSdqGzJcW6YZF0hLaLNpyw8Oq6uCLKEhungnILJHHQdFDvLJ6S+5OQETt/xuorqS2g8OsglqW6YWj2gUwwtFa7otwiX8O6YVHJ9V1mfoopo46Awkubomh9hohyFpSw8YpsI2l5m54JaVsXkZcH2aPCq3clk8slSJ5hTDKhPvG62vdfX0Dhd4qMRAnSKaR1fdpJkiulZE4/mivhAF6jkO1Y7Nxyy/M7e2IdEgqI/ShAd9K+pck69z+FgMIfEtGuOJIkiRQfPAy2r4FjSlTrpYQiWAK3z0L+l3KpZSmC+7owkrrhZIrE5Le1TrWoL6Bw8MYuFCaK1FEhAF8vhkTdAgmEIQzBEXB2WzoUwtlsYAnCS7qJiLPBWN37n1JA4SVRTOeIJOlfQJgIdy3LYj37dorgI1ERRTBOydev6QbL00dERFLp3BLzM2w1phJQeGXTdWkR9VfsCcuVVA6t1LpsRCRL4BCIYE/syyiZKEReQIaDVHq18U1GbaYUUPgLxEJQqjgShVFauuF5rcdmMLgIpodlJyiZThMZToMEB7O52K+0DvWYWkDhFQShVMztDEKWJNd+R+/wpw3BnNSH5VQ6mU6GgigudUpSBuHgpVPef0MCCi/dGEXx8nwgEXHytPm5yRUyx38D8zckAB4O5K7yfCAFvsJagQMKOKCOHv94yvg3aEhAtXwgyeYt3pSytfiPTxn/Bo0JqJIPxCxr0ohN+miD8W/QoIDKfIAwa9FITApoMP4NGhVQkQ9KlyBWPDc0Gv8GDQsozwdlTlgU0Gj8GzQuoDQfEClpCsMYKgpoNP4NLAgoyQeQ8ZKJ37CGHoR30PiHJ6SG49/AioCSfBDNKdKaL9P/Gj/wJXj8Ehvd/8uxJMCcD4gcwKHLN2zevGEJPA/T3bix/b8cawIm80GOJAOhvh2pT4evyV67IhtbZTX+DSwKmMwHYl9/JCTnMjtwOEzShH6PZCn+DawKKOYDWHG0KpNIikQhSTEZtRr/BpYFsHyQw7DaBCFFkkQp0Y0b3v/LsS6A5QPweJqTLotA6qH/wbca/wY2BJjyQZZ+JwunIxvxb2BHQEk+sBv/BrYElJwPbMa/gT0B5vOBzfg3sCnAdD6wGf8GdgUU84Hd+DewLcDIB3bj38C+AJYP7Ma/wTQEFH4b690aiGztjekPSPaYjoBC4eZVG+IdJf+9ssz0BBSG7j1Q7+uPBpimgOkzI2BGQImAh73nn+8tY5Fvkdd7wUKvz/txr+/CC+FCw+f1ng0vL231ehdfAB3Pp8VF3sWL4c3vXeyj0MZSYIaH2XQaJQL8QhsnlMFxLsHj4Tw80CLwPMdxHnhxTs4jcHyL2wll3tPscXk8LqEF+ntc9JdzOPjZTsHhYMMU4doEP5tOo0TAYkEbuwQXTOxqc0AJpuLhh9JChTiaoOSgwrQ6AEq0ThvE4YB7gTdaLqFNWMym0ygVUBzKBM/PFjjnO13nQNnZdBLM4eTaPJyg9aUi4HbBFHAJE7dyc06mNmmdRaWCJaqMyNcW4K3S/cQmQXC74ZadszgouN2Cxymc5mlqAYucMc/dJrgFV5PDBU1t0LvZ4+ahyDmEecJsnhecc/RRzPBeNp1G2RKwPiYcc8fUibz6xm63sDevqsfU/J75+/PP8tw5Dvdheq3m/R6P++nxkYdcrZx7178njqrj/vb9+bzWVGXEehbQzFkKf6qqTTMx6B5Uj6vHjk0MnnlIHZ3XxjlOOwLV0Oh38WdDj8PgkP788Xweak4dh09B6y43G2YSF2fNAie6J/KD7vmH1fF5e/MT83l3WzO/f2LYPc95srD/2PB8iA9nEzcA2vJnc/yAOt4+68xLzm1+Vh0+gwdPrHRCrp4Tsi5mmk5Q1YEmflA96h5QJ57a8+MnOO6weph6+5wx9Y3BJ/bsbjq5Pa/u/qe6r4Xfo6rPPdIuNHP71fzgnj2XtOiDlFJvCSppFVR1n29XXh2b931qVDUvtIweP3S6p03gh1X1qKrud7seUtUzBo6NtzvOep1a/u8XtYzQd3V4LhvFTD0nrBIFnGsCXABeu8DO6o8ef+Sx2cKwut8J0XbuX8EjB/ZeLLSPqf969Kequod7+9yPPgOaxk4/oh4dHHjsYqGVjWLGmgU4N0w+qh7f+y7uqYmJ+e92z+U8r02M8Kfwguv1/PD893t41wJwxQl4jfG8r7Vl/k/Uo57X1H3t1KOr+IBFC7h4uO9Tn1bzC1oeUdW/jY2O7n0PhN+hI6PPfeAQVBwZHfnek2r+0cG9T6rqxx7Kjxza9w9YLliC0dE3RnZXplbLFjhh/NjjzoV59Zn2H0ISgFTw3DwQQJ3hg8MQfBCG+8YgTubwwkh+5Ac0/PIj/pZxrSk/UBmGVi3AO3f5z3POavf7uHb/eR+h+5/rrHv8sEv6mj/s8y280OdfeLHvdAfPzfL6/e6WBf57zmrnuA9dBDvjIt/CamFg0QLcaS4IaG4O5Hm4nTanm3vvO2g1z78P/nBNsA3wbtdJbo/DyTWf4/TQPaup1e1pbj1lDl8tD9SxwALYjenuVgL9iPZTpaC/0T56P72kNU320kYx4GA/XsCm0ygR4OOc7KNvHryT87HpNMoEwFb7JgN5u7aAXYKncgn+y8AUu9h0GiUCCoODA286g4NsMp1SAW8BMwJmBMwImBHw/y6gUPgPnMncyEC8DLMAAAAASUVORK5CYII='
    
    api_client = APIClient(AppConfig)
    file_manager = FileManager(AppConfig)
    mod_manager = ModManager(AppConfig, api_client, file_manager)
    profile_manager = ProfileManager(AppConfig, api_client, mod_manager, file_manager)

    app = App(AppConfig, api_client, mod_manager, profile_manager, file_manager)
    app.run()