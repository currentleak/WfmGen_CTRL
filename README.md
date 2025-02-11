# WfmGen_CTRL
A graphical user interface for managing an external waveform generator connected via a USB (virtual COM port), providing options to enter frequency, amplitude, burst mode, and various parameters.

chatGPT 03-mini high

write a python script:
user interface for control of an external waveform generator, connected on an usb port (virtual com port)
the interface allow to enter frequency, amplitude, burst mode and parameters

1st gpt mods
can you add to the script:
1- detection of the OS
2- Scan Serial bus available
3- Serial port selection is a drop down list of the port available

2nd gpt mods
add a disconnect button, connect button should be disabled when connection is active
correction: refresh button should also be disabled when connected
correction: send should be disabled if not connected

