from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Request, HTTPException, Body, BackgroundTasks
import uvicorn
from pydantic import BaseModel
from enum import Enum
import numpy as np
import cv2
import math
import os
import os.path
import subprocess
#import threading
import redis
import asyncio
import json
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import tempfile
import zipfile
import base64
from .merge_image import main

r = redis.Redis()
r.set("raman_state", "0")
r.set("operation_client", "0")
r.set("requestAval", "0")
r.set("acquisitionEnded", "0")
r.set("acquisitionState", "None")
r.set('ramanX', "-1")
r.set('ramanY', "-1")

WHITE_COLOR = 255
EDGE_MIN_PIXEL_DIMENSION = 20

class Pattern:
    def __init__(self):
        self.startRowPattern = -1
        self.startColumnPattern = -1
        self.endRowPattern = -1
        self.endColumnPattern = -1
        
class Status:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.glassStartFound = False
            self.glassEndFound = False
            self._initialized = True
            self.startGlass = -1
            self.endGlass = -1
    
    def glassStartFounded(self, row):
        self.glassStartFound = True
        self.startGlass = row

    def glassEndFounded(self, row):
        self.glassEndFound = True
        self.endGlass = row

    def newAcquisition(self):
        self.glassStartFound = False
        self.glassEndFound = False
        self._initialized = True
        self.startGlass = -1
        self.endGlass = -1

@asynccontextmanager
async def lifespan(app: FastAPI):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)
        app.state.PATH = config["path"]
        app.state.PATH_RESOLUTION = config["path_resolution"]
        os.makedirs(app.state.PATH, exist_ok=True)
        os.makedirs(app.state.PATH_RESOLUTION, exist_ok=True)
    yield None

app = FastAPI(
    title="Scannerizzazione immagini LabSpec6",
    description="""Riceve immagini da LabSpec6, le analizza per trovare
        quelle che effettivamente contengono i campioni""",
    version="1.0.1",
    lifespan=lifespan
)

class ResultImageProcessing(Enum):
    ERROR = 0
    PATTERN = 1
    GLASS = 2
    EMPTY = 3

class GlassType(Enum):
    TWO_COLORED = 0
    TWO_WHITE = 1
    ONE_COLORED = 2
    ONE_WHITE = 3
    ONE_BOTH = 4
    EMPTY = 5

class PathPayload(BaseModel):
    path: str

def searchEdge(img):

    stato = ResultImageProcessing.EMPTY
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binaryImg = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    height, width = binaryImg.shape
    approxWidth = width / 5 * 3 # approssimazione della larghezza per trovare le linee anche se qualche pixel per errore è diverso
    startRow = -1 #riga del pixel di inizio del vetrino
    
    dst = cv2.Canny(img_gray, 50, 150, None, 3)
    lines = cv2.HoughLinesP(dst, 1, np.pi / 180, 10, minLineLength = 50, maxLineGap=20)

    if lines is not None: #approccio che funziona se non c'e un vetrino sopra
        print(len(lines))
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = x2 - x1
            dy = y2 - y1
    
            if dx == 0:
                angle_deg = 90  # linea verticale
            else: #calcola angolo con asse x
                angle_rad = math.atan2(dy, dx)
                angle_deg = abs(math.degrees(angle_rad))
        
            if angle_deg < 30 or angle_deg > 150: #tolleranza, definire costanti
            
                stato = ResultImageProcessing.GLASS
                print("linea trovata")
                startRow = y1
                break
    else:
        pixelYnum = 0
        for i in range(height): #metodo per vetrini con vetrino sovrapposto
            n = 0
            for x in range(width):
                if binaryImg[i][x] == WHITE_COLOR:
                    n += 1
            if n > (approxWidth):
                pixelYnum += 1
                if startRow  == -1:
                    startRow = i
        print(pixelYnum)
        if pixelYnum > EDGE_MIN_PIXEL_DIMENSION and pixelYnum < height / 2:
            stato = ResultImageProcessing.GLASS
    
    print(startRow)
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('off'); plt.imshow(binaryImg, cmap='gray'); plt.title("Imaged sent") # cambia img o binaryImg in base al metodo da usare
    #plt.show()

    if stato.name == "GLASS":
        return {
            'result': stato.name,
            'row': int(startRow * 810 / height) 
        }
    else:
        return {
            'result': stato.name,
            'row': -1
        }

