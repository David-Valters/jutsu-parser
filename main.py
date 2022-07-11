import os,requests
from bs4 import BeautifulSoup
import math
import sys
import time

units = {	
'B' : {'size':1, 'speed':'B/s'},
'KB' : {'size':1024, 'speed':'KB/s'},
'MB' : {'size':1024*1024, 'speed':'MB/s'},
'GB' : {'size':1024*1024*1024, 'speed':'GB/s'}
}

def check_unit(length): # length in bytes
    if length < units['KB']['size']:
        return 'B'
    elif length >= units['KB']['size'] and length <= units['MB']['size']:
        return 'KB'
    elif length >= units['MB']['size'] and length <= units['GB']['size']:
        return 'MB'
    elif length > units['GB']['size']:
        return 'GB'

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


def downloadFile(url, path,file_name,session) :
    with open(os.path.join(path,file_name+".mp4"), 'wb') as f:
        
        start = time.time() # start time
        r = session.get(url, stream=True)
        print (f"Downloading {file_name}\n")
        # total length in bytes of the file
        total_length = float(r.headers.get('content-length'))

        d = 0 # counter for amount downloaded

        # when file is not available
        if total_length is None:
            f.write(r.content)
        else:
            for chunk in r.iter_content(8192):
                
                d += float(len(chunk))
                f.write(chunk) # writing the file in chunks of 8192 bytes

                # amount downloaded in proper units
                downloaded = d/units[check_unit(d)]['size']
                
                # converting the unit of total length or size of file from bytes.
                tl = total_length / units[check_unit(total_length)]['size']
                
                trs = d // (time.time() - start) # speed in bytes per sec
                
                #speed in proper unit
                download_speed = trs/units[check_unit(trs)]['size']
                
                speed_unit = units[check_unit(trs)]['speed'] # speed in proper units

                done = 100 * d / total_length # percentage downloaded or done.
                
                fmt_string = "\r%6.2f %s [%s%s] %7.2f%s / %4.2f %s %7.2f %s"
                
                set_of_vars = ( float(done), '%',
                                '*' * int((done/2)/2),
                                '_' * int((50-done/2)/2),
                                downloaded, check_unit(d),
                                tl, check_unit(total_length),
                                download_speed, speed_unit)

                sys.stdout.write(fmt_string % set_of_vars)
                sys.stdout.flush()

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

class MySession():
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Encoding": "*"
    }
    # session.keep_alive = False
    def get(self,url,stream=False):
        print('...')
        return self.session.get(url,stream=stream)

class Taytl:
    url = "" #'https://jut.su/naruuto/season-2/episode-3.html'
    _soup=None
    path=[]
    def __init__(self,url:str,session):
        self._soup=None
        self.path=[]
        self.url=url
        self.exists =True
        try:
            r = session.get(self.url)
        except requests.exceptions.ConnectionError:
            print("CONECT ERROR\nВідсутнє підключення до інтернету або не дійсне посилання")
            self.exists=False
            return         
        self._soup=BeautifulSoup(r.content,'html.parser')
        if self.get_error_mes():
            print(self.get_error_mes())
            self.exists=False
            return None
        real_url=self._soup.find('link',rel='canonical')
        if real_url:
            real_url=real_url['href']
            if self.url!=real_url:                
                print(f'Посилання {self.url} переправлене на {real_url}')
                self.url=real_url
        else:
            print(f"Не вдалось визначити реальне посилання сторінки ({url}) по коду html або ви ввели не вірне посилання")
        self.path.append(self.get_name_taytl())
        if 'season' in url:
            i1=url.find('season')
            i2=url.find('/',i1)
            n=url[i1+7:i2]
            self.path.append(f"{n} сезон {self.path[0]}")

    def get_error_mes(self):
        item=self._soup.find('div',class_="clear berrors")
        if item:
            return item.text
        else:
            return None

    def get_name_with_url(self):#/naruuto/season-2/episode-3.htm
        i1=self.url.find('//')
        i2=self.url.find('/',i1+2)
        return self.url[i2:-1]

    def get_site_name(self):#https://jut.su
        i1=self.url.find('//')
        i2=self.url.find('/',i1+2)
        return self.url[:i2]

    def get_base_taytl_url(self):#https://jut.su/naruuto/
        arr=self.url.split('/')
        return "/".join(arr[:4])+'/'

    def _get_urls(self):
        last_href=''
        urls=self._soup.find_all('a')
        if urls==None:
            return None
        list_url=[]
        site_name=self.get_site_name()
        for i in urls:
            text=i.text.strip().split('\n')[0]
            try:
                href=i['href']
            except:
                continue
            if site_name not in href:
                href=site_name+href
            if href not in ['#', '/'] and self.get_name_with_url() in href and href!=self.url and href!=last_href:    
                last_href=href
                list_url.append({"url":href,"name":text})
        return list_url
    def get_name_taytl(self):#Наруто
        item= self._soup.find('a',href=self.get_base_taytl_url(),itemprop="item")
        return item.text.strip().replace("Смотреть ", "") if item else None

    def get_parts(self):
        list_part=[]
        for i in self._get_urls():
            if 'episode' not in i['url'] :
                list_part.append(i)
        return list_part

    def get_episodes(self):
        list_episod=[]
        for i in self._get_urls():
            if 'episode'  in i['url'] :
                list_episod.append(i)
        return list_episod

    def isEpisod(self):
        if '.html' in self.url:
            return True
        else:
            return False 


