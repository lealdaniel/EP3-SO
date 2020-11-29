from datetime import datetime

def main() :
	close = 0
	data = ''
	arguments = ''
	global FAT
	global blocks
	global bitmap 
	global totalUsed
	global fileNumber
	global dirNumber
	FAT = [-1 for i in range(24900)]
	blocks = []
	bitmap = [1 for i in range(24900)]
	filename = ''
	totalUsed = 0
	fileNumber = 0
	dirNumber = 0

	while close == 0 :
		arguments = input("[ep3]: ")
		arguments = arguments.split(' ')
		print(arguments)

		if arguments[0] == "mount":
			filename = arguments[1]
			# try:
			with open(filename, "r") as f:
				data = f.read()
				data = data.split('\\')
				print(data)
				FAT, bitmap, blocks = loadFATandBitmap(data)
					# print(FAT[:10], bitmap[:10])
			# except:
			# 	print("Não foi possível montar o sistema de arquivos")

		if arguments[0] == "cp":
			copyFile(arguments[1], arguments[2])
			# print(blocks)

		if arguments[0] == "mkdir":
			mkdir(arguments[1])

		if arguments[0] == "rmdir":
			rmdir(arguments[1])
			print(blocks, FAT[:15], bitmap[:15])

		if arguments[0] == "cat":
			index = findFile(arguments[1])
			content = getRemainingContent(index, blocks[index])
			updateAcessedTime(arguments[1])

			print(content)
			print(blocks)

		if arguments[0] == "touch":
			touchFile(arguments[1])
			print(blocks[0])


		if arguments[0] == "rm":
			rm(arguments[1])
			print(blocks)

		if arguments[0] == "ls":
			listDirectory(arguments[1])

		if arguments[0] == "find":
			search(arguments[1], arguments[2])

		if arguments[0] == "df":
			freeSpace = sum(bitmap)*4000 - 25000
			# 14*4000 é o tanto que ocupam o fat e o bitmap
			wastedSpace = sum([1 for i in bitmap if i == 0])*4000 - totalUsed + 14*4000
			print("Quantidade de diretórios:", dirNumber)
			print("Quantidade de arquivos:", fileNumber)
			print("Espaço livre:", freeSpace)
			print("Espaço disperdiçado:", wastedSpace)


		if arguments[0] == "teste":
			index = findFile(arguments[1])
			print(index)

		if arguments[0] == "umount":
			if filename != '':
				with open(filename, 'w') as f:
					FAT_string = "|".join(str(i) for i in FAT)
					bitmap_string = ''.join(str(i) for i in bitmap)
					blocks_string = '\\'.join(blocks)
					print(blocks_string[:100])
					f.write(bitmap_string + '\\' + FAT_string + '\\' + blocks_string)
			else :
				print("Nenhum sistema de arquivos foi montado")

		if arguments[0] == "sai":
			exit(0)

def copyFile(real_file, file_name):

	with open(real_file, "r") as file:

		global totalUsed
		global fileNumber
		data = file.read()
		blocks_, blocks_size = len(data), 4000
		blocks_slices = range(4000, blocks_, blocks_size) 
		data_blocks = []
		last_i = 0
		for i in blocks_slices:
			data_blocks.append(data[last_i:i])
			last_i = i

		if last_i < len(data):
			data_blocks.append(data[last_i:])
		# o tamanho de 100MB menos os separadores
		maxsize = 100000000 - 25000
		if totalUsed + len(data) + len(data_blocks) > maxsize:
			print("Não há espaço para adicionar o arquivo")
			return 

		indexes = checkForFreeSpace(len(data_blocks))
		if indexes:
			new_name = file_name
			new_name = file_name.split('/')
			new_name = new_name[-1]
			directory_input = createDirectoryInput(new_name, indexes[0], len(data))
			if addFileToDirectory(directory_input, file_name) == -1:
				for index in indexes:
					bitmap[index] = 1
				print("Não existe espaço para a criação desse arquivo")
				return	

			for i in range(len(indexes)-1):
				blocks[indexes[i]] = data_blocks[i]
				FAT[indexes[i]] = indexes[i+1]
			blocks[indexes[-1]] = data_blocks[-1]
			FAT[indexes[-1]] = -1
			totalUsed += len(data) + len(data_blocks)
			print("cheguei aqui", FAT[:20])
			dir_name = getDirName(file_name)
			fileNumber += 1
			updateDirSize(dir_name, len(data))


