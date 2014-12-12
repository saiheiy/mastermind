import mastermind
import random

def randomized_tests():
    """
    simulates many "human" inputs and checks whether ComputerPlayer can solve within 10 steps
    """
    num_tests = 1000
    colors = "rgoybp"
    colors_len = len(colors)
    for test_i in range(num_tests):
        human_input = ''.join([colors[random.randint(0,colors_len-1)] for i in range(4)]) 
        gc = mastermind.GuessChecker(human_input)
        comp = mastermind.ComputerPlayer()
        try_count = 0
        win_flag = False
        while (not win_flag) and (try_count < 10):
            guess = comp.smart_guess()
            feedback = gc.check_guess(guess)
            comp.process_feedback(feedback)
            if feedback == (0,4):
                win_flag = True
                break
            try_count += 1
        if win_flag:
            print 'Test %s: %s -- Passed'%(test_i, human_input)
        else:
            print 'Test %s: %s -- Failed!!!!'%(test_i, human_input)


if __name__ == '__main__':
    randomized_tests()
