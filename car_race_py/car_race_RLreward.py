import numpy as np

_final_score = -99999
_player_pos = -1
_lis = []
_l_final = []


def _calculate_path(p, yy, xx, r, score):
    global _lis
    global _l_final
    global _final_score
    # global aux_dir
    # global final_dir
    if p[yy * 5 + xx] != 0:
        if yy == 0:
            score += p[yy * 5 + xx]
            if score > _final_score and score < 0:
                _final_score = score
                # final_dir =  aux_dir
                _l_final = []
                for ll in _lis:
                    _l_final.append(ll)
        else:
            # buscar a izquierda
            if xx < 4 and p[yy * 5 + xx + 1] < 0 and r != 1:
                # if yy == 5:
                #     aux_dir = 0
                _lis.append([('y', yy), ('xx', xx), ('peso', p[yy * 5 + xx])])
                _calculate_path(p, yy, xx + 1, 0, score + p[yy * 5 + xx])
                del _lis[-1]
            # buscar a derecha
            if xx > 0 and p[yy * 5 + xx - 1] < 0 and r != 0:
                # if yy == 5:
                #     aux_dir = 1
                _lis.append([('y', yy), ('xx', xx), ('peso', p[yy * 5 + xx])])
                _calculate_path(p, yy, xx - 1, 1, score + p[yy * 5 + xx])
                del _lis[-1]
            # buscar arriba
            if yy > 0 and p[(yy - 1) * 5 + xx] < 0:
                # if yy == 5:
                #     aux_dir = .5
                _lis.append([('y', yy), ('xx', xx), ('peso', p[yy * 5 + xx])])
                _calculate_path(p, yy - 1, xx, .5, score + p[yy * 5 + xx])
                del _lis[-1]


def get_reward(grid):
    global _player_pos
    global _l_final
    global _final_score
    inpu = grid[0]
    path = np.zeros((1, 30))
    np.copyto(path, inpu)
    for y in range(6):
        for x in range(5):
            if inpu[y * 5 + x] == 0 or inpu[y * 5 + x] == .5:
                if inpu[y * 5 + x] == .5:
                    _player_pos = x
                if x == 0:
                    if y == 0:
                        path[0][y * 5 + x] = inpu[y * 5 + x + 1] - 2
                    else:
                        path[0][y * 5 + x] = inpu[(y - 1) * 5 + x] + inpu[y * 5 + x + 1] - 2
                elif x == 4:
                    if y == 0:
                        path[0][y * 5 + x] = inpu[y * 5 + x - 1] - 2
                    else:
                        path[0][y * 5 + x] = inpu[(y - 1) * 5 + x] + inpu[y * 5 + x - 1] - 2
                else:
                    if y == 0:
                        path[0][y * 5 + x] = inpu[y * 5 + x - 1] + inpu[y * 5 + x + 1] - 3
                    else:
                        path[0][y * 5 + x] = inpu[(y - 1) * 5 + x] + inpu[y * 5 + x - 1] + inpu[y * 5 + x + 1] - 3
    # print("[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "------------------------------"
    #       .format(*grid[0]))
    # print("[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "------------------------------"
    #       .format(*path[0]))
    _final_score = -99999
    _calculate_path(path[0], 5, _player_pos, .5, 0)
    if _final_score != -99999:
        return 1
    else:
        return -1
