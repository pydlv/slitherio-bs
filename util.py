import math


def hex_color_to_rgb(hex_color: str) -> (int, int, int):
    stripped = hex_color.lstrip("#")

    return tuple(int(stripped[i:i+2], 16) for i in (0, 2, 4))


def dist2(x1, y1, x2, y2):
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def spread(original, target_length):
    result = []

    original_last_index = len(original) - 1

    for i in range(target_length):
        percent_done = i / (target_length - 1)
        # Find the index on the original
        index = min(original_last_index, round(percent_done * original_last_index))

        result.append(original[index])

    return result


def angle_to_mouse_coords(angle):
    x = math.cos(angle) * 1000
    y = math.sin(angle) * 1000
    return x, y
