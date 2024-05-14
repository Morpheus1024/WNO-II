
from PIL import Image
import os
import numpy as np

zdjecia = []
sciezka_zdjecia = 'Data/przedmioty'
for zdjecie in os.listdir(sciezka_zdjecia): zdjecia.append(Image.open(sciezka_zdjecia + '/' + zdjecie))

stocks = []
sciezka_stock = 'Data/stock_png'
for zdjecie in os.listdir(sciezka_stock): stocks.append(Image.open(sciezka_stock + '/' + zdjecie))
    
i = 0
path_dataset = 'Dataset'
# Create a text file


for stock in stocks:
    if stock.size[0] > 0 or stock.size[1] > 0: stock = stock.resize((600,600))
 
    for image in zdjecia:
       #get image name
        klasa = os.path.basename(image.filename)

        if "sword" in klasa: klasa = 0  
        elif "komb" in klasa: klasa = 1
        elif "driver" in klasa: klasa = 2

        image = image.resize((int(150), int(150)))
    
        heigth, width = image.size

        angle = np.random.randint(-89, 90)

        x = np.random.randint(0, stock.size[0]-width)
        y = np.random.randint(0, stock.size[1]-heigth)

        nowy_obraz = stock.copy()
        nowy_obraz.paste(image.rotate(angle), (x, y), image.rotate(angle))

        nowy_obraz.save(f'{path_dataset}/{i}.jpg')

        with open('dataset.txt', 'a') as file:
            file.write(f'{i}.jpg, {x}, {y}, {width}, {heigth}, {klasa}\n')

        i += 1
        nowy_obraz = None
