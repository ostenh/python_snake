#!/usr/bin/env python2
import sys
import os
import tty
import select
import json
import termios
from copy import deepcopy as copy
from multiprocessing import Process
from time import sleep
from random import randint


class Snake:
   def __init__(self):
      self.height = 20
      self.width = 20
      self.length = 1
      self.sleep_time = 0.1
      self.path = []
      self.apples = []
      self.start_pos = [1,2]
      self.path.append(self.start_pos)

      # Char stuff
      self.border_char = '|'
      self.snake_char = '*'
      self.padd_char = ' '
      self.apple_char = '~'
      self.spider_char = '$'

      self.last_input = None
      self.dir = 'e'
      self.score = 0

      # Read the highsores.
      self.hs = self.Highscore()

      # some test data!
      self.add_new_apple()

      # Set some terminal stuff
      fd = sys.stdin.fileno()
      self.old_tty = termios.tcgetattr(fd)
      tty.setraw(sys.stdin.fileno())


   def __exit__(self):
      fd = sys.stdin.fileno()
      termios.tcsetattr(fd, termios.TCSADRAIN, self.old_tty)


   class Highscore():
      def __init__(self):
         self.file = "highscores.json"

         try:
            fh = open(self.file)
            self.data = json.loads(fh.read())
            self.highscores = self.data['Highscores']
            fh.close()
         except:
            print("File dosn't exist, or corrupt file!")
            self.data = {}
            self.data['Highscores'] = []
            self.highscores = self.data['Highscores']
         # finally:
            

      def add_score(self, nick, score):
         for entry in self.highscores:
            if entry['nick'] == nick:
               print("Nick exist override the score!")
               if score >= entry['score']:
                  entry['score'] = score
               return
         self.highscores.append({'nick': nick, 'score': score})


      def save(self):
         try:
            fh = open(self.file, 'w+')
            fh.write(json.dumps(self.data, sort_keys=True, indent=3, separators=(',', ': ')))
            fh.close()
         except:
            print("Failed to save highscores")


   def empty_array(self, array):
      for i in range(0,len(array)):
         array[i] = self.padd_char

   def read_input(self):
      while select.select([sys.stdin],[], [], 0) == ([sys.stdin], [], []):
         return sys.stdin.read(1)
      return None

   def draw(self):
      data_map = []
      row = []

      # Create the right length of a row
      for i in range(0,self.width+2):
         row.append(self.padd_char)

      row[0] = self.border_char
      row[self.width+1] = self.border_char

      # Create the right lenght of a colloum
      # and fill it with copy's of row
      for i in range(0,self.height+2):
         data_map.append(copy(row))

      # Create the top and bottom border lines
      for u in {0, self.height+1}:
         for i in range(0, self.width+2):
            data_map[u][i] = self.border_char

      for apple in self.apples:
         data_map[apple[1]+1][apple[0]+1] = self.apple_char

      for pos in self.path:
         data_map[pos[1]+1][pos[0]+1] = self.snake_char

      # Clear the screen
      print("\r\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

      # Print a nice header
      for u in range(0, self.width + 2):
         print(self.border_char),

      print("\r\n%c Snake%*c" % (self.border_char, self.width*2-(17), ' ')),
      print("Score: %3d %c" % (self.score, self.border_char)),


      # Print the map
      print('\r')
      for i in range(0,self.height+2):
         for u in range(0,self.width+2):
            row = data_map[i]
            print(row[u]) ,
         print('\r')

   def got_apple(self, pos):
      for apple in self.apples:
         if pos == apple:
            return True
      return False

   def add_new_apple(self):
      x = randint(0,self.width-1)
      y = randint(0,self.height-1)

      pos = [x,y]
      if not self.got_apple(pos):
         self.apples.append(pos)

   def self_hit(self, pos):
      for loc in self.path:
         if loc == pos:
            return True
      return False

#  n
# e w
#  s

#  w 
# a d
#  s
   def logic(self):

      self.last_input = self.read_input()


      if self.last_input is not None:
         if self.last_input == 'a' and not self.dir == 'e':
            print "Setting dir: w"
            self.dir = 'w'
         elif self.last_input == 'w' and not self.dir == 's':
            print "Setting dir: n"
            self.dir = 'n'
         elif self.last_input == 'd' and not self.dir == 'w':
            print "Setting dir: e"
            self.dir = 'e'
         elif self.last_input == 's' and not self.dir == 'n':
            print "Setting dir: s"
            self.dir = 's'
         elif self.last_input == 'q': #quits the game
            self.__exit__()
            exit()
         self.last_input = None

      last_pos = self.path[-1]
      new_pos = copy(last_pos)


      if self.dir is 'e':
         new_pos[0] += 1
      if self.dir is 'w':
         new_pos[0] -= 1
      if self.dir is 'n':
         new_pos[1] -= 1
      if self.dir is 's':
         new_pos[1] += 1

      if new_pos[0] >= self.width:
         new_pos[0] = 0
      if new_pos[0] < 0:
         new_pos[0] = self.width-1

      if new_pos[1] >= self.height:
         new_pos[1] = 0
      if new_pos[1] < 0:
         new_pos[1] = self.height-1

      if self.self_hit(new_pos):
         return False



      self.path.append(new_pos)
#      if not self.extend:
      if not self.got_apple(new_pos):
         self.path.pop(0)
      else:
         self.apples.pop(self.apples.index(new_pos))
         self.add_new_apple()
         self.score += 1

      return True

   def run(self):
      while 1:
         if not self.logic():
            self.__exit__()
            nick = raw_input("Nickname: ")
            self.hs.add_score(nick, self.score)
            self.hs.save()
            print("Dead!")
            break;
         self.draw()
         sleep(self.sleep_time)

   def start(self):
#      hs = Highscore()
      self.run()
      #p = Process(target=self.run)
      #p.start()

      #while 1:
      #   sleep(1)
      #   self.last_input = raw_input()
      #   print self.path
      #   sleep(4)

      #p.join()


#a = Snake.Highscore()
#a.add_score("0st3n", randint(0,1000))
#a.save()
if __name__ == '__main__':
#   pass
   a = Snake()
   a.start()
   a.__exit__()