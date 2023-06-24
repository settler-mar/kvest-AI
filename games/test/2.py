class DoorsClass:
    state = 1
    lines = []
    st_map = [
        [0, 1],
        [0, 1, 2],
        [0, 2]
    ]

    def create(self, lines):
        self.lines = lines
        # print(self.index, [l.index for l in lines])
        for line in lines:
            line.add(self)

    def __init__(self, index, st):
        self.index = index
        self.state = st

    def calc(self, in_line):
        active = None
        for i, line in enumerate(self.lines):
            if line.index == in_line:
                active = i
                break
        # print('active', active)

        st_map = self.st_map[self.state]
        if active not in st_map:
            return

        for i in st_map:
            self.lines[i].active(self.index)


class LineClass:
    state = 0
    doors = []

    def __init__(self, index):
        self.index = index

    def add(self, door):
        self.doors.append(door)

    def active(self, in_door=None):
        if self.state:
            return
        self.state = 1

        # print('line', self.index, self.doors)
        for door in self.doors:
            if in_door == None or door.index != in_door:
                door.calc(self.index)


connects = [
    [10, 5, 8],
    [12, 10, 11],
    [0, 1, 2],
    [2, 4, 7],
    [1, 5, 3],
    [11, 9, 7],
    [6, 4, 3],
    [6, 8, 9],
]


def calc_st(index, a):
    st_map = [
        [-7],
        [0],
        [3, 5],
        [4, 6]
    ]
    r = None
    for i, st in enumerate(a):
        if st == 1:
            continue
        if index in st_map[i]:
            return st
        if -index in st_map[i]:
            return 2 - st

        # if r == None:
        #     r = (st == 2)
        # else:
        #     r = (st == 2) ^ r
    # print(index, r)
    if r == None:
        return 1
    return [0, 2][r]


class GameClass:
    def process(self, *a):
        lines_lst = [LineClass(i) for i in range(13)]
        doors_lst = [DoorsClass(i, calc_st(i, a)) for i in range(9)]

        for j, connect in enumerate(connects):
            doors_lst[j].create([lines_lst[i] for i in connect])

        lines_lst[0].active()
        return lines_lst[12].state


cnt = 0
cnt_w = 0

for a1 in range(3):
    for a2 in range(3):
        for a3 in range(3):
            for a4 in range(3):
                cnt += 1
                if not GameClass().process(a1, a2, a3, a4):
                    print(a1, a2, a3, a4)
                    cnt_w += 1

print('total:', cnt)
print('win:', cnt_w)
print('pers', int(100 * cnt_w / cnt))

# print(GameClass().process(2, 0, 2, 0))
# print(GameClass().process(0, 0, 0, 0))
