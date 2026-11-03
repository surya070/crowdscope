"""Serve the self-contained synthetic movement demo using only Python's stdlib."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import argparse, subprocess, sys, webbrowser

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--port',type=int,default=8766)
 parser.add_argument('--no-browser',action='store_true')
 parser.add_argument('--regenerate',action='store_true',help='Rerun JuPedSim first; requires the root requirements.txt environment')
 args=parser.parse_args()
 root=Path(__file__).resolve().parents[2]
 if args.regenerate:
  subprocess.run([sys.executable,str(root/'research/assistance/run_presentation_demo.py')],cwd=root,check=True)
 folder=root/'output/assistance_live_demo'
 if not (folder/'replay.html').is_file():
  parser.error('Replay is missing. Obtain the saved demo files or use --regenerate with the project dependencies installed.')
 handler=partial(SimpleHTTPRequestHandler,directory=str(folder))
 try: server=ThreadingHTTPServer(('127.0.0.1',args.port),handler)
 except OSError:
  if args.port==0: raise
  server=ThreadingHTTPServer(('127.0.0.1',0),handler)
 url=f'http://127.0.0.1:{server.server_port}/replay.html'
 print(f'Assistance demo: {url}\nPress Ctrl+C to stop.',flush=True)
 if not args.no_browser:webbrowser.open(url)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()

if __name__=='__main__':main()
