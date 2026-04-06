def print_results(results, df_id, headers, suffix):
    filename = 'results' + (suffix if suffix not in (None, '') else '') + '.csv'
    with open(filename, 'w') as f:
        print(headers, file=f)
        for i, res in enumerate(results):
            print(f"{df_id.iloc[i]}, {res}", file=f)