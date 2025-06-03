import sys
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from natsort import natsorted
from pathlib import Path

def main():

    directory = Path(r"D:\Giorgio\unipi\Tirocinio\VBscript\colonne\acquisizione3")
    
    listImg = natsorted(os.listdir(directory))
    startRow = -1
    endRow = -1
    for img_name in listImg:
        
        path = directory / img_name
        
        imgOp = cv2.imread(str(path))
        img_gray = cv2.cvtColor(imgOp, cv2.COLOR_BGR2GRAY)
        matrix1 = np.ones(img_gray.shape, dtype="uint8") * 50 
        img_gray = cv2.subtract(img_gray, matrix1)

        _, img = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
        plt.figure(figsize=[15,8])
        plt.subplot(); plt.axis('off'); plt.imshow(img, cmap='gray'); plt.title("Imaged sent")
        plt.show()
        height, width = img.shape

        rowImg = img_name.split(".")[0]
        for i in range(height):
            n = 0
            for x in range(width):
                if img[i][x]==0:
                    n += 1
            if n > (width//2) and startRow == -1:
                startRow = int(rowImg)
                pixelStart = startRow + i
                print("trovato inizio bordo")
                print(str(pixelStart))
            
            elif n>(width//2) and startRow != -1 and startRow != rowImg:
                endRow = int(rowImg)
                pixelEnd = endRow + i
                print("trovato fine bordo")
                print(str(pixelEnd))
                return

main()