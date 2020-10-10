import csv

def read_csv(filename):
    """Input a CSV file, grab its info in a list. Every line is a list."""
    file = open(filename)
    file_reader = csv.reader(file)
    file_data = list(file_reader)
    file.close()
    return file_data

def convert_list_to_dict(list_of_lists, *args):
    """Take the list and for however many arguments, create a dictionary of the small list and return a list."""
    print(args)
    main_list_of_dicts = []
    len_of_each_list = len(args[0])
    for i in list_of_lists:
        new_dict = {}
        x = 0
        while x < len_of_each_list:
            new_dict[args[0][x]] = i[x]
            x += 1
        main_list_of_dicts.append(new_dict)
    return main_list_of_dicts

def write_csv(fieldnames, details, filename):
    """Fieldnames is a list of the column names. Details needs to be a dictionary with fieldnames that will match the csv columns."""
    #add the fieldnames below
    fieldnames = fieldnames
    with open(filename,'a',newline='') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow(details)
    csvfile.close()


if __name__ == "__main__":
    filename = "home_schooled.csv"
    fieldnames = ['email', 'zip']
    file_data = read_csv(filename)
    check_list = []
    new_list = []
    for i in file_data:
        if i[0] not in check_list:
            check_list.append(i[0])
            new_list.append(i)
        else:
            pass
    list_of_dicts = convert_list_to_dict(new_list, ['email', 'zip'])
    for i in list_of_dicts:
        write_csv(fieldnames, i, 'school_is_for_fools.csv')