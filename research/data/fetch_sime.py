"""Range-read the public SiME archive; cache and CRC-check individual members."""
from pathlib import Path
import io,json,urllib.request,zipfile,hashlib,time,re,sys
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/raw/sime2017'; OUT.mkdir(parents=True,exist_ok=True)
URL='https://ped.fz-juelich.de/data/experiments/2017.06.10_Wermelskirchen_SiME/data/2017sime/2017sime_trajectories_txt.zip'
class Remote(io.RawIOBase):
 def __init__(self):
  self.pos=0;self.requests=[];self.cache=[]
  index=OUT/'archive_index.json'
  self.size=json.loads(index.read_text())['archive_bytes'] if index.exists() else 0
  _,headers=self.fetch(0,0);self.size=int(headers['Content-Range'].split('/')[-1])
 def fetch(self,start,end):
  key=OUT/f'range_{start}_{end}.bin'
  if key.exists():return key.read_bytes(),{'Content-Range':f'bytes {start}-{end}/{self.size}'}
  if end-start+1>65536:
   parts=[(a,min(a+65535,end)) for a in range(start,end+1,65536)]
   with ThreadPoolExecutor(max_workers=3) as pool:
    chunks=list(pool.map(lambda bounds:self.fetch(*bounds)[0],parts))
   data=b''.join(chunks);key.write_bytes(data)
   return data,{'Content-Range':f'bytes {start}-{end}/{self.size}'}
  req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}','User-Agent':'Academic dataset feasibility audit'})
  t=time.monotonic()
  for attempt in range(3):
   try:
    with urllib.request.urlopen(req,timeout=30) as r:
     if r.status!=206:raise ValueError(f'Range request not supported: {r.status}')
     headers=dict(r.headers); data=r.read(end-start+1)
    break
   except (TimeoutError,OSError):
    if attempt==2:raise
  if len(data)!=end-start+1:raise ValueError('Truncated range')
  key.write_bytes(data)
  self.requests.append({'start':start,'end':end,'bytes':len(data),'seconds':round(time.monotonic()-t,2)})
  return data,headers
 def seekable(self):return True
 def readable(self):return True
 def tell(self):return self.pos
 def seek(self,n,whence=0):
  self.pos=n if whence==0 else self.pos+n if whence==1 else self.size+n
  return self.pos
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  if n==0 or self.pos>=self.size:return b''
  n=min(n,self.size-self.pos)
  for start,data in self.cache:
   if start<=self.pos and self.pos+n<=start+len(data):
    result=data[self.pos-start:self.pos-start+n];self.pos+=n;return result
  start=self.pos;end=min(self.size-1,start+max(n,65536)-1)
  data,_=self.fetch(start,end);self.cache.append((start,data))
  self.pos+=n;return data[:n]
def main():
 remote=Remote(); z=zipfile.ZipFile(remote)
 listing=[{'name':i.filename,'size':i.file_size,'compressed_size':i.compress_size,'crc32':i.CRC,'offset':i.header_offset} for i in z.infolist()]
 (OUT/'archive_index.json').write_text(json.dumps({'url':URL,'archive_bytes':remote.size,'members':listing},indent=2))
 if len(sys.argv)==1:
  print(json.dumps({'archive_bytes':remote.size,'members':listing[:30],'member_count':len(listing)},indent=2),flush=True)
 else:
  for target in sys.argv[1:]:
   names=[i.filename for i in z.infolist() if Path(i.filename).name==target and not i.is_dir()]
   if not names:raise ValueError('No match '+target)
   for name in names:
    dest=OUT/'members'/Path(name).name;dest.parent.mkdir(exist_ok=True)
    if not dest.exists():dest.write_bytes(z.read(name))
    else:
     import zlib
     assert zlib.crc32(dest.read_bytes())==z.getinfo(name).CRC
    print(json.dumps({'file':str(dest.relative_to(ROOT)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'crc_checked':True}),flush=True)
 (OUT/'last_access.json').write_text(json.dumps({'url':URL,'requests':remote.requests},indent=2))
if __name__=='__main__':main()
