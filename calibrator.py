# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 15:19:53 2026

@author: D-Cole
"""

import numpy as np
import csv
from gnuradio import gr

class calibrator(gr.basic_block):
    """
    This GNU radio block will calibrate using the position switching
    method: The user must point to a reference position and toggle this
    calibration block, then untoggle it to apply its output (file) after
    integration. 
    
    Block expects input from integrator output. See vector_integrator.py. 
    """
    
    def __init__(self, vector_size, apply_cal = False,
                 write_to_file = True, output_path = 'h_line_cal.csv'):
        
        gr.basic_block.__init__(
            self,
            name = 'calibrator',
            in_sig = [(np.float32, vector_size)],
            out_sig = [(np.float32, vector_size)])
        
        self.N = vector_size
        self.apply_cal = apply_cal
        self.write_to_file = write_to_file
        self.cal_spectrum = None

        self.outfile = None
        self.writer  = None
        if self.write_to_file:
            self._open_file()    


    def _open_file(self):
        # Opens (or re-opens) the CSV file for appending
        if self.outfile is None:
            self.outfile = open(self.output_path, 'a', newline='')
            self.writer  = csv.writer(self.outfile)
    
    def _close_file(self):
        if self.outfile is not None:
            self.outfile.close()
            self.outfile = None
            self.writer = None
            
    def set_write_to_file(self, write_to_file):
        """
        Callback GNU Radio calls when the GUI toggle changes while running.
        Opens or closes the file handle in step with the toggle GUI.
        """
        self.write_to_file = write_to_file
        if self.write_to_file:
            self._open_file()
        else:
            self._close_file()
    
    
    def general_work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        