def getDirName(file_name):
	dir_name = file_name.split('/')
	if dir_name[-1] == '':
		dir_name.pop()

	dir_name = dir_name[:-1]
	dir_name = '/'.join(dir_name) + '/'
	return dir_name

def getFileName(file_name):
	filename = file_name.split('/')
	if filename[-1] == '':
		filename.pop()
		filename[-1] += '/'

	filename = filename[-1]
	return filename

def touchFile(file_name):

	global totalUsed
	global fileNumber
	file_index = findFile(file_name)
	if file_index >= 0:
		updateModifiedTime(index)
		updateAcessedTime(index)
	else:
		new_name = file_name
		new_name = file_name.split('/')
		new_name = new_name[-1]
		block_index = checkForFreeSpace(1)
		if block_index:
			block_index = block_index[0]
		# index teste
		# block_index = 7
		directory_input = createDirectoryInput(new_name, block_index, 0)
		if addFileToDirectory(directory_input, file_name) == -1:
			bitmap[block_index] = 1
			print("Não existe espaço para a criação desse arquivo1")

		if block_index:
			totalUsed += len(directory_input)
			print(block_index)
			blocks[block_index] = ''
			FAT[block_index] = -1
			bitmap[block_index] = 0
			fileNumber += 1
		else:
			print("Não existe espaço para a criação desse arquivo2")
		# print(blocks[:10])
		# se nao podemos adicionar no diretorio, temos que reverter as mudanças

def mkdir(dir_name):
	global totalUsed
	global dirNumber
	new_name = dir_name
	new_name = dir_name.split('/')
	print(new_name)
	if new_name[-1] == '':
		new_name.pop()

	new_name[-1] += '/'
	new_name = new_name[-1]

	block_index = checkForFreeSpace(1)
	if block_index:
		block_index = block_index[0]
	# index teste
	# block_index = 7
	print(block_index)
	directory_input = createDirectoryInput(new_name, block_index, 0)
	if addFileToDirectory(directory_input, dir_name) == -1:
		bitmap[block_index] = 1
		print("Não existe espaço para a criação desse arquivo")

	if block_index:
		totalUsed += len(directory_input)
		blocks[block_index] = ''
		FAT[block_index] = -1
		bitmap[block_index] = 0
		dirNumber += 1
	else:
		print("Não existe espaço para a criação desse arquivo")
	print(blocks[0])

	# se nao podemos adicionar no diretorio, temos que reverter as mudanças

	# print(blocks)

def createDirectoryInput(file_name, block_index, size):

	current_time = datetime.now()
	current_time = str(int(current_time.timestamp()))
	new_created_time = current_time
	new_update_time = current_time
	new_access_time = current_time
	new_size = str(size)
	new_block = [file_name, str(block_index), new_created_time, new_update_time, new_access_time, new_size]
	new_block = '|'.join(new_block) + ';'

	return new_block

def addFileToDirectory(directory_input, file_name):

	dir_name = getDirName(file_name)
	print(dir_name)
	dir_index = findFile(dir_name)
	print(dir_index)

	updateModifiedTime(dir_name)
	updateAcessedTime(dir_name)

	content = blocks[dir_index]
	# acha o ultimo bloco de conteudo do diretorio que tem lugar vazio
	fat_index = dir_index
	next_index = FAT[dir_index]
	while next_index >= 0 and len(blocks[fat_index]) + len(directory_input) > 4000:
		fat_index = next_index
		next_index = FAT[fat_index]

	content = blocks[fat_index]
	if len(content) + len(directory_input) < 4000:
		content += directory_input
		# print(content, fat_index)
		blocks[fat_index] = content
		return 0

	index = checkForFreeSpace(1)
	if index:
		index = index[0]
	# print(index)
	#index teste
	# index = None
	if index:
		blocks[index] = directory_input
		FAT[index] = -1
		bitmap[index] = 0
	else :
		return -1

