def nested_get(d, k):
    keys = k.split('.')
    for k in keys:
        if d.get(k) == None:
            return None
        d = d[k]
    return d