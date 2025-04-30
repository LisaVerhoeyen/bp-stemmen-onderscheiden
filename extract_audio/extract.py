"""this script needs 3 arguments to run:
    arg 1: path to the input file
    arg 2: path to the output file
    arg 3: format in which the output file needs to be 
        default = wav
"""

import sys
from audio_extract import extract_audio

try:
    INPUT_PATH=str(sys.argv[1])
    OUTPUT_PATH=str(sys.argv[2])
    if len(sys.argv) == 4:
        OUTPUT_FORMAT=sys.argv[3]
    else:
        OUTPUT_FORMAT="wav"

    extract_audio(
        input_path=INPUT_PATH,
        output_path=OUTPUT_PATH,
        output_format=OUTPUT_FORMAT
    )

except(IndexError):
    print("The file must have 2 or 3 arguments, run as: python3 ./extract.py input_path output_path [output_format]")
