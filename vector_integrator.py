# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:35:27 2026

Vector integration algorithm for GNU Radio spectrometer

@author: Daniel
"""

import numpy as np

class vec_int():
    
    def __init__(self, vector_size, samp_rate, pfb_size, integration_time_sec):
        
        self.N   = vector_size
        self.t   = int(integration_time_sec)
        self.vps = int(round(samp_rate / (self.N*pfb_size)))
        self.M   = self.vps*self.t
        
    def integrate(self, fft_real_vector):
        
        vec_count = 0
        sec_count = 0
        vec_sum = np.zeros(len(self.N))
        while vec_count <= self.M:
            
            vec_count += 1
            vec_sum += fft_real_vector
            
            # Returning vector average each second
            if sec_count == self.vps
            
            if vec_count == self.M:
                #avg = vec_sum / self.M
                vec_count = 0
                vec_sum = np.zeros(len(self.N))
                
                # Add code here to print avg values to csv file with integration time header / other metadata
                
                return avg
                
            