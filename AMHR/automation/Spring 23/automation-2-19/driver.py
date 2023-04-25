import re
import pandas as pd
import converter


''' MAIN '''

if __name__ == "__main__":
  # open output file
  f_out = open("output.txt", "w")

  # read in csv
  df = pd.read_csv('AllPrintings.csv') # only has name/text columns

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
    #draw_match = converter.extract_draw(f_out, name, text)

  f_out.close()
