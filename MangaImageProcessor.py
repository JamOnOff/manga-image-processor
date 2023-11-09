import argparse

from tqdm import tqdm
from Images import Images
from OCRController import OCRController

class MangaImageProcessor:
    __entity = None

    __parser = None
    __args = None

    __Images = None
    __OCRController = None
    def __new__(cls):
        if cls.__entity is None:
            cls.__entity = super(MangaImageProcessor, cls).__new__(cls)
            cls.__entity.__initialize()
        return cls.__entity

    def __initialize(self):
        self.__parser = argparse.ArgumentParser(description='Program to process manga images by cutting or concatenating them.')
        #entradas y salidas basicas
        self.__parser.add_argument('-i', '--input', dest='input', help='Input path', required=True)
        self.__parser.add_argument('-o', '--output', dest='output', help='Output path', required=True)
        #modo - split - concatenate
        self.__parser.add_argument('-m', '--mode', choices=['s', 'c', 'ocr'], default='s', help="Processing mode: 'split', 'concatenate' o 'split-with-ocr'")
        self.__parser.add_argument('-l', '--detect-lang', nargs='+', default='ko', help="Language to detect, default = Korean")

        self.__args = self.__parser.parse_args()

        self.__Images = Images(self.__args.input)
        self.__OCRController = OCRController(self.__args.detect_lang)

    def process(self):
        """
        Processes the images based on the mode specified in the command line arguments.

        If the mode is 's', the images are split into individual pages and saved in the output directory.
        If the mode is 'c', the images are concatenated into a single image and saved in the output directory.
        If the mode is 'ocr', each image is split into individual pages and processed using OCR. The resulting text
        files are saved in the output directory.

        Returns:
            None
        """
        output = self.__args.output
        mode = self.__args.mode

        print("\n")
        if mode == 's':
            self.__Images.splitImages(output)
        elif mode == 'c':
            self.__Images.concatenateImages(output)
        else: #ocr
            self.__OCRController.splitImage(self.__Images.getImagesInfoList(), output)

        

if __name__ == "__main__":
    mangaImgP = MangaImageProcessor()
    mangaImgP.process()