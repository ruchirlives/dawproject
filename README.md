**What is it**

This python code takes a midi .mid file and converts it to a .dawproject archive ready for import by Presonus Studio One.
It also sets up each track with a Vienna Ensemble Pro Event VST3 plugin instance, and names each track with both the original track name with the midi channel appended.

**Outline of code**

I. Import necessary libraries
  A. lxml for XML processing
  B. midifunctions for MIDI file processing
  C. zipfile for creating ZIP archives
  D. os for file and directory operations
  E. vstanalyser for modifying VST3 preset files

II. Define global variables
  A. deviceID for the Vienna Ensemble Pro Event VST3 plugin

III. Function: process_musicxml(musicxml_file)
  A. Parse the MusicXML file
  B. Create a list of devices for parts in the MusicXML
     1. Extract part ID, part name, device, and channel information
  C. Create a list of tracks for parts in the MusicXML
     1. Extract part name, device, and channel information
  D. Return the list of tracks

IV. Function: create_project_file(miditracks)
  A. Create the root element for the new XML
  B. Create the Application element
  C. Create the Structure element
     1. Iterate over the MIDI tracks
        a. Extract metadata (track name, channel, instrument name)
        b. Create Track, Channel, Devices, and Vst3Plugin elements
        c. Create the State element for the VST3 plugin
  D. Create the Arrangement element
     1. Create Lanes elements for each MIDI track
        a. Create Clips elements
        b. Create Notes elements and populate with note information
        c. Extract and create Points elements for CC messages
  E. Return the project XML

V. Function: extract_cc_messages_lists(messages)
  A. Extract CC messages from the MIDI messages
  B. Group CC messages by controller number
  C. Return a list of CC message lists

VI. Function: validate(projectxmlfile)
  A. Create an XML schema validator using the XSD schema
  B. Validate the project XML against the XSD schema
  C. Print validation results

VII. Function: create_dawproject_archive(project, name)
  A. Save the project XML file
  B. Create the plugin folder
  C. Create a ZIP archive (.dawproject file)
     1. Add the project XML file to the archive
     2. Add the plugin folder and its contents to the archive
  D. Return the paths of the XML file and .dawproject file

VIII. Function: create_plugin_folder(midi_file)
  A. Create a folder for the VST3 plugin
  B. Iterate over tracks in the MIDI file
     1. Create a VST3 preset file for each track
     2. Save the preset file in the plugin folder
  C. Return the plugin folder path

IX. Function: convert(midi_file)
  A. Load the MIDI file
  B. Extract the name from the file path
  C. Create the project XML using create_project_file()
  D. Create the .dawproject archive using create_dawproject_archive()
  E. Validate the project XML using validate()

