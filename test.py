import re

r = re.compile(r'(?:S|s)?\s*(\d{1,2})\s*(?:E|e|x)\s*(\d{1,2})', re.IGNORECASE).search('S04 E01 Two Swords SDH.srt')

print(r.group(1), r.group(2))
