# Maelstrom
Maestrom is a program for Magic, the Gathering enthusiests to store their physical card collection digitally via a document scanner.
## Description
This program is written in Python. It uses computer vision and tesseract-ocr to extract and process information on your MTG cards. This information is then used with Scryfall's API to extract as much information about the card as we can and then store in your database.

This database is also queryable! This allows you to quickly and easily determine which cards are in your collection. 

Features and bug fixes will roll out regularily.

## Getting Started
### Dependencies
* Python 3.7.0
  * tkinter
  * csv
  * cv2
  * numpy
  * pandas
  * PIL
  * processing
  * pytesseract
  * requests
  * scrython
* Tesseract-OCR
### Hardware
* Document Scanner
### Quick-Start Guide
1. Install Python on your local machine
2. Clone this repository on your local machine
3. Run the install_requirements script in the Installation folder
   * Windows: install_requirements.ps1
   * Mac/Linux: install_requirements.sh
4. Install tesseract-ocr
5. Add tesseract-ocr to your PATH environment
6. Run driver.py to start the program

## Authors
Seth Urbach
sethurbach@gmail.com

