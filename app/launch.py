"""Serve the self-contained demo locally; Python standard library only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import argparse,webbrowser

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8770);parser.add_argument('--no-browser',action='store_true');parser.add_argument('--page',choices=['index.html','framework.html']);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(SimpleHTTPRequestHandler,directory=str(Path(__file__).parent)))
    page=args.page or ('framework.html' if (Path(__file__).parent/'framework_data_LOCAL_ONLY.js').exists() else 'index.html')
    url=f'http://127.0.0.1:{server.server_port}/{page}';print(url,flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
