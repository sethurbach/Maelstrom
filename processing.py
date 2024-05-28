import pytesseract
import cv2
import numpy as np
import os
from tqdm import tqdm
import scrython
import pandas as pd
from time import sleep
import pytesseract
from tkinter import *
from tkinter import messagebox
import sys

 

def process_cards():
  """Function used to search for the card via card image provided.

  Returns a dataframe of cards scanned and processed

  First, the function saves card scan images to a list. 
  Then, the function crops the scans down to just the card itself.
  Next, it will crop the  card image down to just the metadata.
  Lastly, tesseract-ocr extracts the strings from the metadata and uses 
  scrython to search for the card using its set code and collectors number.
  The resulting search is then stored into card_collection.csv for futher data 
  querying and displaying.

  NOTE: this function currently works for modern era cards ONLY. Will be updating
  in the future to include other layouts of metadata.
  """
  # get card scans from directory


  path = "./Card Images/"
  file_list = os.listdir(path)
  scans = []
  for card in tqdm(file_list, desc="retrieving card scans from directory"):
    img = cv2.imread(path + card, 0)
    x, y, w, h = 0, 0, img.shape[1], int(img.shape[0]*0.3)
    crop = img[y:y+h, x:x+w]
    # cv2.imshow("metadata", crop)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    scans.append(crop)
    
  # crop down scans and extract the card
  crops = []
  for img in tqdm(scans, desc="cropping scans and extracting cards"):
    T, bin = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
    bin = np.pad(bin, ((10, 10), (0, 0)), 'constant', constant_values=255)
    contours, hierarchy = cv2.findContours(cv2.bitwise_not(bin), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out=np.zeros_like(img)
    # cv2.drawContours(out, contours, -1, 255, 3)
    # cv2.imshow('contours', out)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    wanted_i = 0
    for i, cnt in enumerate(contours):
      if cv2.boundingRect(cnt)[3] > cv2.boundingRect(contours[i-1])[3]:
        wanted_i = i
    x, y, w, h = cv2.boundingRect(contours[wanted_i])
    crop = img[y:y+h, x:x+w]
    # cv2.imshow("metadata", crop)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    crops.append(crop)

  # crop down to just metadata
  metadata = []
  for img in tqdm(crops, desc="cropping image down to metadata"):
    card_width = img.shape[1]
    card_height = img.shape[0]
    x = int(card_width * 0.047)
    y = int(card_height * 0.92)
    w = int(card_width * 0.145)
    h = int(card_height * 0.06)
    crop = img[y:y+h, x:x+w]
    T, bin = cv2.threshold(crop, 0, 255, cv2.THRESH_OTSU)
    if np.mean(bin) > 127:
      bin = cv2.bitwise_not(bin)
    kernel = np.ones((2, 2), np.uint8)
    bin = cv2.dilate(bin, kernel, iterations=1)
    # cv2.imshow("metadata", bin)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    metadata.append(crop)

  # using pytesseract to extract strings
  collectors_no = []
  set_code = []
  for i, img in enumerate(tqdm(metadata, desc="using tesseract-ocr to extract strings")):
    text = pytesseract.image_to_string(cv2.bitwise_not(img))
    lines = text.split('\n')
    for i, line in enumerate(lines):
      strings = line.split(' ')
      if i == 0:
        string = strings[0]
        if '/' in string:
          string = str.split(string, '/')[0]
        if string.lower() in ['ool', 'oo1', '0o1', 'o01', '0ol', 'o0l']:
          string = '001'
        collectors_no.append(string)
      elif i == 1:
        string = strings[0]
        string = string[:3]
        set_code.append(string)

  errors = []
  # for i, string in enumerate(collectors_no):
  #   if len(string) != 3:
  #     errors.append(i)
  # for i, string in enumerate(set_code):
  #   if len(string) != 3:
  #     errors.append(i)
  # for i in errors:
  #   del collectors_no[i]
  #   del set_code[i]
  # print(collectors_no)
  # print(set_code)

  # searching for card based on pytesseract output and processing data into data frame
  predicted_cards = pd.DataFrame(columns=['Name', 'Set Name', "Set Code", "Prices", "CMC", "Collector Number", 
                                          "Rarity", "Legalities", "Colors", "Color Identity", "Image URIs",
                                          "Border Color", "Type Line"])
  for i, string in enumerate(set_code):
    try:
      search = scrython.cards.Search(q="s:{} cn:{}".format(string, collectors_no[i]))
    
      data = search.data()[0]
      card = pd.DataFrame.from_dict({'Name': [data['name']], 'Set Name': [data['set_name']], 'Set Code': [data['set']], "Prices": [data['prices']],
                                     'CMC': [data['cmc']], 'Collector Number': [data['collector_number']], 'Rarity': [data['rarity']], 
                                     'Legalities': [data['legalities']], 'Colors': [data['colors']], 'Color Identity': [data['color_identity']],
                                     'Image URIs': [data['image_uris']], 'Border Color': [data['border_color']], 'Type Line': [data['type_line']]})
    
      predicted_cards = pd.concat([predicted_cards, card], axis=0, ignore_index=True)
    except scrython.foundation.ScryfallError: 
      errors.append(i)
  rescans = ""
  for error in errors:
     rescans = rescans + " {} ".format(error+1)
  messagebox.showerror("Rescan cards", "Please rescan card(s): {}\nOr enter cards manually!".format(rescans))
  print("Finished!")

  return predicted_cards

#   # saving processed card information into csv file containg card collection
#   path = './'
#   filename = 'card_collection.csv'
#   if os.path.getsize('./card_collection.csv') != 0: 
#     old_card_collection = pd.read_csv(path+filename, index_col=0)
#     card_collection = pd.concat([old_card_collection, card_collection], axis=0, ignore_index=True)
#   card_collection.to_csv(path+filename)
  
#   # function over message
#   print("Finished!")

def add_cards_to_csv(card_df):
  """saving processed card information into csv file containg card collection.
  """
  path = './'
  filename = 'card_collection.csv'
  if os.path.getsize('./card_collection.csv') != 0: 
    card_collection = pd.read_csv(path+filename, index_col=0)
    card_collection = pd.concat([card_collection, card_df], axis=0, ignore_index=True)
  else:
    card_collection = card_df
  card_collection.to_csv(path+filename)

def clear_card_images():
  path = "./Card Images/"
  filelist = os.listdir(path)
  for file in tqdm(filelist, desc="deleting files in Card Images directory"):
    os.remove(path+file)
  print("Cards added to card_collection.csv")

def query(name='', set='', finish='', color1='', color2='', color3='', color4='', color5='', 
          cardtype1='', cardtype2='', cardtype3='', cardtype4='', cardtype5='', cardtype6='', 
          cardtype7='', rarity='', cmc='', price_min='', price_max=''):
  """Returns a dataframe queried from the card_collection.csv
  """
  print(name, set, finish, color1, color2, color3, color4, color5, cardtype1, cardtype2, cardtype3, cardtype4, cardtype5, cardtype6, cardtype7, rarity, cmc, price_min, price_max)
  if color1 or color2 or color3 or color4 or color5:
    color_id = [color1, color2, color3, color4, color5]
    color_id = [color for color in color_id if color != 'X']
  else: color_id = False

  if cardtype1 or cardtype2 or cardtype3 or cardtype4 or cardtype5:
    cardtype = [cardtype1, cardtype2, cardtype3, cardtype4, cardtype5, cardtype6, cardtype7]
    cardtype = [ctype for ctype in cardtype if ctype != 'X']
  else: cardtype = False

  cards_df = pd.read_csv('./card_collection.csv')
  cards_df.columns = [column.replace(" ", "_") for column in cards_df.columns]

  if name:
      cards_df.query("Name == '{}'".format(name), inplace=True)
  if set:
     cards_df.query("Set_Name == '{}'".format(set), inplace=True)
  if finish:
     cards_df.query("Finish == '{}'".format(finish), inplace=True)
  if color_id:
      is_color_id = []
      n = cards_df.shape[0]
      for i in range(n):
          if set(color_id) == set(cards_df.loc[i,'Color_Identity'].replace("'", '').strip('][').split(', ')): 
              is_color_id.append(i)
      cards_df = cards_df.iloc[is_color_id]
  if cardtype:
      is_cardtype = []
      n = cards_df.shape[0]
      for i in range(n):
         if set(cardtype) <= set(cards_df.loc[i,'Type_Line'].split(' ')):
            is_cardtype.append(i)
      cards_df = cards_df.loc[is_cardtype]
  if rarity:
      if rarity == 'M':
          cards_df.query("Rarity == 'mythic'", inplace=True)
      elif rarity == 'R':
          cards_df.query("Rarity == 'rare'", inplace=True)
      elif rarity == 'U':
          cards_df.query("Rarity == 'uncommon'", inplace=True)
      elif rarity == 'C':
          cards_df.query("Rarity == 'common'", inplace=True)
  if cmc:
      cards_df.query("CMC == {}".format(cmc), inplace=True)
  if price_min:
      cards_df.query("Price >= {}".format(float(price_min)), inplace=True)
  if price_max:
      cards_df.query("Price <= {}".format(float(price_max)), inplace=True)

  cards_df.to_csv('./query.csv')
  return cards_df

def remove_entries(name, set, finish, quantity):
  cards_df = pd.read_csv('./card_collection.csv')
  cards_df.columns = [column.replace(" ", "_") for column in cards_df.columns]
  to_remove = cards_df.query("Name == '{}' and Set_Code == '{}' and Finish == '{}'".format(name, set, finish))
  if to_remove.empty:
    messagebox.showerror("ERROR: Card Not Found", "Please check spelling and capitalization of the card you are trying to remove.\nPlease use set code to find the set of the card.\nIt is possible this card is not in your collection.")
    return
  to_remove_indexes = to_remove['Unnamed:_0'].tolist()
  print(type(to_remove_indexes[0]))
  try:
    for i in range(quantity):
      cards_df.drop(index=to_remove_indexes[i], axis='rows', inplace=True)
  except IndexError:
     messagebox.showerror("ERROR: Quantity Too Large", "Quantity specified is too large.\nPlease use a smaller quantity.")
     return
  cards_df.drop("Unnamed:_0", axis=1, inplace=True)
  cards_df.columns = [column.replace("_", " ") for column in cards_df.columns]
  cards_df.to_csv('./card_collection.csv')
  return 

def add_entries(name, set, finish, quantity):
  search = scrython.cards.Search(q="{} s:{}".format(name, set))
  data = search.data()[0]
  card = pd.DataFrame.from_dict({'Name': [data['name']], 'Set Name': [data['set_name']], 'Set Code': [data['set']], "Prices": [data['prices']],
                                  'CMC': [data['cmc']], 'Collector Number': [data['collector_number']], 'Rarity': [data['rarity']], 
                                  'Legalities': [data['legalities']], 'Colors': [data['colors']], 'Color Identity': [data['color_identity']],
                                  'Image URIs': [data['image_uris']], 'Border Color': [data['border_color']], 'Type Line': [data['type_line']]})
  card.insert(5, "Price", 'na')

  for i, prices in enumerate(card['Prices'].tolist()):
    if finish == 'Nonfoil':
        card.at[i, 'Price'] = prices['usd']
    elif finish == 'Foil':
      card.at[i, 'Price'] = prices['usd_foil']
    elif finish == 'Etched':
      card.at[i, 'Price'] = prices['usd_etched']
  card.insert(6, "Finish", finish)
  card.drop('Prices', axis=1, inplace=True)
  cards_df = card
  for qty in range(quantity-1):
     cards_df = pd.concat([cards_df, card], axis=0, ignore_index=True)
  add_cards_to_csv(cards_df)
