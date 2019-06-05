# VFX_hw1_HDR
For generating boli.hdr, one can run



$ python mtb.py --list boli.txt

$ python hdr.py --list boli-after-mtb.txt --output boli.hdr


And one can use MATLAB 2018a and tonemapping.m to do the tonemapping.


$ python mtb.py --list boli.txt


$ tonemapping('boli.hdr', 'boli.png')


Please consult to section of "How to run our Code" in report.pdf for other information.