class Episod:
    url = ""
    _soup=None
    def __init__(self,url:str,session=None,soup=None):
        self.url=url
        if soup:
            self._soup=soup
        else:
            try:
                r = session.get(self.url)
            except requests.exceptions.ConnectionError:
                print("CONECT ERROR")
                return None
            self._soup=BeautifulSoup(r.content,'html.parser')

    @classmethod
    def fromTaytl(cls,taytl:Taytl):     
        return cls(taytl.url,soup=taytl._soup)

    def get_stream_urls(self):
        item=self._soup.find(id="my-player")
        if (item==None):
            return None
        items=item.findAll('source')
        strems=[]
        for i in items:
            strems.append({ "qua":i['res'],"url":i['src'] })#qua-якість
        return strems

    def get_name(self):#<span 
        item=self._soup.find('span',itemprop="description")
        if item == None:
            item=self._soup.find(itemprop="name")
        if item == None:
            return None
        else:      
            name :str = item.text      
            return name.replace("Смотреть ", "")

def menu_episodes(taytl:Taytl):
    list_episodes=[]
    eps=taytl.get_episodes()
    len_eps=len(eps)
    if len_eps==0:
        return [],None
    base_url=taytl.get_base_taytl_url()
    isBase = (True if base_url==taytl.url else False)
    print(f"[1]-Вибрати декілька серій \n[2]-Вибрати останню серію - ({len_eps}) \n[3]-Вибрати всі \n"+("" if isBase else "[0]-Головна сторінка тайтла\n")+"> ",end='')
    v=input_v(1-(0 if isBase else 1),len_eps)

    if v==0:
        return [], base_url

    if v==1:
        print(f"З якої серії почати завантажування(1-{len_eps})? ",end='')
        start=input_v(1,len_eps)
        print(f"По яку серію завантажувати({start}-{len_eps})? ",end='')
        end=input_v(start,len_eps)
        list_episodes=eps[start-1:end]
    elif v==2:
        list_episodes.append(eps[-1])
    elif v==3:
        for i in eps:
            list_episodes.append(i)
        
    return list_episodes, None
def menu_parts(taytl:Taytl):
    parts=taytl.get_parts()
    base_url=taytl.get_base_taytl_url()
    isBase = (True if base_url==taytl.url else False)
    print(f'Введіть номер розділа ')
    min=1
    if not isBase:
        print('[0]-Головна сторінка тайтла')
        min=0
    for count, item in enumerate(parts, start=1):
        print(f"[{count}]-{item['name']}")
    print("> ",end="")
    v=input_v(min,len(parts))
    if v==0:
        return base_url
    else:
        return parts[v-1]['url']
    
def main():
    print('start')
    url=input('Посилання на тайтл:')
    session=MySession()

    while True:
        taytl=Taytl(url, session)
        if not taytl.exists:
            return
        list_episodes=[]
        
        if taytl.isEpisod():
            list_episodes.append(Episod.fromTaytl(taytl))
            break
        else:
            parts=taytl.get_parts()
            if len(parts)==0:
                list_episodes,new_url=menu_episodes(taytl)
                if new_url:
                    url=new_url
                    continue
                break
            else:
                url=menu_parts(taytl)

    if len(list_episodes)!=0:
        print('Збирання даних')
        if not isinstance(list_episodes[0], Episod):
            list_episodes[0]=Episod(list_episodes[0]['url'],session)  

        ll=list_episodes[0].get_stream_urls()
        if not ll:
            print('\nПосилання не дійсне !!!')
            return        
        for i in ll:        
            i["res"]=(session.get(i['url'], stream=True))
        j=1
        print('Виберіть якість: ')
        kl_ep=len(list_episodes)
        subs="/Enter"
        for i in ll:
            print(f"[{j}{subs}] { i['qua'] } {'~' if kl_ep>1 else ''}{convert_size( int(i['res'].headers.get('content-length'))*kl_ep  )}")
            subs=""
            j+=1
        v=input_v(1,len(ll),[''])
        if v=='':
            v=0
        else:
            v-=1
        path="Download"
        for i in taytl.path:
            path=os.path.join(path,i)
        os.makedirs(path, exist_ok=True)
        for i in list_episodes:
            if not isinstance(i, Episod):
                i=Episod(i['url'],session)
            strem_url=i.get_stream_urls()[v]['url']
            downloadFile(strem_url,path,i.get_name(),session)
    else:
        print('На цій сторінці не найдені серії для вибору ')

if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print(' ')
        print("Помилкаа імпорту бібліотеки,введіть 'python -m pip install -r requirements.txt' якщо не допоможt то примусовов обновіть файли 'python update.py'")
    except requests.ConnectionError as e:
        print("OOPS!! Помилка з'єднання. Переконайтеся, що ви підключені до Інтернету.\n")
        print(str(e))			       
    except requests.Timeout as e:
        print("OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("\n\nНе дійсне посилання")
        print(str(e))
        # print (traceback.format_exc())
        
    except KeyboardInterrupt:
        print("\nХтось закрив програму")