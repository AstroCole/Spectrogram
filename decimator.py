# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 at 16:39:53 2026

@author: D-Cole
"""


import numpy as np
from gnuradio import gr

"""
This block will act as a decimator, taking input fft vectors, decimating by 
user-defined bin sizes, and outputting same vector size. 

Default bin size is 1 (no decimation). 
"""

class decimator(gr.sync_block):  

    def __init__(self, bin_factor = 1, vec_length = 4096): 
        
        gr.sync_block.__init__(
            self,
            name='Vector Decimator',   # will show up in GRC
            in_sig=[(np.float32, vec_length)],
            out_sig=[(np.float32, vec_length)])
        
        self.vec_length = vec_length
        self.bin_factor = int(bin_factor)


    def set_dec_int(self, bin_factor):
        """
        For user interface defining decimation length. self.bin_factor should
        be evenly divisible by vec_length.
        """
        bin_factor = int(bin_factor)
        print_count = 0
        if bin_factor is not None:
            # Testing even divisibility
            even_test = (self.vec_length % bin_factor == 0)
            
            if even_test:
                self.bin_factor = bin_factor
                print_count = 0
            
            else:
                self.bin_factor = 1
                print_count += 1
                if print_count >= 1:
                    print('Please ensure decimation bins are divisible by the vector length: '+str(self.vec_length))
                    
        else:
            self.bin_factor = 1
        

    def work(self, input_items, output_items):

        vec = input_items[0]
        out = output_items[0]
                
        for i in range(len(vec)):
            
            binned = np.mean(vec[i].reshape(-1, self.bin_factor), axis=1)   # shorter array of averages
            stretched = np.repeat(binned, self.bin_factor)                # back to vector_size, each average repeated
        
            out[i] = stretched
                
        return len(output_items[0])







