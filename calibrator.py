# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 15:19:53 2026

@author: D-Cole
"""

import numpy as np
import csv
import os.path
from gnuradio import gr

class calibrator(gr.basic_block):
    """
    This GNU radio block will calibrate using the position switching
    method: The user must point to a reference position and toggle calibration
    file generation using a button connected to vector_integrator.py input. Once
    a calibration file is made (h_line_cal.csv), this code will apply that calibration
    to the data. If no calibration exists, the code will send a notice and simply pass 
    the data through.
    """
    
    def __init__(self, vector_size, apply_cal = False, cal_path = 'h_line_cal.csv'):
        
        gr.basic_block.__init__(
            self,
            name = 'calibrator',
            in_sig = [(np.float32, vector_size)],
            out_sig = [(np.float32, vector_size)])
        
        self.N = vector_size
        self.apply_cal = apply_cal
        self.cal_path = cal_path
 
    
    def read_cal(self):
        """
        Currently ignores calibration file header. In the future, could add matching
        of calibration file integration times using header information.
        """
        with open(self.cal_path, mode = 'r') as file:
            calreader = csv.reader(file)
            next(calreader)
            calstr = next(calreader)
            cal = np.array(calstr, dtype=float)
        return cal
    
    
    def general_work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]        
        n_produced = 0

        if os.path.isfile(self.cal_path):
            cal = self.read_cal()
            
            for i in range(len(inp)):    
                
                p_cal = (inp[i] - cal[i]) / cal[i]
                
                if n_produced < len(out):
                    out[n_produced] = p_cal
                    n_produced += 1
                    
        else:
            # Basically "just passes on the inputs" if no calibration file exists
            print("Could not calibrate: No calibration file found.")
            
            out[:] = inp[:]
            return len(inp)
        
        
        self.consume(0, len(inp)) # Tells the scheduler that we consumed all input items
        return n_produced
        
        
        
        
        
        
        
        
        
        
        