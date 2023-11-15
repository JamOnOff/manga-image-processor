import os
import cv2
import easyocr
import torch

from tqdm import tqdm

class OCRController:
    __entity = None
    
    __reader = None
    __data = []

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
            """
            Recursively cleans the OCR data by removing empty sublists and ensuring that each sublist contains
            a list of coordinates and a string of text.

            Args:
                data (list): The OCR data to be cleaned.

            Returns:
                list: The cleaned OCR data.
            """
            
            if len(data) == 2 and type(list[-1]) is str: # 1 sublista con las coordenadas y 1 con el texto
                return [data]
            
            cleanList = []
            for d in data:
                if not d: # si la sublista está vacia
                    continue
                if len(d) == 2 and type(d[-1]) is str:
                    cleanList.append(d)
                    continue

                subLista = self.__cleanData(d)
                if subLista:
                    cleanList += subLista
            
            return cleanList

    def __detectCollisionY_aux(self, list1 , list2):
            dist = 10
            p1 = list1[0]
            p2 = list1[1]
            p3 = list1[2]
            
            if p1[1] - dist < list2[0][1] and list2[0][1] < p3[1] + dist:
                return True
            if p1[1] - dist < list2[1][1] and list2[1][1] < p3[1] + dist:
                return True
            if p1[1] - dist < list2[2][1] and list2[2][1] < p3[1] + dist:
                return True
            if p1[1] - dist < list2[3][1] and list2[3][1] < p3[1] + dist:
                return True
            
            return False
    
    def __detectCollisionY(self, list1 , list2):
        """
            Determines if there is a collision between two lists of points in the Y-axis.

            Args:
            - list1: A list of 4 points representing a rectangle.
            - list2: A list of 4 points representing a rectangle.

            Returns:
            - True if there is a collision between the two lists in the Y-axis, False otherwise.
            """
        return (self.__detectCollisionY_aux(list1, list2) or self.__detectCollisionY_aux(list2, list1))

    def __mergeBoxes(self, boxList):
        mergedList = []
        merge = False

        while boxList: # mientras la lista no esté vacia
            subL1 = boxList.pop(0)
            mergedBox = []

            addBox = True # si se agrega la caja a la lista
            for i in range(len(boxList)):
                subL2 = boxList[i]
                if self.__detectCollisionY(subL1[0], subL2[0]): # pasa las coordenadas de la caja
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

    def __createMissingBoxes(self, boxList, img):
            """
            Creates missing bounding boxes in a list of bounding boxes.

            Args:
                boxList (list): List of bounding boxes.
                img (numpy array): The image from which the bounding boxes were extracted.

            Returns:
                list: List of bounding boxes with missing boxes added.
            """
            height, width, _ = img.shape

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

    def __verifyData(self, data, img):
        height, width, _ = img.shape

        # ajusta los puntos de las cajas
        newDataList = []
        for d in data:
            addData = True
            for i in range(len(d[0])):
                if d[0][i][1] > height or d[0][i][0] > width or d[0][i][1] < 0 or d[0][i][0] < 0:
                    addData = False
                    break
            
            if not addData or d[0][0][0] == d[0][1][0] or d[0][0][1] == d[0][3][1]:
                continue
            newDataList.append(d)
        
        return newDataList

    def __process(self, img):
            """
            Processes the given image using OCR to extract text data from it.

            Args:
                img: A numpy array representing the image to be processed.

            Returns:
                None
            """
            height, width, _ = img.shape
            maxHeight = 5000
            
            if height > maxHeight:
                for y1 in tqdm(range(0, height, int(maxHeight * 0.8)), desc = "Processing split image with OCR "):
                    y2 = y1 + maxHeight
                    if y2 > height:
                        y2 = height

                    splitImage = img[y1:y2, 0:width]
                    newData = self.__cleanData(self.__reader.readtext(splitImage, detail=1, paragraph=True))

                    for d in newData:
                        for i in range(len(d[0])): # recorre los puntos de la caja
                            d[0][i][1] += y1 # ajusta el eje y
                    self.__data += self.__mergeBoxes(newData)
            else:
                self.__data = self.__cleanData(self.__reader.readtext(img, detail=1, paragraph=True))
            self.__data = self.__verifyData(self.__mergeBoxes(self.__data), img)
            self.__data.sort(key=lambda y: y[0][0][1]) # ordena las cajas por el eje 'Y' del primer punto
    
    def splitImage(self, imagesInfo, output_dir):
            """
            Splits the input image into multiple sub-images based on the detected text boxes.
            Saves each sub-image as a separate file in the specified output directory.

            Args:
                imageInfo: A tuple containing the input image and its name.
                output_dir: The directory where the sub-images will be saved.

            Returns:
                None
            """
            numImagen = 1
            for imgInf in tqdm(imagesInfo, desc = "Processing images with OCR"):
                img, imageName = imgInf
                self.__process(img)
                
                width = img.shape[1]
                boxList = self.__createMissingBoxes(self.__data, img)
                for i in tqdm(range(len(boxList)), desc = f"Saving image: {imageName}"):
                    box = boxList[i]
                    splitImage = img[box[0][0][1]:box[0][2][1], 0:width]

                    imageName_output = imageName + f"_{numImagen}.jpg"
                    cv2.imwrite(os.path.join(output_dir, imageName_output), splitImage)
                    numImagen += 1