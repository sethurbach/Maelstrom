from tkinter import *
from tkinter import ttk
import csv
from processing import *
import cv2
import PIL
from PIL import ImageTk
import numpy as np
import os
import requests  

class ConsoleRedirect:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.insert('end', text) 


class GUI(Tk):
    def __init__(self, query=False):
        """Creates the main window of the program"""
        super().__init__()
        self.title('Maelstrom')
        self.geometry("1500x900")
        logo = PhotoImage(file='./Maelstrom_Logo.png')
        self.iconphoto(False, logo)
        self.main_pane = PanedWindow(bd=4, relief='raised')
        self.main_pane.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.main_panel.pack(fill=BOTH, expand=1)
        self.query_view()
        self.child_pane = PanedWindow(self.main_pane, orient=VERTICAL, bd=4, relief='raised')
        self.main_pane.add(self.child_pane)
        self.quick_price_stats()
        self.csv_viewer(query)
        self.menu()
        
    def menu(self):
        """Adds a menu to the window"""
        menu = Menu(self)
        self.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='Process Cards', command=lambda : self.card_processing_window())
        filemenu.add_command(label='Clear Card Images', command=lambda : clear_card_images())
        filemenu.add_command(label='Add Cards', command=lambda: self.add_entries_window())
        filemenu.add_command(label='Remove Cards', command=lambda: self.remove_entries_window())
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quit)
        viewmenu = Menu(menu)
        menu.add_cascade(label='View', menu=viewmenu)
        viewmenu.add_command(label='Refresh Window', command=lambda : self.refresh())
        helpmenu = Menu(menu)
        menu.add_cascade(label='Help', menu=helpmenu)
    
    def csv_viewer(self, query=False):
        """Shows contents of card_collection.csv in tabular format"""
        csv_pane = PanedWindow(self.child_pane, orient=VERTICAL, bd=4, relief='raised')
        self.child_pane.add(csv_pane)
        tree = ttk.Treeview(csv_pane, columns=('Name', 'Set Name', "Set Code", "CMC", "Price", 'Finish', "Collector Number", 
                                          "Rarity", "Legalities", "Colors", "Color Identity", "Image URIs",
                                          "Border Color"))
        tree.column("#0", width=0)
        tree.column("Name", width=0, stretch=True)
        tree.column("Set Name", width=100)
        tree.column("Set Code", width=100)
        tree.column("CMC", width=0)
        tree.column("Price", width=0)
        tree.column("Finish", width=0)
        tree.column("Collector Number", width=0)
        tree.column("Rarity", width=100)
        tree.column("Legalities", width=50)
        tree.column("Colors", width=50)
        tree.column("Color Identity", width=50)
        tree.column("Image URIs", width=100)
        tree.column("Border Color", width=50)
        # tree.heading('#1', text='Name')
        # tree.heading('#2', text='Set Code')
        # tree.heading('#3', text='CMC')
        # tree.heading('#4', text='Price')
        # tree.heading('#5', text='Finish')
        # tree.heading('#6', text='Collector Number')
        # # tree.heading('#7', text='Rarity')
        # tree.heading('#8', text='Legalities')
        # tree.heading('#9', text='Colors')
        # tree.heading('#10', text='Color Identity')
        # tree.heading('#11', text='Image URIs')
        # tree.heading('#12', text='Border Color')
        v_scrollbar = Scrollbar(csv_pane, orient='vertical', command=tree.yview)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = Scrollbar(csv_pane, orient='horizontal', command=tree.xview)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        tree.configure(yscrollcommand=h_scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        if query:
            with open("./query.csv", 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    tree.insert("", "end", values=row)
        else:
            with open("./card_collection.csv", 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    tree.insert("", "end", values=row)
    
    def card_processing_window(self):
        # log = Toplevel(self)
        # log.title("Processig in Progress...")
        # log.geometry("600x200")
        # textbox = Text(log)
        # textbox.pack()
        # old_stdout = sys.stdout
        # sys.stdout = ConsoleRedirect(textbox)
        cards_df = process_cards()
        # sys.stdout = old_stdout
        # log.destroy()
        window = Toplevel(self)
        window.title("Card Processing")
        window.geometry("900x900")
        wait_var = IntVar()
        
        cards_df.insert(4, 'Finish', 'NA')
        img_uris = cards_df['Image URIs'].tolist()
        foil_cards = []
        nonfoil_cards = []
        etched_cards = []
        correct_cards = []
        to_save = pd.DataFrame(columns=['Name', 'Set Name', "Set Code", "CMC", "Price", 'Finish', "Collector Number", 
                                          "Rarity", "Legalities", "Colors", "Color Identity", "Image URIs",
                                          "Border Color", 'Type Line'])
        def foil_card():
            foil_cards.append(i)
            correct_cards.append(i)
            wait_var.set(1)
        def nonfoil_card():
            nonfoil_cards.append(i)
            correct_cards.append(i)
            wait_var.set(1)
        def etched_card():
            etched_cards.append(i)
            correct_cards.append(i)
            wait_var.set(1)
        def incorrect_card():
            wait_var.set(1)
        foil_b = Button(window, text="Nonfoil", command = nonfoil_card)
        foil_b.pack()
        nonfoil_b = Button(window, text="Foil", command = foil_card)
        nonfoil_b.pack()
        etched_b = Button(window, text="Etched", command = etched_card)
        etched_b.pack()
        incorrect_b = Button(window, text="Incorrect", command = incorrect_card)
        incorrect_b.pack()
        for i, type in enumerate(img_uris):
            uri = type['normal']
            img = requests.get(uri).content
            img = np.fromstring(img, np.uint8)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            # rearange the color channels for tkinter
            b,g,r = cv2.split(img)
            img = cv2.merge((r,g,b))
            im = PIL.Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=im)
            card_image = Label(window, image=imgtk)
            card_image.image = imgtk
            card_image.pack()
            window.wait_variable(wait_var)
            wait_var.set(0)
            card_image.pack_forget()
        for i in correct_cards:
            if i in foil_cards:
                cards_df.at[i, 'Finish'] = 'Foil'
            elif i in nonfoil_cards:
                cards_df.at[i, 'Finish'] = 'Nonfoil'
            elif i in etched_cards:
                cards_df.at[i, 'Finish'] = 'Etched'
        for i, prices in enumerate(cards_df['Prices'].tolist()):
            if cards_df.at[i, 'Finish'] == 'Nonfoil':
                cards_df.at[i, 'Price'] = prices['usd']
            elif cards_df.at[i, 'Finish'] == 'Foil':
                cards_df.at[i, 'Price'] = prices['usd_foil']
            elif cards_df.at[i, 'Finish'] == 'Etched':
                cards_df.at[i, 'Price'] = prices['usd_etched']
        to_save = pd.concat([to_save, cards_df.loc[cards_df.index.isin(correct_cards)]], axis=0, ignore_index=True)
        add_cards_to_csv(to_save)
        window.destroy()
        self.refresh()

    def refresh(self, query=False):
        self.destroy()
        self.__init__(query)
    
    def quick_price_stats(self):
        if os.path.getsize('./card_collection.csv') != 0: 
            cards_df = pd.read_csv('./card_collection.csv')
            total = np.sum(cards_df['Price'])
            avg = np.mean(cards_df['Price'])
            median = np.nanmedian(cards_df['Price'])
            label = Label(self.child_pane, text="Price Total:\t${}\t\tPrice Average:\t${}\t\tPrice Median:\t${}".format(round(total, 2), round(avg, 2), round(median, 2)))
            self.child_pane.add(label)
        else:
            total = 0
            avg = 0
            median = 0
            label = Label(self.child_pane, text="Price Total:\t${}\t\tPrice Average:\t${}\t\tPrice Median:\t${}".format(round(total, 2), round(avg, 2), round(median, 2)))
            self.child_pane.add(label) 

    def query_view(self):
        frame = Frame(self.main_pane, relief='raised', bd=4)
        self.main_pane.add(frame)
        title = Label(frame, text='Query')
        title.grid(row=0)
        title.rowconfigure(0, weight=1)
        title.columnconfigure(0, weight=1)

        name_l = Label(frame, text='Card Name')
        name = Entry(frame)
        name_l.grid(row=1)
        name.grid(row=1, column=1)

        set_l = Label(frame, text='Set')
        set = Entry(frame)
        set_l.grid(row=2)
        set.grid(row=2, column=1)

        finish_l = Label(frame, text='Finish')
        finish = StringVar()
        finish_b1 = Radiobutton(frame, text="Nonfoil", variable=finish, value='Nonfoil', tristatevalue=0)
        finish_b2 = Radiobutton(frame, text="Foil", variable=finish, value='Finished', tristatevalue=0)
        finish_b3 = Radiobutton(frame, text="Etched", variable=finish, value='Etched', tristatevalue=0)
        finish_b4 = Radiobutton(frame, text="All", variable=finish, value='All', tristatevalue=0)
        finish_l.grid(row=3)
        finish_b1.grid(row=3, column=1)
        finish_b2.grid(row=3, column=2)
        finish_b3.grid(row=3, column=3)
        finish_b4.grid(row=3, column=4)

        colors_l = Label(frame, text='Colors')
        color_1 = StringVar()
        color_2 = StringVar()
        color_3 = StringVar()
        color_4 = StringVar()
        color_5 = StringVar()
        colors_b1 = Checkbutton(frame, text='White', variable = color_1, onvalue='W', offvalue='X', tristatevalue=0)
        colors_b2 = Checkbutton(frame, text='Blue', variable = color_2, onvalue='U', offvalue='X', tristatevalue=0)
        colors_b3 = Checkbutton(frame, text='Black', variable = color_3, onvalue='B', offvalue='X', tristatevalue=0)
        colors_b4 = Checkbutton(frame, text='Red', variable = color_4, onvalue='R', offvalue='X', tristatevalue=0)
        colors_b5 = Checkbutton(frame, text='Green', variable = color_5, onvalue='G', offvalue='X', tristatevalue=0)
        colors_l.grid(row=4)
        colors_b1.grid(row=4, column=1)
        colors_b2.grid(row=4, column=2)
        colors_b3.grid(row=4, column=3)
        colors_b4.grid(row=5, column=1)
        colors_b5.grid(row=5, column=2)

        card_type_l = Label(frame, text='Card Type')
        card_type_1 = StringVar()
        card_type_2 = StringVar()
        card_type_3 = StringVar()
        card_type_4 = StringVar()
        card_type_5 = StringVar()
        card_type_6 = StringVar()
        card_type_7 = StringVar()
        card_type_8 = StringVar()
        card_type_b1 = Checkbutton(frame, text='Creature', variable=card_type_1, onvalue='Creature', offvalue='X', tristatevalue=0)
        card_type_b2 = Checkbutton(frame, text='Artifact', variable=card_type_2, onvalue='Artifact', offvalue='X', tristatevalue=0)
        card_type_b3 = Checkbutton(frame, text='Enchantment', variable=card_type_3, onvalue='Enchantment', offvalue='X', tristatevalue=0)
        card_type_b4 = Checkbutton(frame, text='Instant', variable=card_type_4, onvalue='Instant', offvalue='X', tristatevalue=0)
        card_type_b5 = Checkbutton(frame, text='Sorcery', variable=card_type_5, onvalue='Sorcery', offvalue='X', tristatevalue=0)
        card_type_b6 = Checkbutton(frame, text='Planeswalker', variable=card_type_6, onvalue='Planeswalker', offvalue='X', tristatevalue=0)
        card_type_b7 = Checkbutton(frame, text='Battle', variable=card_type_7, onvalue='Battle', offvalue='X', tristatevalue=0)
        card_type_b8 = Checkbutton(frame, text='Legendary', variable=card_type_8, onvalue='Legendary', offvalue='X', tristatevalue=0)
        card_type_l.grid(row=6)
        card_type_b1.grid(row=6, column=1)
        card_type_b2.grid(row=6, column=2)
        card_type_b3.grid(row=6, column=3)
        card_type_b4.grid(row=6, column=4)
        card_type_b5.grid(row=7, column=1)
        card_type_b6.grid(row=7, column=2)
        card_type_b7.grid(row=7, column=3)
        card_type_b8.grid(row=7, column=4)
        

        rarity_l = Label(frame, text='Rarity')
        rarity = StringVar()
        rarity_b1 = Radiobutton(frame, text="Mythic", variable=rarity, value='M', tristatevalue=0)
        rarity_b2 = Radiobutton(frame, text="Rare", variable=rarity, value='R', tristatevalue=0)
        rarity_b3 = Radiobutton(frame, text="Uncommon", variable=rarity, value='U', tristatevalue=0)
        rarity_b4 = Radiobutton(frame, text="Common", variable=rarity, value='C', tristatevalue=0)
        rarity_l.grid(row=8)
        rarity_b1.grid(row=8, column=1)
        rarity_b2.grid(row=8, column=2)
        rarity_b3.grid(row=8, column=3)
        rarity_b4.grid(row=8, column=4)
        
        cmc_l = Label(frame, text="CMC")
        cmc = Entry(frame)
        cmc_l.grid(row=9)
        cmc.grid(row=9, column=1)

        price_min_l = Label(frame, text='Price Minimum')
        price_min = Entry(frame)
        price_min_l.grid(row=10)
        price_min.grid(row=10, column=1)

        price_max_l = Label(frame, text='Price Maximum')
        price_max = Entry(frame)
        price_max_l.grid(row=11)
        price_max.grid(row=11, column=1)

        space = Label(frame)
        space.grid(row=12)

        query_b = Button(frame, text='Submit', command=lambda: [query(name.get(), set.get(), finish.get(), color_1.get(), color_2.get(), color_3.get(),
                                                                           color_4.get(), color_5.get(), card_type_1.get(), card_type_2.get(), 
                                                                           card_type_3.get(), card_type_4.get(), card_type_5.get(), 
                                                                           card_type_6.get(), card_type_7.get(), rarity.get(), cmc.get(), 
                                                                           price_min.get(), price_max.get()), self.refresh(query=True)])
        query_b.grid(row=13)
        clear_b = Button(frame, text='Clear', command=lambda: self.refresh())
        clear_b.grid(row=13, column=1)

    def remove_entries_window(self):
        self.window = Toplevel(self)
        name_l = Label(self.window, text='Card Name')
        name = Entry(self.window)
        name_l.grid(row=1)
        name.grid(row=1, column=1)

        set_l = Label(self.window, text='Set')
        set = Entry(self.window)
        set_l.grid(row=2)
        set.grid(row=2, column=1)

        finish_l = Label(self.window, text='Finish')
        finish = StringVar()
        finish_b1 = Radiobutton(self.window, text="Nonfoil", variable=finish, value='Nonfoil', tristatevalue=0)
        finish_b2 = Radiobutton(self.window, text="Foil", variable=finish, value='Foil', tristatevalue=0)
        finish_b3 = Radiobutton(self.window, text="Etched", variable=finish, value='Etched', tristatevalue=0)
        finish_l.grid(row=4)
        finish_b1.grid(row=4, column=1)
        finish_b2.grid(row=4, column=2)
        finish_b3.grid(row=4, column=3)

        quantity_l = Label(self.window, text='Qty')
        quantity = Entry(self.window)
        quantity.insert(0, "1")
        quantity_l.grid(row=5)
        quantity.grid(row=5, column=1)

        remove_b = Button(self.window, text='Remove Cards', command=lambda: [remove_entries(name.get(), set.get().lower(), finish.get(), int(quantity.get()))])
        remove_b.grid(row=12)
        finish_b = Button(self.window,  text='Finish', command=lambda: [self.refresh()])
        finish_b.grid(row=12, column=1)

    def add_entries_window(self):
        self.window = Toplevel(self)
        name_l = Label(self.window, text='Card Name')
        name = Entry(self.window)
        name_l.grid(row=1)
        name.grid(row=1, column=1)

        set_l = Label(self.window, text='Set')
        set = Entry(self.window)
        set_l.grid(row=2)
        set.grid(row=2, column=1)

        finish_l = Label(self.window, text='Finish')
        finish = StringVar()
        finish_b1 = Radiobutton(self.window, text="Nonfoil", variable=finish, value='Nonfoil', tristatevalue=0)
        finish_b2 = Radiobutton(self.window, text="Foil", variable=finish, value='Foil', tristatevalue=0)
        finish_b3 = Radiobutton(self.window, text="Etched", variable=finish, value='Etched', tristatevalue=0)
        finish_l.grid(row=4)
        finish_b1.grid(row=4, column=1)
        finish_b2.grid(row=4, column=2)
        finish_b3.grid(row=4, column=3)

        quantity_l = Label(self.window, text='Qty')
        quantity = Entry(self.window)
        quantity.insert(0, "1")
        quantity_l.grid(row=5)
        quantity.grid(row=5, column=1)

        remove_b = Button(self.window, text='Add Cards', command=lambda: [add_entries(name.get(), set.get().lower(), finish.get(), int(quantity.get()))])
        remove_b.grid(row=12)
        finish_b = Button(self.window,  text='Finish', command=lambda: [self.refresh()])
        finish_b.grid(row=12, column=1)
