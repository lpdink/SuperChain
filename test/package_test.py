MAX_SIZE = 4


class Package:
    @classmethod
    def regain_package(cls, p_256):
        new_obj = cls()
        new_obj._sha256 = p_256
        new_obj.pool = [None for _ in range(new_obj.max_size)]
        return new_obj

    def __init__(self) -> None:
        self.pool = list()  # sha256:batch
        self.max_size = MAX_SIZE
        self._sha256 = None

    def __getitem__(self, idx):
        return self.pool[idx][1]

    def __len__(self):
        return len(self.pool)

    def add(self, batch_256, batch):
        assert self.max_size > len(self.pool), f"{self.max_size}, {len(self.pool)}"
        self.pool.append((batch_256, batch))
        return self

    def put_in_with_bx(self, batch, bx):
        self.pool[bx] = batch
        return self

    def is_full(self):
        assert self.max_size >= len(self.pool)
        return len(self.pool) == self.max_size

    def regain_done(self):
        for item in self.pool:
            if item is None:
                return False
        return self.is_full()


if __name__ == "__main__":
    package = None
    batch_data_256 = 1
    batch_data = 2
    for i in range(100):
        if package is None:
            package = Package()
            package.add(batch_data_256, batch_data)
        else:
            package.add(batch_data_256, batch_data)
            if package.is_full():
                # p_256 = package.get_sha256()
                package = None

    # @property
    # def get_sha256(self):
    #     if self._sha256 is not None:
    #         return self._sha256
    #     if not self.is_full():
    #         raise RuntimeError(
    #             "Is illegal to compute sha256 when package is not full.")
    #     all_text = ""
    #     for _, batch in self.pool:
    #         all_text += str(batch)
    #     self._sha256 = sha256(all_text)
    #     return self._sha256
