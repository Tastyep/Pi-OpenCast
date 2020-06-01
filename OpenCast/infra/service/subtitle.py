from pathlib import Path


class SubtitleConverter:
    def vtt_to_srt(self, subtitle: Path):
        print(f"subtitle: {subtitle}")
        dest = subtitle.with_suffix(".srt")
        with open(subtitle, "r") as fp:
            content = fp.readlines()

        output = []
        subtitle_count = 0
        in_caption = False
        for line in content:
            if "-->" in line:
                tokens = line.split(" --> ")
                if len(tokens) < 3:
                    continue

                in_caption = True
                if subtitle_count > 0:
                    output.append("\n")
                subtitle_count += 1
                output.append(f"{subtitle_count}\n")
                output.append(line.replace(".", ","))
            elif line != "" and in_caption:  # Skip vtt header and notes
                output.append(line)
            else:
                in_caption = False

        with open(dest, "w") as fp:
            fp.writelines(output)

        return dest
