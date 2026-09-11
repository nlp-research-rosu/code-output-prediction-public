import sys


def possible(a, b, moves):
    size = len(a)
    source = "0" * moves + a + "0" * moves
    source_size = len(source)
    prefix_ones = [0] * (source_size + 1)
    for index, character in enumerate(source):
        prefix_ones[index + 1] = prefix_ones[index] + (character == "1")

    last_source_one = source.rfind("1")
    last_target_one = b.rfind("1")
    position = 0
    index = 0
    while index < size:
        if index == size - 1:
            length = source_size - position
            has_one = prefix_ones[source_size] > prefix_ones[position]
            return length > 0 and length % 2 == 1 and has_one == (b[index] == "1")

        if b[index] == "1":
            target = (
                last_source_one
                if index == last_target_one
                else source.find("1", position)
            )
            if target < position:
                return False
            length = target - position + 1
            if length % 2 == 0:
                length += 1
            position += length
            if position > source_size:
                return False
            index += 1
            continue

        end = index
        while end < size and b[end] == "0":
            end += 1
        run_length = end - index
        if end == size:
            if position <= last_source_one:
                position += 2 * ((last_source_one - position) // 2 + 1)
            remaining = source_size - position
            return remaining >= run_length and (remaining - run_length) % 2 == 0

        while True:
            if position + run_length > source_size:
                return False
            ones = prefix_ones[position + run_length] - prefix_ones[position]
            if ones == 0:
                break
            position += 2
        position += run_length
        index = end
    return position == source_size


def solve(a, b):
    leading_a = len(a) - len(a.lstrip("0"))
    leading_b = len(b) - len(b.lstrip("0"))
    trailing_a = len(a) - len(a.rstrip("0"))
    trailing_b = len(b) - len(b.rstrip("0"))
    minimum = max(0, leading_b - leading_a, trailing_b - trailing_a)
    for moves in (minimum, minimum + 1):
        if possible(a, b, moves):
            return moves
    return -1


def main():
    data = sys.stdin.buffer.read().split()
    test_count = int(data[0])
    output = []
    offset = 1
    for _ in range(test_count):
        offset += 1
        a = data[offset].decode()
        b = data[offset + 1].decode()
        offset += 2
        output.append(str(solve(a, b)))
    sys.stdout.write("\n".join(output))


if __name__ == "__main__":
    main()
