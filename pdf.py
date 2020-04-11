# TODO: remove images with ghostscript

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from io import StringIO
from matplotlib import pyplot as plt
import operator

vals = []

# TODO: Change this value for a common approach
threshold_rate = 0.05
col_count = 10

resourcemanager = PDFResourceManager()
retstr = StringIO()
#codec = 'utf-8'
laparams = LAParams(detect_vertical=True)
#device = TextConverter(resourcemanager, retstr, laparams=laparams)
device = PDFPageAggregator(resourcemanager, laparams=laparams)
fp = open("atlas_text.pdf", 'rb')
interpreter = PDFPageInterpreter(resourcemanager, device)
password = ""
caching = True
pagenos=set()

title = ""
article = ""

def eliminate_log(pk, desc, *args):
    pass
    #print(pk, "ELIMINATED:", desc, *args)

for PageNumer, page in enumerate(PDFPage.get_pages(fp, pagenos , password=password,caching=caching, check_extractable=True)):
    # TODO: Cover page can be ignored.
    if PageNumer == 49:
        interpreter.process_page(page)
        layout = device.get_result()
        #print(layout)
        page_elements = []
        
        width = round(page.mediabox[2])
        height = round(page.mediabox[3])
        
        half_line = height / 2
        header_threshold = 0 #round(height * threshold_rate)
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
        
        if (len(page_elements) > 0):
            page_elements.sort(key = operator.itemgetter(0, 1))
            # TODO These calculations can be more efficient
            smallest_size = min(page_elements, key=operator.itemgetter(4))[4]
            # biggest_size = max(page_elements, key=operator.itemgetter(4))[4]
            title = max(page_elements, key=operator.itemgetter(4))[-2]
            content = ""

            atl=[]
            btl=[]

            for i in page_elements:
                print(i[2]-i[0],i[0],i[1],i[2],i[3],i[4],i[5][:20],len(i[5]))
                # TODO stringio may be used

                size = i[4]
                # RULE: Remove smallest text - generally image descriptions
                text = i[-2]
                if size != smallest_size:
                    content += text + "\n"
                else:
                    eliminate_log(pk, "Smallest text in the page", text)
                
                #ATL - BTL - Segmentation Logic
                if(i[1] < half_line):
                    atl.append(i[3])
                else:
                    btl.append(i[1])

            if (len(atl) >= 1 and len(btl) >= 1):
                atl_bottom_line = max(atl)
                btl_top_line = min(btl)
                space = btl_top_line - atl_bottom_line

                if space > 5:
                    seperator_line = atl_bottom_line + space / 2
                    print(pk, "atl", atl, "btl", btl)
                    print(pk, seperator_line, atl_bottom_line, btl_top_line, space, "\n")
            
            #print(pk, "TITLE", title)
            #print(pk, "CONTENT", content)

fp.close()
device.close()
retstr.close()

# Plots
# plt.plot(vals)
# plt.show()
