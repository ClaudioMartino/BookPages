from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys
import os
os.system("color")
os.environ['MOZ_HEADLESS'] = '1'  # Firefox without UI

COLOR = {
    "WARN": "\033[93m", # yellow
    "GREEN": "\033[92m",
    "ERR": "\033[91m", # red
    "ENDC": "\033[0m",
}

print("Welcome!")

# Input file can be given as parameter
if(len(sys.argv) == 2):
   titles_file = str(sys.argv[1])
else:
   titles_file = "titles.txt"  # default file

print("Input file: " + titles_file)

output_file = "output.txt"
url = "https://www.readinglength.com/"

# Open driver
print("Opening browser...")
driver = webdriver.Firefox()

results = []
line_count = 0
err_count = 0

start_time = time.time()

try: 
   with open(titles_file, encoding="utf8") as f:
      all_lines = f.readlines()
      tot_books = len(all_lines)
      print(COLOR["WARN"], str(tot_books) + " books in total", COLOR["ENDC"])
      for line in all_lines:
         title = line.strip()  # remove \n

         # Open main page
         driver.get(url)

         # Search book
         inputElement = driver.find_element_by_id("downshift-0-input")
         inputElement.send_keys(title)
         inputElement.send_keys(Keys.ENTER)
         print(str(line_count) +") " + title)

         # Wait for the page to load
         time.sleep(1)
         for n in range(10):
            try:
               book_data = driver.find_element_by_class_name("book-data")
               break
            except:
               # If page not yet loaded
               time.sleep(3)

         try:
            words_str = book_data.find_element_by_xpath("//*[contains(text(),'Word Count')]/following-sibling::p").text;
            words = int(((words_str.split(" "))[0]).replace('.','') )
            print("Words: " + str(words))
         except:
            print(COLOR["ERR"], "Word count not found", COLOR["ENDC"])
            words = "ERR"

         try:
            pages_str = book_data.find_element_by_xpath("//*[contains(text(),'Pages')]/following-sibling::p").text;
            pages = int(((pages_str.split(" "))[0]).replace('.','') )
            print("Pages: " + str(pages))
         except:
            print(COLOR["ERR"], "Pages not found", COLOR["ENDC"])
            pages = "ERR"

         res = [str(line_count), title, str(words), str(pages)]
         results.append(res)

         if(words == "ERR" or pages == "ERR"):
            err_count += 1

         line_count += 1

         # Report once every ten
         if line_count%10 == 0:
            avg = 60*line_count/(time.time() - start_time) # avg speed [books/min]
            rem = tot_books - line_count # remaining books
            rem_time = rem/avg # remaining time [min]
            print(COLOR["WARN"], "AVG: "+ str(round(avg, 2)) + " books/min ; " + str(round(60/avg, 2)) + " s/book", COLOR["ENDC"])
            # Progress bar (size 20)
            print(COLOR["WARN"], " [", COLOR["ENDC"], end='', sep='')
            for i in range(20):
               if i < round(20*line_count/tot_books):
                  print(COLOR["WARN"], "#", COLOR["ENDC"], end='', sep='')
               else:
                  print(COLOR["WARN"], ".", COLOR["ENDC"], end='', sep='')
            print(COLOR["WARN"], "] " + str(round(100*line_count/tot_books, 2))  + "% ("+ str(line_count) + "/" + str(tot_books) + ")", COLOR["ENDC"], sep='')
            print(COLOR["WARN"], "Extimated remaining time: " + str(round(rem_time, 2)) + " min", COLOR["ENDC"])
            if err_count>0: 
               print(COLOR["WARN"], str(err_count) + " errors (" + str(round(100*err_count/line_count, 2)) + "%)", COLOR["ENDC"])

except: 
   print(COLOR["ERR"], "Error opening input file", COLOR["ENDC"])

print(COLOR["GREEN"], "\n Processed " + str(line_count) + " books in " + str((time.time() - start_time)) + " s", COLOR["ENDC"])
if err_count>0: 
   print(COLOR["GREEN"], "Error: " + str(err_count) , COLOR["ENDC"])

with open(output_file, mode='w', encoding="utf8", newline='') as res_file:
   sep = '\t'
   for res in results:
      res_line = sep.join(res)
      res_file.write(res_line + '\n')      

# Close driver
driver.close()