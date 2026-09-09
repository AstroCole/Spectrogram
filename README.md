# Spectrogram

Repository for custom spectrogram or custom functions and blocks for GNU Radio.





\---Log \& Info---



21 Aug 2026: The 'vector_integrator.py' is the first code added here. My first spectrogram is largely being built through GNU Radio, copying a lot of structure from DSPIRA's own spectrogram as learning material. Timed vector integration is a key step for hydrogen line detection, and I am building my own function to do so that can be integrated with GNU Radio python blocks. 


06 Sep 2026: 'calibratory.py' code is a second code to create a custom calibration block in GNU radio companion (GRC). I also customized 'vector_integrator.py' to with a button-press enabled calibration file generator that the calibrator block can read. Calibration is the final step for a functional spectrogram, so now further testing and smaller refining is all that's needed! 


09 Sep 2026: Completed GRC flowgraphs for remote setup with headless pc sending data via ZMQ (wifi) connection to control station with GUI displays. hline_spec.grc is the base flowgraph with full data flow and GUIs combined, operational on any pc hooked up to an RTL-SDR with GNU Radio installed and my custom OOT blocks initialized (see 'adding_gnuradio_oot_block_checklist.md'). cygnus_spec.grc is the headless spectrogram flowgraph hooked up to ZMQ PUB Sinks which will also require the custom OOT blocks to be initialized in its hosted radioconda environment (keep in mind you'll need to generate the flowgraph using GRC before transferring that file to the host server). cygnus_gui.grc is the flowgraph for receiving that ZMQ data on the control station over wifi, simply presenting the data flows using QT GUIs. 
