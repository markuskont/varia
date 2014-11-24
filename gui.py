#!/usr/bin/env python

# Simple GUI test with tkinter module

import Tkinter

def textinput():
	print hi

def main(argv):
	window = Tkinter.Tk()
	
	# text input

	Tkinter.Label(window, text="First").grid(row=0)
	Tkinter.Label(window, text="Second").grid(row=1)

	e1 = Tkinter.Entry(window)
	e2 = Tkinter.Entry(window)

 	e1.grid(row=0, column=1)
 	e2.grid(row=1, column=1)

	#label.grid()
	#label.entry = Tkinter.Entry(label)
	#label.entry.grid(column=0,row=0,sticky='EW')

	window.mainloop()


if __name__ == "__main__":
	main("asd")