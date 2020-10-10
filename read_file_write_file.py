
def open_file(filename):
    """Open the file and return a list of strings"""
    file = open(filename, 'r')
    file_lines = file.readlines()
    #print (file_lines)
    file.close()
    new_list = []
    for i in file_lines:
        new_list.append(i.strip())
    return new_list

def write_file(list_to_write, filename):
    """Take the list you want to write, open the file to overwrite, write and close the file"""
    file = open(filename, 'w')
    for i in list_to_write:
        file.write(str(i)+'\n')
    file.close()





if __name__ == "__main__":
    filename = "new_file.txt"
    open_file(filename)