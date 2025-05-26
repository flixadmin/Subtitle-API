from requests import Session
from requests_toolbelt import MultipartEncoder
import re
import time
import json


def uploadSubtitle(slug: str, path: str, name: str):
    cookie = "abyss=eyJmbGFzaCI6e30sImd1ZXN0X2lkIjoiYzBhYmM5ZmNiZWQyMzY1OGUyMzI5MjA3MGMyYWE2NTUiLCJwYXNzcG9ydCI6eyJ1c2VyIjoiNDQ3NjE4In0sImlwIjoiMTAzLjE3My4xNzUuMTY5In0=; abyss.sig=YemxfhZf5o9bVcq9hfMjgGmYHcY; _ga=GA1.1.921076215.1748149797; _ga_C8809JR9MZ=GS2.1.s1748149797$o1$g0$t1748149801$j0$l0$h0; _gcl_au=1.1.1111893865.1748149797.1779181965.1748149798.1748149800"
    ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0"
    att = 0

    class r:
        text = 'Nothing...'
    while att <= 50:
        att += 1
        try:
            s = Session()
            s.headers = {'Cookie': cookie, 'User-Agent': ua}
            r = s.get('https://abyss.to/dashboard/subtitle?v=' + slug)
            if 'login' in r.text.lower():
                print('Cannot Login to abyss')
                raise Exception('Please Update Login Cookie')
            m = re.findall(r'''add\((?:'|")upload(?:'|"), (.*?)\)''', r.text)
            if not m:
                raise Exception('Upload ID not found.')
            uid = m[0]
            mpe = MultipartEncoder({'id': uid, 'file': (path.split('/')[-1].split('\\')[-1], open(
                path, 'rb'), 'application/octet-stream')}, boundary='----geckoformboundary931ad85bb6faf2723003fcb3ce0a202e')
            r = s.post('https://cdn.iamcdn.net/subtitle/upload', headers={
                       'Content-Type': mpe.content_type, 'Origin': 'https://abyss.to', 'Referer': 'https://abyss.to/'}, data=mpe)
            if r.status_code != 200:
                raise Exception(
                    'Subtitle upload failed to cdn. Resp: ' + r.text)
            sub_slug = r.json()['slug']
            r = s.post('https://abyss.to/dashboard/subtitle?v=' + slug, data={
                       'name': name, 'slug': sub_slug, 'type': path.split('.')[-1], 'url': 'undefined'})
            if not r.json()['status']:
                raise Exception(
                    'Error while setting subtitle to the video. Resp: %s' % r.text)
            return bool(1)
        except Exception as err:
            print(err, '\nSubtitle Uploading Response:',
                  r.text, 'Retrying...', att)
            time.sleep(10)

    raise Exception(f'Retried {att} times... But Cannot upload subtitle')


watch_data = json.load(open('watch_data.json'))
sub_data = json.load(open('sub_data.json'))
try:
    done = json.load(open('done.json'))
except:
    done = []

total = len([i for k, v in watch_data.items() for i in v])

for k, v in watch_data.items():
    for i in v:
        if 'movie' in k:
            i['subs'] = {f'English [SubDL] {i+1}': x for i,
                         x in enumerate(sub_data[k])}
        else:
            i['subs'] = {f'English [SubDL] {i+1}': x for i,
                         x in enumerate(sub_data[k].get(json.dumps((i['s'], i['e'])), []))}

for k, v in watch_data.items():
    for i in v:
        if i['url'] in done: continue
        try:
            for n, p in i['subs'].items(): uploadSubtitle(i['url'].split('?')[0].split('/')[-1], p, n)
            done.append(i['url'])
            json.dump(done, open('done.json', 'w'), indent=4)
        except Exception as e:
            print(e)
        print('Completed:', len(done), 'Total:', total)

