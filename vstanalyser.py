import vst3preset
import json
import re


def modify_vst3preset_file(
    part=0,
    instance="a0aa6b18f4454184b1849295693e4446",
    preset_file="vepro_event.vstpreset",
):
    preset = vst3preset.parse_vst3preset_file(preset_file)

    chunk_name = "Comp"
    chunk = preset.chunks[chunk_name]
    decoded_data = chunk.decode()
    cleaned_data = re.sub(r"^.*?{", "{", decoded_data)
    data = json.loads(cleaned_data)
    data["data"]["custom"]["inputIndex"] = part  # 0-based index of the part
    data["data"]["custom"]["id"] = instance
    modified = json.dumps(data)
    chunk = modified.encode()
    preset.chunks[chunk_name] = chunk
    preset.write_file("modified.vstpreset")
    return preset
