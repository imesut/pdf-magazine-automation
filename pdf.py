# TODO add keys to arrays for performance
# TODO: What can be functional parameters
# 1. col_count - 12 worked for Atlas | 10 worked for Ist. Life
# 2. file name

# PDF MINER
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage

# SYSTEM UTILS
import operator
import os
import sys
# TODO Evaluate time for benchmark purposes
#import time

# UTILS
from footer_items import get_repeating_footer_items
from seperator import get_seperator_line

# VISUALIZATION
from matplotlib import pyplot as plt

################################################################################

pdf_file_name = ""
current_file_name = ""
if len(sys.argv) > 1:
    pdf_file_name = sys.argv[1]
else:
    pdf_file_name = "pozitif.pdf"

name_wo_ext = pdf_file_name[:-4]
folder = "output/" + name_wo_ext + "/"
if not os.path.isdir("output/"):
    os.mkdir("output/")
if not os.path.isdir(folder):
    os.mkdir(folder)

################################################################################

article = ""
plt_vals = []
log_file = open("output/" + pdf_file_name + ".log", "w")
pages = []
width = 0
height = 0
first_time = True

# TODO: Change this value for a common approach
threshold_rate = 0  # 0.05
col_count = 6

article_count = 1
title_size = 0
ord_x_pri, ord_y_pri, ord_x_sec, ord_y_sec, ord_size, ord_text = 0, 1, 2, 3, 4, 5

################################################################################


def eliminate_log(pN, desc, *args):
    log_file.write("p: " + str(pN) + " ELIMINATED: " + desc + str(args) + "\n")


def create_file():
    global article_count
    current_file_name = folder + name_wo_ext + "_" + str(article_count) + ".txt"
    otf = open(current_file_name, "w")
    article_count += 1
    return otf, current_file_name


def get_text_size_of_line(horizontal_text_line):
    # RULE: Check if just first char is higher than others
    size = []
    count = 0
    for char in horizontal_text_line:
        if isinstance(char, LTChar):
            size.append(int(char.size / 5))
            count += 1
        if count == 5:  # Max 5 character is enough
            break
    # size returns an array like [7, 1, 1, 1, 1] if just first letter is high
    # We'll return the last item
    return size[-1]


output_text_file, current_file_name = create_file()


def calculate_titles_and_insert(text_boxes, *args):
    # Title Calculation
    # When new title calculated seperate files

    global output_text_file, first_time, title_size, current_file_name

    min_size = title_size
    if len(args) == 1:
        min_size = args[0]

    titles = list(filter(lambda x: x[ord_size] >= min_size, text_boxes))


    # print("title size", min_size)
    # print("title logic", text_boxes[:5])
    # print(titles)

    # print(titles)

    if len(titles) > 0:
        merged_title = " ".join(
            list(map(lambda x: x[ord_text], titles))).capitalize()
        # print(merged_title)
        if len(merged_title) > 250:
            log_file.write("Title length exceed 250 characters, behaving like normal text, min_size is increasing to", min_size+1)
            titles = calculate_titles_and_insert(text_boxes, min_size + 1)
        else:
            if not first_time:
                output_text_file.close()
                with open(current_file_name, "r") as f:
                    if len(f.read()) < 500:
                        output_text_file = open(current_file_name, "w")
                    else:
                        output_text_file, current_file_name = create_file()
            output_text_file.write("# " + merged_title + "\n")
            first_time = False

    return titles


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
                        eliminate_log(
                            pN, "Not in threshold but single word", text)
                    elif(len(text) < 2):
                        eliminate_log(pN, "Text Length is too small", text)
                    else:
                        for line in text_box:
                            # Be sure line is an exact line =)
                            if isinstance(line, LTTextLineHorizontal):
                                size = get_text_size_of_line(line)
                                text_boxes.append((xP, yP, xS, yS, size, text))
                                #print((xP, yP, xS, yS, size, text[:30]))
                                break  # analysis of first line is enough
                else:
                    eliminate_log(pN, "Header / Footer text:", xP, yP, text)
    return text_boxes


def generate_content(text_boxes):
    content = ""
    for i in text_boxes:
        text = i[ord_text]
        add_new_line = True
        # RULE: Add to the previous line if sentence begins with lower letter
        if text[0] == text[0].lower():
            add_new_line = False
        text += text + " "
        if add_new_line:
            text = "\n" + text
        content += text
    output_text_file.write(content)


