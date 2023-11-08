import os
import cv2

from tqdm import tqdm

def extractLetters(s):
    # Función para extraer solo las letras del nombre de la imagen
    return ''.join(filter(str.isalpha, os.path.splitext(s)[0]))

def extractNumbers(s):
    # Función para extraer el número de una cadena
    try:
        numStr = ''.join(filter(str.isdigit, s))
        if numStr != '':
            return int(numStr)
        else:
            return 0
    except ValueError:
        return s

class Images:
    __entity = None
    
    __imageInfoList = [] # lista de las imágenes con su nombre
    def __new__(cls, input_dir):
        if cls.__entity is None:
            cls.__entity = super(Images, cls).__new__(cls)
            cls.__entity.__initialize(input_dir)
        return cls.__entity

    def __initialize(self, input_dir):
        print("\nLoading images...")

        nameList = os.listdir(input_dir)
        nameList.sort(key=extractNumbers)
        for fileName in tqdm(nameList): # Recorre los archivos de la carpeta de entrada
            if fileName.endswith(".jpg") or fileName.endswith(".png"):
                imagen = cv2.imread(os.path.join(input_dir, fileName), cv2.IMREAD_UNCHANGED)
                self.__imageInfoList.append([imagen, extractLetters(os.path.splitext(fileName)[0])])
        
    def splitImages(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        numImagen = 1
        for imageInfo in self.__imageInfoList:
            image, imageName = imageInfo
            height, width, _ = image.shape
            
            for y1 in tqdm(range(0, height, width)):
                y2 = y1 + width
                if y2 > height:
                    y2 = height
                    
                splitImage = image[y1:y2, 0:width]
                nombreImagen_salida = imageName + f"_{numImagen}.jpg"
                
                dir_salida = os.path.join(output_dir, nombreImagen_salida)
                cv2.imwrite(dir_salida, splitImage)
                
                numImagen += 1

    def getImagesInfoList(self):
        return self.__imageInfoList
    
    def concatenateImages(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        heightSum = 0
        num = 1
        
        pos1 = 0

        imageList = [subList[0] for subList in self.__imageInfoList]

        for pos2 in tqdm(range(len(imageList))):
            image, imageName = self.__imageInfoList[pos2]
            heightImage = image.shape[0]
            if(heightSum + heightImage > 60000):
                concatImage = cv2.vconcat(imageList[pos1:pos2+1])
                
                cv2.imwrite(os.path.join(output_dir, imageName + f"_{num}.jpg"), concatImage)
                
                pos1 = pos2 + 1
                heightSum = 0
                num += 1
            else:
                heightSum += heightImage
        
        if(heightSum != 0):
            concatImage = cv2.vconcat(imageList[pos1:])
            cv2.imwrite(os.path.join(output_dir, imageName + f"_{num}.jpg"), concatImage)