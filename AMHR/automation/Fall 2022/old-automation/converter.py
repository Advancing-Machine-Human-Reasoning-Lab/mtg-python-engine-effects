import re
import json

''' HELPERS '''

# dict to convert spelled out numbers to ints
num_dict = {
  'one': '1',
  'two': '2',
  'three': '3',
  'four': '4',
  'five': '5',
  'six': '6',
  'seven': '7',
  'eight': '8',
  'nine': '9',
  'ten': '10'
}

''' TRIGGERS '''

def extract_triggers(output_file, card_name, card):
  # import phrases dict from trigger_phrases.json
  # json structure:
  #   phrase to look for : trigger to write if found
  with open('trigger_phrases.json') as j:
    trigger_phrases = json.load(j)

  # make regex string with phrases to look for
  regex = '('
  for p in trigger_phrases:
    regex = regex + p + '|'
  regex = regex[:-1] + ')'  # replace last | with )

  # fill in {0} with card name for phrases that specifically mention the card
  regex = regex.format(card_name)

  # extract and map trigger phrases to triggers
  found_phrases = re.findall(re.compile(regex), card)
  if found_phrases:  # if a phrase was found (list is not empty)
    # write the Triggers tag to output file
    output_file.write('\n\t\tTriggers:\n')

    # for each found phrase
    for p in found_phrases:
      # if {0} was filled in with the card name, replace it to index the phrases dict
      if card_name in p:
        p = p.replace(card_name, '{0}')

      # write corresponding trigger to output file
      try:
        output_file.write('\t\t\t\t' + trigger_phrases[p] + '\n')
      except:
        pass


''' TARGETS '''

def extract_targets(output_file, card_name, card):
  # card name is not currently used in this function but I'm keeping it passed any way just in case

  # import phrases dict from target_phrases.json
  # json structure:
  #   phrase to look for : target specification to write
  with open('target_phrases.json') as j:
    target_phrases = json.load(j)

  # make regex string with phrases to look for
  regex = '('
  for p in target_phrases:
    regex = regex + p + '|'
  regex = regex[:-1] + ')'

  # extract and map target phrases to targets
  found_phrases = re.findall(re.compile(regex), card)
  if found_phrases:  # if a phrase was found (list is not empty)
    # write the Targets tag to output file
    output_file.write('\n\t\tTargets:\n')

    # for each found phrase
    for p in found_phrases:
      # write the corresponding target to the output file
      output_file.write('\t\t\t\t' + target_phrases[p] + '\n')


''' FUNCTIONS '''

# convert any phrase that requires the use of the create_token function
def extract_tokens(output_file, card_text):
  regex = '^Create (.*?) (\d\/\d [A-Za-z]+ [A-Za-z]+) creature tokens with ([A-Za-z]+)'
  matches = re.search(re.compile(regex), card_text)
  if matches is not None:
    try:
      return ('\n\n\t\tself.controller.create_token(\'' + matches.group(2) +
              '\', ' + num_dict[matches.group(1)] + ', \'' + matches.group(3) +
              '\')\n\n')
    except:
      pass
  else:
    return None

#Extract any cards where the text is draw ____ card(s). If it is "draw a card" fills a with "one"
def extract_draw(output_file, card_text):
  regex = '^Draw (.*?) cards? \.'  #Add $ to the end for cards that are only draw ___ cards.
  matches = re.search(re.compile(regex), card_text)
  if matches is not None:
    if matches.group(1) in num_dict:
      return ('\n\n\t\tself.controller.draw(' + num_dict[matches.group(1)] +
              ')\n\n')
    elif matches.group(1) == 'a':
      return ('\n\n\t\tself.controller.draw(' + num_dict['one'] + ')\n\n')

  else:
    return None
