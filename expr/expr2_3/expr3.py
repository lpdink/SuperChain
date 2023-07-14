import matplotlib.pylab as plt
import numpy as np

package_nums = np.arange(16, 256+16, 16)
label_package_nums = np.arange(16, 256+16, 16)
tps = [1815,1341,1205,1176,1021,982,964,886,801,768,726,701,666,654,602,584]
plt.rcParams['figure.figsize'] = (11.2, 6.3) #6，8分别对应宽和高
# plt.plot(range(len(package_nums)), [tps[i] for i in range(0, len(tps), 2)], marker=".", markersize=10)
plt.plot(range(len(package_nums)), tps, marker=".", markersize=10)
plt.xticks(range(0, len(package_nums)), label_package_nums)
plt.xlabel("node nums")
plt.ylabel(f"TPS")
plt.grid()
# plt.legend()
plt.savefig(f"{__file__}.svg", format="svg", dpi=1200)
plt.savefig(f"{__file__}.png")