from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Request
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
import base64
from redlock import Redlock
import time
from fastapi.responses import FileResponse

dlm = Redlock([{"host": "localhost", "port": 6379, "db": 0}]) #metto una lock sulla porta 6379 del localhost, che è dove gira Redis

#imgReady = threading.Condition()
r = redis.Redis()
r.set("raman_state", "0")
r.set("operation_client", "0")
r.set("requestAval", "0")
r.set("acquisitionEnded", "0")
r.set("acquisitionState", "None")

WHITE_COLOR = 255
EDGE_MIN_PIXEL_DIMENSION = 20
PATH =r"C:\\Users\Giorgio\cartellaProva" #da file di configurazione

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


app = FastAPI(
    title="Scannerizzazione immagini LabSpec6",
    description="""Riceve immagini da LabSpec6, le analizza per trovare
        quelle che effettivamente contengono i campioni""",
    version="1.0.1"
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
        
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('off'); plt.imshow(binaryImg, cmap='gray'); plt.title("Imaged sent") # cambia img o binaryImg in base al metodo da usare
    #plt.show()

    if stato == "GLASS":
        return {
            'result': stato.name,
            'row': startRow * 820 / height
        }
    else:
        return {
            'result': stato.name,
            'row': -1
        }

#metodo che trova il pixel esatto di inizio del vetrino e fine del vetrino
#una volta trovato l'inizio del vetrino il motore di LabSpec6 si deve spostare in fondo e 
#si usa lo stesso processo per trovare la fine del vetrino
@app.post("/edgeImage", status_code=201)
async def edgeImage(file : UploadFile = File(...)):
    if(file.content_type != "image/jpeg"):
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
async def patternImage(file : UploadFile = File(...)):
    if(file.content_type != "image/jpeg"):
        stato = ResultImageProcessing.ERROR
        return {
            'result': stato.name,
            'row' : -1
        }

    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)
    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)

    filepath = os.path.join(PATH, file.filename)
    cv2.imwrite(filepath, img)
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('off'); plt.imshow(binaryImg, cmap='gray'); plt.title("Imaged sent") # cambia img o binaryImg in base al metodo da usare
    #plt.show()

    stato = ResultImageProcessing.EMPTY
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
async def endAcquisition():
    r.set("acquisitionState", "Started")
    process = subprocess.run(["python", r"D:\Giorgio\unipi\Tirocinio\VBScript\merge_image.py", PATH, "mosaicQualcosa"]) #parametro da ottenere da client  
    if process.returncode == 0:
        r.set("acquisitionState", "Ended")
        r.set("pathAcquisition", "mosaicQualcosa.jpg") 
    else:
        r.set("acquisitionState", "Error")

    return {"status": "done"}

@app.websocket("/stateWs")
async def receiveState(websocket: WebSocket):
    client = r.get("operation_client")
    if client.decode() == "1":
        print("client già connesso")
        return
    await websocket.accept()
    print("connessione accettata")
    r.set("operation_client", 1)

    while True:
        state = r.get("raman_state")
        print(state.decode())
        try:
            msg = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
        except asyncio.TimeoutError:
            msg = None
        except WebSocketDisconnect:
            r.set("operation_client", "0")
            break
        if state.decode() == "0":
            await websocket.send_text("Disconnected")

        operationState = r.get("acquisitionState")
        if operationState != "None":
            if operationState.decode() == "Error":
                await websocket.send_text("Error")  
                r.set("acquisitionState", "None")
            elif operationState.decode() == "Ended":
                path = r.get("pathAcquisition")
                path = path.decode()
                
                await websocket.send_text(path)  
                r.set("acquisitionState", "None")

        if msg == "acquisition":
            r.set("requestAval", "1")
            r.set("operation_client", "1")
            r.set("operationType", "acquisition")
        else:
            try:
                if state.decode() == "1":
                    await websocket.send_text("Connected")
            except WebSocketDisconnect:
                r.set("operation_client", "0")
                break

@app.get("/image/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(PATH, filename)
    if not os.path.exists(file_path):
        print("File non trovato!")
    return FileResponse(file_path, media_type="image/jpeg")

@app.patch("/ramanConnection", status_code=200)
async def ramanStatus(request:Request):
    r.set("raman_state", "1")
    print("LabSpec connesso")
    requestAval = r.get("requestAval")
    print(requestAval)
    
    while not requestAval.decode() == "1":
        if await request.is_disconnected():
            print("LabSpec disconnesso")
            r.set("raman_state", "0")
            return {"status": "Disconnected"}
        await asyncio.sleep(0.2)  
        requestAval = r.get("requestAval")

    newRequest = r.get("operationType")
    print(newRequest.decode())
    r.set("requestAval", "0")
    return {"status": newRequest.decode()}
    
     
#Start server with uvicorn
if __name__ == "__main__":
    #request = []
    #image = None
    uvicorn.run("server_scan_image:app", host="0.0.0.0", port=5500, reload=False, timeout_keep_alive=15, log_level="info", workers=2)