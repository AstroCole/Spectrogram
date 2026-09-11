#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Spectrometer
# Author: DCole
# Description: Using core setup from DSPiRA Spectrometer
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import my_h_line_tools
from gnuradio import zeromq
import numpy as np
import osmosdr
import time
import threading




class cygnus_spec(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Spectrometer", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.vec_length = vec_length = 4096
        self.sinc_loc = sinc_loc = np.arange(-np.pi*4/2., np.pi*4/2., np.pi/vec_length)
        self.sinc = sinc = np.sinc(sinc_loc/np.pi)
        self.hamming = hamming = 1
        self.write_to_file = write_to_file = False
        self.write_cal = write_cal = 0
        self.samp_rate = samp_rate = 2048000
        self.integration_time_sec = integration_time_sec = 5
        self.custom_window = custom_window = sinc*np.hamming(4*vec_length)
        self.apply_cal = apply_cal = False
        self.SDR_RF_Gain = SDR_RF_Gain = 40
        self.Frequency = Frequency = 1.4204058e9

        ##################################################
        # Blocks
        ##################################################

        self.zeromq_pub_sink_0_0_0 = zeromq.pub_sink(gr.sizeof_float, vec_length, 'tcp://*:5679', 100, False, (-1), '', True, True)
        self.zeromq_pub_sink_0_0 = zeromq.pub_sink(gr.sizeof_float, vec_length, 'tcp://*:5678', 100, False, (-1), '', True, True)
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'rtl=0,bias=1'
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(Frequency, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(SDR_RF_Gain, 0)
        self.rtlsdr_source_0.set_if_gain(10, 0)
        self.rtlsdr_source_0.set_bb_gain(10, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.my_h_line_tools_timed_vec_int_0 = my_h_line_tools.timed_vec_int(vec_length, samp_rate, integration_time_sec, write_to_file, 'h_line_output.csv', 'h_line_cal.csv')
        self.my_h_line_tools_calibrator_0 = my_h_line_tools.calibrator(vec_length, apply_cal, 'h_line_cal.csv')
        self.fft_vxx_0 = fft.fft_vcc(vec_length, True, window.blackmanharris(vec_length), True, 1)
        self.blocks_stream_to_vector_0_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_multiply_const_vxx_0_2 = blocks.multiply_const_vcc(custom_window[0:vec_length])
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vcc(custom_window[vec_length:2*vec_length])
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc(custom_window[2*vec_length:3*vec_length])
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc(custom_window[-vec_length:])
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(vec_length)
        self.blocks_delay_0_1 = blocks.delay(gr.sizeof_gr_complex*1, (vec_length*3))
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, (vec_length*2))
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(vec_length)
        self.blocks_add_xx_0 = blocks.add_vcc(vec_length)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_xx_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.my_h_line_tools_timed_vec_int_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.zeromq_pub_sink_0_0_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_stream_to_vector_0_1, 0))
        self.connect((self.blocks_delay_0_1, 0), (self.blocks_stream_to_vector_0_2, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_multiply_const_vxx_0_2, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0_2, 0), (self.blocks_multiply_const_vxx_0_2, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.my_h_line_tools_calibrator_0, 0), (self.zeromq_pub_sink_0_0, 0))
        self.connect((self.my_h_line_tools_timed_vec_int_0, 0), (self.my_h_line_tools_calibrator_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_delay_0_1, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_stream_to_vector_0, 0))


    def get_vec_length(self):
        return self.vec_length

    def set_vec_length(self, vec_length):
        self.vec_length = vec_length
        self.set_custom_window(self.sinc*np.hamming(4*self.vec_length))
        self.set_sinc_loc(np.arange(-np.pi*4/2., np.pi*4/2., np.pi/self.vec_length))
        self.blocks_delay_0.set_dly(int(self.vec_length))
        self.blocks_delay_0_0.set_dly(int((self.vec_length*2)))
        self.blocks_delay_0_1.set_dly(int((self.vec_length*3)))
        self.blocks_multiply_const_vxx_0.set_k(self.custom_window[-self.vec_length:])
        self.blocks_multiply_const_vxx_0_0.set_k(self.custom_window[2*self.vec_length:3*self.vec_length])
        self.blocks_multiply_const_vxx_0_1.set_k(self.custom_window[self.vec_length:2*self.vec_length])
        self.blocks_multiply_const_vxx_0_2.set_k(self.custom_window[0:self.vec_length])
        self.fft_vxx_0.set_window(window.blackmanharris(self.vec_length))

    def get_sinc_loc(self):
        return self.sinc_loc

    def set_sinc_loc(self, sinc_loc):
        self.sinc_loc = sinc_loc
        self.set_sinc(np.sinc(self.sinc_loc/np.pi))

    def get_sinc(self):
        return self.sinc

    def set_sinc(self, sinc):
        self.sinc = sinc
        self.set_custom_window(self.sinc*np.hamming(4*self.vec_length))
        self.set_sinc(np.sinc(self.sinc_loc/np.pi))

    def get_hamming(self):
        return self.hamming

    def set_hamming(self, hamming):
        self.hamming = hamming

    def get_write_to_file(self):
        return self.write_to_file

    def set_write_to_file(self, write_to_file):
        self.write_to_file = write_to_file
        self.my_h_line_tools_timed_vec_int_0.set_write_to_file(self.write_to_file)

    def get_write_cal(self):
        return self.write_cal

    def set_write_cal(self, write_cal):
        self.write_cal = write_cal
        self.my_h_line_tools_timed_vec_int_0.set_write_cal(self.write_cal)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_integration_time_sec(self):
        return self.integration_time_sec

    def set_integration_time_sec(self, integration_time_sec):
        self.integration_time_sec = integration_time_sec
        self.my_h_line_tools_timed_vec_int_0.set_integration_time_sec(self.integration_time_sec)

    def get_custom_window(self):
        return self.custom_window

    def set_custom_window(self, custom_window):
        self.custom_window = custom_window
        self.blocks_multiply_const_vxx_0.set_k(self.custom_window[-self.vec_length:])
        self.blocks_multiply_const_vxx_0_0.set_k(self.custom_window[2*self.vec_length:3*self.vec_length])
        self.blocks_multiply_const_vxx_0_1.set_k(self.custom_window[self.vec_length:2*self.vec_length])
        self.blocks_multiply_const_vxx_0_2.set_k(self.custom_window[0:self.vec_length])

    def get_apply_cal(self):
        return self.apply_cal

    def set_apply_cal(self, apply_cal):
        self.apply_cal = apply_cal
        self.my_h_line_tools_calibrator_0.set_apply_cal(self.apply_cal)

    def get_SDR_RF_Gain(self):
        return self.SDR_RF_Gain

    def set_SDR_RF_Gain(self, SDR_RF_Gain):
        self.SDR_RF_Gain = SDR_RF_Gain
        self.rtlsdr_source_0.set_gain(self.SDR_RF_Gain, 0)

    def get_Frequency(self):
        return self.Frequency

    def set_Frequency(self, Frequency):
        self.Frequency = Frequency
        self.rtlsdr_source_0.set_center_freq(self.Frequency, 0)




