import sys
import os
import shutil
import re
from pathlib import Path
import yaml
from pyannote.audio import Pipeline, Model
from pyannote.audio.pipelines import SpeakerDiarization
from pydub import AudioSegment
from natsort import natsorted
from pathlib import Path

def create_temps():
    os.mkdir("./temp/")
    os.mkdir("./temp/audio/")

def remove_temps():
    shutil.rmtree("./temp")

def get_pipeline():
    # Get the pipeline and make sure the correct parameters are in place
    trained_pipeline = Pipeline.from_pretrained(Path("./pipeline/config.yaml"))
    model = Model.from_pretrained("./models/trained_model.ckpt")
    trained_pipeline.segmentation_model = model

    with open("./parameters/config.yaml", "r") as f:
        parameters = yaml.safe_load(f)

    params = parameters["params"]

    params_clust = params["clustering"]

    trained_pipeline.instantiate({
            "segmentation": {"min_duration_off": params["segmentation"]["min_duration_off"]},
            "clustering": params["clustering"]
    })

    pipeline = SpeakerDiarization(
    segmentation=model,
    embedding=trained_pipeline.embedding,
    embedding_exclude_overlap=trained_pipeline.embedding_exclude_overlap,
    clustering=trained_pipeline.klustering,
    )

    with open("./parameters/config.yaml", "r") as f:
        loaded_parameters = yaml.safe_load(f)

    loaded_params = loaded_parameters["params"]

    params_clust = loaded_params["clustering"]

    parameters_segm = parameters["params"]["segmentation"]


    pipeline.instantiate({
        "segmentation": {
            "min_duration_off": parameters_segm["min_duration_off"],
            "threshold": parameters_segm["threshold"]
        },
        "clustering": params_clust
    })

    return pipeline

def create_rttm(file_name, diarization):
    # delete file if it already exists so a new file can get created
    if os.path.exists(f"./temp/{file_name}.rttm"):
        os.remove(f"./temp/{file_name}.rttm")

    f = open(f"./temp/{file_name}.rttm", "w")
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        f.write(f"SPEAKER {file_name} 1 {round(turn.start, 3)} {round(turn.end-turn.start, 3)} <NA> <NA> {speaker} <NA> <NA>\n")

    f.close()

def create_audio_files(path, file_name, diarization):
    audio = AudioSegment.from_wav(path)

    os.mkdir(f"./temp/audio/{file_name}/")


    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if not os.path.isdir(f"./temp/audio/{file_name}/{speaker}"):
            os.mkdir(f"./temp/audio/{file_name}/{speaker}")

        segment = audio[turn.start * 1000:turn.end * 1000]  # Convert seconds to milliseconds
        segment.export(f"./temp/audio/{file_name}/{speaker}/speaker_{speaker}_{turn.start:.1f}-{turn.end:.1f}.wav", format="wav")

def create_audio_per_speaker(file_name):
    speakers = os.listdir(f"./temp/audio/{file_name}")

    for speaker in speakers:
        files_list = os.listdir(f"./temp/audio/{file_name}/{speaker}")
        files_list = natsorted(files_list)

        combined = AudioSegment.from_file(f"./temp/audio/{file_name}/{speaker}/{files_list[0]}")
        for i in range(1,len(files_list)):
            combined = combined.append(AudioSegment.from_file(f"./temp/audio/{file_name}/{speaker}/{files_list[i]}"), crossfade=0.0)

        combined.export(f"./results/{file_name}/{speaker}.wav", format="wav")


if __name__ in "__main__":
    path_to_audio = str(sys.argv[1])

    file_name = re.search(r'.*\\(.+?)\.wav', path_to_audio).group(1)

    pipeline = get_pipeline()

    print("the model is working, this might take a while")
    diarization = pipeline(path_to_audio)

    create_temps()

    create_rttm(file_name, diarization)

    create_audio_files(path_to_audio, file_name, diarization)
    print("small audio files created")

    if not os.path.exists("./results"):
        os.mkdir("./results")

    os.mkdir(f"./results/{file_name}")

    create_audio_per_speaker(file_name)

    remove_temps()

    print("You can find your separated audio in the results folder")