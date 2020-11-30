from datetime import datetime

def main() :
	close = 0
	data = ''
	arguments = ''
	global FAT
	global blocks
	global bitmap 
	FAT = [-1 for i in range(25000)]
	blocks = []
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
					FAT, bitmap = loadFATandBitmap(data)
					print(FAT[:10], bitmap[:10])
			except:
				print("Não foi possível montar o sistema de arquivos")

		if arguments[0] == "cp":
			pass

		if arguments[0] == "mkdir":
			pass

		if arguments[0] == "rmdir":
			rmdir(arguments[1])
			print(blocks)

		if arguments[0] == "cat":
			index = findFile(arguments[1])
			content = getFileParsed(arguments[1], index)
			updateAcessedTime(index)
			print(content[-1])

		if arguments[0] == "touch":
			index = findFile(arguments[1])
			if index >= 0:
				updateModifiedTime(index)
				updateAcessedTime(index)
				print(blocks[index])
			else:
				print(arguments[1])
				new_name = arguments[1]
				new_name = arguments[1].split('/')
				new_name = new_name[-1]

				block_index = checkForFreeSpace(1)[0]
				new_block = createFileBlock(new_name, '', block_index)
				directory_input = new_block[:-1] + ';'

				if block_index:
					blocks[block_index] = new_block
					FAT[block_index] = -1
					bitmap[block_index] = 0
				else:
					print("Não existe espaço para a criação desse arquivo")

				# se nao podemos adicionar no diretorio, temos que reverter as mudanças
				if addFileToDirectory(directory_input, arguments[1], block_index) == -1:
					blocks[block_index] = ''
					FAT[block_index] = -1
					bitmap[block_index] = 1
					print("Não existe espaço para a criação desse arquivo")

				print(blocks)


		if arguments[0] == "rm":
			removeFileContent(arguments[1])
			removeFileFromDirectory(arguments[1])
			print(blocks)

		if arguments[0] == "ls":
			try :
				listDirectory(arguments[1])
			except:
				pass

		if arguments[0] == "find":
			search(arguments[1], arguments[2])

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

def createFileBlock(file_name, content, block_index):
	current_time = datetime.now()
	current_time = str(int(current_time.timestamp()))
	new_created_time = current_time
	new_update_time = current_time
	new_access_time = current_time
	new_size = str(len(content))
	new_content = content
	new_block = [file_name, str(block_index), new_created_time, new_update_time, new_access_time, new_size, new_content]
	new_block = '|'.join(new_block)

	return new_block



def addFileToDirectory(directory_input, file_name, added_index):

	dir_name = file_name.split('/')
	dir_name = dir_name[:-1]
	dir_name = '/'.join(dir_name)
	if len(dir_name) == 0:
		dir_name = "/"

	dir_index = findFile(dir_name)
	content = blocks[dir_index]
	content_split = content.split("|")
	
	fat_index = -1
	next_index = int(content_split[1])
	# acha o ultimo bloco do diretório
	while next_index >= 0:
		fat_index = next_index
		next_index = FAT[fat_index]

	content = blocks[fat_index]
	content = content[:-1]
	if len(content) + len(directory_input) < 40:
		content += directory_input + '}'
		print(content, fat_index)
		blocks[fat_index] = content
		return 0

	blocks[fat_index] = content


	index = checkForFreeSpace(1)[0]

	if index >= 0:
		blocks.insert(index, directory_input + '}')
		FAT[fat_index] = index
		FAT[index] = -1
		bitmap[index] = 0

	else:
		return -1

def checkForFreeSpace(number_blocks):
	indexes = []
	for i in range(len(bitmap)):
		if bitmap[i]:
			indexes.append(i)
		if len(indexes) >= number_blocks:
			return indexes

	return None


def updateAcessedTime(block_index):
	current_time = datetime.now()
	new_block = blocks[block_index].split('|')
	new_block[4] = str(int(current_time.timestamp()))
	new_block = '|'.join(new_block)
	blocks[block_index] = new_block

def updateModifiedTime(block_index):
	current_time = datetime.now()
	new_block = blocks[block_index].split('|')
	new_block[3] = str(int(current_time.timestamp()))
	new_block = '|'.join(new_block)
	blocks[block_index] = new_block


def loadFATandBitmap(data):
	bitmap_string = data[0]
	FAT_string = data[1].split('|')
	for i in range(len(FAT_string)):
		FAT[i] = int(FAT_string[i])

	for i in range(len(bitmap_string)):
		bitmap[i] = int(bitmap_string[i])

	return FAT, bitmap


def findFile(filename):
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

		content = getRemainingContent(fat_index, '')
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


def getRemainingContent(initialIndex, initialData):
	index = FAT[initialIndex]

	if index == -1:
		return initialData

	finalData = initialData
	while index >= 0:
		finalData += blocks[index]
		index = FAT[index]

	return finalData