def checkForFreeSpace(number_blocks):

	# o tamanho de 100 MB menos os separadores de blocos
	maxsize = 100000000 - 25000
	if number_blocks*4000 + totalUsed > maxsize:
		return None

	indexes = []
	for i in range(len(bitmap)):
		if bitmap[i]:
			indexes.append(i)
		if len(indexes) >= number_blocks:
			for index in indexes:
				bitmap[index] = 0
			print(indexes)
			return indexes

	return None

def updateDirSize(file_name, size):
	dir_name = getDirName(file_name)
	# dir_name = getDirName(dir_name)
	file_name = getFileName(file_name)
	block_index = findFile(dir_name)
	print("OOOO", dir_name, block_index, file_name)
	found = 0
	index = block_index
	while found == 0 and index >= 0:
		dir_block = blocks[index]
		dir_list = dir_block.split(';')

		for i in range(len(dir_list)):
			item = dir_list[i].split('|')
			print(item[0], file_name)
			if item != [''] and (item[0] == file_name or item[0] == file_name + '/'):
				new_item = item
				new_item[5] = str(int(item[5]) + size)
				new_item = '|'.join(new_item)
				dir_list[i] = new_item
				found = 1
				break

		if found == 1:
			dir_list = ';'.join(dir_list)
			blocks[index] = dir_list 

		else:
			index = FAT[index]

def updateModifiedTime(file_name):

	dir_name = getDirName(file_name)
	file_name = getFileName(file_name)
	block_index = findFile(dir_name)
	found = 0
	index = block_index
	while found == 0 and index >= 0:
		dir_block = blocks[index]
		dir_list = dir_block.split(';')

		for i in range(len(dir_list)):
			item = dir_list[i].split('|')
			if item != [''] and (item[0] == file_name or item[0] == file_name + '/'):
				new_item = item
				current_time = datetime.now()
				new_item[4] = str(int(current_time.timestamp()))
				new_item = '|'.join(new_item)
				dir_list[i] = new_item
				found = 1
				break

		if found == 1:
			dir_list = ';'.join(dir_list)
			blocks[index] = dir_list 

		else:
			index = FAT[index]

def updateAcessedTime(file_name):

	dir_name = getDirName(file_name)
	file_name = getFileName(file_name)
	block_index = findFile(dir_name)
	found = 0
	index = block_index
	while found == 0 and index >= 0:
		dir_block = blocks[index]
		dir_list = dir_block.split(';')

		for i in range(len(dir_list)):
			item = dir_list[i].split('|')
			if item != [''] and (item[0] == file_name or item[0] == file_name + '/'):
				new_item = item
				current_time = datetime.now()
				new_item[3] = str(int(current_time.timestamp()))
				new_item = '|'.join(new_item)
				dir_list[i] = new_item
				found = 1
				break

		if found == 1:
			dir_list = ';'.join(dir_list)
			blocks[index] = dir_list 

		else:
			index = FAT[index]

def loadFATandBitmap(data):

	global totalUsed
	FAT_string = ''
	bitmap_string = ''
	for block in data[:7]:
		bitmap_string += block

	for block in data[7:14]:
		FAT_string += block
	totalUsed += len(FAT_string) + len(bitmap) + 14
	FAT_string = FAT_string.split("|")
	print("len" , len(FAT_string))
	blocks = data[14:]
	for i in range(len(FAT_string)):
		FAT[i] = int(FAT_string[i])

	for i in range(len(bitmap_string)):
		bitmap[i] = int(bitmap_string[i])
	print(bitmap[:10])
	return FAT, bitmap, blocks


