#!/usr/bin/python
import random
import inflect
import quote_puzzle
import dict_puzzle

p = inflect.engine()
primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
fuzz_amount = 3

def make_puzzle(obfuscate=True):
  answer = 0
  bonus = 0
  puzzle = random.choice(["Prove you're not a robot: ", "Are you a robot?: ", "Anti-bot check: ", "Counter-cndorphant measures: ", "Cosnok countermeasures: ", "Anti-tildethief precautions: "])
  puzzle += random.choice(["What is", "How many is", "What do you get from", "What do you get with", "What is the value of", "Can you answer", "Can you tell me"])
  puzzle += " "
  roll = random.randrange(0,18)
  var1 = random.randrange(1,10)
  var2 = random.randrange(1,10)
  var3 = random.randrange(1,20)
  var4 = random.randrange(1,20)
  let1_ord = random.randrange(ord('a'), ord('z')+1)

  if roll == 0:
      answer = var1 + var2
      puzzle += p.number_to_words(var1) + " " + random.choice(["and", "plus", "sum", "add"]) + " " + p.number_to_words(var2)

  elif roll == 1:
      answer = var1 * var2
      puzzle += p.number_to_words(var1) + " " + random.choice(["times", "multiply", "multiplied by", "product"]) + " " + p.number_to_words(var2)
  elif roll == 2:
      if var2 > var1:
          var1,var2 = var2,var1
      answer = var1 - var2
      puzzle += p.number_to_words(var1) + " " + random.choice(["minus", "subtract", "take away", "less"]) + " " + p.number_to_words(var2)
  elif roll == 3:
      if var2 > var1:
          var1,var2 = var2,var1
      answer = var1 * 2 / var2
      puzzle += p.number_to_words(var1*2) + " " + random.choice(["divided by", "over"]) + " " + p.number_to_words(var2) + " (no remainder)"
  elif roll == 4:
      answer = var1 ** var2
      puzzle += p.number_to_words(var1) + " to the " + p.ordinal(p.number_to_words(var2)) + " power"
  elif roll == 5:
      p1 = random.choice(primes)
      p2 = random.choice(primes)
      def answer(guess):
          # Check the the numbers entered are correct, regardless of order
          # or surrounding whitespace.
          attempt = sorted(word.strip() for word in guess.split(","))
          correct = sorted([str(p1), str(p2)])
          return attempt == correct
      bonus = 1
      puzzle += p.number_to_words(p1 * p2) + " when factored into its two primes (answer in the form of the two primes with a comma between)"
  elif roll == 6:
      prime = random.choice(primes)
      answer = prime % var1
      puzzle += p.number_to_words(prime) + " modulus " + p.number_to_words(var1)
  elif roll == 7:
      if let1_ord + var1 > ord('z'):
          let1_ord -= var1
      answer = chr(let1_ord + var1)
      puzzle = "What letter comes " + p.number_to_words(var1) + " letters after '" + chr(let1_ord) + "'"
      obfuscate = False
  elif roll == 8:
      if let1_ord - var1 < ord('a'):
          let1_ord += var1
      answer = chr(let1_ord - var1)
      puzzle = "What letter comes " + p.number_to_words(var1) + " letters before '" + chr(let1_ord) + "'"
      obfuscate = False
  elif roll == 9:
      answer, puzzle = quote_puzzle.get_quote()
      obfuscate = False
  elif roll == 10:
      answer = str(min(var1, var2, var3, var4))
      puzzle = "What is the " + random.choice(["smallest", "lowest"]) + " of " + p.number_to_words(var1) + ", " + p.number_to_words(var2) + ", " + p.number_to_words(var3) + ", and " + p.number_to_words(var4)
  elif roll == 11:
      answer = str(max(var1, var2, var3, var4))
      puzzle = "What is the " + random.choice(["biggest", "largest"]) + " of " + p.number_to_words(var1) + ", " + p.number_to_words(var2) + ", " + p.number_to_words(var3) + ", and " + p.number_to_words(var4)
  elif roll <= 14: #12-14
      answer, puzzle = dict_puzzle.get_puzzle()
      obfuscate = False
  elif roll <= 17: #15-17
      answer, puzzle = dict_puzzle.get_anagram()
      obfuscate = False

  puzzle += "?"
  if obfuscate == True:
      for _ in range(fuzz_amount):
          idx = random.randrange(len(puzzle)-1) #get between 0 and string length
          puzzle = ''.join([puzzle[0:idx], chr(random.randint(33,126)), puzzle[idx+1:]])
  return [puzzle, answer, bonus]
