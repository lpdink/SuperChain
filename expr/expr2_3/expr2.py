import matplotlib.pylab as plt
import numpy as np

package_nums = (np.arange(4, 36, 4)*256*250/1024).astype(np.int64)
tps = [1117, 2202, 3566, 4500, 5696, 6317, 7556, 8804]

plt.plot(range(len(package_nums)), tps, marker=".", markersize=10)
plt.xticks(range(len(package_nums)), package_nums)
plt.xlabel("block size(KB)")
plt.ylabel(f"TPS")
plt.grid()
# plt.legend()
plt.savefig(f"{__file__}.svg", format="svg", dpi=1200)
# plt.savefig(f"{__file__}.png")