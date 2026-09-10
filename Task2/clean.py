from bs4 import BeautifulSoup
import sys

seen_titles = set()

def processPage(pageStr):
    data = BeautifulSoup(pageStr, features="lxml-xml")
    for page in data.findAll('page'):
        titles = page.findChildren('title')
        if len(titles) == 0:
            page.decompose()
            continue
        title = page.findAll('title')[0].text
        if title in seen_titles or title.startswith('Thread') or title.startswith('Message') or title.startswith('Board'):
            page.decompose()
            continue
        else:
            seen_titles.add(title)

        for revision in page.findAll('revision')[1:]:
            revision.decompose()
    return str(data).replace('<?xml version="1.0" encoding="utf-8"?>', '')


def removeHistory(path):
    outFile = open(path.replace('-history', ''), 'w')
    curPage = ''
    started = False
    for line in open(path):        
        if line == '<page>\n':
            started = True
            if curPage != '':
                newStr = processPage(curPage)
                outFile.write(newStr)
            curPage = line
        elif not started:
            outFile.write(line)
        else:
            curPage += line

    outFile.write('\n</mediawiki>\n')
    outFile.close() 

removeHistory(sys.argv[1])
