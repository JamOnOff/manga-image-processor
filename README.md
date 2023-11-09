# Manga Image Processor

Program for manga image processing by splitting or concatenating. 

The main function is optical character recognition ([OCR](jaided.ai/easyocr/)) division with layers to crop images up to 60,000 pixels tall while preserving the text separately in the images.

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

