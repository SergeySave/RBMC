import glob
import numpy as np
import matplotlib.pyplot as plt

def parse_file(path):
    with open(path) as f:
        lines = f.read().splitlines()
    return lines


def create_knowledge_data(entries):
    means = []
    sdevs = []
    number = []
    now = 2
    while True:
        current = [float(entry[now]) for entry in entries if len(entry) > now]
        now += 1
        if len(current) == 0:
            return np.array(means), np.array(sdevs), np.array(number)
        else:
            means.append(np.mean(current))
            sdevs.append(np.std(current))
            number.append(len(current))

if __name__ == "__main__":
    parsed = [parse_file(path) for path in glob.glob("results/*.txt")]
    err_count = sum(1 for i in parsed if len(i) == 0)
    not_erred = [i for i in parsed if len(i) != 0]
    win_count = sum(1 for i in not_erred if i[1] == "True")
    loss_count = sum(1 for i in not_erred if i[1] == "False")

    print(err_count)
    print(win_count)
    print(loss_count)

    bar_width = 0.5

    loss_plot = plt.bar([0], loss_count, bar_width)
    win_plot = plt.bar([0], win_count, bar_width, bottom=loss_count)
    err_plot = plt.bar([0], err_count, bar_width, bottom=(loss_count+win_count))

    plt.ylabel("Number of Games")
    plt.title("Games by Outcome and Opponent")
    plt.xticks([0], ['Oracle'])
    plt.yticks(np.arange(0, len(parsed), 50))
    plt.legend([loss_plot[0], win_plot[0], err_plot[0]], ['Losses', 'Wins', 'Errors'])

    plt.show()

    knowmean, knowsdev, knownums = create_knowledge_data(not_erred)
    
    x = np.arange(len(knowmean))    
    plt.fill_between(x, knowmean-knowsdev, knowmean+knowsdev, alpha=0.25, color='red')
    plt.plot(x, knowmean, '-', color='blue')
    plt.ylabel("Average Certainty")
    plt.title("Average Certainty at each round")
    plt.xlabel("Rounds")

    plt.show()

    plt.plot(x, knownums/len(not_erred), '-', color='blue')
    plt.ylabel("Fraction of Games")
    plt.title("Fraction of Games at each round")
    plt.xlabel("Rounds")

    plt.show()
