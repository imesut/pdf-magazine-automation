# TODO: remove images with ghostscript

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from io import StringIO
from matplotlib import pyplot as plt
import operator

vals = []

# TODO: Change this
threshold_rate = 0.05
col_count = 10

resourcemanager = PDFResourceManager()
retstr = StringIO()
#codec = 'utf-8'
laparams = LAParams(detect_vertical=True)
#device = TextConverter(resourcemanager, retstr, laparams=laparams)
device = PDFPageAggregator(resourcemanager, laparams=laparams)
fp = open("swi.pdf", 'rb')
interpreter = PDFPageInterpreter(resourcemanager, device)
password = ""
caching = True
pagenos=set()

title = ""
article = ""

def eliminate_log(pk, desc, *args):
    print(pk, "ELIMINATED:", desc, *args)

for PageNumer,page in enumerate(PDFPage.get_pages(fp, pagenos , password=password,caching=caching, check_extractable=True)):
    if PageNumer == 53:
        interpreter.process_page(page)
        layout = device.get_result()
        #print(layout)
        page_elements = []
        
        width = round(page.mediabox[2])
        height = round(page.mediabox[3])
        
        header_threshold = round(height * threshold_rate)
        footer_threshold = round(height * (1 - threshold_rate))
        footer_threshold_2 = round(height * (1 - threshold_rate * 2))
        
        # pk -> page key
        pk = "p" + str(PageNumer)
        col_width_divider = width / col_count

        print(pk, "PAGE INFO: ", "width", width, "height", height, "header_threshold", header_threshold, "footer_threshold", footer_threshold)

        for element in layout:
            #print(element)
            if isinstance(element, LTTextBoxHorizontal):
                # Calculates text's column number
                # (Sometimes two successing texts x value differ a little. eliminating differences by assigning col values)
                xP = round(element.x0 / col_width_divider)
                yP = height-round(element.y1)
                xS = round(element.x1 / col_width_divider) 
                yS = height-round(element.y0)
                
                # Plain
                text = element.get_text()
                # Cleaned
                text = text.replace("-\n", "").replace("\n", "")

                # RULE: Elminate header and footer texts like page numbers and magazine name
                if (yP > header_threshold and yP < footer_threshold):
                    # RULE: Eliminate single word text which is close to the threshold
                    if((yP < header_threshold * 2 or yP > footer_threshold_2) and len(text.split(" ")) < 2):
                        eliminate_log(pk, "Not in threshold but single word", text)
                    elif(len(text) < 2):
                        eliminate_log(pk, "Text Length is too small", text)
                    else:
                        for sub_element in element:
                            if isinstance(sub_element, LTTextLineHorizontal):
                                size = int(sub_element.height)
                                page_elements.append((xP, yP, xS, yS, size, text, len(text)))
                                break
                        #page_elements.append((xP, yP, xS, yS, text, len(text)))
                else:
                    eliminate_log(pk, "Header / Footer text:", xP, yP, text)
        
        page_elements.sort(key = operator.itemgetter(0, 1))
        # TODO These calculations can be more efficient
        smallest_size = min(page_elements, key=operator.itemgetter(4))[4]
        # biggest_size = max(page_elements, key=operator.itemgetter(4))[4]
        title = max(page_elements, key=operator.itemgetter(4))[-2]
        content = ""
        for i in page_elements:
            print(i[2]-i[0],i[0],i[1],i[2],i[3],i[4],i[5][:20])
        # TODO stringio may be used
        for i in page_elements:
            size = i[4]
            # RULE: Remove smallest text - generally image descriptions
            text = i[-2]
            if size != smallest_size:
                content += text + "\n"
            else:
                eliminate_log(pk, "Smallest text in the page", text)
        
        #print(pk, "TITLE", title)
        #print(pk, "CONTENT", content)

fp.close()
device.close()
retstr.close()

# Plots
# plt.plot(vals)
# plt.show()
