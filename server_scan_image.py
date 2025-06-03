from fastapi import FastAPI, UploadFile, File
import uvicorn
from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

class Status:
    _instance = None
    _initialized = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.glassStartFound = False
            self.glassEndFound = False
            self._initialized = True
            self.startGlass = -1
            self.endGlass = -1
            self.startRowPattern = -1
            self.startColumnPattern = -1
            self.endRowPattern = -1
            self.endColumnPattern = -1
    
    def glassStartFounded(self, row):
        self.glassStartFound = True
        self.startGlass = row

    def glassEndFounded(self, row):
        self.glassEndFound = True
        self.endGlass = row

app = FastAPI(
    title="Scannerizzazione immagini LabSpec6",
    description="""Riceve immagini da LabSpec6, le analizza per trovare
        quelle che effettivamente contengono i campioni""",
    version="1.0.0"
)

class ResultImageProcessing(Enum):
    ERROR = 0
    PATTERN = 1
    GLASS = 2
    EMPTY = 3

async def searchEdge(file):
    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)

    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    matrix1 = np.ones(img_gray.shape, dtype="uint8") * 50 
    img_gray = cv2.subtract(img_gray, matrix1)
    _, img = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('off'); plt.imshow(img, cmap='gray'); plt.title("Imaged sent")
    #plt.show()
    height, width = img.shape
    startRow = -1
    for i in range(height):
        n = 0
        for x in range(width):
            if img[i][x]==0:
                n += 1
        if n > (width//2) and startRow == -1:
            startRow = i
            print("trovato inizio bordo")
            print(str(startRow))
            return startRow
    
    return -1


#metodo che trova il pixel esatto di inizio del vetrino
@app.post("/edgeImage", status_code=201)
async def edgeImage(file1 : UploadFile = File(...), file2 : UploadFile = File(...)):
    if(await file1.content_type != "image/jpg" or await file2.content_type != "image/jpg"):
        return {
            'row': -1,
            'pixel': -1
        }
    
    res1 = searchEdge(file1)
    res2 = searchEdge(file2)

    if res1 <= -1 and res2 <= -1:
        return{
            'row': -1,
            'pixel': -1
        }
    elif res1 > -1:
        return{
            'row': 1,
            'pixel': res1
        }
    elif res2 > -1:
        return{
            'row': 2,
            'pixel': res2
        }
    

#metodo che trova la prima immagine dove il laser riflette
@app.post("/laserImage", status_code=201)
async def newLaserImage(row : int, file : UploadFile = File(...)):
    if(await file.content_type != "image/jpg"):
        stato = ResultImageProcessing.ERROR
        return {
            'result': stato.name
        }
    
    searchStatus = Status()
    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)

    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)

    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('off'); plt.imshow(img); plt.title("Imaged sent")
    #plt.show()

    if not searchStatus.glassStartFound:
        result = scanImage(img)
        if result[result] == ResultImageProcessing.GLASS:
            searchStatus.glassStartFounded(row)
        return result
    elif not searchStatus.glassEndFound:
        result = scanImage(img)
        if result[result] == ResultImageProcessing.EMPTY:
            searchStatus.glassEndFounded(row)
        return result


def scanImage(img):
    center = (img.shape[0]//2, img.shape[1]//2)
    crop_img = img[center[0]-20:center[0]+20, center[1]-20:center[1]+20]
    stato = ResultImageProcessing.ERROR

    blue = green = red = 0
    for row in crop_img:
        for pixel in row:
            blue += pixel[0]
            green += pixel[1]
            red += pixel[2]
        
    blue /= crop_img.shape[0] * crop_img.shape[1]
    green /= crop_img.shape[0] * crop_img.shape[1]
    red /= crop_img.shape[0] * crop_img.shape[1]
    if(green > 50):
        stato = ResultImageProcessing.GLASS
    elif(green < 20 and blue < 20 and red < 20):
        stato = ResultImageProcessing.EMPTY
        
    return {'result': stato.name}

    

#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run("server_scan_image:app", host="0.0.0.0", port=5500, reload=True, timeout_keep_alive=0, log_level="info")