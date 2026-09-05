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
    
    
    def _load_cal(self):
        if os.path.isfile(self.cal_path):
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
        
        else:
            return None
          
        
    def set_apply_cal(self, apply_cal):
        self.apply_cal = apply_cal
        #self.cal = self._load_cal()


    def general_work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]   
        
        cal = None
        if self.apply_cal:
            cal = self._load_cal()
            
        n_produced = 0

        if cal is not None:   
            # In case of zeros to prevent divide by zero
            snum = 1e-15
            cal  = np.where(cal == 0.0, snum, cal)
             
            for i in range(len(inp)):    
                                
                if n_produced < len(out):
                    p_cal = (inp[i] - cal) / cal
                    out[n_produced] = p_cal
                    n_produced += 1
                    
            self.consume(0, len(inp)) # Tells the scheduler that we consumed all input items
            return n_produced
        
        else:
            # Basically "just passes on the inputs" if no calibration file exists
            if self.apply_cal:
                print("Could not calibrate: No calibration file found.")
            
            out[:len(inp)] = inp[:]
            n_produced = len(inp)
        
        self.consume(0, len(inp)) # Tells the scheduler that we consumed all input items
        return n_produced
        
        
        
        
        
        
        
        
        
        
        