from pdfminer.layout import LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from .constants import ord_size, ord_y_pri, ord_y_sec, ord_text
from .footer_items import get_repeating_footer_items

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



def clean_chars_for_bottom_item(text):
    return "".join([char for char in text if not char.isdigit()])



# LAYOUT ANALYSIS
# Title size and footer items determined
def determine_title_size_and_footer_items(pages, height):
    sizes = []
    bottom_items = []
    bottom_line = height - 150  # height * 0.85

    for page in pages:
        for tb in page:
            size = tb[ord_size]
            sizes.append(size)
            if tb[ord_y_pri] > bottom_line:
                print(tb)
                text = clean_chars_for_bottom_item(tb[ord_text])
                text = text[:15] # First part of the text is enough and fast
                bottom_items.append((tb[ord_y_pri], tb[ord_y_sec], text))

    sizes.sort()
    title_size = sizes[int(len(sizes) * 0.85)]
    # print(sizes)
    print("title size: ", title_size)
    del sizes
    return title_size, bottom_items, bottom_line



def remove_footer(bottom_items, pages, bottom_line):
    # Removes footer
    # RULE: Remove footer fext like page number and magazine name
    # Get footer items and remove from all of the pages
    footer_items_to_remove = get_repeating_footer_items(bottom_items)
    #print("footer_items_to_remove", footer_items_to_remove)
    for page in pages:
        for text_box in page:
            if text_box[ord_y_pri] > bottom_line:
                for waste in footer_items_to_remove:
                    yl_i = text_box[ord_y_pri]
                    yh_i = text_box[ord_y_sec]
                    text_i = clean_chars_for_bottom_item(text_box[ord_text][:25])
                    yl_w = waste[0]
                    yh_w = waste[1]
                    text_w = waste[2]
                    if yl_i == yl_w and yh_i == yh_w and text_i.startswith(text_w):
                        page.remove(text_box)
                        # TODO Change as log
                        print("removed", text_box)
    return pages