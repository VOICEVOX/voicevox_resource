import http.client
import json
import math
import os
from os.path import join, split
from urllib.parse import urlencode


def main():
    text_path = join(*split(__file__)[:-1], "rashoumon.txt")
    f = open(text_path, "r")
    texts = f.readlines()
    f.close()

    texts = [text.rstrip() for text in texts]

    char_dir = join(*split(__file__)[:-2], "character_info")
    chars = os.listdir(char_dir)

    conn = http.client.HTTPConnection("localhost", 50021)

    for idx, char in enumerate(chars):
        char_name, uuid = char.split("_")
        print(
            f"processing character {char_name}, uuid: {uuid}, progress: {idx+1}/{len(chars)}"
        )

        meta_path = join(char_dir, char, "metas.json")
        f = open(meta_path, "r")
        meta = json.loads(f.read())
        f.close()

        # get original meta from engine, for only it has the style information
        conn.request("GET", f"/speaker_info?speaker_uuid={uuid}")
        data = conn.getresponse().read().decode("utf-8")

        ranges = []
        speaker_info = json.loads(data)
        # iterate through the styles, get their range on the full text of `rashoumon`
        for style in speaker_info["style_infos"]:
            style_id = style["id"]
            pitches = pitch_range(style_id, texts, conn)
            mean, std = analyze_pitch(pitches)
            if mean < 1.0:
                # for the whisper styles
                low = 0.0
                high = 0.0
            # calculate bound
            low = mean - 3 * std
            high = mean + 3 * std
            # round to 2 decimals
            low = math.floor(low * 100) / 100
            high = math.ceil(high * 100) / 100
            # range safety
            low = max(0.0, low)
            high = min(6.5, high)
            ranges.append({"style_id": style_id, "low": low, "high": high})
            print(
                f"style: {style_id},\t mean: {round(mean, 2)},\t std: {round(std, 2)},\t high: {high},\t low: {low}"
            )
        meta["range"] = ranges

        f = open(meta_path, "w")
        f.write(json.dumps(meta, indent=4))  # pretty print
        f.close()


def analyze_pitch(pitches: dict[float, int]) -> tuple[float, float]:
    count = 0
    s = 0.0
    for k, v in pitches.items():
        if k < 1.0:
            continue
        count += v
        s += k * v
    if count < 10:
        # too little voiced phonemes
        return (0.0, 0.0)
    mean = s / count

    var_s = 0.0
    for k, v in pitches.items():
        if k < 1.0:
            continue
        var_s += (k - mean) ** 2 * v
    std = math.sqrt(var_s / count)

    return mean, std


def pitch_range(speaker_id: int, texts: list[str], conn: http.client.HTTPConnection):
    pitches = {}
    for text in texts:
        body = urlencode({"speaker": speaker_id, "text": text})
        conn.request("POST", f"/audio_query?{body}")
        data = json.loads(conn.getresponse().read().decode("utf-8"))
        try:
            for accent_phrases in data["accent_phrases"]:
                for mora in accent_phrases["moras"]:
                    pitch = mora["pitch"]
                    pitch = round(pitch, 2)
                    if pitch not in pitches:
                        pitches[pitch] = 1
                    else:
                        pitches[pitch] += 1
        except Exception as e:
            print(f"Exception at text {text}, error: {str(e)}")
            continue
    return pitches


if __name__ == "__main__":
    main()
