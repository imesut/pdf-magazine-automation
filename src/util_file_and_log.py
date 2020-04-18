import os, sys

pdf_file_name = ""
file_count = 1

if len(sys.argv) > 1:
    pdf_file_name = sys.argv[1]
else:
    pdf_file_name = "pozitif.pdf"

folder = "output/" + pdf_file_name[:-4] + "/"

def check_and_create_folders():
    if not os.path.isdir("output/"):
        os.mkdir("output/")
        check_and_create_folders()
    else:
        if not os.path.isdir(folder):
            os.mkdir(folder)

log_file = open(pdf_file_name + ".log", "w")

def create_file():
    global file_count
    otf = open(folder + pdf_file_name + "_" + str(file_count) + ".txt", "w")
    file_count += 1
    return otf

# LOGGING
def eliminate_log(pN, desc, *args):
    log_file.write("p: " + str(pN) + " ELIMINATED: " + desc + str(args) + "\n")

def finish_logging(): log_file.close()