"""Compare old and new data."""
from dictdiffer import diff

from diff_types import GroupDiff, PersonDiff


def run_diff(old_data, new_data):
    """
    Compare people for changes.

    Notes on the diff:
    d is a generator, each entry is a tuple:

        (kind_of_change, path_to_change, actual_diff)

        where:
            kind_of_change is 'change'|'add'|'remove'
            path_to_change is a string: '{id}.{field}' or a list: ['id', ...]
            actual_diff is a tuple: (old_val, new_val)
    """
    for i in diff(old_data, new_data, expand=True):
        if i[0] == 'remove':
            for id_, person in i[2]:
                yield PersonDiff(
                    path='Person removed',
                    item=person,
                )
            continue

        if i[0] == 'add':
            for id_, person in i[2]:
                yield PersonDiff(
                    path='Person added',
                    item=person,
                )
            continue

        if i[0] == 'change':
            id_, diff_path = parse_path(i[1])
            if diff_path in ['last_login', 'date_modified']:
                # strip out noise
                continue
            person = new_data[id_]
            old = i[2][0]
            new = i[2][1]

            yield PersonDiff(
                path=diff_path,
                item=person,
                old=old,
                new=new,
            )


def run_diff_groups(old_data, new_data, ppl):
    """
    Compare groups for changes.

    Notes on the diff:
    d is a generator, each entry is a tuple:

        (kind_of_change, path_to_change, actual_diff)

        where:
            kind_of_change is 'change'|'add'|'remove'
            path_to_change is a string: '{id}.{field}' or a list: ['id', ...]
            actual_diff is a tuple: (old_val, new_val)
    """
    old_data = collapse_people(old_data, ppl)
    new_data = collapse_people(new_data, ppl)
    for i in diff(old_data, new_data):
        if '.people' in i[1]:
            if i[0] == 'remove':
                g_id, _ = parse_path(i[1])
                group = new_data[g_id]
                names = '\t\n'.join([x[1] for x in i[2]])
                yield GroupDiff(
                    path=f'People removed from "{group["name"]}":\n\t{names}',
                    item=group,
                )
                continue

            if i[0] == 'add':
                g_id, _ = parse_path(i[1])
                group = new_data[g_id]
                names = '\t\n'.join([x[1] for x in i[2]])
                yield GroupDiff(
                    path=f'People added to "{group["name"]}":\n\t{names}',
                    item=group,
                )
                continue

        if i[0] == 'remove':
            for id_, group in i[2]:
                yield GroupDiff(
                    path='Group removed',
                    item=group,
                )
            continue

        if i[0] == 'add':
            for id_, group in i[2]:
                yield GroupDiff(
                    path='Group added',
                    item=group,
                )
            continue

        if i[0] == 'change':
            id_, diff_path = parse_path(i[1])
            if diff_path in ['date_modified']:
                # strip out noise
                continue
            group = new_data[id_]
            old = i[2][0]
            new = i[2][1]

            yield GroupDiff(
                path=diff_path,
                item=group,
                old=old,
                new=new,
            )


def extract_person_name(id_, ppl):
    """Extract names of added/removed people."""
    p = ppl[id_]
    return '{firstname} {lastname}'.format(**p)


def parse_path(path):
    """Parse the path returned from `dictdiffer`."""
    if isinstance(path, str):
        path = path.split('.')

    path = [str(x) if isinstance(x, int) else x for x in path]

    return path[0], '.'.join(path[1::])


def collapse_people(groups, ppl):
    """
    Convert people in group from a list of dicts to a dict: {id: name}.

    We do this so the only changes picked up by the diffs are additions
    and removals.
    """
    for id_, group in groups.items():
        try:
            people = {p['id']: extract_person_name(p['id'], ppl) for p in group['people']['person']}
        except TypeError:
            people = {}

        group['people'] = people
        groups[id_] = group

    return groups
