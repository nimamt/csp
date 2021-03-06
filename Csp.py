from Inference import Inference
from Var import Var


class Csp():
    rows = -1
    cols = -1
    row_vals = None
    col_vals = None
    row_nvals = None
    col_nvals = None
    data: "list[list[int]]" = None
    mp: "list[list[list[Var]]]" = None
    variables = None
    saved_arcs: list = None

    def __init__(self, rows, cols, row_vals, col_vals, row_nvals, col_nvals, data, mp, variables):
        self.rows = rows
        self.cols = cols
        self.row_vals = row_vals
        self.col_vals = col_vals
        self.row_nvals = row_nvals
        self.col_nvals = col_nvals
        self.data = data
        self.mp = mp
        self.variables = variables
        for i in variables:
            i.constraints = self.constraints(i)
        self.saved_arcs = self.arcs()

    def claim(self, r, c, value, inferences: list):
        var = self.mp[r][c]
        for i in var.domain:
            if i != value:
                if not var.removed_domain[i+1]:
                    inferences.append(Inference(var, i))

    def claim_charge(self, r, c, charge, inferences: list):

        # left
        if c-1 >= 0:
            var = self.mp[r][c-1]
            var.revoke_charge_claim(r, c-1, charge, inferences)

        # right
        if c+1 < self.cols:
            var = self.mp[r][c+1]
            var.revoke_charge_claim(r, c+1, charge, inferences)
        # up
        if r-1 >= 0:
            var = self.mp[r-1][c]
            var.revoke_charge_claim(r-1, c, charge, inferences)
        # down
        if r+1 < self.rows:
            var = self.mp[r+1][c]
            var.revoke_charge_claim(r+1, c, charge, inferences)

    def append(self, var: Var, value: int):
        r1, c1 = var.second_block()
        v1, v2 = ('e', 'e')

        if value == 1:
            v1 = '+'
            v2 = '-'
        elif value == -1:
            v1 = '-'
            v2 = '+'

        var.value = value
        self.data[var.r][var.c] = v1
        self.data[r1][c1] = v2

    def append_inferences(self, inferences: "list[Inference]"):
        for i in inferences:
            if not i.var.removed_domain[i.val+1]:
                i.var.removed_domain[i.val+1] = True
                
                no_choice = True
                for i in i.var.removed_domain:
                    if i is False:
                        no_choice = False
                        break
                if no_choice:
                    return False
        return True

    def remove(self, var: Var, value: int):
        r1, c1 = var.second_block()
        var.value = -100
        if var.type == 0:
            self.data[var.r][var.c] = 'l'
            self.data[r1][c1] = 'r'
        if var.type == 1:
            self.data[var.r][var.c] = 'u'
            self.data[r1][c1] = 'd'

    def remove_inferences(self, inferences: "list[Inference]"):
        for i in inferences:
            i.var.removed_domain[i.val+1] = False

    def print(self):
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.data[i][j]
                if x == 'u' or x == 'l' or x == 'd' or x == 'r':
                    x = 'e'
                print(x, end=' ')
            print()
        print()

    def check_range(self, r, c):
        return r >= 0 and c >= 0 and r < self.rows and c < self.cols

    def constraints(self, var: Var):
        constraints = []
        if var.type == 0:

            if self.check_range(var.r, var.c-1):
                v = self.mp[var.r][var.c-1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r+1, var.c):
                v = self.mp[var.r+1][var.c]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r-1, var.c):
                v = self.mp[var.r-1][var.c]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r-1, var.c+1):
                v = self.mp[var.r-1][var.c+1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r+1, var.c+1):
                v = self.mp[var.r+1][var.c+1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r, var.c+2):
                v = self.mp[var.r][var.c+2]
                if v not in constraints:
                    constraints.append(v)

        if var.type == 1:

            if self.check_range(var.r-1, var.c):
                v = self.mp[var.r-1][var.c]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r, var.c-1):
                v = self.mp[var.r][var.c-1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r, var.c+1):
                v = self.mp[var.r][var.c+1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r+1, var.c-1):
                v = self.mp[var.r+1][var.c-1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r+1, var.c+1):
                v = self.mp[var.r+1][var.c+1]
                if v not in constraints:
                    constraints.append(v)

            if self.check_range(var.r+2, var.c):
                v = self.mp[var.r+2][var.c]
                if v not in constraints:
                    constraints.append(v)

        return constraints

    def arcs(self) -> list:
        arcs = []
        for v in self.variables:
            constraints = v.constraints
            for i in constraints:
                arcs.append((v, i))
        return arcs

    def ac3(self, inferences):
        queue = self.saved_arcs.copy()

        while len(queue) != 0:
            x_i, x_j = queue.pop()
            # performance gain
            if x_i.value == 0:
               continue
            # performance gain
            if self.revise(x_i, x_j, inferences):
                no_choice = True
                for i in x_i.removed_domain:
                    if i is False:
                        no_choice = False
                        break
                if no_choice:
                    return False
                for x_k in list(filter(lambda x_k: x_k is not x_j, x_i.constraints)):
                    queue.append((x_k, x_i))
        return True

    def revise(self, x_i: Var, x_j: Var, inferences):
        revised = False
        # performance gain
        if not x_j.removed_domain[0+1]:
            return False
        # if x_i.real_domain() == [0]:
            # return False
        # performance gain
        for x in x_i.real_domain():
            if self.no_value_satisfies(x_i, x, x_j):
                # print('r: %d c: %d r1: %d c1: %d type: %d type1: %d, val: %d' % (x_i.r, x_i.c, x_j.r, x_j.c, x_i.type, x_j.type, x))
                # print(x_i.real_domain())
                # print(x_j.real_domain())

                inferences.append(Inference(x_i, x))
                x_i.removed_domain[x+1] = True
                revised = True
        return revised

    def no_value_satisfies(self, x_i: Var, val: int, x_j: Var):
        for i in x_j.real_domain():
            # depending on performance gain section in revise
            # if val == 0 or i == 0:
                # return False
            if val == 0:
                return False
            if self.is_match(x_i,x_j,val,i):
                return False
        return True

    def is_match(self, x_i, x_j, val, i):
        r1, c1 = x_j.second_block()

        if x_i.first_neighbor(x_j.r, x_j.c):
            if val == i:
                return False

        if x_i.second_neighbor(x_j.r, x_j.c):
            if -1*val == i:
                return False

        if x_i.first_neighbor(r1, c1):
            if val == -1*i:
                return False

        if x_i.second_neighbor(r1, c1):
            if -1*val == -1*i:
                return False
        
        return True
