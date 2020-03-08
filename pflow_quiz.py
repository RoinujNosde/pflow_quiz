from tkinter import Tk
from interfaces import TelaInicial

def main():
    root = Tk()
    inicio = TelaInicial(root)
    root.mainloop()

if __name__ == '__main__':
    main()