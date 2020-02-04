from quart import Quart, request, send_from_directory
import json
import base58
import os
import urllib

app = Quart(__name__)

# load conf
with open('./config.json') as f:
    config = json.load(f)
app.config.update(config)

@app.route('/')
async def index():
    return 'Hello World'

@app.route('/file')
async def serve():
    key = request.args.get('key')
    url = request.args.get('url')
    enc_key=str(base58.b58encode(key), 'utf-8')
    enc_url=str(base58.b58encode(url), 'utf-8')

    ext = url.split(".")[-1]
    if len(ext)>5:
        ext = "unkonwn"
    fn = enc_key+"_"+enc_url+"."+ext
    path_fn = "stores/"+fn
    print(path_fn)
    if os.path.exists(path_fn):
        print("SERVE FROM FILE")
    else:
        urllib.request.urlretrieve(url, path_fn)
    return await send_from_directory('stores', fn)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['SERVER_PORT'])
