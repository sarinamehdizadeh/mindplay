from tkinter import*
from tkinter import messagebox
from tkinter.font import Font
import random
import sqlite3
import pandas as pd 
from datetime import datetime

class DataBase:
    def __init__(self , db):
        self.__db_name = db
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS [MindPlay](
                        [id] INT PRIMARY KEY NOT NULL UNIQUE, 
                        [player_name] NVARCHAR NOT NULL, 
                        [target_number] INT NOT NULL, 
                        [attemps] INT NOT NULL, 
                        [result] NVARCHAR NOT NULL, 
                        [play_time] NVARCHAR NOT NULL);
                            """)
        
        self.connection.commit()
        self.connection.close()

    def insert_game(self,id , player , target , attempts, result , play_time):
        self.connection = sqlite3.connect(self.__db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("INSERT INTO MindPlay VALUES(?,?,?,?,?,?)",(id ,player, target,attempts, result , play_time))
        self.connection.commit()
        self.connection.close()

    def GetAllGames(self):
        self.connection = sqlite3.connect(self.__db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT * FROM MindPlay")
        result = self.cursor.fetchall()
        self.connection.close()
        return result
    
    def GetByPlayer(self , player_name):
        self.connection = sqlite3.connect(self.__db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT * FROM MindPlay WHERE player_name is = ?" , (player_name , ))
        result = self.cursor.fetchall()
        self.connection.close()
        return result
    
    def GetBestGames(self):
        self.connection = sqlite3.connect(self.__db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT * FROM MindPlay WHERE attemps < 3")
        result = self.cursor.fetchall()
        self.connection.close()
        return result

    def GetStats(self):
        self.connection = sqlite3.connect(self.__db_name)
        df = pd.read_sql("SELECT * FROM MindPlay" , self.connection)
        self.connection.close()
        if df.empty:
            return None

        return {
            "total": len(df),
            "average_attempts" : df["attemps"].mean(),
            "best_attempt" : df["attemps"].min()
        }
    def get_max_id(self):
        self.connection = sqlite3.connect(self.__db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT MAX(id) FROM MindPlay")
        result = self.cursor.fetchall()
        return result



# /===================================================create database


db = DataBase('MindPlay.db')




# ////////////////////////////////////////////////////  function
target_number = random.randint(0,100)
attempts = 0 

def SubmitGuess():
    player = entry_name.get()
    guess = entry_guess.get()
    if not guess and player :
        messagebox.showerror('error' , 'field is empty')
        return
    if guess.isdigit() == False:
        messagebox.showerror('error' , 'only numbers!')
        return
    guess = int(guess)
    global attempts
    if guess < target_number:
        messagebox.showinfo('!' , 'try a larger number!')
        attempts += 1 
    elif guess > target_number:
        messagebox.showinfo('!' , 'try a smaller number!')
        attempts += 1 
    else:
        messagebox.showinfo('congrats' , 'good job!')
        SaveGame()
        ResetGame()


def SaveGame():
    player = entry_name.get()
    now = datetime.now()
    player_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    # ==============================auto id 
    max_id = db.get_max_id()[0][0]
    if max_id is None:
        new_id=1
    else:
        new_id = max_id+1
    # ======================================
    db.insert_game(new_id,player , target_number , attempts , "win", player_time_str )
    LoadGames()

def ResetGame():
    global target_number
    global attempts
    target_number = random.randint(0,100)
    attempts = 0
    entry_guess.delete(0,END)

def LoadGames():
    listbox.delete(0,END)
    for row in db.GetAllGames():
        listbox.insert(END , row)

def ShowStatus():
    stats = db.GetStats()
    if stats is None:
        messagebox.showerror('error' , 'no data is available')
        return
    messagebox.showinfo(
        "game data",
        f"all games untill now: {stats['total_games']}\n"
        f"average attempts are{stats['avg_attempts']:.2f}\n" #what???
        f"best record was:{stats['best_attempt']}"
    )



# ==============================================================tikinter

window = Tk()
window.title("Mind Play Game")
window.geometry("500x400")
padx = 5
pady = 5
vazir_font = Font(family='Vazir' , size=13)

window.grid_columnconfigure(0,weight=1)
window.grid_columnconfigure(1,weight=1)
window.grid_rowconfigure(2,weight=1)

lbl_name = Label(window , text= 'enter name', font = vazir_font)
lbl_guess = Label(window , text= 'enter guess', font = vazir_font)
entry_guess = Entry(window , justify='center')
entry_name = Entry(window , justify='center')

lbl_name.grid(row=0 , column=0)
lbl_guess.grid(row=0 , column=1)
entry_name.grid(row=1 , column=0)
entry_guess.grid(row= 1, column= 1)
listbox = Listbox(window , font= vazir_font)
listbox.grid(row=2 , column=0 , columnspan=2 , sticky="ew" , padx=padx , pady=pady )
button_submitguess = Button(window , text='submit' , command= SubmitGuess , font= vazir_font)
button_submitguess.grid(row=3 , column= 0 , columnspan=2, sticky= "ew" ,padx=padx , pady=pady)


LoadGames()





































window.mainloop()