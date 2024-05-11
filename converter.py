from lxml import etree
from midifunctions import get_midi_info
import zipfile
import os
from vstanalyser import modify_vst3preset_file

# Device ID for the Vienna Ensemble Pro Event VST3 plugin
deviceID = "AE6C5A1D474345A684AFE06B58D6AEBF"


def process_musicxml(musicxml_file):
    musicxml_tree = etree.parse(musicxml_file)
    musicxml_root = musicxml_tree.getroot()

    # Create list of devices for parts in the MusicXML
    xmldevices = []

    for part in musicxml_root.findall(".//score-part"):
        part_id = part.get("id")
        part_name = part.find("part-name").text
        # Create the Devices element
        device = part.find("midi-device").text
        # Create the Channel element
        channel = part.find("midi-instrument/midi-channel").text

        xmldevices.append(
            {
                "part_id": part_id,
                "part_name": part_name,
                "device": device,
                "channel": channel,
            }
        )

    # Create list of tracks for parts in the MusicXML
    xmltracks = []

    for part in musicxml_root.findall(".//part"):
        part_id = part.get("id")
        # Create the Devices element
        matching_item = next(
            (item for item in xmldevices if item["part_id"] == part_id), None
        )

        part_name = matching_item["part_name"]
        device = matching_item["device"]
        channel = matching_item["channel"]

        xmltracks.append({"part_name": part_name, "device": device, "channel": channel})

    return xmltracks


def create_project_file(miditracks):
    # Create the root element for the new XML
    project = etree.Element("Project", version="1.0")

    # Create the Application element
    application = etree.SubElement(
        project, "Application", name="MIDI to XML Converter", version="1.0"
    )

    # Create the Structure element
    structure = etree.SubElement(project, "Structure")

    for i in range(1, len(miditracks) + 1):
        meta = [
            msg["MetaMessages"] for msg in miditracks[i - 1] if "MetaMessages" in msg
        ][0]
        # Create a new Track element
        track_name = meta["track_name"] + "_ch_" + str(meta["channel"] + 1)

        track_element = etree.SubElement(
            structure,
            "Track",
            contentType="notes",
            id="trk_" + str(i) + "_" + meta["track_name"],
            name=track_name,
            loaded="true",
        )
        # using schema:
        # Create the Channel element
        channel_element = etree.SubElement(
            track_element,
            "Channel",
            audioChannels="2",
            role="regular",
            solo="false",
        )

        # Create the Devices element
        devices_element = etree.SubElement(channel_element, "Devices")

        # Create the VST3Plugin element
        vst3plugin_element = etree.SubElement(
            devices_element,
            "Vst3Plugin",
            deviceID=deviceID,
            deviceName=meta["instrument_name"],
            deviceRole="instrument",
            loaded="true",
            name=meta["instrument_name"],
        )

        # Create the state element
        state_element = etree.SubElement(
            vst3plugin_element,
            "State",
            external="false",
            path=f"plugins/{deviceID}_Vienna Ensemble Pro Event Input_{meta['instrument_name']}.vstpreset",
        )

    arrangement = etree.SubElement(project, "Arrangement")
    lanes_element = etree.SubElement(arrangement, "Lanes", timeUnit="beats")
    for i in range(1, len(miditracks) + 1):
        meta = [
            msg["MetaMessages"] for msg in miditracks[i - 1] if "MetaMessages" in msg
        ][0]

        # Create a new Lanes element
        sublanes_element = etree.SubElement(
            lanes_element, "Lanes", track="trk_" + str(i) + "_" + meta["track_name"]
        )

        clips_element = etree.SubElement(sublanes_element, "Clips")
        clip_element = etree.SubElement(
            clips_element,
            "Clip",
            name=meta["track_name"],
            time="0.0",
            # get the duration of the track by finding the time of last note plus its duration
            duration=str(meta["duration"]),
            playStart="0.0",
            contentTimeUnit="beats",
            fadeTimeUnit="beats",
        )
        clip_lanes_element = etree.SubElement(clip_element, "Lanes")

        notes_element = etree.SubElement(clip_lanes_element, "Notes")
        # Iterate over the messages in the track
        for msg in miditracks[i - 1]:
            if "note" in msg:
                note = msg["note"]
                note_element = etree.SubElement(
                    notes_element,
                    "Note",
                    time=str(note["time"]),
                    key=str(note["key"]),
                    vel=str(note["vel"]),
                    duration=str(note["duration"]),
                    channel=str(note["channel"]),
                )

        cc_messages_lists = extract_cc_messages_lists(miditracks[i - 1])
        for cc_messages_list in cc_messages_lists:
            points_element = etree.SubElement(
                clip_lanes_element, "Points", unit="normalized"
            )
            target_element = etree.SubElement(
                points_element,
                "Target",
                expression="channelController",
                controller=str(cc_messages_list[0]["control"]),
            )

            for cc_msg in cc_messages_list:
                cc_element = etree.SubElement(
                    points_element,
                    "RealPoint",
                    time=str(cc_msg["time"]),
                    value=str(cc_msg["value"] / 127),
                    interpolation="linear",
                )

    return project


