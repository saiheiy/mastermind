import re

class GuessChecker(object):
    def __init__(self, pattern_in):
        self.pattern = pattern_in

    def check_guess(self, guess):
        """
        returns (x, y) if nothing matched
        where 
        x denotes number of pegs that have right color but wrong position
        y denotes number of pegs that have right color and position
        """
        x = 0
        y = 0

        #search for pegs with right color and position
        remaining_guesses = []
        remaining_patterns = []
        for (ii,pi) in enumerate(self.pattern):
            if pi == guess[ii]:
                y += 1
            else:
                remaining_patterns.append(pi)
                remaining_guesses.append(guess[ii])

        #search for remaining pegs with right color but wrong position
        for pi in remaining_patterns:
            if pi in remaining_guesses:
                x += 1
                remaining_guesses.remove(pi)
        return (x, y)

class ComputerPlayer(object):
    """
    does a brute-force strategy with pruning to break code within 10 steps
    """
    def __init__(self):
        self.unsolved_pegs = []
        self.solved_pegs = []
        self.solved_positions = set()
        self.colors = "rgoybp"
        self.unused_colors = list(self.colors)
        self.color_ind = -1
        self.total_positions_solved = 0
        self.colors_left_to_find = 4
        self.cur_unsolved_peg = None
        self.max_unsolved_pos = 3
        return

    def print_status(self):
        print 'unsolved pegs: %s'%self.unsolved_pegs
        print 'solved_pegs: %s'%self.solved_pegs
        print 'solved_positions: %s'%self.solved_positions
        #print 'cur_color: %s'%self.colors[self.color_ind]
        print 'total_positions_solved: %s'%self.total_positions_solved
        print 'cur_unsolved_peg: %s'%self.cur_unsolved_peg

    def smart_guess(self):
        self.color_ind += 1
       
        if self.colors_left_to_find == 0:
            cur_color = self.unused_colors[0]
        else:
            cur_color = self.colors[self.color_ind]

        guess = [cur_color]*4

        for sp in self.solved_pegs:
            position = sp['position']
            color = sp['color']
            guess[position] = color

        if self.cur_unsolved_peg != None:
            guess[self.cur_unsolved_peg['position']] = self.cur_unsolved_peg['color'] 

        return ''.join(guess)

    def process_feedback(self, fb):
        num_right_color_only, num_right_both = fb
        total_right = num_right_color_only + num_right_both
        if self.cur_unsolved_peg:
            num_new_color_gains = total_right - self.total_positions_solved - 1
        else:
            num_new_color_gains = total_right - self.total_positions_solved
    
        for i in range(num_new_color_gains):
            self.push_new_peg_candidate()
        
        self.short_circuit_last_color()

        if (num_right_both - self.total_positions_solved) == (num_new_color_gains + 1):
            #satisfies condition that current peg is solved (right color and position)
            self.add_solved_peg()
        elif self.cur_unsolved_peg != None:
            #current peg still not at right position.  tell future candidates of same color to ignore this position and increment current peg's position
            for p in self.unsolved_pegs:
                if p['color'] == self.cur_unsolved_peg['color']:
                    p['exclude'].add(self.cur_unsolved_peg['position'])
            self.cur_unsolved_peg['position'] += 1

        while self.rotate_cur_unsolved_peg() and (self.churn_through_solved_positions() or self.short_circuit_last_position()):
            pass
        return

    def push_new_peg_candidate(self):
        self.unsolved_pegs.append({'color': self.colors[self.color_ind], 'position':0, 'count':0, 'exclude': set()})
        self.colors_left_to_find -= 1
        if self.colors[self.color_ind] in self.unused_colors:
            self.unused_colors.remove(self.colors[self.color_ind])

    def rotate_cur_unsolved_peg(self):
        #ensure next peg to choose is one of most colors within unsolved_pegs (guarentees lower steps required to find position, also necessary to guarantee it solves within 10 steps)
        if self.cur_unsolved_peg != None:
            self.unsolved_pegs.append(self.cur_unsolved_peg)
        if len(self.unsolved_pegs) > 0:
            colors_count_dic = {}
            for p in self.unsolved_pegs:
                colors_count_dic[p['color']] =  colors_count_dic.get(p['color'], 0)
                colors_count_dic[p['color']] += 1
            for p in self.unsolved_pegs:
                p['count'] = colors_count_dic[p['color']]
            self.unsolved_pegs.sort(key = lambda d:d['count']+len(d['exclude'])/10.0)
            self.cur_unsolved_peg = self.unsolved_pegs.pop()

        return self.cur_unsolved_peg != None

    def churn_through_solved_positions(self):
        #skip checking position if it is already solved or has prevoiusly been excluded by a peg of same color
        flag = False
        while (self.cur_unsolved_peg['position'] in self.solved_positions) or (self.cur_unsolved_peg['position'] in self.cur_unsolved_peg['exclude']):
            self.cur_unsolved_peg['position'] += 1
            flag = True
        return flag

    def short_circuit_last_position(self):
        #if only one position left to check, it must be (one of) the right position(s) for current peg
        flag = False
        if self.cur_unsolved_peg['position'] == self.max_unsolved_pos:
            self.add_solved_peg()                
            flag = True
        return flag

    def short_circuit_last_color(self):
        #if one color left, remaining colors must be of last color (purple)
        if self.color_ind == len(self.colors) - 2:
            self.color_ind += 1
            tmp_colors_left_to_find = self.colors_left_to_find
            for i in range(tmp_colors_left_to_find):
                self.push_new_peg_candidate()
        return

    def add_solved_peg(self):
        self.solved_positions.add(self.cur_unsolved_peg['position'])
        self.total_positions_solved += 1
        self.max_unsolved_pos = max(pi for pi in range(4) if pi not in self.solved_positions) if self.total_positions_solved < 4 else -1 
        self.solved_pegs.append(self.cur_unsolved_peg)
        self.cur_unsolved_peg = None
    

def main():
    while True:
        human_input = raw_input("enter a pattern of 4 (repeatable) colors out of (r,g,o,y,b,p).  (ie. if (r,p,y,r), then enter \"rpyr\"): ").strip().replace(" ", "").replace(",", "")
        if not re.match('^[rgoybp]{4}$', human_input):
            print 'invalid input, please try again'
        else:
            break

    gc = GuessChecker(human_input)
    comp = ComputerPlayer()

    try_count = 0
    win_flag = False
    while (not win_flag) and (try_count < 10):
        guess = comp.smart_guess()
        print 'Computer Guess %s:  %s'%(try_count+1, guess)
        feedback = gc.check_guess(guess)
        print 'Human feedback: %s right color only, %s right both color and position'%feedback
        comp.process_feedback(feedback)
        if feedback == (0,4):
            print 'Computer won:  correct guess=%s'%guess
            win_flag = True
            break

        try_count += 1
        #comp.print_status()   #uncomment this line for debugging

    if win_flag == False:
        print 'You beat the computer!'
        
if __name__ == '__main__':
    main()
