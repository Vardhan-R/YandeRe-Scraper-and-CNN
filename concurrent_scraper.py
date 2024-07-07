from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import concurrent.futures, csv, os, requests, sys, threading

def concurrentMain(post_id: int) -> None:
	'''
	Saves the image, rating and general tags of the post with the given post id.

	## Parameters
	post_id : int
		The post id of the post to be saved.

	## Returns
	out : None
		Returns `None`.
	'''

	print(post_id)

	URL = f"https://yande.re/post/show/{post_id}"
	r = s.get(URL) # send a request using the already opened session, `s`

	soup = BeautifulSoup(r.content, parser)

	if soup.find("title").text == "Not Found (404)": # if the page is not found
		print("No page found.\n")
		didNotSave(post_id, NO_PAGE_FOUND)
		return

	stats_div = soup.find("div", attrs={"id": "stats"})

	while stats_div == None: # while the statistics of the post are not found
		pass

	stats = stats_div.findAll("li") # get all the statistics as a list

	# search for the rating statistic
	rating = None
	for stat in stats:
		try:
			if stat.text[:6] == "Rating":
				rating = stat.text[8:].strip()
				break
		except:
			pass
	if rating == None: # if the rating is not found
		print("No rating found.")
		didNotSave(post_id, NO_RATING_FOUND)
		return
	print(rating)

	general_tags = ';'.join([tag_elem.find_all("a")[1].text for tag_elem in soup.find_all("li", attrs={"class": "tag-type-general"})]) # get the general tags fo the post
	print(general_tags, '\n')

	img = soup.find("img", attrs={"id": "image"}) # sample image
	if img == None: # if the post was deleted
		print("No image found.\n")
		didNotSave(post_id, NO_IMAGE_FOUND)
		return

	img_lnk = img["src"] # get the link of the sample image

	img_format = img_lnk.split('.')[-1]
	if img_format == "gif": # don't save GIF's
		print(".gif file found.")
		didNotSave(post_id, GIF_FILE_FOUND)
		return
	
	# resize the image, and save it in the images folder, as [post id].jpg
	im = Image.open(BytesIO(s.get(img_lnk).content))
	resized_im = im.resize((width, height))
	resized_im.save(f".\\images\\{post_id}.jpg")
	resized_im.close()
	im.close()

	hash_code = img_lnk.split('/')[4] # get the hash code of the post to save it later (for any future reconstruction of the post's URL)

	# if all the data was found successfully, then add an entry into the .csv file
	with file_lock_1: # multiple workers should not try to write to the file simultaneously
		with open(output_csv, 'a', newline='') as fp:
			w = csv.DictWriter(fp, ["post id", "hash", "rating", "tags"])
			w.writerow({"post id": post_id, "hash": hash_code, "rating": rating, "tags": general_tags})

def didNotSave(post_id: int, reason: int) -> None:
	'''
	If the post is not saved, then update the .csv file with the reason.

	1: no page found.

	2: no image found.

	3: .gif file found.

	4: no rating found.

	## Parameters
	post_id : int
		The post id of the post which wasn't saved.
	reason : int
		The code for the reason for not saving the post.

	## Returns
	out : None
		Returns `None`.
	'''

	with file_lock_2: # multiple workers should not try to write to the file simultaneously
		with open(no_output_csv, 'a', newline='') as fp:
			w = csv.DictWriter(fp, ["post id", "reason"])
			w.writerow({"post id": post_id, "reason": reason})

def findErrors() -> list[int]:
	'''
	Find the posts which have been missed (perhaps due to a failed request).

	## Returns
	errors : list[int]
		Returns the post id's of the posts (as a list of integers) which have not been fully processed.

	## Note
	Duplicate entries are not accounted for, and may disrupt the functionality.
	'''

	entries = getCol(output_csv, 0, True, int) + getCol(no_output_csv, 0, True, int) # get all the post id's
	sorted_entries = sorted(entries) # sort the post id's in ascending order

	with open(cntr_txt, 'r') as fp:
		from_id = int(fp.readline().strip()) # last entry + 1
	first_entry = 1
	offset = 0
	errors = []

	for ind, entry in enumerate(sorted_entries):
		while first_entry + ind + offset < entry:
			print(first_entry + ind + offset)
			errors.append(first_entry + ind + offset)
			offset += 1

	errors += list(range(entry + 1, from_id)) # check the final few post id's

	print(errors, len(errors), '\n')

	return errors

	# # an attempt at obtaining the errors in linear time (if the entries are sorted in ascending order of the post id's) (the following implementation does not work)
	# errors = []

	# fp_1 = open(output_csv, 'r')
	# fp_2 = open(no_output_csv, 'r')

	# reader_1 = csv.reader(fp_1)
	# reader_2 = csv.reader(fp_2)

	# next(reader_1)
	# next(reader_2)

	# post_id_1 = int(next(reader_1)[0])
	# post_id_2 = int(next(reader_2)[0])

	# prev = min(post_id_1, post_id_2)

	# while True:
	# 	if post_id_1 < post_id_2:
	# 		try:
	# 			post_id_1 = int(next(reader_1)[0])
	# 		except:
	# 			break
	# 		curr = min(post_id_1, post_id_2)
	# 		if curr - 1 == prev:
	# 			prev = curr
	# 		elif curr - 1 > prev:
	# 			errors += [post_id for post_id in range(prev + 1, curr)]
	# 			prev = curr
	# 		elif curr == prev:
	# 			print(f"Double stored {post_id_1}.")
	# 			fp_1.close()
	# 			fp_2.close()
	# 			time.sleep(3)
	# 			exit()
	# 		else:
	# 			print(f"Stored data is unsorted around {curr}.")
	# 			time.sleep(3)
	# 			break
	# 	elif post_id_1 > post_id_2:
	# 		try:
	# 			post_id_2 = int(next(reader_2)[0])
	# 		except:
	# 			break
	# 		curr = min(post_id_1, post_id_2)
	# 		if curr - 1 == prev:
	# 			prev = curr
	# 		elif curr - 1 > prev:
	# 			errors += [post_id for post_id in range(prev + 1, curr)]
	# 			prev = curr
	# 		elif curr == prev:
	# 			print(f"Double skipped {post_id_2}.")
	# 			fp_1.close()
	# 			fp_2.close()
	# 			time.sleep(3)
	# 			exit()
	# 		else:
	# 			print(f"Skipped data is unsorted around {curr}.")
	# 			time.sleep(3)
	# 			break
	# 	else:
	# 		print(f"A lot went wrong with {post_id_1}.")
	# 		fp_1.close()
	# 		fp_2.close()
	# 		time.sleep(3)
	# 		exit()
	# 	print(curr)

	# fp_1.close()
	# fp_2.close()

	# return errors

