import re
import pandas as pd
import converter

''' OUTPUT FILE WRITE HELPERS '''

# write 30 #'s and name of card
def write_header(name):
  f_out.write("#" * 30)
  f_out.write("\n")
  f_out.write(name)


''' MAIN '''

if __name__ == "__main__":
  f_out = open("output.txt", "w")

  df = pd.read_csv('AllPrintings.csv') # only has name/text columns
  for index, row in df.iterrows():
    tokens_match = converter.extract_tokens(f_out, str(row['text']))
    if tokens_match is not None:
      write_header(str(row['name']))
      f_out.write(tokens_match)

    draw_match = converter.extract_draw(f_out, str(row['text']))
    if draw_match is not None:
      write_header(str(row['name']))
      f_out.write(draw_match)

  f_out.close()
