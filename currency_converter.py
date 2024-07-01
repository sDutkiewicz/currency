import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
from ui import UI

DEFAULT_API_KEY = "DGjJxMGE3QiXTkCXZNfIK1sKFccmCMoi"

class CurrencyConverter(UI):
    def __init__(self, master):
        super().__init__(master)
        self.api_key = DEFAULT_API_KEY
        self.currencies = self.get_currencies()
        self.setup_widgets()

    def prompt_for_api_key(self):
        """Prompt the user to enter a new API key."""
        return simpledialog.askstring("API Key", "Enter a new API key:")

    def get_currencies(self):
        """Fetch currency symbols and names from the API"""
        while True:
            url = "https://api.apilayer.com/exchangerates_data/symbols"
            headers = {"apikey": self.api_key}
            response = requests.get(url, headers=headers) # Send a GET request to the API

            if response.status_code == 401:  # Unauthorized
                messagebox.showerror("Error", "Invalid API key. Please enter a new API key.")
                self.api_key = self.prompt_for_api_key()
                if not self.api_key:  # User canceled the input
                    return {}
            elif response.status_code != 200: # Check if the response status code is not 200 (OK)
                print(f"Error: Unable to fetch data from API. Status code: {response.status_code}")
                return {}
            else:
                try: # Try to decode the JSON response
                    data = response.json()
                    return data['symbols']
                except requests.exceptions.JSONDecodeError:
                    print("Error decoding JSON from response")
                    return {}

    def create_currency_combobox(self, master):
        """Create widget with currency symbols and names as values"""
        combobox = ttk.Combobox(master, state="readonly")
        currency_list = [f"{code} - {name}" for code, name in self.currencies.items()]
        combobox['values'] = currency_list
        return combobox

    def update_flag(self, currency, label):
        """Update the flag image for a currency using the flagsapi.com API"""
        try:
            if currency in ["XAG", "XAU", "XDR", "XOF", "BTC", "XCD", "XAF", "XPF"]:
                # Use a default no-flag image URL for specific currencies without flags
                self.set_default_flag(label)
            elif currency == "EUR":
                flag_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/2560px-Flag_of_Europe.png"
                self.set_flag_image(flag_url, label)
            else:
                # Use the flagsapi.com API to fetch the flag image for the currency
                flag_url = f"https://flagsapi.com/{currency[:2]}/flat/64.png"
                self.set_flag_image(flag_url, label)
        except Exception as e:
            print(f"Error fetching flag image for {currency}: {e}")
            self.set_default_flag(label)

    def set_flag_image(self, url, label):
        """Set the flag image for a currency using the image URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                flag_image = Image.open(BytesIO(image_data)) # Open the image from the response content
                flag_image = flag_image.resize((30, 20), Image.LANCZOS) # Resize the image
                flag_photo = ImageTk.PhotoImage(flag_image) # Create a PhotoImage object from the image
                label.image = flag_photo
                label.config(image=flag_photo)
            else:
                print(f"Flag image not found at {url}. Using default no-flag image.")
                self.set_default_flag(label)
        except Exception as e:
            print(f"Error setting flag image from {url}: {e}")
            self.set_default_flag(label)

    def set_default_flag(self, label):
        """Set a default no-flag image for specific currencies without flags"""
        try:
            # Use a default no-flag image URL for specific currencies without flags
            default_flag_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_None.svg/1024px-Flag_of_None.svg.png"
            response = requests.get(default_flag_url)
            if response.status_code == 200:
                image_data = response.content
                flag_image = Image.open(BytesIO(image_data))
                flag_image = flag_image.resize((30, 20), Image.LANCZOS)
                flag_photo = ImageTk.PhotoImage(flag_image)
                label.image = flag_photo
                label.config(image=flag_photo)
            else:
                label.config(image='')
        except Exception as e:
            print(f"Error setting default flag image: {e}")
            label.config(image='')

    def switch_currencies(self):
        """Switch the 'from' and 'to' currencies and update the flag images accordingly."""
        from_currency = self.from_currency.get()
        to_currency = self.to_currency.get()
        self.from_currency.set(to_currency)
        self.to_currency.set(from_currency)
        self.update_flag(to_currency.split()[0], self.from_currency_flag)
        self.update_flag(from_currency.split()[0], self.to_currency_flag)

    def convert_currency(self):
        """Convert the amount from the 'from' currency to the 'to' currency and display the result."""

        # Get the amount entered by the user
        try:
            amount = float(self.amount.get())
        except ValueError:
            print("Invalid amount entered.")
            return

        # Get the currency codes from the selected currencies
        from_currency = self.from_currency.get().split()[0]
        to_currency = self.to_currency.get().split()[0]

        # Construct the URL for the conversion API
        url = f"https://api.apilayer.com/exchangerates_data/convert?to={to_currency}&from={from_currency}&amount={amount}"
        headers = {"apikey": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 401:  # Unauthorized
            messagebox.showerror("Error", "Invalid API key. Please enter a new API key.")
            self.api_key = self.prompt_for_api_key()
            self.convert_currency()  # Retry with new API key
            return
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from API. Status code: {response.status_code}")
            return
        try:
            data = response.json()
            converted_amount = round(float(data["result"]), 2)
        except (requests.exceptions.JSONDecodeError, KeyError):
            print("Error decoding JSON from response")
            return

        # Display the converted amount in the result entry widget
        self.result.config(state="normal")
        self.result.delete(0, tk.END)
        self.result.insert(0, str(converted_amount))
        self.result.config(state="readonly")
