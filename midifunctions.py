import mido


def gettimeinbeats(time):
    inbeats = time / 480
    return inbeats


def get_midi_info(midi_file):
    # Load the MIDI file
    midi = mido.MidiFile(midi_file)
    tracks = []
    # Create notes for each track in the MIDI file
    for i, track in enumerate(midi.tracks):  # ignore the first track
        if i == 0:
            continue
        tracks.append(get_midi_track(track))

    return tracks


def get_midi_track(track):
    # timestamp all the msgs in track
    time = 0
    for msg in track:
        time += gettimeinbeats(msg.time)
        msg.time = time-4  # subtract 4 beats to make the start time 0

    # Create an array of the note off messages
    noteoffs = [msg for msg in track if msg.type == "note_off" and msg.note == msg.note]

    trackarray = []

    # Get the duration of the track
    duration = noteoffs[-1].time
    track_name = track.name
    instrument_name = [msg.name for msg in track if msg.type == 'instrument_name'][0]
    track_midi_channel = [msg.channel for msg in track if msg.type == 'channel_prefix'][0]
    trackarray.append({"MetaMessages": {'duration':duration, 'track_name':track_name, 'instrument_name':instrument_name, 'channel':track_midi_channel}})

    for msg in track:
        if msg.type == "note_on":
            # find the matching note_off in noteoffs
            matching_noteoff = next(
                (noteoff for noteoff in noteoffs if noteoff.note == msg.note), None
            )
            noteoffs.remove(matching_noteoff)

            note = {
                "time": msg.time,
                "key": msg.note,
                "vel": msg.velocity / 127,
                "duration": matching_noteoff.time - msg.time,
                "channel": msg.channel,
            }

            trackarray.append(
                {
                    "note": note,
                }
            )

        elif msg.type == "control_change":
            trackarray.append(
                {
                    "control_change": {
                        "time": msg.time,
                        "control": msg.control,
                        "value": msg.value,
                    }
                }
            )

        elif msg.type == "program_change":
            trackarray.append(
                {
                    "program_change": {
                        "time": msg.time,
                        "program": msg.program,
                    }
                }
            )
        elif msg.type == "pitchwheel":
            trackarray.append(
                {
                    "pitchwheel": {
                        "time": msg.time,
                        "pitch": msg.pitch,
                    }
                }
            )
        elif msg.type == "channel_prefix":
            trackarray.append(
                {
                    "channel_prefix": {
                        "time": msg.time,
                        "channel": msg.channel,
                    }
                }
            )
        elif msg.type == "track_name":
            trackarray.append(
                {
                    "track_name": {
                        "time": msg.time,
                        "name": msg.name,
                    }
                }
            )
        elif msg.type == "instrument_name":
            trackarray.append(
                {
                    "instrument_name": {
                        "time": msg.time,
                        "name": msg.name,
                    }
                }
            )

    return trackarray
