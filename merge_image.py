from PIL import Image
from natsort import natsorted  # per ordinare immagini
import os
import os.path
import sys

def main(dir):

    actual_dir = os.getcwd()
    new_dir = os.path.join(actual_dir, dir)
    if(not os.path.isdir(new_dir)):
        print("path non valido")
        return -1
    
    #numImg = len(os.listdir(new_dir))
    firstImg = os.listdir(new_dir)[0]
    path = os.path.join(new_dir, firstImg)
    width, height = Image.open(path).size
    totalWidth = (width) * 14 #valore assoluto che poi dovrò cambiare
    totalHeight = height * 10 #come sopra

    new_img = Image.new("RGB", (totalWidth, totalHeight), "white")    # "white" e' il colore di sfondo

    listImg = natsorted(os.listdir(new_dir))
    i = 0
    forCol = 0 
    forRow = 0
    
    for file in listImg:

        path = os.path.join(new_dir, file)
        img = Image.open(path)
        new_img.paste(img, (forCol, forRow))

        i += 1
        if(i % 10 == 0):
            i = 0
            forCol += width
            forRow = 0
        else:
            forRow += height
    
    # Salva la nuova immagine
    new_img.save(dir + "_unita.jpg")
    return 0


if len(sys.argv) == 2:
    main(sys.argv[1])
else:
    print("Uso:", sys.argv[0], "nome_directory")
