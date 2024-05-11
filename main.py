from converter import convert, process_musicxml
import tkinter.filedialog as file


def main():
    # Get the MIDI file
    midi_file = file.askopenfilename(
        title="Select a MIDI file", filetypes=[("MIDI files", "*.mid")]
    )

    # Convert the MIDI file
    dawproject = convert(midi_file)
    print("Done! Created", dawproject)


if __name__ == "__main__":
    main()
