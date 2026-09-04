#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 dcole.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
import csv
import time
from gnuradio import gr

class timed_vec_int(gr.basic_block):
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
    
    def __init__(self, vector_size, samp_rate, pfb_size, integration_time_sec,
                 write_to_file = True, output_path = 'h_line_output.csv',
                 write_cal = False, cal_path = 'h_line_cal.csv'):
        """
        self.vps assumes a NON-OVERLAPPING PFB: See GNU Radio blocks. If PFB switches to 
        overlapping method, the "pfb_size" factor in self.vps may need to be dropped.
        
        Also, write_cal is designed to trigger using a push button: True when pressed, false 
        on automatic release. The logic in this code therefore actions on "True" but there
        is no action on "False". This could cause problems if the input type is changed, i.e.
        to a toggle method.
        """
        gr.basic_block.__init__(
            self,
            name = 'timed_vec_int',
            in_sig = [(np.float32, vector_size)],
            out_sig = [(np.float32, vector_size)])
        
        self.N   = vector_size
        self.t   = int(integration_time_sec)
        self.vps = int(round(samp_rate / (self.N*pfb_size)))
        self.M   = self.vps*self.t
    
        self.vec_sum   = np.zeros(self.N, np.float64)
        self.vec_count = 0
        
        self.write_to_file = write_to_file
        self.output_path   = output_path
        self.outfile = None
        self.writer  = None
        if self.write_to_file:
            self._open_file()
        
        # self.write_cal = write_cal
        self.cal_path  = cal_path
        self.calfile   = None
        self.calwriter = None
        # if self.write_cal:
        #     self._open_cal()
    
    
#%% Functions defining integration file writing
        
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
    
    
#%% Functions defining calibration file writing
    
    def _open_cal(self):
        # Opens calibration file for calibration if toggled; will overwrite
        if self.calfile is None:
            self.calfile = open(self.cal_path, 'w')
            self.calwriter = csv.writer(self.calfile)
    
    def _close_cal(self):
        if self.calfile is not None:
            self.calfile.close()
            self.calfile = None
            self.calwriter = None
    
    def set_write_cal(self, write_cal):
        """
        Callback GNU Radio calls when the calibration push button fires.
        Fires only when the button is pressed (True). 
        """
        if write_cal:
            self._open_cal()

    
    
    def stop(self):
        """
        GNU Radio calls stop as part of normal shutdown sequence. This
        ensures the CSV file is closed cleanly when the app stops.
        """
        self._close_file()
        self._close_cal()
        return True
    
    
#%% Functions for integration
    
    def set_integration_time_sec(self, integration_time_sec):
        """
        Callback for live integration time switching. Recomputes M and 
        discards any in-progress accumulation.
        """
        self.t = int(integration_time_sec)
        self.M = self.vps * self.t
        self.vec_count = 0
        self.vec_sum = np.zeros(self.N, dtype = np.float64)
        
        
    def general_work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]
        
        n_produced = 0
        
        for i in range(len(inp)):
            self.vec_sum += inp[i]
            self.vec_count += 1
            
            if self.vec_count >= self.M:
                avg = (self.vec_sum / self.M).astype(np.float32)
                
                if self.write_to_file and self.writer is not None:
                    timestamp = time.time()
                    # Writes time of integration, number of vectors integrated, and integration time to file
                    self.writer.writerow([timestamp, self.M, self.t] + avg.tolist())
                    self.outfile.flush()
                
                if self.calwriter is not None:
                    timestamp = time.time()
                    self.calwriter.writerow([timestamp, self.M, self.t] + avg.tolist())
                    self.calfile.flush()
                    print("Calibration file completed.")
                    self._close_cal()
                    
                if n_produced < len(out):
                    out[n_produced] = avg
                    n_produced += 1
                    
                self.vec_count = 0
                self.vec_sum = np.zeros(self.N, dtype=np.float64)
            
        self.consume(0, len(inp)) # Tells the scheduler that we consumed all input items
        return n_produced