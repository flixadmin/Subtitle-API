import json
from subdl import getMovieSubtitles, getTVSubtitles

data = json.load(open('watch_data.json'))
try: subData = json.load(open('sub_data.json'))
except: subData = {}
total = len(data.keys())
done = 0

for k, v in data.items():
    if k in subData.keys(): continue
    itype, tmdb_id = k.split('-')
    tmdb_id = int(tmdb_id)

    if itype == 'movie': subData[k] = getMovieSubtitles(tmdb_id)
    else:
        se = [(i['s'], i['e']) for i in v]
        subData[k] = {json.dumps(p) : l for p, l in getTVSubtitles(tmdb_id, se).items()}
    done += 1
    print(f'\r{done} Done out of {total}', end='')
    json.dump(subData, open('sub_data.json', 'w'), indent=4)

