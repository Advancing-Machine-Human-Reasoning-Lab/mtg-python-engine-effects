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


# write 30 #'s and name of card
def write_header(output_file, name):
  output_file.write("\n\n")
  output_file.write("#" * 30)
  output_file.write("\n")
  output_file.write(name)


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


def extract_targets(output_file, card_name, card_text):
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
  found_phrases = re.findall(re.compile(regex), card_text)
  if found_phrases:  # if a phrase was found (list is not empty)

    # for each found phrase
    for p in found_phrases:
      # find if take_damage should be called on target
      damage_match = extract_damage(output_file, p, card_name, card_text)
      if damage_match is not None:
        # write header
        write_header(output_file, card_name)

        # write the Targets tag to output file
        output_file.write('\n\t\tTargets:\n')

        # write the corresponding target to the output file
        output_file.write('\t\t\t\t' + target_phrases[p] + '\n')

        output_file.write(damage_match)


''' FUNCTIONS '''


# convert any phrase that requires the use of the create_token function
def extract_token(output_file, card_name, card_text):
  regex = '^Create (.*?) (\d\/\d [A-Za-z]+ [A-Za-z]+) creature tokens with ([A-Za-z]+).$'
  matches = re.search(re.compile(regex), card_text)
  if matches is not None:
    write_header(output_file, card_name)
    try:
      output_file.write('\n\n\t\tself.controller.create_token(\'' +
                        matches.group(2) + '\', ' +
                        num_dict[matches.group(1)] + ', \'' +
                        matches.group(3) + '\')\n\n')
    except:
      pass
  else:
    return None


#Extract any cards where the text is draw ____ card(s) and cards with draw and discard. If it is "draw a card" fills a with "one"
def extract_draw(output_file, card_name, card_text):
  output = []
  regex = '^Draw (.*?) cards?(, then discard (.*?) cards?)?\.$'
  matches = re.search(re.compile(regex), str(card_text))
  if matches is not None:
    print(matches)
    if matches.group(1) in num_dict:
      output.append('\t\tself.controller.draw(' + num_dict[matches.group(1)] +
                    ')\n\n')
    elif matches.group(1) == 'a':
      output.append('\t\tself.controller.draw(' + num_dict['one'] + ')\n\n')
    elif matches.group(1) == 'x':
      output.append('')  #Do nothing (for now) if card says "Draw X cards"
    if matches.group(2) is not None:
      if matches.group(3) in num_dict:
        output.append('\t\tself.controller.discard(' +
                      num_dict[matches.group(1)] + ')\n\n')
      elif matches.group(3) == 'a':
        output.append('\t\tself.controller.discard(' + num_dict['one'] +
                      ')\n\n')  #self.controller.draw(
    return output
  else:
    return None


def extract_damage(output_file, target_match, card_name, card_text):
  regex = '^{0} deals (\d*) damage ' + target_match + '.$'
  regex = regex.format(card_name)

  matches = None
  try:
    matches = re.search(re.compile(regex), card_text)
  except:
    pass  # +2 Mace is the only card that triggers this except
    # regex hates the + at the start of the string
  if matches is not None:
    return '\n\t\ttargets[0].take_damage(self, ' + str(matches[1]) + ')\n\n'
  else:
    return None

def extract_gain_life(outputfile, card_text):
  regex = 'You gain (\d) life.$'
  matches = re.search(re.compile(regex), card_text)

  if matches is not None:
    outputfile.write('\n\n\t\tself.controller.gain_life(' + matches.group(1) + ')\n\n')
  else:
    return None
