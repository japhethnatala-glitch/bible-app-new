import glob
import os

# Folder where your WEB book files are stored
folder = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(folder, "verses_web.txt")

# Collect only book files that start with a number (e.g. "1 Genesis.txt")
book_files = [f for f in glob.glob(os.path.join(folder, "*.txt"))
              if os.path.basename(f)[0].isdigit()]

# Sort them numerically by the leading number
book_files.sort(key=lambda f: int(os.path.basename(f).split()[0]))

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in book_files:
        # Just write the book title line and contents
        with open(filename, "r", encoding="utf-8") as infile:
            outfile.write(infile.read() + "\n")

print("Merged Bible saved as verses_web.txt")
