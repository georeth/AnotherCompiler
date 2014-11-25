import fileinput

def for_each_file_do(process):
    filename = None
    content = ''
    for line in fileinput.input():
        if fileinput.filename() != filename:
            if filename is not None:
                process(content, filename)
            content = ''
            filename = fileinput.filename()
        content += line
    if content:
        process(content, filename)