def fixErrors(errors: list[int], max_workers: int) -> None:
	'''
	Tries to save the given posts.

	## Parameters
	errors : list[int]
		The post id's of the posts which are to be saved.
	max_workers : int
		The maximum number of workers running concurrently.

	## Returns
	out : None
		Returns `None`.
	'''

	# concurrently process the posts
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
		executor.map(concurrentMain, errors)

	# assume that all of the given posts been saved, and update accordingly
	with open(coms_txt, 'w') as fp:
		fp.write('1')

def getCol(csv_file: str, col: int, headings_present: bool, dtype: type = str) -> list:
	'''
	Extracts a particular column of the entries and return them in the specified format.

	## Parameters
	csv_file : str
		The path to the csv file.
	col : int
		The column number to be extracted.
	headings_present : bool
		If `True`, then the first row will be skipped (as it would be assumed that it contains the headings). Else, the first row would not be skipped.
	dtype : type, optional
		Converts the entries into the specified data type (`str` by default).

	## Returns
	entries : list
		Returns the list of the entries in the specified column and format.
	'''

	entries = []
	with open(csv_file, 'r') as fp:
		reader = csv.reader(fp)
		if headings_present:
			next(reader)
		while True:
			try:
				entries.append(dtype(next(reader)[col]))
			except:
				break
	return entries

# get the command-line arguments, which are of the form [file executed, number of posts to processed, maximum number of workers running concurrently, width of the resized image, height of the resized image, Beautiful Soup parser]
n, max_workers, width, height = [int(arg) for arg in sys.argv[1:5]]
parser = sys.argv[5]

s = requests.Session() # start a new session for all the workers to use

file_lock_1, file_lock_2 = threading.Lock(), threading.Lock() # file locks to prevent multiple workers from writing to the same file simultaneously

NO_PAGE_FOUND, NO_IMAGE_FOUND, GIF_FILE_FOUND, NO_RATING_FOUND = 1, 2, 3, 4 # reasons for not saving a post

# paths to the necessary directory and files
images_dir = ".\\images" # directory for the images
coms_txt = ".\\communication.txt" # for communication between this program and the Windows Powershell program exists ("0" iff there was an error in processing the previous posts, and "1" iff the next posts can be processed)
cntr_txt = ".\\next_post_id.txt" # to keep track of the post id of the next post to be processed
output_csv = ".\\data.csv" # stores the post id, hash code, rating and general tags
no_output_csv = ".\\did_not_save.csv" # stores the post id and reason for a post not being saved

# initialise the directory if it does not exist
if not os.path.isdir(images_dir):
	os.mkdir(images_dir, 711)

if os.path.isfile(coms_txt): # checks if the file exists
	with open(coms_txt, 'r') as fp:
		if fp.readline().strip() == "0": # if all the previous posts have not been processed
			fixErrors(findErrors(), max_workers) # try to find those posts and save them
			exit()
else: # if the file does not exist...
	# then initialise it, assuming that the next posts can be processed
	with open(coms_txt, 'w') as fp:
		fp.write("1")

if os.path.isfile(cntr_txt): # checks if the file exists
	with open(cntr_txt, 'r') as fp:
		from_id = int(fp.readline().strip()) # get the post id of the next post to be processed
else: # if the file does not exist...
	# then initialise it with "1", as that is the first post id to be processed
	from_id = 1
	with open(cntr_txt, 'w') as fp:
		fp.write("1")

# initialise the file if it does not exist
if not os.path.isfile(output_csv):
	with open(output_csv, 'w', newline='') as fp:
		w = csv.DictWriter(fp, ["post id", "hash", "rating", "tags"])
		w.writeheader()

# initialise the file if it does not exist
if not os.path.isfile(no_output_csv):
	with open(no_output_csv, 'w', newline='') as fp:
		w = csv.DictWriter(fp, ["post id", "reason"])
		w.writeheader()

# concurrently process the posts
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
	executor.map(concurrentMain, list(range(from_id, from_id + n)))

s.close() # close the session

# update the next post id to be processed
with open(cntr_txt, 'w') as fp:
	fp.write(str(from_id + n))

print("End of Python program.")
