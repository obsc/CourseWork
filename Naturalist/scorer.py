import os
import optparse

if __name__ == '__main__':
    parser = optparse.OptionParser()
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        print "ERROR!!!"

    sim = 100
    animals = 40
    trees = 70
    simmap = ''
    print_neg = False

    for i in range(1,len(args)):
        arg = args[i].strip()
        if arg.startswith('num='):
            (k,v) = arg.split('=')
            sim = int(v.strip())
        if arg.startswith('animals='):
            (k,v) = arg.split('=')
            animals = int(v.strip())
        if arg.startswith('trees='):
            (k,v) = arg.split('=')
            trees = int(v.strip())
        if arg.startswith('map='):
            (k,v) = arg.split('=')
            simmap = v.strip()
        if arg.startswith('verbose'):
            print_neg = True

    num = 0
    score = 0
    moves = 0
    time = 0
    negs = []
    negscore = []
    for i in range(sim):
        print 'Simulation ' + str(i)
        simscript = 'java -cp bin;classes Simulator '
        simscript += args[0]
        simscript += ' --headless'
        simscript += ' --seed='+str(i)
        simscript += ' --nanimals='+str(animals)
        simscript += ' --ntrees='+str(trees)
        if (simmap != ''):
            simscript += ' --map='+simmap

        os.system(simscript + ' > output.txt')

        f = open('output.txt', 'r')

        for line in f:
            line = line.strip()
            if line.startswith("Mission accomplished!"):
                num += 1
            if line.startswith('Score:'):
                (k,v) = line.split()
                v = v.strip()
                score += int(v)
                if int(v) < 0:
                    negs.append(num-1)
                    negscore.append(v)
            if line.startswith('Moves:'):
                (k,v) = line.split()
                v = v.strip()
                moves += int(v)
            if line.startswith('Time elapsed:'):
                (k1,k2,v,k3) = line.split()
                v = v.strip()
                time += int(v)

        f.close()

    print "Total Number of Simulations: " + str(num)
    print "Average Score: " + str(float(score)/num)
    print "Average Moves: " + str(float(moves)/num)
    print "Average Time: " + str(float(time)/num)
    print "Total Score: " + str(score)
    print "Total Moves: " + str(moves)
    print "Total Time: " + str(time)
    print "Negative Trials: " + str(len(negs))
    if print_neg:
        for i in range(len(negs)):
            print "Simulation " + str(negs[i]) + " - Score: " + str(negscore[i])
