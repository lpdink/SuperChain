import matplotlib.pyplot as plt
import numpy as np

def get_cosi_nreqs(num):
    return 4*(num-2)

def get_pbft_nreqs(num):
    return 3*(num-1)+2*(num-1)*(num-1)

def main():
    total_width = 0.8
    width = total_width/2
    node_nums = [i*16 for i in range(1, 17, 2)]
    plt.bar(np.arange(len(node_nums)), np.log([get_cosi_nreqs(num) for num in node_nums]), width=width,label = "CoSi")
    plt.bar(np.arange(len(node_nums))+width, np.log([get_pbft_nreqs(num) for num in node_nums]), width=width,label = "PBFT")
    plt.xticks(np.arange(len(node_nums))+width, node_nums)
    plt.yticks(np.arange(0, 14, 2), [0]+["10$^"+str({i})+"$" for i in range(2, 14, 2)])
    plt.xlabel("node nums")
    plt.ylabel(f"request nums ")
    plt.legend()
    plt.savefig(f"{__file__}.svg", format="svg", dpi=1200)
    # plt.savefig(f"{__file__}.png")

if __name__=="__main__":
    main()