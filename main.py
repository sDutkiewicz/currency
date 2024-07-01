import tkinter as tk
from currency_converter import CurrencyConverter

if __name__ == "__main__":
    root = tk.Tk()

    
    converter = CurrencyConverter(root)
    root.mainloop()
