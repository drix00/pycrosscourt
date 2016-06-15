#!/usr/bin/env python
"""
.. py:currentmodule:: main_gui
   :synopsis: Application to prepare the EBSD data to open in CrossCourt.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Application to prepare the EBSD data to open in CrossCourt.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = "0.1"
__date__ = "Jun 15, 2016"
__copyright__ = "Copyright (c) 2016 Hendrix Demers"
__license__ = "Apache License Version 2.0"

# Standard library modules.
from tkinter import ttk
from tkinter import filedialog, N, W, E, S, StringVar, DoubleVar, Tk
import logging
import os
import xml.etree.ElementTree as ET

# Third party modules.
from PIL import Image

# Local modules.

# Project modules

# Globals and constants variables.

class TkMainGui(ttk.Frame):
    def __init__(self, root, default_folder=""):
        ttk.Frame.__init__(self, root, padding="3 3 12 12")
        self.default_folder = default_folder

        logging.debug("Create main frame")
        #mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        logging.debug("Create variable")
        self.filepath_ctf = StringVar()
        self.image_folder = StringVar()
        self.vh_ratio = DoubleVar(value=0.76200)
        self.results_text = StringVar()

        self.pcx = 0.0
        self.pcy = 0.0
        self.dd = 0.0

        logging.debug("Create ctf components")
        ctf_entry = ttk.Entry(self, width=80, textvariable=self.filepath_ctf)
        ctf_entry.grid(column=2, row=1, sticky=(W, E))
        ttk.Button(self, text="Select CTF file", command=self.open_ctf_file).grid(column=3, row=1, sticky=W)

        logging.debug("Create image folder components")
        image_entry = ttk.Entry(self, width=80, textvariable=self.image_folder)
        image_entry.grid(column=2, row=2, sticky=(W, E))
        ttk.Button(self, text="Select Image folder", command=self.open_image_folder).grid(column=3, row=2, sticky=W)

        logging.debug("Create vh_ratio components")
        ttk.Label(self, text="VH Ratio").grid(column=1, row=3, sticky=(W, E))
        image_entry = ttk.Entry(self, width=10, textvariable=self.vh_ratio)
        image_entry.grid(column=2, row=3, sticky=(W, E))

        ttk.Button(self, text="Prepare data", command=self.prepare_data, width=80).grid(column=2, row=4, sticky=W)

        results_label = ttk.Label(self, textvariable=self.results_text, state="readonly")
        results_label.grid(column=2, row=5, sticky=(W, E))

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        ctf_entry.focus()

    def open_ctf_file(self):
        logging.debug("open_ctf_file")

        filename = filedialog.askopenfilename(filetypes=(("CTF file", "*.ctf"), ), initialdir=self.default_folder)
        logging.debug(filename)
        self.filepath_ctf.set(filename)

        basename = os.path.splitext(filename)[0]
        if os.path.isdir(basename + "Images"):
            self.image_folder.set(basename + "Images")
        elif os.path.isdir(basename + "_Images"):
            self.image_folder.set(basename + "_Images")

    def open_image_folder(self):
        logging.debug("open_image_folder")

        folder_name = filedialog.askdirectory(initialdir=self.default_folder)
        logging.debug(folder_name)
        self.image_folder.set(folder_name)

    def prepare_data(self):
        logging.debug("prepare_data")

        self.find_pattern_parameters()
        self.create_cpr_file()
        self.rename_image_folder()

        if self.pcx == 0.0 or self.pcy == 0.0 or self.dd == 0.0 or self.vh_ratio == 0.0:
            self.results_text.set("Error")
        else:
            self.results_text.set("Completed")

    def find_pattern_parameters(self):
        logging.debug("find_pattern_parameters")

        number_files = 0
        extension = ""
        folder_name = self.image_folder.get()
        for filename in sorted(os.listdir(folder_name), reverse=True):
            try:
                basename, extension = os.path.splitext(filename)
                items = basename.split("_")
                number_files = int(items[-1])
                break
            except:
                pass
        logging.debug(number_files)
        logging.debug(filename)
        start = filename.rfind("_%i" % (number_files))
        image_filename = filename[:start+1] + "%0*i" % (len(str(number_files)), number_files/2) + extension
        logging.debug(image_filename)
        image_filepath = os.path.join(folder_name, image_filename)
        image = Image.open(image_filepath)
        for items in image.tag.values():
            logging.debug(items)
            try:
                root = ET.fromstring(items[0])
                logging.debug(root.tag)
                logging.debug(root.attrib)
                for element in root.iter('pattern-center-x-pu'):
                    self.pcx = float(element.text)
                for element in root.iter('pattern-center-y-pu'):
                    self.pcy = float(element.text)
                for element in root.iter('detector-distance-pu'):
                    self.dd = float(element.text)

            except (TypeError, ET.ParseError):
                pass

    def create_cpr_file(self):
        logging.debug("create_cpr_file")

        lines = []
        lines.append("\n")
        line = "VHRatio=%.5f\n" % (self.vh_ratio.get())
        lines.append(line)
        line = "PCX=%.17f\n" % (self.pcx)
        lines.append(line)
        line = "PCY=%.17f\n" % (self.pcy)
        lines.append(line)
        line = "DD=%.17f\n" % (self.dd)
        lines.append(line)
        line = "IsFake=false;\n"
        lines.append(line)
        line = "// set isfake to true for X_Y image names and false for HLK style image names.\n"
        lines.append(line)

        filepath_ctf = self.filepath_ctf.get()
        filepath_cpr = os.path.splitext(filepath_ctf)[0] + ".cpr"
        logging.debug(filepath_cpr)
        with open(filepath_cpr, 'w') as file_cpr:
            file_cpr.writelines(lines)

    def rename_image_folder(self):
        logging.debug("rename_image_folder")

        folder_name = self.image_folder.get()
        if folder_name.endswith("_Images"):
            logging.debug(folder_name)
            start = folder_name.rfind("_Images")
            new_folder_name = folder_name[:start] + "Images"
            logging.debug(new_folder_name)
            try:
                os.replace(folder_name, new_folder_name)
            except  OSError as message:
                logging.error(message)
def main_gui():
    import sys
    logging.debug("main_gui")

    logging.debug("Create root")
    root = Tk()
    root.title("Prepare EBSD data for CrossCourt")
    if len(sys.argv) > 1:
        default_folder = sys.argv[1]
    else:
        default_folder = ""
    TkMainGui(root, default_folder=default_folder).pack()

    logging.debug("Mainloop")
    root.mainloop()

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.INFO)
    main_gui()
