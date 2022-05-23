import os,requests
from bs4 import BeautifulSoup
import math
import sys

def download(get_response):
    file_name  = "hz.mp4"
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def convert_size(size_bytes,write_type=1):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   s='%.2f' % s
   if(write_type):
       return "%s %s" % (s, size_name[i])
   else:
       return s
def down(response,file_name="hz.mp4",path=''):
    with open(os.path.join(path,file_name), "wb") as f:
        if response.status_code!=200:
                print("Error conect to player: "+str(response.status_code))
                return None
        print("Downloading %s" % file_name)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            finish=f"Done({convert_size(total_length)})             "
            for data in response.iter_content(chunk_size=1024 * 1024):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                status=f"{convert_size(dl)}/{convert_size(total_length)}"

                sys.stdout.write(f"\r[%s%s] {(lambda dl: status if dl!=total_length else finish    )(dl)}   " % ('#' * done, '-' * (50-done)) )	
                sys.stdout.flush()
            print()
def input_v(min:int,maxx:int=None,list=[])->int:
    while True:
        try:
            v=input()
            if list!=[]:
                for i in list:
                    if i==v:
                        return i
            v=int(v)
            if v<min:
                print('Введене число менше допустимого')
                continue
            if maxx!=None and v>maxx:
                print('Введене число більше допустимого')
                continue
        except ValueError:
            print('Введіть число ')  
            continue
        return v
def main():
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
        "Accept-Encoding": "*",
        "Connection": "close"
    }
    session.keep_alive = False

    URL=input('Введіть посилання (приклад https://jut.su/naruuto/season-1/episode-133.html): ')
    try:
        r = session.get(URL)
    except requests.exceptions.ConnectionError:
        print("CONECT ERROR")
        return
    print(r.status_code)
    soup=BeautifulSoup(r.content,'html.parser')
    item=soup.find(id="my-player")
    items=item.findAll('source')
    ll=[]
    for i in items:
        ll.append({ "qua":i['res'],"url":i['src'] })#qua-якість

    print('Load...')
    for i in ll:        
        i["res"]=(session.get(i['url'], stream=True))
    j=1
    print('Виберіть якість: ')
    subs="/Enter"
    for i in ll:
        print(f"[{j}{subs}] { i['qua'] } {convert_size( int(i['res'].headers.get('content-length'))  )}")
        subs=""
        j+=1
    v=input_v(1,len(ll),[''])
    if v=='':
        v=0
    else:
        v-=1
    response=ll[v]["res"]
    URL=ll[v]["url"]
    print(response.status_code)
    name=URL.split("/")[-1].split(".")[0]+f"_{ll[v]['qua']}_"+".mp4"
    down(response,name)
    input('нажміть Enter щоб закрити вікно')











main()