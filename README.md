# Manga Image Processor

Program to process manga images by cutting or concatenating them.



````
-h, --help                                        Print help information
-i, --input      path to folder                   Path to the images to be processed
-o, --output      path to folder                  Path to where the images will be saved
-m, --mode {s, c, ocr}                            Processing mode: 
                                                      split (s): Dividing the image vertically by the width results in images with dimensions of width x width.
                                                      concatenate (c): Vertically concatenate images. If the height limit of a single image is exceeded, several images will be created.
                                                      split-with-ocr (ocr): The software detects the text within the image and separates it vertically into individual images without causing any harm to the text.

-l, --detect-lang { jaided.ai/easyocr/ }          Language to detect, default = Korean

````

