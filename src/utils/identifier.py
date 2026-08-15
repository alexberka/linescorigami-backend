def num_to_alpha(number, home=True):
  if number <= 0:
    return '_'

  cycle = 0
  while number > 26:
    number -= 26
    cycle += 1

  offset = 64 if home else 96

  return f'{cycle if cycle > 0 else ''}{chr(number + offset)}'

def parse_identifier(row):
  away_box = row['away_box']
  home_box = row['home_box']
  away_score = row['away_score']
  home_score = row['home_score']
  away_hits = row['away_hits']
  home_hits = row['home_hits']
  away_errors = row['away_errors']
  home_errors = row['home_errors']

  nine_shape = ''
  home_no_bat = False
  nine_score = ''
  ex_shape = ''
  ex_score = ''

  innings = 0
  away_index = 0
  home_index = 0
  while True:
    add_shape = ''
    add_score = ''
    if away_index > len(away_box) - 1:
      break

    next_away = away_box[away_index]

    if next_away == '0':
      add_shape += '0'
    elif next_away in '123456789':
      add_shape += '1'
      add_score += num_to_alpha(int(next_away), False)
    elif next_away == '(':
      away_index += 1
      runs = ''
      while away_index < len(away_box) - 1 and away_box[away_index] != ')':
        if away_box[away_index] in '0123456789':
          runs += away_box[away_index]
        away_index += 1
      add_shape += '1'
      add_score += num_to_alpha(int(runs), False)
    
    away_index += 1

    if home_index > len(home_box) - 1:
      break

    next_home = home_box[home_index]

    if next_home == '0':
      add_shape += '0'
    elif next_home in '123456789':
      add_shape += '1'
      add_score += num_to_alpha(int(next_home))
    elif next_home == '(':
      home_index += 1
      runs = ''
      while home_index < len(home_box) - 1 and home_box[home_index] != ')':
        if home_box[home_index] in '0123456789':
          runs += home_box[home_index]
        home_index += 1
      add_shape += '1'
      add_score += num_to_alpha(int(runs))
    elif next_home.lower() == 'x':
      home_no_bat = True
      add_shape += '0'
    
    home_index += 1

    innings += 1

    if innings <= 9:
      nine_shape += add_shape
      nine_score += add_score
    else:
      ex_shape += add_shape
      ex_score += add_score

    if home_no_bat:
      break

  nine_shape = int(nine_shape, 2)

  if ex_shape:
    ex_shape = f'{innings - 9}.{int(ex_shape, 2)}'

  rhe = f'{num_to_alpha(away_score, False)}{num_to_alpha(home_score)}{num_to_alpha(away_hits, False)}{num_to_alpha(home_hits)}{num_to_alpha(away_errors, False)}{num_to_alpha(home_errors)}'

  return {
    "9_shape": nine_shape,
    "home_no_bat": home_no_bat,
    "9_score": nine_score,
    "ex_shape": ex_shape,
    "ex_score": ex_score,
    "rhe": rhe,
    "less_than_nine": innings < 9
  }
