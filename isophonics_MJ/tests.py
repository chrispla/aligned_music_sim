import reader

lab_dir = "/Users/chris/Google Drive/Publication Files/ICMC2021/Datasets/isophonics_MJ/seglab"
audio_dir = "/Users/chris/Google Drive/Publication Files/ICMC2021/Datasets/isophonics_MJ/audio"
ref = reader.ref_paths(lab_dir, audio_dir)

lab_paths = reader.read_paths(lab_dir, '.lab')
audio_paths = reader.read_paths(audio_dir,' .flac')

lab_data = []
labels = []
for lab in lab_paths:

    with open(lab, "r") as f:
        data = []
        while True:

            line = f.readline()
            if not line: #if EOF
                break

            line = line.split()

            # convert start and end time string to float
            line[0] = float(line[0])
            line[1] = float(line[1])

            #check label
            if line[2] not in labels:
                labels.append(line[2])

            data.append(line)

    lab_data.append(lab)

print(labels)