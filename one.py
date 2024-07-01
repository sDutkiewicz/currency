import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

API_KEY = "2hSEw2BvhwriTiVb74X0fcPMZb4mdFMx"

class CurrencyConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("Currency Converter")
        self.master.geometry("600x450")
        self.master.resizable(False, False)

        # Apply modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        self.style.configure('Card.TFrame', background='#f0f0f0', borderwidth=2, relief='raised')
        
        # Menu bar
        self.menubar = tk.Menu(master)
        self.about_menu = tk.Menu(self.menubar, tearoff=0)
        self.about_menu.add_command(label="Author", command=self.show_author_info)
        self.menubar.add_cascade(label="About", menu=self.about_menu)
        master.config(menu=self.menubar)

        # Create background
        self.background_image = Image.open("background.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        
        self.background_label = tk.Label(master, image=self.background_photo)
        self.background_label.place(relwidth=1, relheight=1)

        # Container frame for widgets
        self.frame = ttk.Frame(master, style="Card.TFrame", padding=(20, 20, 20, 20))
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.currencies = self.get_currencies()

        self.welcome_label = ttk.Label(self.frame, text="Welcome to Currency Converter", font=("Helvetica", 16, "bold"))
        self.welcome_label.grid(column=0, row=0, columnspan=2, pady=10)

        self.amount_label = ttk.Label(self.frame, text="Amount:")
        self.amount_label.grid(column=0, row=1, padx=10, pady=5, sticky=tk.E)
        self.amount = ttk.Entry(self.frame)
        self.amount.grid(column=1, row=1, padx=10, pady=5, sticky=tk.W)

        self.from_currency_label = ttk.Label(self.frame, text="From Currency:")
        self.from_currency_label.grid(column=0, row=2, padx=10, pady=5, sticky=tk.E)
        self.from_currency_frame = ttk.Frame(self.frame)
        self.from_currency_frame.grid(column=1, row=2, padx=10, pady=5, sticky=tk.W)
        self.from_currency = self.create_currency_combobox(self.from_currency_frame)
        self.from_currency.pack(side=tk.LEFT)
        self.from_currency.set("USD - United States Dollar")
        self.from_currency.bind("<<ComboboxSelected>>", lambda event: self.update_flag(self.from_currency.get().split()[0], self.from_currency_flag))

        self.from_currency_flag = ttk.Label(self.from_currency_frame)
        self.from_currency_flag.pack(side=tk.LEFT)
        self.update_flag("USD", self.from_currency_flag)

        self.to_currency_label = ttk.Label(self.frame, text="To Currency:")
        self.to_currency_label.grid(column=0, row=3, padx=10, pady=5, sticky=tk.E)
        self.to_currency_frame = ttk.Frame(self.frame)
        self.to_currency_frame.grid(column=1, row=3, padx=10, pady=5, sticky=tk.W)
        self.to_currency = self.create_currency_combobox(self.to_currency_frame)
        self.to_currency.pack(side=tk.LEFT)
        self.to_currency.set("EUR - Euro")
        self.to_currency.bind("<<ComboboxSelected>>", lambda event: self.update_flag(self.to_currency.get().split()[0], self.to_currency_flag))

        self.to_currency_flag = ttk.Label(self.to_currency_frame)
        self.to_currency_flag.pack(side=tk.LEFT)
        self.update_flag("EUR", self.to_currency_flag)

        self.switch_button = ttk.Button(self.frame, text="Switch", command=self.switch_currencies)
        self.switch_button.grid(column=1, row=4, pady=5)

        self.result_label = ttk.Label(self.frame, text="Converted Amount:")
        self.result_label.grid(column=0, row=5, padx=10, pady=5, sticky=tk.E)
        self.result = ttk.Entry(self.frame, state="readonly")
        self.result.grid(column=1, row=5, padx=10, pady=5, sticky=tk.W)

        self.convert_button = ttk.Button(self.frame, text="Convert", command=self.convert_currency)
        self.convert_button.grid(column=1, row=6, pady=10)

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    

    def show_author_info(self):
        messagebox.showinfo("Author", "This application was created by Stanisław Dutkiewicz")

    def get_currencies(self):
        url = "https://api.apilayer.com/exchangerates_data/symbols"
        headers = {"apikey": API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from API. Status code: {response.status_code}")
            return {}
        try:
            data = response.json()
            currencies = data['symbols']
        except requests.exceptions.JSONDecodeError:
            print("Error decoding JSON from response")
            currencies = {}
        return currencies

    def create_currency_combobox(self, master):
        combobox = ttk.Combobox(master, state="readonly")
        currency_list = []
        for code, name in self.currencies.items():
            currency_list.append(f"{code} - {name}")
        combobox['values'] = currency_list
        return combobox

    def update_flag(self, currency, label):
        try:
            if currency == "EUR":
                flag_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/2560px-Flag_of_Europe.png"
            else:
                flag_url = f"https://flagsapi.com/{currency[:2]}/flat/64.png"
            response = requests.get(flag_url)
            if response.status_code == 200:
                image_data = response.content
                flag_image = Image.open(BytesIO(image_data))
                flag_image = flag_image.resize((30, 20), Image.LANCZOS)
                flag_photo = ImageTk.PhotoImage(flag_image)
                label.image = flag_photo
                label.config(image=flag_photo)
            else:
                print(f"Flag image for {currency} not found.")
        except Exception as e:
            print(f"Error fetching flag image for {currency}: {e}")

    def switch_currencies(self):
        from_currency = self.from_currency.get()
        to_currency = self.to_currency.get()
        self.from_currency.set(to_currency)
        self.to_currency.set(from_currency)
        self.update_flag(to_currency.split()[0], self.from_currency_flag)
        self.update_flag(from_currency.split()[0], self.to_currency_flag)

    def convert_currency(self):
        try:
            amount = float(self.amount.get())
        except ValueError:
            print("Invalid amount entered.")
            return

        from_currency = self.from_currency.get().split()[0]
        to_currency = self.to_currency.get().split()[0]

        url = f"https://api.apilayer.com/exchangerates_data/convert?to={to_currency}&from={from_currency}&amount={amount}"
        headers = {"apikey": API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from API. Status code: {response.status_code}")
            return
        try:
            data = response.json()
            converted_amount = round(float(data["result"]), 2)
        except (requests.exceptions.JSONDecodeError, KeyError):
            print("Error decoding JSON from response")
            return

        self.result.config(state="normal")
        self.result.delete(0, tk.END)
        self.result.insert(0, str(converted_amount))
        self.result.config(state="readonly")

if __name__ == "__main__":
    root = tk.Tk()
    converter = CurrencyConverter(root)
    root.mainloop()
