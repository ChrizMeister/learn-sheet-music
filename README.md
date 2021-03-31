# learn-sheet-music
 A Python program using the Kivy library to help teach how to read sheet music. The project title and code is currently still a work in progress.
 
## Functionality
When run this program creates a GUI application which contains an interactive piano and the ledger lines contained in sheet music. The piano can be interacted with using either the mouse to click on individual piano keys, using the keyboard for individual piano keys, or by connecting a MIDI input device. When pressing a key, the program will show the currently pressed note(s) on the ledger lines along with the name of the note(s) being pressed and will output the midi values of the notes being pressed. 

In addition, when the user clicks the 'Start' button the program will begin to generate random music notes (within a specific range) and show them on the ledger lines. If the user then presses the correct piano key for the shown note then the program shows a 'Correct' message at the top and then generates a new note for the user to guess. This is designed to help users practice the names of the notes, which notes correlate to specific locations on the piano, and to help the user learn how to sight-read sheet music. 

The program also allows the user to change the octave of notes that will be actived using the keyboard in order to make sure that they can reach all of the possible notes that can be generated.

## Requirements
- Python 3.0+
- Kivy 1.0.9+ 

### [Download Python](https://www.python.org/downloads/)
### [Download Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html#installation-canonical)