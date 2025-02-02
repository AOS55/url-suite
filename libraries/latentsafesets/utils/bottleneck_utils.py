import libraries.safe.bottleneck_nav as bottleneck

import numpy as np
from tqdm import tqdm


def evaluate_safe_set(s_set,
                      env,
                      file=None,
                      plot=True,
                      show=False,
                      skip=2):
    data = np.zeros((bottleneck.WINDOW_HEIGHT, bottleneck.WINDOW_WIDTH))
    for y in tqdm(range(-bottleneck.WINDOW_HEIGHT//2, bottleneck.WINDOW_HEIGHT//2, skip)):
        row_states = []
        for x in range(0, bottleneck.WINDOW_WIDTH, skip):
            state = env._state_to_image((x, y)) / 255
            row_states.append(state)
        vals = s_set.safe_set_probability_np(np.array(row_states)).squeeze()
        if skip == 1:
            data[y] = vals.squeeze()
        elif skip == 2:
            data[y, ::2], data[y, 1::2] = vals, vals,
            data[y+1, ::2], data[y+1, 1::2] = vals, vals
        else:
            raise NotImplementedError("[name redacted :)] has not implemented logic for skipping %d yet" % skip)

    if plot:
        data_top, data_bottom = np.split(data, 2, axis=0)
        data = np.concatenate((data_bottom, data_top), axis=0)
        env.draw(heatmap=data, file=file, show=show)

    return data


def evaluate_value_func(value_func,
                        env,
                        file=None,
                        plot=True,
                        show=False,
                        skip=2):
    data = np.zeros((bottleneck.WINDOW_HEIGHT, bottleneck.WINDOW_WIDTH))
    for y in tqdm(range(-bottleneck.WINDOW_HEIGHT//2, bottleneck.WINDOW_HEIGHT//2, skip)):
        row_states = []
        for x in range(0, bottleneck.WINDOW_WIDTH, skip):
            state = env._state_to_image((x, y)) / 255
            row_states.append(state)
        vals = value_func.get_value_np(np.array(row_states)).squeeze()
        if skip == 1:
            data[y] = vals.squeeze()
        elif skip == 2:
            data[y, ::2], data[y, 1::2] = vals, vals,
            data[y + 1, ::2], data[y + 1, 1::2] = vals, vals
        else:
            raise NotImplementedError("[name redacted :)] has not implemented logic for skipping %d yet" % skip)

    if plot:
        data_top, data_bottom = np.split(data, 2, axis=0)
        data = np.concatenate((data_bottom, data_top), axis=0)
        # data = np.concatenate(np.split(data,  , axis=0), data[:, 1]//2)
        env.draw(heatmap=data, file=file, show=show)

    return data


def evaluate_constraint_func(constraint,
                             env,
                             file=None,
                             plot=True,
                             show=False,
                             skip=2):
    data = np.zeros((bottleneck.WINDOW_HEIGHT, bottleneck.WINDOW_WIDTH))
    for y in tqdm(range(-bottleneck.WINDOW_HEIGHT//2, bottleneck.WINDOW_HEIGHT//2, skip)):
        row_states = []
        for x in range(0, bottleneck.WINDOW_WIDTH, skip):
            state = env._state_to_image((x, y)) / 255
            row_states.append(state)
        vals = constraint.prob(np.array(row_states)).squeeze()
        if skip == 1:
            data[y] = vals.squeeze()
        elif skip == 2:
            data[y, ::2], data[y, 1::2] = vals, vals,
            data[y + 1, ::2], data[y + 1, 1::2] = vals, vals
        else:
            raise NotImplementedError("[name redacted :)] has not implemented logic for skipping %d yet" % skip)

    if plot:
        data_top, data_bottom = np.split(data, 2, axis=0)
        data = np.concatenate((data_bottom, data_top), axis=0)
        env.draw(heatmap=data, file=file, show=show, board=False)

    return data
