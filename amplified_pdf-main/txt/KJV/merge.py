import glob
import os

folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(folder, "kjv_full.txt")

book_files = [f for f in glob.glob(os.path.join(folder, "*.txt")) 
              if os.path.basename(f)[0].isdigit()]

book_files.sort(key=lambda f: int(os.path.basename(f).split()[0]))

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in book_files:
        book_name = os.path.basename(filename).split(" - ")[0]  # e.g. "1 Genesis"
        outfile.write("\n=== " + book_name + " ===\n\n")  # divider line
        with open(filename, "r", encoding="utf-8") as infile:
            outfile.write(infile.read() + "\n")



