# PDF MINER IMPORT
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from .constants import ord_x_pri, ord_y_pri, ord_size, ord_text, col_count
import operator
from .util_file_and_log import eliminate_log, create_file
from .layout_utils import get_text_size_of_line

first_time = True
col_width_divider = 0
width = 0
height = 0
threshold_rate = 0.1

def fetch_pages(pdf_file_name, start, *args):
    global col_width_divider, height
    if start < 0: start = 0
    stop = 0
    if len(args) > 0: stop = args[0]
    pages = []
    resourcemanager = PDFResourceManager()
    laparams = LAParams(detect_vertical=True, all_texts=True)
    device = PDFPageAggregator(resourcemanager, laparams=laparams)
    fp = open(pdf_file_name, 'rb')
    interpreter = PDFPageInterpreter(resourcemanager, device)
    caching = True
    pagenos = set()

    for pN, page in enumerate(PDFPage.get_pages(fp, pagenos, caching=caching, check_extractable=True)):
        # Cover and index pages ignored.
        if stop > 0: compare = (pN >= start and pN <= stop)
        else: compare = (pN >= start)
        
        if compare:
            interpreter.process_page(page)
            layout = device.get_result()
            width = round(page.mediabox[2])
            height = round(page.mediabox[3])
            col_width_divider = width / col_count
            print(pN, "FETCHING PAGE: ", "width", width, "height", height)
            text_boxes = process_layout(layout, pN)
            pages.append(text_boxes)

    fp.close()
    device.close()
    return pages, height

def generate_articles(pages, title_size, output_text_file):
    # generates outputs here
    for page in pages:
        text_boxes = page
        # if there is too many smal boxes that maybe tabular data
        if len(text_boxes) > 3 and len(text_boxes) < 20:
            text_boxes.sort(key=operator.itemgetter(ord_x_pri, ord_y_pri))

            # TODO this process is slow if items is too much
            # TODO maintenance this after
            # Dividing Page in two part with seperator
            #seperator_line, space = get_seperator_line( list(map(lambda item: [item[ord_y_pri], item[ord_y_sec]], text_boxes)) )
            #print("seperator line: ", seperator_line, "space", space)
            # space = 0
            # if space > 20:
            #     above_the_seperator_items = list(
            #         filter(lambda text_box: text_box[ord_y_sec] < seperator_line, text_boxes))
            #     for item in above_the_seperator_items:
            #         text_boxes.remove(item)
            #     below_the_seperator_items = text_boxes
            #     del text_boxes
            #     # print(above_the_seperator_items)
            #     # print(below_the_seperator_items)
            #     process_article_block(above_the_seperator_items, title_size)
            #     process_article_block(below_the_seperator_items, title_size)

            # else:
            #     process_article_block(text_boxes, title_size)
            process_article_block(text_boxes, title_size, output_text_file)


def process_article_block(block, title_size, output_text_file):
    block.sort(key=operator.itemgetter(ord_x_pri, ord_y_pri))
    titles, output_text_file = calculate_titles_and_insert(block, title_size, output_text_file)
    for item in titles:
        block.remove(item)
    generate_content(block, output_text_file)

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

                if (yP < height * (1 - threshold_rate)):
                    # RULE: Eliminate single word text which is close to the threshold
                    if((yP < height * (threshold_rate * 2) or yP > height * (1 - threshold_rate*2)) and len(text.split(" ")) < 2):
                        eliminate_log(pN, "Not in threshold but single word", text)
                    elif(len(text) < 2):
                        eliminate_log(pN, "Text Length is too small", text)
                    else:
                        for line in text_box:
                            # Be sure line is an exact line =)
                            if isinstance(line, LTTextLineHorizontal):
                                size = get_text_size_of_line(line)
                                text_boxes.append((xP, yP, xS, yS, size, text))
                                #print((xP, yP, xS, yS, size, text[:50]))
                                break  # analysis of first line is enough
                else:
                    eliminate_log(pN, "Header / Footer text:", xP, yP, text)
    return text_boxes

def generate_content(text_boxes, output_text_file):
    content = ""
    for i in text_boxes:
        #print( i[ord_x_pri], i[ord_y_pri], i[ord_x_sec], i[ord_y_sec], i[ord_size], i[ord_text][:20] )
        #size = i[ord_size]
        text = i[ord_text]
        add_new_line = True
        # print(text)

        # RULE: Remove smallest text - generally image descriptions
        # Smallest size, I'm sceptical about this.
        # If there is no footer text smallest size will be main text's size
        # If three or more text box has the same smallest size then ignore it.
        #smallest_size = min(text_boxes, key=operator.itemgetter(ord_size))[ord_size]
        # if len(list(filter(lambda x: x[ord_size] == smallest_size, text_boxes))) < 3:
        #    smallest_size = smallest_size
        # else:
        #    smallest_size = 0
        # if size != smallest_size:
        # else:
        #     eliminate_log(pN, "Smallest text in the page", text)
        # RULE: Merge two lines if second one is beginning with lowercase
        if text[0] == text[0].lower():  # sentence begins with lower letter
            # print("found lowercase beginning")
            # print("content" + content)
            # Remove new line chars (\n) from previous line
            content = content[:-2] + " "
        elif text[-1] not in [".", "!", "?"]:
            add_new_line = False
        # Add space after punctuation mark, begin new sentence
        content += text + " "
        if add_new_line:
            content += "\n"

    output_text_file.write(content)

def calculate_titles_and_insert(text_boxes, title_size, output_text_file):
    # Title Calculation
    # When new title calculated seperate files
    global first_time
    titles = list(filter(lambda x: x[ord_size] >= title_size, text_boxes))

    if len(titles) > 0:
        merged_title = " ".join(
            list(map(lambda x: x[ord_text], titles))).capitalize()
        if not first_time:
            output_text_file.close()
            output_text_file = create_file()
        output_text_file.write("# " + merged_title + "\n")
        first_time = False

    return titles, output_text_file

    # #print("text_boxes", text_boxes)
    # biggest_item = max(text_boxes, key=operator.itemgetter(ord_size))
    # #print("biggest_item", biggest_item)
    # biggest_item_size = biggest_item[4]
    # biggest_items = []
    # if prev_biggest_item_size == 0:
    #     prev_biggest_item_size = biggest_item_size
    #     first_time = True

    # if biggest_item_size >= prev_biggest_item_size:
    # There is a threshold
    #print("Title calculation: ", prev_biggest_item_size, biggest_item_size)
    # Normalize too big titles
    # if biggest_item_size > prev_biggest_item_size:
    #     biggest_item_size = prev_biggest_item_size
    # if abs(biggest_item_size - prev_biggest_item_size) <= 2:
    #     biggest_items = list(filter(lambda x: x[ord_size] >= biggest_item_size, text_boxes))
    #     biggest_items_text = map(lambda x: x[ord_text], biggest_items)
    #     # print("biggest_items", biggest_items)
    #     title = " ".join(biggest_items_text)
    #     title = title.capitalize()
    #     #print("title", title)
    #     if not first_time:
    #         #print("closing file", biggest_item_size, prev_biggest_item_size)
    #         output_text_file.close()
    #         output_text_file = create_file()
    #     output_text_file.write("# " + title + "\n")
    #     prev_biggest_item_size = biggest_item_size
    #     first_time = False
    # return biggest_items
