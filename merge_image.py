from PIL import Image
from natsort import natsorted  # per ordinare immagini
import os
import os.path
import sys

def main(dir):

    actual_dir = os.getcwd()
    new_dir = os.path.join(actual_dir, dir)
    if(not os.path.isdir(new_dir)):
        print(new_dir)
        return -1
    
    listImg = sorted(os.listdir(new_dir), key=lambda name: (int(name.split("_")[1].split(".")[0]), int(name.split("_")[0])))
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
            
    new_path = os.path.join(new_dir, firstImg)
    width, height = Image.open(new_path).size
    totalWidth = width * NUM_X 
    totalHeight = height * NUM_Y

    new_img = Image.new("RGB", (totalWidth, totalHeight), "white")    # "white" e' il colore di sfondo
    
    row = 0
    col = 0
    for file in listImg:
        path = os.path.join(new_dir, file)
        img = Image.open(path)

        x_idx = col * width
        y_idx = row * height
        new_img.paste(img, (x_idx, y_idx))

        col += 1
        if col == NUM_X:
            col = 0
            row += 1
    
    full_path = os.path.join(new_dir, "img_unita.jpg")
    new_img.save(full_path)
    return 0


if len(sys.argv) == 2:
    main(sys.argv[1])
else:
    print("Uso:", sys.argv[0], "nome_directory")
