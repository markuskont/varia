#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Simple GUI test with tkinter module

from Tkinter import *
import random

def callback(obj, array):

	kysimus = random.choice(array)

	w = Label(obj, text=kysimus)
	w.pack()

def main():

	kysimused = ['Mis mõttes mis jaaaaa?', 'Oi kui armas', 'Mõtle midagi paremat välja', 'Kalasaba']

	master = Tk()

	b = Button(master, text="Vasta", width=25, command=callback(master, kysimused))
	b.pack()

	mainloop()


if __name__ == "__main__":
	main()