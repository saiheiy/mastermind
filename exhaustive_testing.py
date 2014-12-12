import mastermind

def exhaustive_testing():
    """
    simulates all possible "human" inputs and checks whether ComputerPlayer can solve within 10 steps
    """
    colors = "rgoybp"
    input_list = ['%s%s%s%s'%(a,b,c,d) for a in colors for b in colors for c in colors for d in colors]
    
    test_result_dic = {"passed":0, "failed":0}

    for test_i, human_input in enumerate(input_list): 
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
            test_result_dic["passed"] += 1
        else:
            print 'Test %s: %s -- Failed!!!!'%(test_i, human_input)
            test_result_dic['failed'] += 1

    print "Num Tests Passed:  %s"%test_result_dic['passed']
    print 'Num Tests Failed:  %s'%test_result_dic['failed']

if __name__ == '__main__':
    exhaustive_testing()
