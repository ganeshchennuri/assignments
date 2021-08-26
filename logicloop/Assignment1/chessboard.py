with open('chess.html','w+') as f:
    f.write('''<!DOCTYPE html>\n<html lang="en">\n<head>\n\t<title>ChessBoard</title>\n\t<style>\n\
        table{
			width: 270px;
			border: 2px solid black;
			border-collapse: collapse
		}
		td{
			width: 30px;
			height: 30px;
		}
	</style>\n</head>\n<body>\n\t<table>\n''')

    for i in range(8):
        f.write('\t\t<tr bordercolor="black">\n')
        for _ in range(4):
            if i%2 == 0:
                f.write('\t\t\t<td bgcolor="white"></td>\n\t\t\t<td bgcolor="black"></td>\n')
            else:
                f.write('\t\t\t<td bgcolor="black"></td>\n\t\t\t<td bgcolor="white"></td>\n')
        f.write('\t\t</tr>\n')
    f.write('\t</table>\n</body>\n')