def main(top_block_cls=cygnus_spec, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    # try:
    #     input('Press Enter to quit: ')
    # except EOFError:
    #     pass
    # tb.stop()
    # tb.wait()
    
    COMMANDS = {
    'stop': 'stop the flowgraph and exit',
    'get_cal': 'capture a new calibration file (point at cold sky first)',
    'apply_cal': 'toggle calibration on/off (default: off)',
    'write_file': 'toggle CSV logging on/off (default: off)',
    'set_int <sec>': 'set integration time in seconds; e.g. 5 min = 300. (default: 5 sec)',
    'set_gain <dB>': 'set SDR RF gain (keep values between 1 and 50; default: 40)',
    'list': 'show this list',
    }
    
    
    print('\n\n ----- Welcome to the Cygnus H-Line Spectrometer! -----')
    print("""
    Enter commands to adjust variables or type "stop" to close.
          
    Type 'list' to see all available commands. 
          """)
    while True:
        try: 
            command_l = input('\n>> ').strip().lower().split(' ')
            
            command = command_l[0]
            if len(command_l) > 1:
                value = command_l[1]

            if command == 'stop':
                break
            
            elif command == 'get_cal':
                tb.set_write_cal(True)
                print("Writing calibration file...")
                
            elif command == 'apply_cal':
                apply_cal = tb.get_apply_cal()
                cal_switch = not apply_cal
                tb.set_apply_cal(cal_switch)
                print('Set calibration to '+str(cal_switch))
            
            elif command == 'write_file':
                write_file = tb.get_write_to_file()
                write_switch = not write_file
                tb.set_write_to_file(write_switch)
                print('Writing to CSV: '+str(write_switch))
                
            elif command == 'set_int':
                int_time = value
                tb.set_integration_time_sec(float(int_time))
                print('Integration time set to '+str(int_time)+' sec')

            elif command == 'set_gain':
                gain = value
                tb.set_SDR_RF_Gain(float(gain))
                print('SDR Gain set to '+str(gain))
            
            elif command == 'list':
                print('\n-------------------- Command List --------------------\n')
                for cmd, desc in COMMANDS.items():
                    print(f"  {cmd:<20} - {desc}")
            
            elif command == '':
                pass
        
        except NameError:
            print("Please supply a value.")
            
        except ValueError:
            print("Invalid format.")
        
        except EOFError:
            pass
            
    print('Closing Cygnus...')     
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    main()









