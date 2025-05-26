import os, atexit, re, colorama
from zipfile import ZipFile, BadZipFile
from requests import get
from io import BytesIO
import asstosrt

KEY = 'PRn5U-DH8acJFimtXaLVhhidZ-ZMTiCs'
os.makedirs('cache', exist_ok=True)

def cleanCache():
    for f in os.listdir('cache'): os.remove(os.path.join('cache', f))
    os.rmdir('cache')

# atexit.register(cleanCache)

def assToSRT(filename):
    open(filename.replace('.ass', '.srt'), 'w', encoding='utf-8').write(asstosrt.convert(open(filename, encoding='utf-8')))
    return filename.replace('.ass', '.srt')

def getSeasonEpisode(filename: str):
    if len(os.path.basename(filename)) < 10: return None
    if 'trailer' in filename.lower(): return None
    try:
        r = re.search(
            r'(?:S(?:eason)?\s*)?(\d{1,2})\s*(?:[.\-_ ]?E(?:pisode)?[.\-_ ]?|[.\-_x])\s*(\d{1,2})',
            filename,
            re.IGNORECASE
        )
        return int(r.group(1)), int(r.group(2))
    except Exception:
        print(colorama.Fore.RED + f'\nSkipping one "{os.path.basename(filename)}"' + colorama.Fore.RESET)
        return None

def unzipFile(url):
    r = get(url)
    if r.status_code != 200:
        raise Exception(f"Error: {r.status_code} - {r.text}")
    try:
        with ZipFile(BytesIO(r.content)) as f:
            old_extracted = f.namelist()
            f.extractall('cache')
    except BadZipFile: return []
    extracted = []
    for i in old_extracted:
        fp = os.path.join('cache', i)
        if i.endswith('.srt'): extracted.append(fp)
        if i.endswith('.ass'): extracted.append(assToSRT(fp))
    return extracted

def getMovieSubtitles(tmdb_id:int):
    query = dict(api_key=KEY, tmdb_id=tmdb_id, type='movie', languages='EN')
    r = get('https://api.subdl.com/api/v1/subtitles', params=query)
    if r.status_code != 200:  raise Exception(f"Error: {r.status_code} - {r.text}")
    try: zips = ['http://dl.subdl.com' + i['url'] for i in r.json()['subtitles']]
    except KeyError as e:
        print(f'\n{colorama.Fore.YELLOW}KeyError on TMDB ID: {tmdb_id} movie{colorama.Fore.RESET} Status: {r.status_code} Resp: {r.text}')
        return []
    files = [f for i in zips for f in unzipFile(i) if f.endswith('.srt')]
    return files

def getTVSubtitles(tmdb_id:int, se:list[tuple[int, int]]):
    def getSingleEpisodeSubtitles(season:int, episode:int):
        query = dict(api_key=KEY, tmdb_id=tmdb_id, type='tv', languages='EN', season_number=season, episode_number=episode)
        r = get('https://api.subdl.com/api/v1/subtitles', params=query)
        if r.status_code != 200:  raise Exception(f"Error: {r.status_code} - {r.text}")
        try: zips = ['http://dl.subdl.com' + i['url'] for i in r.json()['subtitles']]
        except KeyError as e:
            print(f'\n{colorama.Fore.YELLOW}KeyError on TMDB ID: {tmdb_id} tv{colorama.Fore.RESET} Status: {r.status_code} Resp: {r.text}')
            return []
        files = [f for i in zips for f in unzipFile(i) if f.endswith('.srt')]
        return files
        
    idata = {i: [] for i in se}
    for i in se:
        if len(idata[i]) < 2:
            ifiles = getSingleEpisodeSubtitles(*i)
            for f in ifiles:
                try: idata[getSeasonEpisode(f)].append(f)
                except KeyError: pass

    return idata

if __name__ == '__main__':
    print(getTVSubtitles(65320, [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10)]))
    # print(getMovieSubtitles(603))

