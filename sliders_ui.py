# To run, install python 3
# > pip install nicegui
# > python sliders_ui.py

import math
from nicegui import ui   # pip install nicegui


def to_float(value):
    try:
        return float(value)
    except:
        return float(0) # 0 if any error

def to_string_db(value):
    return ("+" if value > 0 else "") + "{:.0f} dB".format(to_float(value)) # Format in dB with no decimals

def clip(value, min, max):
    if value < min:
        value = min
    if value > max:
        value = max
    return value

class Settings:
    def __init__(self):
        # These 2 values mimic the hardware persistent settings, UI values are computed from them
        self._intensity = 0
        self._spectrum = 0
        # Helper settings
        self.INTENSITY_RANGE = [-30, 0]     # Hardware can go down to -30dB but UI should stay above -20dB
        self.SPECTRUM_RANGE = [-20, +20]
        self.MOVEMENT_RANGE = [-20, 0]
        self.VIBRATION_RANGE = [-20, 0]
        self.set_logger(None)

    def set_logger(self, callback):
        self._logger = callback

    def log(self, text):
        if self._logger:
            self._logger(str(text))

    # Read properties

    @property
    def intensity(self):        # Get direct HW intensity
        return self._intensity

    @property
    def spectrum(self):         # Get direct HW spectrum
        return self._spectrum

    @property
    def movement(self):         # Get computed UI movement dB from HW values
        upper_db = self._intensity
        diff_db = self._spectrum
        if diff_db < 0:            
            mov = upper_db              # Movement is upper
        else:
            mov = upper_db - diff_db    # Movement is lower (positive diff)
        return clip(round(mov, 0), *self.MOVEMENT_RANGE)

    @property
    def vibration(self):         # Get computed UI vibration dB 
        upper_db = self._intensity
        diff_db = self._spectrum
        if diff_db < 0:            
            vib = upper_db + diff_db    # Vibration is lower (negative diff)
        else:                   
            vib = upper_db              # Vibration is upper
        return clip(round(vib, 0), *self.VIBRATION_RANGE)

    # Write properties

    @intensity.setter
    def intensity(self, value):     # Set direct HW intensity (with validation)
        self._intensity = clip(value, *self.INTENSITY_RANGE)
        self.log("Intensity set to " + str(self._intensity))

    @spectrum.setter
    def spectrum(self, value):      # Set direct HW spectrum (with validation)
        self._spectrum = clip(value, *self.SPECTRUM_RANGE)
        self.log("Spectrum set to " + str(self._spectrum))

    @movement.setter
    def movement(self, value):      # Set HW values to get desired computed UI movement dB
        self.log("Updating movement to " + str(value))
        mov = value  
        vib = self.vibration        # get current computed vibration
        self._set_from_mov_vib(mov, vib)

    @vibration.setter
    def vibration(self, value):     # Set HW values to get desired computed UI vibration dB
        self.log("Updating vibration to " + str(value))
        mov = self.movement         # get current computed movement
        vib = value
        self._set_from_mov_vib(mov, vib)

    def _set_from_mov_vib(self, mov, vib):
        upper_db = max(mov, vib)
        diff_db = vib - mov
        # set intensity and spectrum with validation (clip)
        self._intensity = clip(upper_db, *self.INTENSITY_RANGE)
        self._spectrum = clip(diff_db, *self.SPECTRUM_RANGE)
        self.log("  Intensity set to " + str(self._intensity))
        self.log("  Spectrum set to " + str(self._spectrum))
        

# Prepare UI
def prep_ui(settings):
    with ui.card().classes('w-96'):
        ui.label('Hardware Settings').classes('text-h6')
        with ui.row().classes('w-full justify-between'):
            ui.label('Hardware Intensity:')
            ui.label().bind_text_from(settings, 'intensity', backward=to_string_db)
        ui.slider(min=-20, max=0, step=1).bind_value(settings, 'intensity')
        with ui.row().classes('w-full justify-between'):
            ui.label('Hardware Spectrum:')
            ui.label().bind_text_from(settings, 'spectrum', backward=to_string_db)
        ui.slider(min=-20, max=20, step=1).bind_value(settings, 'spectrum')

    with ui.card().classes('w-96'):
        ui.label('UI Settings').classes('text-h6')
        with ui.row().classes('w-full justify-between'):
            ui.label('UI Movement Intensity (dB)')
            ui.label().bind_text_from(settings, 'movement', backward=to_string_db)
        ui.slider(min=-20, max=0, step=1).bind_value(settings, 'movement')
        with ui.row().classes('w-full justify-between'):
            ui.label('UI Vibration Intensity (dB)')
            ui.label().bind_text_from(settings, 'vibration', backward=to_string_db)
        ui.slider(min=-20, max=0, step=1).bind_value(settings, 'vibration')

    with ui.card().classes('w-96'):
        ui.label('Log').classes('text-h6')
        ui_log = ui.log(max_lines=30).classes('w-full h-48 leading-none text-xs')
        ui_log.push("Drag sliders to see interaction")

    settings.set_logger(ui_log.push) # Use ui.log.push method as logger for changes in settings


if __name__ in {"__main__", "__mp_main__"}:  # Allow for nicegui multiprocessing
    # Initialize settings before UI
    settings = Settings()
    # Start UI in browser
    prep_ui(settings)
    ui.run(port=9000, title="Haptic Intensity Sliders")