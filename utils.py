def nested_get(d, k):
    keys = k.split('.')
    for k in keys:
        if not d.get(k):
            return None
        d = d[k]
    return d