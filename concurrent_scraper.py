from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import concurrent.futures, csv, os, requests, sys, threading, time

def concurrentMain(post_id: int) -> None:
	URL = f"https://yande.re/post/show/{post_id}"
	r = s.get(URL)

	soup = BeautifulSoup(r.content, "html5lib")
	
	if soup.find("title").text == "Not Found (404)":
		print("No page found.\n")
		didNotSave(post_id, NO_PAGE_FOUND)
		return

	img = soup.find("img", attrs={"id": "image"})
	if img == None:
		print("No image found.\n")
		didNotSave(post_id, NO_IMAGE_FOUND)
		return

	img_lnk = img["src"]

	img_format = img_lnk.split('.')[-1]
	if img_format == "gif":
		print(".gif file found.")
		didNotSave(post_id, GIF_FILE_FOUND)
		return
	Image.open(BytesIO(s.get(img_lnk).content)).resize((128, 128)).save(f".\\images\\{post_id}.jpg")

	hash_code = img_lnk.split('/')[4]

	stats_div = soup.find("div", attrs={"id": "stats"})

	if stats_div == None:
		didNotSave(post_id, NO_STATS_DIV_FOUND)
		return

	stats = stats_div.findAll("li")

	print(post_id)

	rating = None
	for stat in stats:
		try:
			if stat.text[:6] == "Rating":
				rating = stat.text[8:].strip()
				break
		except:
			pass
	if rating == None:
		didNotSave(post_id, NO_RATING_FOUND)
		return
	print(rating)

	general_tags = ';'.join([tag_elem.find_all("a")[1].text for tag_elem in soup.find_all("li", attrs={"class": "tag-type-general"})])
	print(general_tags, '\n')

	with file_lock_1:
		with open(output_csv, 'a', newline='') as fp:
			w = csv.DictWriter(fp, ["post id", "hash", "rating", "tags"])
			w.writerow({"post id": post_id, "hash": hash_code, "rating": rating, "tags": general_tags})

def didNotSave(post_id: int, reason: int) -> None:
	with file_lock_2:
		with open(no_output_csv, 'a', newline='') as fp:
			w = csv.DictWriter(fp, ["post id", "reason"])
			w.writerow({"post id": post_id, "reason": all_reasons[reason]})

def findErrors() -> list[int]:
	'''
	Assumes that the .csv files may not be sorted in ascending order of the post id's.
	'''

	entries = getCol(output_csv, 0, True, int) + getCol(no_output_csv, 0, True, int)
	sorted_entries = sorted(entries)

	with open(cntr_txt, 'r') as fp:
		from_id = int(fp.readline().strip())
	first_entry = 1
	offset = 0
	errors = []

	for ind, entry in enumerate(sorted_entries):
		while first_entry + ind + offset < entry:
			print(first_entry + ind + offset)
			errors.append(first_entry + ind + offset)
			offset += 1

	errors += [e for e in range(entry + 1, from_id)]

	print(errors, len(errors))

	return errors

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
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
		executor.map(concurrentMain, errors)

	with open(coms_txt, 'w') as fp:
		fp.write('1')

def getCol(csv_file: str, col: int, headings_present: bool, dtype: type = str) -> list:
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

s = requests.Session()

file_lock_1, file_lock_2 = threading.Lock(), threading.Lock()

NO_PAGE_FOUND, NO_IMAGE_FOUND, NO_STATS_DIV_FOUND, NO_RATING_FOUND, GIF_FILE_FOUND = 1, 2, 3, 4, 5
all_reasons = {NO_PAGE_FOUND: "no page found.",
			   NO_IMAGE_FOUND: "no image found.",
			   NO_STATS_DIV_FOUND: "no stats div found.",
			   NO_RATING_FOUND: "no rating found.",
			   GIF_FILE_FOUND: ".gif file found."}

coms_txt = ".\\communication.txt"
cntr_txt = ".\\id_counter.txt"
output_csv = ".\\data.csv"
no_output_csv = ".\\did_not_save.csv"

n, max_workers = [int(arg) for arg in (sys.argv[1:])]

if os.path.isfile(coms_txt):
	with open(coms_txt, 'r') as fp:
		if fp.readline().strip() == '0':
			fixErrors(findErrors(), max_workers)
			exit()
else:
	with open(coms_txt, 'w') as fp:
		fp.write('1')

if os.path.isfile(cntr_txt):
	with open(cntr_txt, 'r') as fp:
		from_id = int(fp.readline().strip())
else:
	from_id = 1
	with open(cntr_txt, 'w') as fp:
		fp.write("1")

if not os.path.isfile(output_csv):
	with open(output_csv, 'w', newline='') as fp:
		w = csv.DictWriter(fp, ["post id", "hash", "rating", "tags"])
		w.writeheader()

if not os.path.isfile(no_output_csv):
	with open(no_output_csv, 'w', newline='') as fp:
		w = csv.DictWriter(fp, ["post id", "reason"])
		w.writeheader()

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
	executor.map(concurrentMain, [post_id for post_id in range(from_id, from_id + n)])

with open(cntr_txt, 'w') as fp:
	fp.write(f"{from_id + n}\n")