# metodo che trova il pixel esatto di inizio del vetrino e fine del vetrino
#una volta trovato l'inizio del vetrino il motore di LabSpec6 si deve spostare in fondo e 
#si usa lo stesso processo per trovare la fine del vetrino
@app.post("/edgeImage", status_code=201)
async def edgeImage(file : UploadFile = File(...)):
    stop = r.get("stop")

    if(file.content_type != "image/jpeg" or stop.decode() == "1"):
        stato = ResultImageProcessing.ERROR
        return {
            'result': stato.name,
            'row' : -1
        }
    
    searchStatus = Status()
    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)

    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)

    res = searchEdge(img)
    print(res["result"])
    row = int(file.filename.split(".")[0])
    print(row)
    res["row"] = res["row"] + row

    if not searchStatus.glassStartFound:
        
        if res["result"] == "GLASS":
            print(res["row"])
            searchStatus.glassStartFounded(res["row"])  
    elif not searchStatus.glassEndFound:
        
        if res["result"] == "GLASS":
            print(res["row"])
            searchStatus.glassEndFounded(res["row"])
       
    return res

#post per ricevere immagini che cercano punti dove e presente l'immagine
@app.post("/patternImage", status_code=201)
async def patternImage(request: Request, file : UploadFile = File(...)):
    #stop = r.get("stop")
    if(file.content_type != "image/jpeg"):
        #stato = ResultImageProcessing.ERROR
        return {
            'result': "error",
        }

    path = request.app.state.PATH
    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)
    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)
    print(path)
    filepath = os.path.join(path, file.filename)
    cv2.imwrite(filepath, img)

    return {
        "result": "OK"
    }

@app.post("/highResolutionImage", status_code=201)
async def patternImage(request: Request, file : UploadFile = File(...)):
    if(file.content_type != "image/jpeg"):
        return {
            "status": "error",
        }

    path = request.app.state.PATH_RESOLUTION
    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)
    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)
    print(path)
    filepath = os.path.join(path, file.filename)
    cv2.imwrite(filepath, img)
    return {
        "status": "OK"
    }
    
@app.patch("/startAcquisition", status_code=200)
async def startAcquisition():
    searchStatus = Status()
    print("nuova acquisizione")
    searchStatus.newAcquisition()
    return {
        "status": "OK"
    }

@app.patch("/endAcquisition", status_code=200)
async def endAcquisition(request: Request):
    path = request.app.state.PATH
    merge = main(path, "mosaicQualcosa")
    if merge == 0:
        r.set("acquisitionState", "Ended")
        r.set("pathAcquisition", "mosaicQualcosa.jpg")
    # process = subprocess.run(["python", "merge_image.py", path, "mosaicQualcosa"])  
    # if process.returncode == 0:
    #     r.set("acquisitionState", "Ended")
    #     r.set("pathAcquisition", "mosaicQualcosa.jpg") 
    # else:
    #     r.set("acquisitionState", "Error")

    return {"status": "done"}

@app.patch("/endRamanAcquisition", status_code=200)
async def endRamanAcquisition(request: Request):
        
    data = await request.json()

    filename = data.get("filename", "default.txt")
    content = data.get("content", "")
    path = request.app.state.PATH
    file_location = os.path.join(path, filename)

    with open(file_location, "wb") as f:
        f.write(base64.b64decode(content))
    
    r.set("pathAcquisition", filename) 
    r.set("acquisitionState", "Ended")
        
    return {"status": "done"}

@app.patch("/endPatternAcquisition", status_code=200)
async def endPatternAcquisition(request: Request):
        
    path = request.app.state.PATH_RESOLUTION
    
    r.set("pathAcquisition", path) 
    r.set("acquisitionState", "Ended")
        
    return {"status": "done"}

