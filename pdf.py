# TODO: remove images with ghostscript
# TODO stringio may be used

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from io import StringIO
from matplotlib import pyplot as plt
import operator

pdf_file_name = "atlas_text"
article = ""
vals = []
log_file = open(pdf_file_name + ".log", "w")

# TODO: Change this value for a common approach
threshold_rate = 0.05
col_count = 10

resourcemanager = PDFResourceManager()
retstr = StringIO()
#codec = 'utf-8'
laparams = LAParams(detect_vertical=True)
#device = TextConverter(resourcemanager, retstr, laparams=laparams)
device = PDFPageAggregator(resourcemanager, laparams=laparams)
fp = open(pdf_file_name + ".pdf", 'rb')
interpreter = PDFPageInterpreter(resourcemanager, device)
password = ""
caching = True
pagenos=set()

output_file_count = 1
prev_biggest_item_size = 0

def eliminate_log(pk, desc, *args):
    log_file.write(pk + " ELIMINATED: " + desc + str(*args) + "\n")

def create_file():
    global output_file_count
    otf = open(pdf_file_name + "_" + str(output_file_count) + ".md", "w")
    output_file_count += 1
    return otf

def get_text_size(horizontal_text_line):
    # RULE: Check if just first char is higher than others
    size = []
    count = 0
    for char in horizontal_text_line:
        if isinstance(char, LTChar):
            size.append(int(char.size / 5))
            count += 1
        if count == 5: # Just 5 character is enough
            break
    # size returns an array like [7, 1, 1, 1, 1] if just first letter is high
    # We'll return the last item
    return size[-1]


output_text_file = create_file()

first_time = False

def calculate_and_add_title(text_boxes):
    # Title Calculation
    # When new title calculated seperate files
    global prev_biggest_item_size, output_text_file, first_time
    biggest_item = max(text_boxes, key=operator.itemgetter(4))
    biggest_item_size = biggest_item[4]
    if prev_biggest_item_size == 0:
        prev_biggest_item_size = biggest_item_size
        first_time = True
    
    # if biggest_item_size >= prev_biggest_item_size:
    # There is a threshold
    if abs(biggest_item_size - prev_biggest_item_size) <= 2:
        biggest_items = filter(lambda x: x[4] == biggest_item_size, text_boxes)
        biggest_items_text = map(lambda x: x[5], biggest_items)
        title = " ".join(biggest_items_text)
        if not first_time:
            print("closing file", biggest_item_size, prev_biggest_item_size)
            output_text_file.close()
            output_text_file = create_file()
        output_text_file.write("# " + title)
        prev_biggest_item_size = biggest_item_size
        first_time = False

for pN, page in enumerate(PDFPage.get_pages(fp, pagenos, password=password, caching=caching, check_extractable=True)):
    # Cover page ignored.
    if pN > 0 and pN >= 29 and pN <= 31:
        interpreter.process_page(page)
        layout = device.get_result()
        #print(layout)
        text_boxes = []
        title = ""

        width = round(page.mediabox[2])
        height = round(page.mediabox[3])
        
        half_line = height / 2
        header_threshold = 0 #round(height * threshold_rate)
        footer_threshold = round(height * (1 - threshold_rate))
        footer_threshold_2 = round(height * (1 - threshold_rate * 2))
        
        # pk -> page key
        pk = "p" + str(pN)
        col_width_divider = width / col_count

        print(pk, "PAGE INFO: ", "width", width, "height", height, "header_threshold", header_threshold, "footer_threshold", footer_threshold)

        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                text_box = element
                # Calculates text's column number
                # (Sometimes two successing texts x value differ a little. eliminating differences by assigning col values)
                xP = round(text_box.x0 / col_width_divider)
                yP = height-round(text_box.y1)
                xS = round(text_box.x1 / col_width_divider) 
                yS = height-round(text_box.y0)
                
                # Plain
                text = text_box.get_text()
                # Cleaned
                text = text.replace("-\n", "").replace("\n", "")

                if (yP < footer_threshold):
                    # RULE: Eliminate single word text which is close to the threshold
                    if((yP < header_threshold * 2 or yP > footer_threshold_2) and len(text.split(" ")) < 2):
                        eliminate_log(pk, "Not in threshold but single word", text)
                    elif(len(text) < 2):
                        eliminate_log(pk, "Text Length is too small", text)
                    else:
                        for line in text_box:
                            if isinstance(line, LTTextLineHorizontal): # Be sure line is an exact line =) 
                                size = get_text_size(line)
                                text_boxes.append((xP, yP, xS, yS, size, text, len(text)))
                                break # analysis of first line is enough
                else:
                    eliminate_log(pk, "Header / Footer text:", xP, yP, text)

        if (len(text_boxes) > 0):
            text_boxes.sort(key = operator.itemgetter(0, 1))
            
            # TODO These calculations can be more efficient
            # Smallest size, I'm sceptical about this.If there is no footer text smallest size will be main text's size
            smallest_size = min(text_boxes, key=operator.itemgetter(4))[4]
            
            # TODO seperate this function
            calculate_and_add_title(text_boxes)

            content = ""
            ymax, bottom_item = 0, 0

            for i in text_boxes:
                if i[1] > ymax:
                    ymax = i[1]
                    bottom_item = i

            # RULE: remove footer fext like page number and magazine name
            text_boxes.remove(bottom_item)

            # TODO: Call seperator
            # TODO: Organize vals order

            for i in text_boxes:
                #print(i[0], i[1], i[2], i[3], i[4], i[5][:20], len(i[5]))
                size = i[4]
                # RULE: Remove smallest text - generally image descriptions
                text = i[-2]
                if size != smallest_size:
                    content += text + "\n"
                else:
                    eliminate_log(pk, "Smallest text in the page", text)
                
            output_text_file.write(content)
            print("\n")

fp.close()
device.close()
retstr.close()
log_file.close()

# Plots
# plt.plot(vals)
# plt.show()
