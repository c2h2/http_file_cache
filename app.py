from quart import Quart, request, send_from_directory, redirect
import json
import base58
import os
import urllib
import twint
import subprocess
import time

app = Quart(__name__)

STORE_LOC="stores"
DEFAULT_EXT="jpg"
RETRY_TIMES=2

# load conf
with open('./config.json') as f:
    config = json.load(f)
app.config.update(config)


def key_url_to_file(key, url):
    #ensure url safe.
    enc_key=str(base58.b58encode(key), 'utf-8')
    enc_url=str(base58.b58encode(url), 'utf-8')

    ext = url.split(".")[-1]
    if len(ext)>5:
        ext = DEFAULT_EXT
    fn = enc_key+"_"+enc_url+"."+ext
    path_fn = STORE_LOC+"/"+fn
    if os.path.exists(path_fn):
        #("SERVE FROM FILE")
        pass
    else:
        try:
            urllib.request.urlretrieve(url, path_fn)
        except:
            return STORE_LOC+"/"+"1500x500.png", "1500x500.png"

    return path_fn, fn

def get_twitter_lookup_json(username):
    path_fn = STORE_LOC+"/"+username+"_lookup.json"
    cmd = "twint --user-full --json -u " + username + " -o " + path_fn
    if os.path.exists(path_fn):
        pass
        #print("JSON FROM FILE")
    else:
        #os.remove(path_fn)
        for attempt in range(RETRY_TIMES):
            try:
                subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)           
            except subprocess.CalledProcessError as e:
                print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
                time.sleep(attempt*10) # longer and longer sleep
                continue
            break
    return path_fn


@app.route('/')
async def index():
    return 'Hello World, File Cache Server.'

@app.route('/file')
async def serve():
    path_fn, fn = key_url_to_file(request.args.get('key'), request.args.get('url'))
    return await send_from_directory(STORE_LOC, fn)

@app.route('/twitter_profile_image/<path>')
async def twitter_profile_image(path):
    path_fn = get_twitter_lookup_json(path)

    with open(path_fn) as json_file:
        content = json_file.read().split("\n")[0]
        data = json.loads(content)
        url = data["profile_image_url"]
    
    try:
        path_fn, fn = key_url_to_file("twitter_profile_image", url)
        return await send_from_directory(STORE_LOC, fn)
    except:
        return await send_from_directory(STORE_LOC, "1500x500.png") 

@app.route('/twitter_background_image/<path>')
async def twitter_background_image(path):
    path_fn = get_twitter_lookup_json(path)

    with open(path_fn) as json_file:        
        content = json_file.read().split("\n")[0]
        data = json.loads(content)
        url = data["background_image"]
    
    try:
        path_fn, fn = key_url_to_file("twitter_background_image", url)
        return await send_from_directory(STORE_LOC, fn) 
    except:
        return await send_from_directory(STORE_LOC, "1500x500.png") 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['SERVER_PORT'])