@app.websocket("/stateWs")
async def receiveState(websocket: WebSocket):
    
    await websocket.accept()
    print("connessione accettata")

    while True:
        
        try:
            msg = await asyncio.wait_for(websocket.receive_text(), timeout=20.0)
            msg = json.loads(msg)
            print(msg)
        except asyncio.TimeoutError:
            msg = None
        except WebSocketDisconnect:
            break
        state = r.get("raman_state")
        try:
            if state.decode() == "0":
                result = {"state":"disconnected"}       
            elif state.decode() == "1":
                result = {"state":"connected"}
        except WebSocketDisconnect:
            break

        operationState = r.get("acquisitionState").decode()
        if operationState != "None": 
            print(operationState)
            r.set("acquisitionState", "None")
            op = r.get("operationType")
            path = r.get("pathAcquisition").decode()
            if operationState == "Error": 
                r.set("raman_state", "0")
                result = {"state":"error"}
            else:
                result = {"state":"done", "operation":op.decode(), "path":path}
            print(result)
            await websocket.send_text(json.dumps(result))
            continue       
        
        if msg is None:
            continue
        elif msg["request"] == "acquisition":
            pipe = r.pipeline()
            pipe.set("operationType", "acquisition") 
            pipe.set("requestAval", "1")
            pipe.set("stop", "0")
            pipe.execute()
            result = {"state":"started"}      
        elif msg["request"] == "ramanAcquisition":
            print("avvio acquisizione")
            pipe = r.pipeline()
            pipe.set("operationType", "ramanAcquisition")
            pipe.set("ramanX", str(msg["ramanX"]))
            pipe.set("ramanY", str(msg["ramanY"]))
            pipe.set("requestAval", "1")
            pipe.execute()
            result = {"state":"started"}  
        elif msg["request"] == "patternAcquisition":
            pipe = r.pipeline()
            pipe.set("operationType", "patternAcquisition") 
            pipe.set('startX', str(msg["min_x"]))
            pipe.set('startY', str(msg["min_y"]))
            pipe.set('scope', str(msg["scope"]))
            pipe.set("requestAval", "1")
            pipe.execute()
            result = {"state":"started"}
        elif msg["request"] == "stopAcquisition":
            r.set("stop", "1")
        
        print(result)
        await websocket.send_text(json.dumps(result))
            
@app.get("/image/{filename}")
async def get_image(request: Request,  background_tasks: BackgroundTasks, filename: str):
    path = request.app.state.PATH
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Immagine non trovata")
    background_tasks.add_task(cleanup_folder_and_zip, path)
    return FileResponse(file_path, media_type="image/jpeg")

@app.get("/raman/{filename}")
async def get_raman(request: Request,  background_tasks: BackgroundTasks, filename: str):
    path = request.app.state.PATH
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File non trovato")
    
    background_tasks.add_task(cleanup_folder_and_zip, path)
    return FileResponse(file_path, media_type="text/plain", filename=filename)

def cleanup_folder_and_zip(folder_path: str, zip_path: str = None):
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Errore nella rimozione di {file_path}: {e}")

    if zip_path and os.path.exists(zip_path): 
        try:
            os.remove(zip_path)
        except Exception as e:
            print(f"Errore nella rimozione dello zip: {e}")

@app.get("/highResolutionImages")
async def get_high_resolution(request: Request, background_tasks: BackgroundTasks):
    
    path = request.app.state.PATH_RESOLUTION
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        with zipfile.ZipFile(tmp, 'w') as archive:
            for filename in os.listdir(path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.bmp')):
                    file_path = os.path.join(path, filename)
                    archive.write(file_path, arcname=filename)
        tmp_path = tmp.name

    zip_filename = os.path.basename(path.rstrip("/")) + ".zip"

    background_tasks.add_task(cleanup_folder_and_zip, path, tmp_path)
    return FileResponse(tmp_path, filename=zip_filename, media_type='application/zip')

@app.patch("/ramanConnection", status_code=200)
async def ramanStatus(request:Request):
    client_host, client_port = request.client
    r.set("raman_state", "1")
    print("LabSpec connesso")
    print(f"PATCH /ramanConnection chiamato da {client_host}:{client_port}")
    requestAval = r.get("requestAval")
    
    if requestAval.decode() == "1":
        newRequest = r.get("operationType").decode()
        print("inizio su LabSpec")
        r.set("requestAval", "0")
        if newRequest == "acquisition":
            return {"status": newRequest}
        elif newRequest == "ramanAcquisition":
            x = r.get("ramanX").decode()
            y = r.get("ramanY").decode()
            return {"status":newRequest, "x": x, "y":y}
        elif newRequest == "patternAcquisition":
            x = r.get("startX").decode()
            y = r.get("startY").decode()
            scope = r.get("scope")
            return {"status": newRequest, "x": x, "y": y, "scope":scope}
    else:
        return {"status": "waiting"}
    
#Start server with uvicorn
#if __name__ == "__main__":
def start_raman_server():

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)

        HOST = config['host']
        PORT = config['port']
    uvicorn.run(app, host=HOST, port=PORT, reload=False, timeout_keep_alive=30, log_level="info", workers=1)