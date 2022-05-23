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

def main():
	session = requests.Session()
	session.headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
		"Accept-Encoding": "*",
		"Connection": "close"
	}
	session.keep_alive = False

	try:
		r = session.get('https://jut.su/watashi-ga-motenai/episode-1.html')
	except requests.exceptions.ConnectionError:
		print("CONECT ERROR")
		return
	print(r.status_code)
	soup=BeautifulSoup(r.content,'html.parser')
	item=soup.find(id="my-player")
	items=item.findAll('source')
	ll=[]
	for i in items:
		ll.append([ i['res'],i['src'] ])

	url=ll[0][1]
	response = session.get(url, stream=True)
	print(response.status_code)
	down(response)











main()