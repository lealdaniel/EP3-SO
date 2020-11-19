def main() :
	close = 0
	data = ''
	arguments = ''
	blocks = []
	FAT = [-1 for i in range(25000)]
	bitmap = [1 for i in range(25000)]
	filename = ''
	totalUsed = 0

	while close == 0 :
		arguments = input("[ep3]: ")
		arguments = arguments.split(' ')
		print(arguments)

		if arguments[0] == "mount":
			filename = arguments[1]
			try:
				with open(filename, "r") as f:
					data = f.read()
					totalUsed = len(data)
					data = data.split('\\')
					blocks = data[2:]
					print(blocks)
					FAT, bitmap = loadFATandBitmap(data, FAT, bitmap)
					print(FAT[:10], bitmap[:10])
			except:
				print("Não foi possível montar o sistema de arquivos")

		if arguments[0] == "cp":
			pass

		if arguments[0] == "mkdir":
			pass

		if arguments[0] == "rmdir":
			pass

		if arguments[0] == "cat":
			index = findFile(FAT, blocks, arguments[1])
			file_block = blocks[index]
			file_block = file_block.split("|")
			fat_index = int(file_block[1])
			content = file_block[-1]
			content = getRemainingContent(FAT, fat_index, content, blocks)
			print(content)

		if arguments[0] == "touch":
			pass

		if arguments[0] == "rm":
			pass

		if arguments[0] == "ls":
			listDirectory(FAT, blocks, arguments[1])
			pass
			# descobrir como achar o arquivo

		if arguments[0] == "find":
			pass

		if arguments[0] == "df":
			freeSpace = sum(bitmap)*4096
			# totalSpace = 100000000 - freeSpace
			# wastedSpace = totalSpace - len(''.join([b.split("|") for b in blocks]))
			pass

		if arguments[0] == "umount":
			if filename != '':
				with open(filename, 'w') as f:
					FAT_string = "|".join(FAT)
					bitmap_string = ''.join(bitmap)
					blocks_string = '\\'.join(blocks)
					f.write(FAT_string + '\\' + bitmap_string + '\\' + blocks_string)
			else :
				print("Nenhum sistema de arquivos foi montado")

		if arguments[0] == "sai":
			exit(0)



def loadFATandBitmap(data, FAT, bitmap):
	bitmap_string = data[0]
	FAT_string = data[1].split('|')
	for i in range(len(FAT_string)):
		FAT[i] = int(FAT_string[i])

	for i in range(len(bitmap_string)):
		bitmap[i] = int(bitmap_string[i])

	return FAT, bitmap


def findFile(FAT, blocks, filename):

	if filename == '/':
		return 0

	filePathList = filename.split('/')
	if filePathList[-1] == '':
		filePathList.pop()
		filePathList[-1] += '/'

	index = blocks[0].find('{')
	startIndex = 0
	found = 0
	fat_index = -1
	block_index = 0
	iter_filePath = 0
	fileList = blocks[0][index+1:]

	# tratar o caso que tem mais de um arquivo na lista entao o separador ; entra na conta
	while found == 0:

		fat_index = int(blocks[block_index].split('|')[1])

		content = getRemainingContent(FAT, fat_index, '', blocks)
		fileList += content
		fileList = fileList[:-1]

		if iter_filePath+1 < len(filePathList)-1 and filePathList[iter_filePath+1] + '/' in fileList:

			# ainda nao achamos, estamos navegando os subdiretorios
			aux = fileList.split(';')
			for i in aux:
				if filePathList[iter_filePath+1] + '/'in i :
					file = i.split('|')
					block_index = int(file[1])
					index = blocks[block_index].find("{")
					fileList = blocks[block_index][index+1:]
					iter_filePath += 1
					break


		elif iter_filePath+1 == len(filePathList)-1 and filePathList[iter_filePath+1] in fileList:

			# achamos o que procuravamos
			aux = fileList.split(';')
			for i in aux :
				if filePathList[iter_filePath+1] + '/'in i or filePathList[iter_filePath+1] in i :
					file = i.split('|')
					block_index = int(file[1])
					found = 1 
					break

		else :
			block_index = -1
			found = 1


	return block_index


def getRemainingContent(FAT, initialIndex, initialData, blocks):
	index = FAT[initialIndex]

	if index == -1:
		return initialData

	finalData = initialData
	while index >= 0:
		finalData += blocks[index]
		index = FAT[index]

	return finalData

def listDirectory(FAT, blocks, dirname):
	print(dirname)
	block_index = findFile(FAT, blocks, dirname)

	if block_index == -1:
		print("O diretório não existe")
		return

	file_block = blocks[block_index]
	content_index = file_block.find("{")
	content = file_block[content_index:]
	file_block = file_block.split("|")
	fat_index = int(file_block[1])
	content = getRemainingContent(FAT, fat_index, content, blocks)
	content = content.split(";")
	content[0] = content[0][1:]
	content[-1] = content[-1][:-1]
	print(f"{'NOME' : <10}{'TAMANHO' : ^20}{'ÚLTIMO ACESSO' : >5}")
	for item in content:
		item = item.split("|")
		print(f"{item[0] : <10} {item[5] : ^20} {item[4] : >5}")


if __name__ == "__main__" :
	main()