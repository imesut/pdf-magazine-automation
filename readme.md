# What and Why?

This work is an attempt to get clear text from PDF magazines to provide content for the visually impaired.	This work is an attempt to get clear text from PDF magazines to provide content for the visually impaired.

# Notes

1. Images can be extracted with ghostscript with the command below. But when this process applied, some of the magazines corrupt. So this helper is not added to the repository.
   1. ```gs -o output.pdf -sDEVICE=pdfwrite -dFILTERVECTOR -dFILTERIMAGE input.pdf```
   2. If you want to run after ghost script use like below;
   3. ```gs -o output.pdf -sDEVICE=pdfwrite -dFILTERVECTOR -dFILTERIMAGE input.pdf; python3 pdf.py output.pdf```

2. To convert all pdf magazines use ```for f in *.pdf; do python3 pdf.py "$f"; done```