def extract_cc_messages_lists(messages):
    cc_messages = {}
    for msg in messages:
        if "control_change" in msg:
            ccmsg = msg["control_change"]
            controller_number = ccmsg["control"]
            if controller_number not in cc_messages:
                cc_messages[controller_number] = []
            cc_messages[controller_number].append(ccmsg)
    return list(cc_messages.values())


def validate(projectxmlfile):
    # Create the XML schema validator
    schema_doc = etree.parse("project_schema.xsd")
    schema = etree.XMLSchema(schema_doc)

    # Validate the XML against the XSD schema
    project = etree.parse(projectxmlfile)
    if schema.validate(project):
        print("XML is valid according to the XSD schema.")
    else:
        print("XML is not valid according to the XSD schema.")
        print(schema.error_log)


def create_dawproject_archive(project, name):
    # Save the new XML file
    output_file = "project.xml"
    with open(output_file, "wb") as f:
        f.write(
            etree.tostring(
                project, pretty_print=True, encoding="UTF-8", xml_declaration=True
            )
        )

    print(f"Conversion complete. Output saved as {output_file}.")

    # Define the paths
    xml_file = output_file
    dawproject_file = f"{name}.dawproject"

    # Create a ZipFile object
    with zipfile.ZipFile(dawproject_file, "w") as zipf:
        # Get the base name of the XML file
        xml_base_name = os.path.basename(xml_file)

        # Add the XML file to the zip archive
        zipf.write(xml_file, xml_base_name)

        # Add a folder to the zip archive with all its contents
        zipf.write("plugins", "plugins" + os.sep)  # add the folder itself
        for root, dirs, files in os.walk("plugins"):
            for file in files:
                zipf.write(
                    os.path.join(root, file), os.path.join("plugins", file)
                )  # add the files

    print(f"Successfully created {dawproject_file}")
    return xml_file, dawproject_file


def create_plugin_folder(midi_file):
    # Create a folder for the VST3 plugin
    plugin_folder = "plugins"
    if not os.path.exists(plugin_folder):
        os.makedirs(plugin_folder)

    # iterate over tracks in the MIDI file
    tracks = get_midi_info(midi_file)

    for track in tracks:
        # Create a VST3 preset file for each track
        preset = modify_vst3preset_file(part=4)

        meta = [track["MetaMessages"] for track in track if "MetaMessages" in track][0]
        # create a file name for the preset
        filename = (
            f"{deviceID}_Vienna Ensemble Pro Event Input_"
            + meta["instrument_name"]
            + ".vstpreset"
        )

        preset_file = os.path.join(plugin_folder, filename)
        preset.write_file(preset_file)

    return plugin_folder


def convert(midi_file):
    # Load the MIDI file
    miditracks = get_midi_info(midi_file)

    # extract name from file path
    name = os.path.splitext(os.path.basename(midi_file))[0]
    project = create_project_file(miditracks)

    # Create the plugin folder
    create_plugin_folder(midi_file)

    xml_file, dawproject_file = create_dawproject_archive(project, name)

    validate(xml_file)
    return dawproject_file