def process_article_block(block):
    block.sort(key=operator.itemgetter(ord_x_pri, ord_y_pri))
    titles = calculate_titles_and_insert(block)
    for item in titles:
        block.remove(item)
    generate_content(block)


def clean_chars_for_bottom_item(text):
    return "".join([char for char in text if not char.isdigit()])

################################################################################


resourcemanager = PDFResourceManager()
laparams = LAParams(detect_vertical=True, all_texts=True)
device = PDFPageAggregator(resourcemanager, laparams=laparams)
fp = open(pdf_file_name, 'rb')
interpreter = PDFPageInterpreter(resourcemanager, device)
caching = False
pagenos = set()
print("started to parse: ", pdf_file_name)

for pN, page in enumerate(PDFPage.get_pages(fp, pagenos, caching=caching, check_extractable=True)):
    # Cover and index pages ignored.
    if pN > 1:
        interpreter.process_page(page)
        layout = device.get_result()
        print(pN, end=" ")
        header_threshold = 0  # round(height * threshold_rate)
        width = round(page.mediabox[2])
        height = round(page.mediabox[3])
        col_width_divider = width / col_count
        footer_threshold = round(height * (1 - threshold_rate))
        footer_threshold_2 = round(height * (1 - threshold_rate * 2))
        text_boxes = process_layout(layout, pN)
        pages.append(text_boxes)

fp.close()
device.close()
del pagenos

################################################################################


print("started to process: ", pdf_file_name)


bottom_items = []
sizes = []

top = height * 0.1
bottom = height - 100  # height * 0.85


# LAYOUT ANALYSIS
for page in pages:
    for tb in page:
        size = tb[ord_size]
        sizes.append(size)
        if tb[ord_y_pri] > bottom:
            # Use shortened text
            text = clean_chars_for_bottom_item(tb[ord_text])
            text = text[:15]
            bottom_items.append((tb[ord_y_pri], tb[ord_y_sec], text))

sizes.sort()

# plt.plot(sizes)
# plt.show()

title_size_p85 = sizes[int(len(sizes) * 0.85)]
title_size_p50 = sizes[int(len(sizes) * 0.50)]

if title_size_p85 > title_size_p50:  # as expected
    title_size = title_size_p85
else:
    title_size = title_size_p85 + 1

# print(sizes)
print("title size: ", title_size)
del sizes

################################################################################

# RULE: Remove footer fext like page number and magazine name
# Get footer items and remove from all of the pages
footer_items_to_remove = get_repeating_footer_items(bottom_items)
# print("footer_items_to_remove", footer_items_to_remove)
num = 1
for page in pages:
    print(num)
    for text_box in page:
        if text_box[ord_y_pri] > bottom:
            for waste in footer_items_to_remove:
                yl_i = text_box[ord_y_pri]
                yh_i = text_box[ord_y_sec]
                text_i = clean_chars_for_bottom_item(text_box[ord_text][:25])
                yl_w = waste[0]
                yh_w = waste[1]
                text_w = waste[2]
                if yl_i == yl_w and yh_i == yh_w and text_i.startswith(text_w):
                    page.remove(text_box)
                    log_file.write("removed", text_box)
                    break
    num += 1

################################################################################

for page in pages:
    text_boxes = page
    # if there is too many smal boxes that maybe tabular data
    if len(text_boxes) > 3 and len(text_boxes) < 50:
        text_boxes.sort(key=operator.itemgetter(ord_x_pri, ord_y_pri))

        # TODO this process is slow if items is too much
        # TODO maintenance this after
        # Dividing Page in two part with seperator
        #seperator_line, space = get_seperator_line( list(map(lambda item: [item[ord_y_pri], item[ord_y_sec]], text_boxes)) )

        #print("seperator line: ", seperator_line, "space", space)

        space = 0
        if space > 20:
            above_the_seperator_items = list(
                filter(lambda text_box: text_box[ord_y_sec] < seperator_line, text_boxes))
            for item in above_the_seperator_items:
                text_boxes.remove(item)
            below_the_seperator_items = text_boxes
            del text_boxes

            # print(above_the_seperator_items)
            # print(below_the_seperator_items)

            process_article_block(above_the_seperator_items)
            process_article_block(below_the_seperator_items)

        else:
            process_article_block(text_boxes)

log_file.close()
# TODO chechk if last file is longer than 500 chars
output_text_file.close()
# # Plots
# # plt.plot(sizes)
# # plt.show()