def listDirectory(dirname):

	content = getDirParsed(dirname, findFile(dirname))
	if content:
		print(f"{'NOME' : <10}{'TAMANHO' : ^20}{'ÚLTIMO ACESSO' : >5}")
		if len(content) >= 1:
			for item in content:
				print(f"{item[0] : <10} {item[5] : ^20} {item[4] : >5}")


def getDirParsed(dirname, block_index):

	# block_index = findFile(dirname)

	if block_index == -1:
		print("O diretório não existe")
		return None

	file_block = blocks[block_index]
	print(file_block)
	content_index = file_block.find("{")
	content = file_block[content_index:]
	file_block = file_block.split("|")
	fat_index = int(file_block[1])
	content = getRemainingContent(fat_index, content)
	content = content.split(";")
	content[0] = content[0][1:]
	content.pop()
	for i in range(len(content)):
		content[i] = content[i].split("|")


	return content

def getFileParsed(filename, block_index):
	# block_index = findFile(filename)

	if block_index == -1:
		print("O arquivo não existe")
		return None

	file_block = blocks[block_index]
	file_block = file_block.split("|")
	fat_index = int(file_block[1])
	content = getRemainingContent(fat_index, aux)
	content = content.split("|")

	return content


def searchRec(content, dir_name, file_name):
	if content[0] == file_name and content[0][-1] != "/":
		print(dir_name)
		return

	elif content[0][-1] != "/":
		return

	dir_content = getDirParsed(dir_name, findFile(dir_name))
	
	if dir_content:
		for item in dir_content:
			searchRec(item, dir_name + item[0], file_name)
		


def search(dir_name, file_name):
	dir_content = getDirParsed(dir_name, findFile(dir_name))

	if dir_content:
		for item in dir_content:
			searchRec(item, dir_name + item[0], file_name)


def removeFileContent(file_name):

	block_index = findFile(file_name)
	file_block = blocks[block_index]
	file_block = file_block.split("|")
	print(file_block, file_name)
	fat_index = int(file_block[1])
	while fat_index != -1:
		next_index = FAT[fat_index]
		bitmap[fat_index] = 1
		FAT[fat_index] = -1
		blocks[fat_index] = ""
		fat_index = next_index


def removeFileFromDirectory(file_name):

	if file_name[-1] == '/':
		file_name = file_name[:-1]

	dir_name = file_name.split("/")
	aux_file_name = dir_name[-1]
	dir_name = dir_name[:-1]
	dir_name = "/".join(dir_name)

	if dir_name == '':
		dir_name = '/'

	dir_index = findFile(dir_name)
	updateModifiedTime(dir_index)
	updateAcessedTime(dir_index)

	file_block = blocks[dir_index]
	content_index = file_block.find("{")
	content = file_block[content_index:]
	file_block_split = file_block.split("|")
	fat_index = int(file_block_split[1])
	content = content.split(";")

	for i in range(len(content)):
		if aux_file_name in content[i]:
			content_len = len(content)
			content = content[:i] + content[i+1:]
			
			if i == 0:
				file_block = file_block[:content_index] + '{' + ";".join(content)
			elif i == content_len - 1:
				file_block = file_block[:content_index] + ";".join(content) + '}'

			else:
				file_block = file_block[:content_index] + ";".join(content)
			
			blocks[dir_index] = file_block
			return
			
	prev_index = fat_index
	fat_index = FAT[fat_index]

	while fat_index != -1:
		next_index = FAT[fat_index]
		content = blocks[fat_index]
		content = content.split(";")

		for i in range(len(content)):
			if aux_file_name in content[i]:
				content = content[:i] + content[i+1:]
				content_len = len(content)
				file_block = ";".join(content)

				if next_index == -1 and content_len - 1 == 0:
					blocks[prev_index] += '}'
					FAT[prev_index] = -1
					bitmap[fat_index] = 1
					file_block = ""

				blocks[fat_index] = file_block
				return

		prev_index = fat_index
		fat_index = next_index


def rmdirRec(item, dir_name):

	if item[0][-1] != "/":
		print("entrei aqui")
		removeFileContent(dir_name + item[0]) 
		return
	
	dir_content = getDirParsed(dir_name + item[0], findFile(dir_name + item[0]))
	print(dir_name + item[0])
	# print("alo2", item)
	for item in dir_content:
		rmdirRec(item, dir_name)

	removeFileContent(dir_name + item[0])	


def rmdir(dir_name):

	dir_content = getDirParsed(dir_name, findFile(dir_name + item[0]))

	for item in dir_content:
		rmdirRec(item, dir_name)
	removeFileContent(dir_name)	
	removeFileFromDirectory(dir_name)
	# print(blocks)


if __name__ == "__main__" :
	main()

