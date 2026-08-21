# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:35:27 2026

Vector integration algorithm for GNU Radio spectrometer

@author: Daniel Cole
"""

import numpy as np
import csv
import time
from gnuradio import gr

class vec_int(gr.sync_block):
    """
    The input vectors for this integration are after a block of code that converts the 
    fft outputs to real power spectrum (multiplying each output by its conjugate).
    
    self.M is the number of vectors to compute in the amount of time provided for integration.
    This function integrates that many vectors by summing them all up and outputting the 
    total average.
    
    Note: This is simple on output since it only sends the final avg vector and saves it as
    a file, rather than a continuous spectra GUI update (like a waterfall)
    
    Will output a vector and csv file of the integration with metadata when complete.
    """
    
    def __init__(self, vector_size, samp_rate, pfb_size, integration_time_sec):
        """
        self.vps assumes a NON-OVERLAPPING PFB: See GNU Radio blocks. If PFB switches to 
        overlapping method, the "pfb_size" factor in self.vps may need to be dropped.
        """
        gr.sync_block.__init__(
            self,
            name = 'vec_int',
            in_sig = [(np.float32, vector_size)],
            out_sig = [(np.float32, vector_size)])
        
        self.N   = vector_size
        self.t   = int(integration_time_sec)
        self.vps = int(round(samp_rate / (self.N*pfb_size)))
        self.M   = self.vps*self.t
    
        self.vec_sum = np.zeros(self.N, np.float64)
        self.vec_count = 0
        
        self.outfile = open('h_line_integration_output.csv', 'a', newline = '')
        self.writer  = csv.writer(self.outfile)
                
    def work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]
        
        n_produced = 0
        
        for i in range(len(inp)):
            self.vec_sum += inp[i]
            self.vec_count += 1
            
            if self.vec_count >= self.M:
                out[n_produced] = (self.vec_sum / self.M).astype(np.float32)
                n_produced += 1
                
                timestamp = time.time()
                # Writes time of integration, number of vectors integrated, and integration time to file
                self.writer.writerow([timestamp, self.M, self.t] + out[n_produced].tolist())
                self.outfile.flush()
                
                self.vec_count = 0
                self.vec_sum = np.zeros(self.N, dtype=np.float64)
            
        # Can use GNU radio file sink block to save a binary file, then send it to control station
        # Once control station has the binary file, can read it with code e.g. np.fromfile
        return n_produced
            
            