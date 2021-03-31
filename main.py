# Code by Christopher Sommerville

# kivy_venv\Scripts\activate

import asyncio
from threading import Thread
import os
import math
import random
import time
import sys
import mido
from mido import Message
from mido import MidiFile

from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from win32api import GetSystemMetrics
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import *
from kivy.graphics import Color
from kivy.uix.dropdown import DropDown

MAXIMIZED = (1920, 1017)

SIZE_LARGE = (GetSystemMetrics(0), GetSystemMetrics(1))
SIZE_MEDIUM = (1080, 900)
SIZE_SMALL = (800, 600)
SIZE_MOBILE = (400, 800)

NOTE_ARRAY = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

KEYBOARD_SIZE = 4

dir_path = os.path.dirname(os.path.realpath(__file__))

# Accept a midi value and return the corresponding note and octave
def midi_to_note(midi): # Return note and octave
    remainder = midi % 12
    note = NOTE_ARRAY[remainder]
    octave = (midi // 12) - 1
    return [note, octave]

def note_to_midi(note, octave=1): # Return midi note number, currently unused
    print("Note:", note)
    print("Octave:", octave)
    key_array = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
    index = NOTE_ARRAY.index(note)
    return key_array[index]

# Key objects representing different types/shapes
class Key(Button):
    note = "C"
    midi_note = 60
    sharp = False
    pressed = False

    def __init__(self, midi_output = None):
        super(Key, self).__init__()
        self.output = midi_output

        def newNote(dt):
            self.parent.generate_note(keyboardSize = KEYBOARD_SIZE)

        def removeText(dt):
            self.parent.ids["noteGuess"].text = ""

        def correctGuess(dt):
            self.background_color = (0.1, 0.9, 0.2, 1)
            self.parent.ids["noteGuess"].text = "Correct"
            self.parent.ids["noteGuess"].color = (0, 0.9, 0.3)
            self.parent.remove_note(self.midi_note)
            self.parent.add_note(self.midi_note, color = Color(0.1, 0.9, 0.2), showNoteName=True)
            self.newNoteEvent()

        def incorrectGuess(dt):
            self.background_color = (0.9, 0.1, 0, 1)
            self.parent.ids["noteGuess"].text = "Incorrect"
            self.parent.ids["noteGuess"].color = (0.9, 0.3, 0)

        def changeBGColor(dt):
            self.background_color = (0.0, 0.8, 0.85, 1)

        self.newNoteEvent = Clock.create_trigger(newNote, 1.0)
        self.removeTextEvent = Clock.create_trigger(removeText, 1.5)
        self.correctEvent = Clock.create_trigger(correctGuess)
        self.incorrectEvent = Clock.create_trigger(incorrectGuess)
        self.changeColorEvent = Clock.create_trigger(changeBGColor)

    # Activates when a key is pressed
    def on_press(self, sendMessage = True):  
        if sendMessage:
            msg = mido.Message('note_on', note=self.midi_note, velocity = 50)
            # print(msg)
            self.output.send(msg)

        # print("currentNoteMidi:", self.parent.currentNoteMidi)
        # print("key midi_note:", self.midi_note)
        if self.parent.currentNoteMidi != -1:
            if self.midi_note == self.parent.currentNoteMidi:
                self.correctEvent()
            else:
                self.parent.add_note(self.midi_note, color=Color(0.9, 0.1, 0), showNoteName=True)
                self.incorrectEvent()
            self.removeTextEvent()
        else:
            self.parent.add_note(self.midi_note, user=True, showNoteName=True)
            self.changeColorEvent()

        if len(self.parent.curr_notes) > 0:
            if self.midi_note in self.parent.curr_notes[0]:
                print("press, curr_notes")
                self.parent.remove_note(self.midi_note)
                self.parent.add_note(self.midi_note, color = Color(0.1, 0.9, 0.2), showNoteName=True)
        
        # Revert button color to white if not being pressed
        def checkIfPressed(dt):
            if self.background_color != (1, 1, 1, 1) and self.state == 'normal':
                self.on_release()

        Clock.schedule_once(checkIfPressed, 5)

        self.pressed = True

    # Activates when a key is released
    def on_release(self, sendMessage = True):
        if len(self.parent.curr_notes) > 0:
            if self.midi_note in self.parent.curr_notes[0]:
                self.parent.remove_note(self.midi_note)
                self.parent.add_note(self.midi_note)
            else:
                self.parent.remove_note(self.midi_note)
        else:
            self.parent.remove_note(self.midi_note)
        def defaultBGColor(dt):
            self.background_color = (1, 1, 1, 1)
        Clock.schedule_once(defaultBGColor)
        if sendMessage:
            msg = mido.Message('note_off', note=self.midi_note, velocity = 50)
            self.output.send(msg)

        self.pressed = False

class LeftKey(Key):

    def collide_point(self, x, y):
        if (y >= 0 and y <= self.size[1]):
            if (x >= self.pos[0] + 2 and x <= self.pos[0] + self.size[0] - 2):
                if (y >= 81):
                    return x <= self.pos[0] + 26
                else:
                    return True
        return False

class MiddleKey(Key):

    def collide_point(self, x, y):
        if (y >= 0 and y <= self.size[1]):
            if (x >= self.pos[0] + 2 and x <= self.pos[0] + self.size[0] - 2):
                if (y >= 81):
                    return x >= self.pos[0] + 10 and x <= self.pos[0] + 26
                else:
                    return True
        return False

class RightKey(Key):

    def collide_point(self, x, y):  
        if (y >= 0 and y <= self.size[1]):
            if (x >= self.pos[0] + 2 and x <= self.pos[0] + self.size[0] - 2):
                if (y >= 81):
                    return x >= self.pos[0] + 11
                else:
                    return True
        return False

class SharpKey(Key):
    sharp = True
    def collide_point(self, x, y):
        if (y >= 82 and y <= self.size[1]):
            if (x >= self.pos[0] + 27 and x <= self.pos[0] + self.size[0]):
                return True
        return False

class SingleKey(Key):

    def collide_point(self, x, y):
        if (y >= 0 and y <= self.size[1]):
            if (x >= self.pos[0] + 2 and x <= self.pos[0] + self.size[0]):
                return True
        return False

# Main class for showing the GUI
class PianoWindow(Widget):

    def __init__(self, midi_output = None):
        self.set_all_attributes()
        super(PianoWindow, self).__init__()
        
        self.output = midi_output
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self.currentNoteMidi = -1
        self.add_drop_down()

        self.threads = []
        
    def set_all_attributes(self):
        self.barspace = 35 # Space between lines
        self.barheight = 4 # Height (size) of lines
        self.notewidth = 64 # Width of a note
        self.noteheight = self.barspace + self.barheight # 39 - Height of a note
        self.barwidth = self.notewidth + 20 # Width of bar near note

        self.topline_treble = 244 # Distance from top of screen to first line of treble
        self.bottomline_treble = self.topline_treble + self.barspace * 4 # Distance from top to last line of treble

        self.topline_bass = self.bottomline_treble + self.barspace * 2
        self.bottomline_bass = self.topline_bass + self.barspace * 4

        self.all_keys = {}
        self.notes = {}
        self.guessingStarted = False
        self.keyboardOctave = 0
        self.curr_notes = []

    def add_drop_down(self):
        dropdown = DropDown()
        for index in range(-2, 2):
            if index >= 0:
                btn = Button(text='Octave +%d' % index, size_hint_y=None, height=30)
            else:
                btn = Button(text='Octave %d' % index, size_hint_y=None, height=30)

            def btnSelect(btn):
                dropdown.select(btn.text)
                self.keyboardOctave = int(btn.text[6:])

            btn.bind(on_release=btnSelect)
            dropdown.add_widget(btn)

        mainbutton = Button(text='Octave +0', pos=(280, SIZE_MEDIUM[1] - 90),size=(100, 80))
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        self.add_widget(mainbutton)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self._keyboard = None

    # Activates on pressing a keyboard key
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        note_midi = self.text_to_midi(text)

        if note_midi != -1:
            child = self.all_keys[int(note_midi)]
            if child.state == "normal":
                child.on_press()
                set_state_event = Clock.create_trigger(lambda dt: self.set_child_state(child, 'down'))
                set_state_event()
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    # Activates upon releasing a keyboard key
    def _on_keyboard_up(self, keyboard, keycode,):
        note_midi = self.text_to_midi(keycode[1])

        if note_midi != -1:
            child = self.all_keys[int(note_midi)]
            if child.state == "down":
                child.on_release()
                set_state_event = Clock.create_trigger(lambda dt: self.set_child_state(child, 'normal'))
                set_state_event()

        return True

    # Convert a character (input from the keyboard) into a midi value
    def text_to_midi(self, text):
        values = {"a": 60, "w": 61, "s": 62, "e": 63, "d": 64, "f": 65, "t": 66, "g": 67, "y": 68, "h": 69, "u": 70, "j": 71, "k": 72, "o": 73, "l": 74, "p": 75, ";": 76}
        for key in values:
            values[key] += 12 * self.keyboardOctave
        if text in values:
            return values[text]
        else:
            return -1

    # Methods for creating the keys to be shown on the App
    def left_key(self, pos = (0, 0), note = "A", midi_note = 1, midi_output = None):
        key = LeftKey(midi_output)
        key.id = str(midi_note)
        key.note = note
        key.midi_note = midi_note
        key.size = (36, 203)
        key.pos = pos
        key.background_normal = "images/left.png"
        key.background_down = "images/left_press.png"
        self.add_widget(key)
        self.all_keys[midi_note] = key

    def sharp_key(self, pos = (0, 0), note = "A", midi_note = 1, midi_output = None):
        key = SharpKey(midi_output)
        key.id = str(midi_note)
        key.note = note
        key.midi_note = midi_note
        key.size = (44, 203)
        key.pos = pos
        key.background_normal = "images/sharp.png"
        key.background_down = "images/sharp_press.png"
        self.add_widget(key)
        self.all_keys[midi_note] = key

    def middle_key(self, pos = (0, 0), note = "A", midi_note = 1, midi_output = None):     
        key = MiddleKey(midi_output)
        key.id = str(midi_note)
        key.note = note
        key.midi_note = midi_note
        key.size = (36, 203)
        key.pos = pos
        key.background_normal = "images/middle.png"
        key.background_down = "images/middle_press.png"
        self.add_widget(key)
        self.all_keys[midi_note] = key

    def right_key(self, pos = (0, 0), note = "A", midi_note = 1, midi_output = None):   
        key = RightKey(midi_output)
        key.id = str(midi_note)
        key.note = note
        key.midi_note = midi_note
        key.size = (36, 203)
        key.pos = pos
        key.background_normal = "images/right.png"
        key.background_down = "images/right_press.png"
        self.add_widget(key)
        self.all_keys[midi_note] = key
    
    def single_key(self, pos = (0, 0), note = "A", midi_note = 1, midi_output = None):   
        key = SingleKey(midi_output)
        key.id = str(midi_note)
        key.note = note
        key.midi_note = midi_note
        key.size = (36, 203)
        key.pos = pos
        key.background_normal = "images/single.png"
        key.background_down = "images/single_press.png"
        self.add_widget(key)
        self.all_keys[midi_note] = key

    def check_notes(self):
        if len(self.curr_notes) > 0:
            for note in self.curr_notes[0]:
                if int(note) in self.all_keys:
                    child = self.all_keys[int(note)]
                    if not child.pressed:
                        return

            # print("Correct")
            # print(self.curr_notes)
            del self.curr_notes[0]
            if len(self.curr_notes) > 0:
                for note in self.curr_notes[0]:
                    self.add_note(valueMidi=note)

    def set_child_state(self, child, state):
        child.state = state
        self.check_notes()

    # Recieve midi input
    def recieve(self, msg):
        self.output.send(msg)
        if hasattr(msg, 'note'):
            note_midi = str(msg.note)
            if int(note_midi) in self.all_keys:
                child = self.all_keys[int(note_midi)]
                if msg.type == "note_on":
                    child.on_press(False)
                    set_state_event = Clock.create_trigger(lambda dt: self.set_child_state(child, 'down'))
                    set_state_event()
                else:
                    child.on_release()
                    set_state_event = Clock.create_trigger(lambda dt: self.set_child_state(child, 'normal'))
                    set_state_event()

    # Create all of the keys to be shown on the app based on a keyboard size
    def make_keys(self, keyboardSize = 2):
        if len(mido.get_input_names()) > 0:
            input = mido.open_input(callback=self.recieve, autoreset=True)
        numKeys = 12 * keyboardSize
        if keyboardSize > 7:
            keyboardSize = 7
        if keyboardSize == 1:
            base = 60
        elif keyboardSize <= 3:
            base = 48
        elif keyboardSize <= 5:
            base = 36
        else:
            base = 24

        x_left = 0
        for i in range(numKeys):
            if i % 12 == 0:
                self.left_key((x_left + 34 * 7 * (i // 12), 0), "C", i + base, self.output)
            elif i % 12 == 1:
                self.sharp_key(((x_left + 34 * 7 * (i // 12), 0)), "C#", i + base, self.output)
            elif i % 12 == 2:
                self.middle_key((x_left + 34 + (34 * 7 * (i // 12)), 0), "D", i + base, self.output)
            elif i % 12 == 3:
                self.sharp_key((x_left + 34 + (34 * 7 * (i // 12)), 0), "D#", i + base, self.output)
            elif i % 12 == 4:
                self.right_key((x_left + 34 * 2 + (34 * 7 * (i // 12)), 0), "E", i + base, self.output)
            elif i % 12 == 5:
                self.left_key((x_left + 34 * 3 + (34 * 7 * (i // 12)), 0), "F", i + base, self.output)
            elif i % 12 == 6:
                self.sharp_key((x_left + 34 * 3 + (34 * 7 * (i // 12)), 0), "F#", i + base, self.output)
            elif i % 12 == 7:
                self.middle_key((x_left + 34 * 4 + (34 * 7 * (i // 12)), 0), "G", i + base, self.output)
            elif i % 12 == 8:
                self.sharp_key((x_left + 34 * 4 + (34 * 7 * (i // 12)), 0), "G#", i + base, self.output)
            elif i % 12 == 9:
                self.middle_key((x_left + 34 * 5 + (34 * 7 * (i // 12)), 0), "A", i + base, self.output)
            elif i % 12 == 10:
                self.sharp_key((x_left + 34 * 5 + (34 * 7 * (i // 12)), 0), "A#", i + base, self.output)
            elif i % 12 == 11:
                self.right_key((x_left + 34 * 6 + (34 * 7 * (i // 12)), 0), "B", i + base, self.output)

        self.single_key((x_left + 34 * 7 * (numKeys // 12), 0), "C", numKeys + base, self.output)

    # Generate a midi note based on the size of the keyboard
    def generate_note(self, keyboardSize = 4, note = -1):
        if keyboardSize == 1:
            base = 60
        elif keyboardSize <= 3:
            base = 48
        elif keyboardSize <= 5:
            base = 36
        else:
            base = 24
        if note == -1:
            valueMidi = random.randint(base, base + 12 * keyboardSize)
        else:
            valueMidi = note
        valueMidi = random.randint(48, 72) # Middle C = 60. C3, C4, C5
        # valueMidi = 48
        # print("valueMidi:", valueMidi)

        self.currentNoteMidi = valueMidi
        self.add_note(valueMidi, showNoteName=False)

    # Add a music note to the screen
    def add_note(self, valueMidi=60, user=False, color=None, showNoteName=False):
        newNote = InstructionGroup()
        #if valueMidi in self.notes:
            # self.remove_note(valueMidi)
        if valueMidi not in self.notes:
            positions = self.get_note_position(valueMidi) # notePos, sharpPos, linePos
            mainColor = Color(0, 0, 0)
            if color is not None:
                mainColor = color 
            elif user:
                mainColor = Color(0.1, 0.7, 0.9)
            else:
                mainColor = Color(0, 0, 0)

            newNote.add(mainColor)

            newNote.add(
                Rectangle(
                    group=str(valueMidi),
                    source="images/wholenotesmall_white.png",
                    size=(self.notewidth, self.noteheight),
                    pos=positions[0]
                )
            )

            if showNoteName:
                label = Label()
                label.text = str(midi_to_note(valueMidi)[0])
                label.font_size = 50
                label.texture_update()
                if len(label.text) > 1:
                    size = (60, 45)
                else:
                    size = (30, 45)
                newNote.add(Color(0.1, 0.1, 0.1, 0.9))
                newNote.add(
                    Rectangle(
                        group=str(valueMidi),
                        size=(size[0] + 5, size[1]),
                        pos=(positions[0][0] + self.notewidth + 15, positions[0][1] - 4)
                    )
                )

                
                newNote.add(mainColor)
                newNote.add(
                    Line(
                        width=1,
                        rectangle= (positions[0][0] + self.notewidth + 15, 
                                    positions[0][1] - 4, size[0] + 5, size[1])
                    )
                )
                
                newNote.add(
                    Rectangle(
                        group=str(valueMidi),
                        size=size,
                        texture = label.texture,
                        pos=(positions[0][0] + self.notewidth + 17, positions[0][1] - 4)
                    )
                )
                
            
            if positions[1] != -1: # sharp
                rect = Rectangle(
                        source="images/sharp_symbol_small_white.png",
                        pos=positions[1], 
                        size = (40, 78)
                    )
                func = lambda a : a
                rect.texture.ask_update(func)
                newNote.add(rect)

            if positions[2] != -1: # Lines
                for pos in positions[2]:
                    newNote.add(
                        Rectangle(
                            pos=pos,
                            size=(self.barwidth, self.barheight)
                        )
                    )
            
            self.canvas.after.add(newNote)
            # print("new note added, value:", valueMidi)
            self.notes[valueMidi] = newNote
            # print(self.notes)

    def remove_note(self, valueMidi):
        if valueMidi in self.notes:
            # print("removing note:", valueMidi)
            note = self.notes[valueMidi]
            self.canvas.after.remove(note)
            del self.notes[valueMidi]

    def get_note_position(self, valueMidi):
        result = [-1, -1, -1]
        x = self.width / 2 - (self.notewidth / 2)
        x_bar = self.width/2 - (self.barwidth / 2)
        y_base = self.top - self.bottomline_treble - self.barspace

        treble_basepos_note = [x, y_base - self.barspace / 2]
        treble_basepos_bar  = [x_bar, y_base]

        bass_basepos_bar  = [x_bar, self.top - self.bottomline_bass - self.barspace]

        sharpNotes = [1, 3, 6, 8, 10]
        sharpNotesReverse = [2, 4, 6, 9, 11]

        diff = valueMidi - 60
        total = abs(diff)

        numSharps = 0
        sharp = False
        if diff >= 0:
            numLoops = math.ceil(diff / 12)
            for i in range(numLoops):
                for val in sharpNotes:
                    if not sharp and diff % 12 == val:
                        sharp = True
                    if total >= val:
                        numSharps += 1
                total -= 12
            diff -= numSharps
        else:
            numLoops = abs(math.floor(diff / 12))
            for i in range(numLoops):
                tempSharps = 0
                for val in sharpNotesReverse:
                    if not sharp and abs(diff) % 12 == val:
                        sharp = True
                    if total >= val:
                        tempSharps += 1
                if total <= 12:
                    if (tempSharps == 1 and total == 2) or (tempSharps == 2 and total == 4) or (tempSharps == 3 and total == 6) or  \
                       (tempSharps == 4 and total == 9) or (tempSharps == 5 and total == 11):
                        tempSharps -= 1

                numSharps += tempSharps
                total -= 12
            
            diff += numSharps


        treble_basepos_note[1] += diff * (self.barspace / 2)

        result[0] = tuple(treble_basepos_note) 
        if sharp:
            sharpX = treble_basepos_note[0] - self.notewidth / 1.2
            sharpY = treble_basepos_note[1] - self.noteheight / 2
            # sharpImg.pos = (sharpX, sharpY)
            result[1] = (sharpX, sharpY)

        if valueMidi == 60 or valueMidi == 61:
            result[2] = [tuple(treble_basepos_bar)]
        elif valueMidi >= 81:
            treble_basepos_bar[1] += 12 * (self.barspace / 2)
            result[2] = []
            result[2].append(tuple(treble_basepos_bar))
            if valueMidi >= 84:
                treble_basepos_bar1 = treble_basepos_bar
                treble_basepos_bar1[1] += self.barspace
                result[2].append(tuple(treble_basepos_bar1))
        
        if valueMidi <= 40:
            result[2] = []
            result[2].append(tuple(bass_basepos_bar))
            if valueMidi <= 37:
                result[2].append((bass_basepos_bar[0], bass_basepos_bar[1] - self.barspace))

        return result

class PianoApp(App):

    def build(self):
        Window.size = SIZE_MEDIUM
        Window.left = 0
        Window.top = 30
        Window.minimum_width = SIZE_MEDIUM[0]
        Window.minimum_height = SIZE_MEDIUM[1]
        midi_output = mido.open_output()
        piano_window = PianoWindow(midi_output)        
        piano_window.make_keys(KEYBOARD_SIZE)
        # Window.maximize()
        piano_window.add_note(111)
        piano_window.remove_note(111)

        return piano_window


def main():
    PianoApp().run()

if __name__ == '__main__':
   main()