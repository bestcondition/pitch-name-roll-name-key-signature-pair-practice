import sys
from collections import defaultdict

from _curses import window


pitch_roll_key_list = [
    # [1, 'do', 'C', ],
    [2, 're', 'D', ],
    [3, 'mi', 'E', ],
    [4, 'fa', 'F', ],
    [5, 'sol', 'G', ],
    [6, 'la', 'A', ],
    [7, 'si', 'B', ],
]
name_list = ['音名', '唱名', '调号']

all_pair = [
    tuple(map(str, p))
    for p in pitch_roll_key_list
]

name_key_map = [
    {
        p[i]: p
        for p in all_pair
    }
    for i, name in enumerate(name_list)
]


def random_choice_and_judge(std_scr: window):
    import random
    import time
    import dataclasses
    
    from prettytable import PrettyTable
    from colorama import Fore, Style
    import readchar as _readchar
    
    def readchar():
        c = _readchar.readchar()
        if ord(c) == 3:
            print('程序退出')
            sys.exit()
        else:
            return c

    def seq_lower_eq(a_list, b_list):
        def lower(_v):
            return str(_v).lower()
        a_list = list(map(lower, a_list))
        b_list = list(map(lower, b_list))
        return a_list == b_list

    def table_solo(_table: PrettyTable):
        std_scr.clear()
        std_scr.addstr(f'{weights}')
        std_scr.addstr(_table.get_string())
        std_scr.refresh()

    @dataclasses.dataclass
    class Accuracy:
        total = 0
        wrong = 0
        sum_time = 0

        def add(self, t):
            self.total += 1
            self.sum_time += t
    
        def bingo(self, t):
            self.add(t)

        def fail(self, t):
            self.add(t)
            self.wrong += 0

        @property
        def weight(self):
            total = self.total or 0.00001
            return (self.wrong + 1) * (1 + self.sum_time) / (total ** 2)
            
    pair_to_acc = defaultdict(Accuracy)
    for p in all_pair:
        _ = pair_to_acc[p]
        
    while True:
        weights = [
            pair_to_acc[p].weight
            for p in all_pair
        ]
        chosen_pair = random.choices(
            all_pair,
            weights=weights
        )[0]
        table = PrettyTable()
        table.field_names = name_list
        show_index = random.randint(0, len(name_list) - 1)
        value = [''] * len(name_list)
        value[show_index] = chosen_pair[show_index]
        table.add_row(value)
        
        std_scr.clear()
        std_scr.addstr('开始')
        std_scr.refresh()
        readchar()
        std_scr.clear()
        
        table_solo(table)
        
        def first_empty_index():
            for i, v in enumerate(value):
                if v == '':
                    return i
    
        def input_table():
            empty_index = first_empty_index()
            
            c_list = []
            c = readchar()
            while True:
                if c == ' ':
                    value[empty_index] = ''.join(c_list)
                    table.clear_rows()
                    table.add_row(value)
                    table_solo(table)
                    break
                else:
                    c_list.append(c)
                    value[empty_index] = ''.join(c_list)
                    table.clear_rows()
                    table.add_row(value)
                    table_solo(table)
                    c = readchar()
    
        t0 = time.time()
        input_table()
        input_table()
        delta_t = time.time() - t0
    
        flag = seq_lower_eq(
            value, chosen_pair
        )
        if not flag:
            pair_to_acc[chosen_pair].fail(delta_t)
        else:
            pair_to_acc[chosen_pair].bingo(delta_t)
        table.clear_rows()
        table.add_row(chosen_pair)
        msg = [
            '正确' if flag else '错误',
            f'{delta_t:.2f}秒',
            table.get_string()
        ]
        std_scr.clear()
        std_scr.addstr('\n'.join(msg))
        std_scr.refresh()
        readchar()


def main():
    import curses
    
    curses.wrapper(random_choice_and_judge)


if __name__ == '__main__':
    main()
