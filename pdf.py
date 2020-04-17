

# TODO: remove images with ghostscript
# TODO stringio may be used
# TODO add keys to arrays for performance
# TODO: What can be parameters
# 1. col_count - 12 worked for Atlas | 10 worked for Ist. Life

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from io import StringIO
from matplotlib import pyplot as plt
import operator
from seperator import get_seperator_line

pdf_file_name = "pozitif"
article = ""
plt_vals = []
# x_axis = []
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
caching = True
pagenos=set()

output_file_count = 1
prev_biggest_item_size = 0
ord_x_pri, ord_y_pri, ord_x_sec, ord_y_sec, ord_size, ord_text = 0, 1, 2, 3, 4, 5

def eliminate_log(pN, desc, *args):
    log_file.write("p: " + str(pN) + " ELIMINATED: " + desc + str(args) + "\n")

def create_file():
    global output_file_count
    otf = open(pdf_file_name + "_" + str(output_file_count) + ".txt", "w")
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
def calculate_titles_and_insert(text_boxes):
    # Title Calculation
    # When new title calculated seperate files

    global prev_biggest_item_size, output_text_file, first_time

    #print("text_boxes", text_boxes)
    biggest_item = max(text_boxes, key=operator.itemgetter(ord_size))
    #print("biggest_item", biggest_item)
    biggest_item_size = biggest_item[4]
    biggest_items = []
    if prev_biggest_item_size == 0:
        prev_biggest_item_size = biggest_item_size
        first_time = True
    
    # if biggest_item_size >= prev_biggest_item_size:
    # There is a threshold
    print("Title calculation: ", prev_biggest_item_size, biggest_item_size)
    # Normalize too big titles
    if biggest_item_size > prev_biggest_item_size:
        biggest_item_size = prev_biggest_item_size
    if abs(biggest_item_size - prev_biggest_item_size) <= 2:
        biggest_items = list(filter(lambda x: x[ord_size] >= biggest_item_size, text_boxes))
        biggest_items_text = map(lambda x: x[ord_text], biggest_items)
        # print("biggest_items", biggest_items)
        title = " ".join(biggest_items_text)
        title = title.capitalize()
        #print("title", title)
        if not first_time:
            #print("closing file", biggest_item_size, prev_biggest_item_size)
            output_text_file.close()
            output_text_file = create_file()
        output_text_file.write("# " + title + "\n")
        prev_biggest_item_size = biggest_item_size
        first_time = False
    return biggest_items

def process_layout(layout, pN):
    text_boxes = []
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

            # Eliminate tablular data
            if text.find("\t") == -1:
                # Cleaned
                text = text.replace("-\n", "").replace("\n", "")

                if (yP < footer_threshold):
                    # RULE: Eliminate single word text which is close to the threshold
                    if((yP < header_threshold * 2 or yP > footer_threshold_2) and len(text.split(" ")) < 2):
                        eliminate_log(pN, "Not in threshold but single word", text)
                    elif(len(text) < 2):
                        eliminate_log(pN, "Text Length is too small", text)
                    else:
                        for line in text_box:
                            if isinstance(line, LTTextLineHorizontal): # Be sure line is an exact line =) 
                                size = get_text_size(line)
                                
                                # plt_vals.extend([size]*round(len(text)/10))
                                # x_axis.extend([pN]*round(len(text)/10))
                                text_boxes.append((xP, yP, xS, yS, size, text))
                                print((xP, yP, xS, yS, size, text[:50]))
                                break # analysis of first line is enough
                else:
                    eliminate_log(pN, "Header / Footer text:", xP, yP, text)
    return text_boxes

def generate_content(text_boxes):
    content = ""
    for i in text_boxes:
        #print( i[ord_x_pri], i[ord_y_pri], i[ord_x_sec], i[ord_y_sec], i[ord_size], i[ord_text][:20] )
        size = i[ord_size]
        text = i[ord_text]
        add_new_line = True
        #print(text)
            
        # RULE: Remove smallest text - generally image descriptions
        # Smallest size, I'm sceptical about this.
        # If there is no footer text smallest size will be main text's size
        # If three or more text box has the same smallest size then ignore it.
        #smallest_size = min(text_boxes, key=operator.itemgetter(ord_size))[ord_size]
        #if len(list(filter(lambda x: x[ord_size] == smallest_size, text_boxes))) < 3:
        #    smallest_size = smallest_size
        #else:
        #    smallest_size = 0
        #if size != smallest_size:
        # else:
        #     eliminate_log(pN, "Smallest text in the page", text)
        # RULE: Merge two lines if second one is beginning with lowercase
        if text[0] == text[0].lower(): # sentence begins with lower letter
            # print("found lowercase beginning")
            # print("content" + content)
            content = content[:-2] + " " # Remove new line chars (\n) from previous line
        elif text[-1] not in [".", "!", "?"]:
            add_new_line = False
        content += text
        if add_new_line : content += "\n"
            

            
    output_text_file.write(content)

def process_article_block(block):
    block.sort(key = operator.itemgetter(ord_x_pri, ord_y_pri))
    titles = calculate_titles_and_insert(block)
    for item in titles:
        block.remove(item)
    generate_content(block)

for pN, page in enumerate(PDFPage.get_pages(fp, pagenos, caching=caching, check_extractable=True)):
    # Cover and index pages ignored.
    if pN > 1 and pN < 31:
        interpreter.process_page(page)
        # LAYOUT INITIALIZATION - Each page may have different width and height
        layout = device.get_result()
        width, height = round( page.mediabox[2] ), round( page.mediabox[3] )
        col_width_divider = width / col_count
        half_line = height / 2
        header_threshold = 0 #round(height * threshold_rate)
        footer_threshold = round(height * (1 - threshold_rate))
        footer_threshold_2 = round(height * (1 - threshold_rate * 2))
        
        print(pN, "PAGE INFO: ", "width", width, "height", height, "header_threshold", header_threshold, "footer_threshold", footer_threshold)

        text_boxes = process_layout(layout, pN)

        if len(text_boxes) > 3:            
            text_boxes.sort(key = operator.itemgetter(ord_x_pri, ord_y_pri))

            # RULE: remove footer fext like page number and magazine name
            bottom_item = max(text_boxes, key=operator.itemgetter(ord_x_pri))
            text_boxes.remove(bottom_item)

            # Dividing Page in two part with seperator
            seperator_line, space = get_seperator_line( list(map(lambda item: [item[ord_y_pri], item[ord_y_sec]], text_boxes)) )
            
            print("seperator line: ", seperator_line, "space", space)

            if space > 20:
                above_the_seperator_items = list(filter(lambda text_box: text_box[ord_y_sec] < seperator_line, text_boxes))
                for item in above_the_seperator_items: text_boxes.remove(item)
                below_the_seperator_items = text_boxes
                del text_boxes

                #print(above_the_seperator_items)
                #print(below_the_seperator_items)
                
                process_article_block(above_the_seperator_items)
                process_article_block(below_the_seperator_items)

            else:
                process_article_block(text_boxes)

fp.close()
device.close()
retstr.close()
log_file.close()

# Plots
# plt.xticks(plt_vals, x_axis)
# plt.plot(plt_vals)
plt.show()
