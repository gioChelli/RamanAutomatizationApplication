from fastapi import FastAPI, UploadFile, File
import uvicorn
from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt

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
            self.pattern = []
    
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
        self.pattern = []
        print("resetto")

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

def searchEdge(img):
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    matrix1 = np.ones(img_gray.shape, dtype="uint8") * 60 
    img_gray = cv2.subtract(img_gray, matrix1)
    _, binaryImg = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)

    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('off'); plt.imshow(binaryImg, cmap='gray'); plt.title("Imaged sent") # cambia img o binaryImg in base al metodo da usare
    #plt.show()
    
    height, width = binaryImg.shape
    startRow = -1 #riga del pixel di inizio del vetrino
    pixelYnum = 0
    for i in range(height):
        n = 0
        for x in range(width):
            if binaryImg[i][x]==255:
                n += 1
        if n > (width*3/4):
            pixelYnum += 1
            if startRow  == -1:
                startRow = i

    if pixelYnum > 5 and pixelYnum < 30:
        stato = ResultImageProcessing.GLASS
        return {
            'result': stato.name,
            'row': startRow * 820 / binaryImg.shape[1]
        }
    else:
        stato = ResultImageProcessing.EMPTY
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
    print(searchStatus.glassStartFound)
    
    if not searchStatus.glassStartFound:
        
        if res["result"] == "GLASS":
            print("Trovato inizio")
            searchStatus.glassStartFounded(res["row"])
        
    elif not searchStatus.glassEndFound:
        
        if res["result"] == "EMPTY":
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
    
    searchStatus = Status()
    
    array = file.filename.split("_")
    print(array)
    x = int(array[0])
    y = int(file.filename.split(".")[0])

    byteImg = await file.read()
    npImg = np.frombuffer(byteImg, np.uint8)
    img = cv2.imdecode(npImg, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binaryImg = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    _, contours = cv2.findContours(binaryImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    filter_contours = []
    for cnt in contours:
        first = cnt[0][0]
        last = cnt[-1][0]
        if np.linalg.norm(np.array(first) - np.array(last)) < 1.0:
            filter_contours.append(cnt)

    img = np.zeros(binaryImg.shape, dtype="uint8")
    if(len(filter_contours)):
        cv2.drawContours(img, filter_contours, -1, 255, 2)
    plt.figure(figsize=[15,8])
    plt.subplot(); plt.axis('off'); plt.imshow(binaryImg, cmap='gray'); plt.title("Imaged sent") # cambia img o binaryImg in base al metodo da usare
    plt.show()

    stato = ResultImageProcessing.ERROR
    return { 
        'result': stato.name,
        'row' : -1,
        'column': -1
    }
    
@app.get("/startAcquisition", status_code=200)
async def startAcquisition():
    searchStatus = Status()
    print("qua")
    searchStatus.newAcquisition()
     
#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run("server_scan_image:app", host="0.0.0.0", port=5500, reload=True, timeout_keep_alive=0, log_level="info")