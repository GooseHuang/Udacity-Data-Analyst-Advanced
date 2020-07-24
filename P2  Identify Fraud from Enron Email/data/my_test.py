def convert_csv(data_dict):
    with open('data.csv', 'w') as csvfile:
        fieldnames = ['name'] + data_dict.itervalues().next().keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for value in data_dict:
            key = data_dict[value]
            key['name'] = value
            writer.writerow(key)

data_dict