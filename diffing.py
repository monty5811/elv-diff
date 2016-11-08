from dictdiffer import diff


def run_diff(old, new):
    """
    Notes on the diff:
    d is a generator, each entry is a tuple:

        (kind_of_change, path_to_change, actual_diff)

        where:
            kind_of_change is 'change'|'add'|'remove'
            path_to_change is a string: '{id}.{field}' or a list: ['id', ...]
            actual_diff is a tuple: (old_val, new_val)
    """
    d = diff(old, new, expand=True)
    out = []
    for i in d:
        id_, path_to_diff = parse_path(i[1])
        if path_to_diff in ['last_login', 'date_modified']:
            # strip out noise
            continue
        person = new[id_]
        out.append(
            {
                'diff_path': path_to_diff,
                'person': person,
                'old': i[2][0],
                'new': i[2][1],
            }
        )

    return out


def parse_path(path):
    if type(path) is str:
        path = path.split('.')

    path = [str(x) if type(x) is int else x for x in path]

    return path[0], '.'.join(path[1::])
