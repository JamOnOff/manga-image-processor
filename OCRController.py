import os
import cv2
import easyocr
import torch

from tqdm import tqdm

class OCRController:
    __entity = None
    
    __reader = None
    __data = None

    __device = None
    def __new__(cls, detectLanguage):
        if cls.__entity is None:
            cls.__entity = super(OCRController, cls).__new__(cls)
            cls.__entity.__initialize(detectLanguage)
        return cls.__entity


    def __initialize(self, detectLanguage):
        # Verifica si CUDA (GPU) está disponible
        if torch.cuda.is_available():
            self.__device = 'cuda'
        else:
            self.__device = 'cpu'
        
        # Inicializa EasyOCR con el dispositivo apropiado
        if type(detectLanguage) is list:
            self.__reader = easyocr.Reader(detectLanguage, model_storage_directory=None, gpu=self.__device)
        else:
            self.__reader = easyocr.Reader([detectLanguage], model_storage_directory=None, gpu=self.__device)

    def __cleanData(self, data):
        if len(data) == 2 and type(list[-1]) is str: # 1 sublista con las coordenadas y 1 con el texto
            return data
        
        cleanList = []
        for d in data:
            if not d: # si la sublista está vacia
                continue
            if len(data) == 2 and type(data[-1]) is str:
                cleanList.append(d)
                continue

            subLista = self.__cleanData(d)
            if subLista:
                cleanList.append(subLista)
        
        return cleanList

    def __detectCollision_aux(self, list1 , list2):
        dist = 10
        p1 = list1[0]
        p2 = list1[1]
        p3 = list1[2]
        
        if p1[0] - dist < list2[0][0] and list2[0][0] < p2[0] + dist and p1[1] - dist < list2[0][1] and list2[0][1] < p3[1] + dist:
            return True
        if p1[0] - dist < list2[1][0] and list2[1][0] < p2[0] + dist and p1[1] - dist < list2[1][1] and list2[1][1] < p3[1] + dist:
            return True
        if p1[0] - dist < list2[2][0] and list2[2][0] < p2[0] + dist and p1[1] - dist < list2[2][1] and list2[2][1] < p3[1] + dist:
            return True
        if p1[0] - dist < list2[3][0] and list2[3][0] < p2[0] + dist and p1[1] - dist < list2[3][1] and list2[3][1] < p3[1] + dist:
            return True
        
        return False
    
    def __detectCollision(self, list1 , list2):
        return (self.__detectCollision_aux(list1, list2) or self.__detectCollision_aux(list2, list1))

    def __mergeBoxes(self, boxList):
        mergedList = []
        merge = False

        while boxList: # mientras la lista no esté vacia
            subL1 = boxList.pop(0)
            mergedBox = []

            addBox = True # si se agrega la caja a la lista
            for i in range(len(boxList)):
                subL2 = boxList[i]
                if self.__detectCollision(subL1[0], subL2[0]): # pasa las coordenadas de la caja
                    mergedBox = [[[min(subL1[0][0][0], subL2[0][0][0]), min(subL1[0][0][1], subL2[0][0][1])], 
                                    [max(subL1[0][1][0], subL2[0][1][0]), min(subL1[0][1][1], subL2[0][1][1])], 
                                    [max(subL1[0][2][0], subL2[0][2][0]), max(subL1[0][2][1], subL2[0][2][1])], 
                                    [min(subL1[0][3][0], subL2[0][3][0]), max(subL1[0][3][1], subL2[0][3][1])]], subL1[1] + ". " + subL2[1]]
                    mergedList.append(mergedBox)

                    boxList.pop(i)

                    merge = True
                    addBox = False
                    break

            if addBox: # no hubo fución
                mergedList.append(subL1)
        
        if merge:
            return self.__mergeBoxes(mergedList) # se llama recursivamente hasta que no haya fuciones
        return mergedList

    def __createMissingBoxes(self, boxList, width, height):
        newList = []
        y = 0 # Y de la caja anterior
        for b in boxList:
            if y < b[0][0][1]:
                # crear caja faltante
                newList.append([[[0, y], [width, y], [width, b[0][0][1]], [0, b[0][0][1]]], ""])

            y = b[0][2][1]
            newList.append(b)

        if y < height:
            newList.append([[[0, y], [width, y], [width, height], [0, height]], ""])
        
        return newList

    def __process(self, imagen):
        self.__data = self.__reader.readtext(image=imagen, detail=1, paragraph=True)
    
    def splitImage(self, imageInfo, output_dir):
        image, imageName = imageInfo
        self.__process(image)

        boxList = self.__mergeBoxes(self.__cleanData(self.__data))
        
        boxList.sort(key=lambda y: y[0][0][1]) # ordena las cajas por el eje y del primer punto
        
        height, width, _ = image.shape
        boxList = self.__createMissingBoxes(boxList, width, height)
    
        for i in tqdm(range(len(boxList))):
            box = boxList[i]
            splitImage = image[box[0][0][1]:box[0][2][1], 0:width]

            imageName_output = imageName + f"_{i}.jpg"
            
            dir_salida = os.path.join(output_dir, imageName_output)
            cv2.imwrite(dir_salida, splitImage)