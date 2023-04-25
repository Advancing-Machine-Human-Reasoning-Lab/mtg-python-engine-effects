import re
import pandas as pd
import converter


def write_header(name):
  f_out.write("\n\n")
  f_out.write("#" * 30)
  f_out.write("\n")
  f_out.write(name)


''' MAIN '''

if __name__ == "__main__":
  # open output file
  f_out = open("output.txt", "w")

  # read in csv
  df = pd.read_csv('AllPrintings.csv')  # only has name/text columns

  # remove cards where name contains '//'
  df = df[df['name'].str.contains('//') == False]

  # for each row in the dataframe
  for index, row in df.iterrows():
    # grab info
    name = str(row['name'])
    text = str(row['text'])
    

    # extract create_token calls
    #tokens_match = converter.extract_token(f_out, name, text)

    converter.extract_targets(f_out, name, text)

    # extract draw calls
    #I made the matches function return a list to match when there was both draw and discard in one function, it would return both
    draw_match = converter.extract_draw(f_out, text)
    if draw_match is not None and draw_match:
      write_header(str(row['name']))
      f_out.write("\n\n")
      print(str(row['name']))
      for item in draw_match:
        f_out.write(item)

  f_out.close()
