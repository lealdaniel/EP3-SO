def main() :
	close = 0
	data = ''
	arguments = ''
	blocks = []
	FAT = [-1 for i in range(25000)]
	bitmap = [0 for i in range(25000)]
	filename = ''
	totalUsed = 0

	while close == 0 :
		arguments = input("[ep3]: ")
		arguments = arguments.split(' ')
		print(arguments)
		if arguments[0] == "mount":
			filename = arguments[1]
			try :
				with open(arguments[1], "r") as f:
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
			# precisa descobrir como achar o arquivo
			index = findFile(FAT, blocks, arguments[1])
			# content = locateContent(FAT, index, content, blocks)
			# content = 'name|fat|creat|acces|update|size|dasdasdasdasdas'
			# content = content.split("|")
			# content = ''.join(content[6])
			print(index)

		if arguments[0] == "touch":
			pass

		if arguments[0] == "rm":
			pass

		if arguments[0] == "ls":
			pass
			# descobrir como achar o arquivo
			listDirectory(blocks, arguments[1])

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

	filePathList = filename.split('/')
	index = blocks[0].find('{')
	startIndex = 0
	found = 0
	fat_index = -1
	block_index = 0
	iter_filePath = 0
	fileList = blocks[0][index+1:]
	# print(fileList)
	while found == 0:

		# if fileList[-1] != '}':
			# fat_index = int(blocks[block_index].split('|')[1])

		content = locateContent(FAT, fat_index, '', blocks)
		fileList += content
		fileList = fileList[:-1]

		if iter_filePath+1 < len(filePathList)-1 and filePathList[iter_filePath+1] + '/' in fileList:

			aux  = fileList.split("|")
			aux_iter = iter(aux)
			for i in aux_iter :
				if i == filePathList[iter_filePath+1] + '/':
					block_index = int(next(aux_iter))
					index = blocks[block_index].find("{")
					fileList = blocks[block_index][index+1:]
					iter_filePath += 1
					break


		elif iter_filePath+1 == len(filePathList)-1 and filePathList[iter_filePath+1] in fileList:

			aux  = fileList.split("|")
			aux_iter = iter(aux)
			for i in aux_iter :
				if i == filePathList[iter_filePath+1]:
					block_index = int(next(aux_iter))
					found = 1 
					break

		else :
			block_index = -1
			found = 1


	return block_index


def locateContent(FAT, initialIndex, initialData, blocks):
	if initialIndex == -1:
		return initialData

	index = initialIndex
	finalData = initialData
	while index >= 0:
		finalData += blocks[index]
		index = FAT[index]

	return finalData


def listDirectory(blocks, dirname):
	dirname = dirname.split('/')
	print(dirname, blocks)
	init_block = blocks[0].split("|")
	filelist = init_block[5:]
	print(init_block, filelist)
	if int(init_block[1]) >= 0:
		# fudeu
		pass

	# data = [b.split("|") for b in blocks if dirname[1]+'/' == b.split("|")[0]]
	# print(data)

if __name__ == "__main__" :
	main()