def findFile(filename):
	if filename == '/':
		return 0

	filePathList = filename.split('/')
	if filePathList[-1] == '':
		filePathList.pop()
		filePathList[-1] += '/'

	startIndex = 0
	found = 0
	fat_index = 0
	block_index = 0
	iter_filePath = 0
	fileList = blocks[0]

	# tratar o caso que tem mais de um arquivo na lista entao o separador ; entra na conta
	while found == 0:

		content = getRemainingContent(block_index, blocks[block_index])
		fileList = content
		# print(content, iter_filePath, len(filePathList), filePathList[iter_filePath+1])
		# if content == '':
		# 	return -1
		if iter_filePath+1 < len(filePathList)-1 and filePathList[iter_filePath+1] + '/' in fileList:

			# ainda nao achamos, estamos navegando os subdiretorios
			aux = fileList.split(';')
			for i in aux:
				file = i.split('|')
				print(file)
				if filePathList[iter_filePath+1] + '/' == file[0] :
					# print(filePathList[iter_filePath+1])
					block_index = int(file[1])
					fileList = blocks[block_index]
					iter_filePath += 1
					break


		elif iter_filePath+1 == len(filePathList)-1 and filePathList[iter_filePath+1] in fileList:

			# achamos o que procuravamos
			aux = fileList.split(';')
			for i in aux :
				file = i.split('|')
				print("AA", file, file)
				if filePathList[iter_filePath+1] + '/' == file[0] or filePathList[iter_filePath+1] == file[0] :
					block_index = int(file[1])
					found = 1 
					break

			# se o loop acaba, nao achamos
			if found == 0: 
				block_index = -1
				found = 1
		else :
			print(iter_filePath)
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
				# print(item)
				time = datetime.fromtimestamp(int(item[4]))
				time_string = time.strftime("%d/%m/%Y, %H:%M:%S")
				print(f"{item[0] : <10} {item[5] : ^20} {time_string : >5}")


def getDirParsed(dirname, block_index):

	block_index = findFile(dirname)

	if block_index == -1:
		print("O diretório não existe")
		return None

	file_block = blocks[block_index]
	content = file_block
	content = getRemainingContent(block_index, content)
	content = content.split(";")
	content.pop()
	for i in range(len(content)):
		content[i] = content[i].split("|")


	return content


def searchRec(content, dir_name, file_name):
	if content[0] == file_name and content[0][-1] != "/":
		print(dir_name)
		return

	elif content[0][-1] != "/":
		return

	index = findFile(dir_name)
	dir_content = getDirParsed(dir_name, index)
	
	if dir_content:
		for item in dir_content:
			if item != [''] :
				searchRec(item, dir_name + item[0], file_name)
		


def search(dir_name, file_name):
	index = findFile(dir_name)
	dir_content = getDirParsed(dir_name, index)

	if dir_content:
		for item in dir_content:
			if item != ['']:
				searchRec(item, dir_name + item[0], file_name)


def rm(file_name):
	removeFileContent(file_name)
	removeFileFromDirectory(file_name)


def removeFileContent(file_name):

	block_index = findFile(file_name)
	file_block = blocks[block_index]
	fat_index = block_index
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
	updateModifiedTime(dir_name)
	updateAcessedTime(dir_name)

	#update time here
	file_block = blocks[dir_index]
	content = file_block
	content = content.split(";")

	for i in range(len(content)):

		if aux_file_name in content[i]:
			content_len = len(content)
			content = content[:i] + content[i+1:]
			
			file_block =  ";".join(content)
			
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
					FAT[prev_index] = -1
					bitmap[fat_index] = 1
					file_block = ""

				blocks[fat_index] = file_block
				return

		prev_index = fat_index
		fat_index = next_index


def rmdirRec(item, dir_name):
	global fileNumber
	global dirNumber
	if item[0][-1] != "/":
		print(dir_name + item[0])
		removeFileContent(dir_name + item[0]) 
		fileNumber -= 1
		return

	index = findFile(dir_name + item[0])
	dir_content = getDirParsed(dir_name + item[0], index)
	new_dir_name = dir_name + item[0]
	for item in dir_content:
		if item != ['']:
			rmdirRec(item, new_dir_name)

	dirNumber -= 1
	removeFileContent(new_dir_name)


def rmdir(dir_name):

	global dirNumber	
	if dir_name[-1] == '/':

		index = findFile(dir_name)
		dir_content = getDirParsed(dir_name, index)
		for item in dir_content:
			if item != ['']:
				rmdirRec(item, dir_name)

		dirNumber -= 1
		removeFileContent(dir_name)	
		removeFileFromDirectory(dir_name)
		print(blocks)


if __name__ == "__main__" :
	main()


