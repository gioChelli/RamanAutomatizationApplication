from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
from pydantic import BaseModel
from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from natsort import natsorted  # per ordinare immagini
import os
import os.path

WHITE_COLOR = 255
EDGE_MIN_PIXEL_DIMENSION = 10

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
    approxWidth = width / 10 * 9 # approssimazione della larghezza per trovare le linee anche se qualche pixel per errore è diverso
    startRow = -1 #riga del pixel di inizio del vetrino

    dst = cv2.Canny(binaryImg, 25, 100, None, 3)
    lines = cv2.HoughLinesP(dst, 1, np.pi / 180, 30, minLineLength = approxWidth, maxLineGap=10)

    if lines is not None: #approccio che funziona se non c'e un vetrino sopra
        
        stato = ResultImageProcessing.GLASS
        #print("linea trovata")
        x1, y1, x2, y2 = lines[0][0]
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
    
def mergeImages(path):
    
    listImg = sorted(os.listdir(path), key=lambda name: (int(name.split("_")[1].split(".")[0]), int(name.split("_")[0])))
    firstImg = listImg[0]
    START_Y = int(firstImg.split("_")[0])
    START_X = int(firstImg.split("_")[1].split(".")[0])
    
    NUM_X = 0
    NUM_Y = 0
    for im in listImg:
        y = int(im.split("_")[0])
        x = int(im.split("_")[1].split(".")[0])
        if x == START_X:
            NUM_X += 1
        if y == START_Y:
            NUM_Y += 1
            
    new_path = os.path.join(path, firstImg)
    width, height = Image.open(new_path).size
    totalWidth = width * NUM_X 
    totalHeight = height * NUM_Y

    new_img = Image.new("RGB", (totalWidth, totalHeight), "white")    # "white" e' il colore di sfondo
    
    row = 0
    col = 0
    for file in listImg:
        imgPath = os.path.join(path, file)
        img = Image.open(imgPath)

        x_idx = col * width
        y_idx = row * height
        new_img.paste(img, (x_idx, y_idx))

        col += 1
        if col == NUM_X:
            col = 0
            row += 1
    
    full_path = os.path.join(path, "img_unita.jpg")
    new_img.save(full_path)

    return full_path

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
    
@app.get("/startAcquisition", status_code=200)
async def startAcquisition():
    searchStatus = Status()
    print("nuova acquisizione")
    searchStatus.newAcquisition()
    return {"status": "boh"}

@app.post("/endAcquisition", status_code=201)
async def endAcquisition(payload: PathPayload = Form(...)):
    
    full_path = mergeImages(payload.path)

    img = cv2.imread(full_path, cv2.IMREAD_COLOR)
    if img is None:
        return {"status":"failed"}

    plt.figure(figsize=[15,8])
    plt.subplot(); plt.axis('off'); plt.imshow(img, cmap='gray'); plt.title("Imaged sent") # cambia img o binaryImg in base al metodo da usare
    plt.show()

    return {"status": "done"}
     
#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run("server_scan_image:app", host="0.0.0.0", port=5500, reload=False, timeout_keep_alive=0, log_level="info")