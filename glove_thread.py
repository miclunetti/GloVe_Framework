import time
import string
import json
import numpy as np

from Features import paper_features
from Utils import glovedict
from Features.spatial import get_avg_distance_matrix_lyrics
from Features.core_extractor import process_dataset
from HelperMethods.helper import _write_output
from Options.run_options import RunOptions
from multiprocessing import Pool



if __name__ == "__main__":
    # Parsing args
    opt = RunOptions().get_parser().parse_args()

    # Data Configurations
    start_time = time.time()

    gloved = glovedict.glove_dict(opt.glove_embedding_path)

    with open(opt.stop_words_path, 'r') as myfile:
        stop_words=set(myfile.read().replace('\n', '')\
                .replace(string.punctuation,'').lower().split(' '))

    # Thread Configuration
    dataset_lines = open(opt.input, 'r').readlines()
    dataset = [json.loads(line) for line in dataset_lines]
    song_number = len(dataset)
    song_indexes = []
    songs_per_process = int((len(dataset)/opt.cores) + 1)

    for i in range(0, song_number, int(songs_per_process)):
        song_indexes.append(i + np.array(range(songs_per_process)))
    song_indexes[-1] = song_indexes[-1][song_indexes[-1]<song_number]

    p = Pool(opt.cores)

    args_distance = zip(song_indexes, [opt] * len(song_indexes))

    avg_distance_results = p.map(get_avg_distance_matrix_lyrics, args_distance)
    avg_distance = np.mean(np.concatenate(avg_distance_results))
    print('Average distance computed successfully')
    print('Extracing features')

    extraction_parameters = zip(song_indexes, [avg_distance] * len(song_indexes), [opt] * len(song_indexes))

    _out1 = p.map(process_dataset, (extraction_parameters))
    output = np.concatenate(_out1)
    print(output[0])
    _write_output(output, opt.output)

    elapsed_time = time.time() - start_time
    print("Elapsed time: {}".format(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
