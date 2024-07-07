# [yande.re](https://yande.re/post) Scraper and CNN
A fast web scraper (**350+ images per minute**) using Beautiful Soup, concurrency and Windows PowerShell for [yande.re](https://yande.re/post). And a CNN which classifies the images based on their rating (**75%** accuracy).

## Installation and Setup
1. Download the repository.

2. Make sure that the [requirements](requirements.md) are met.

## Usage

### 1. Web Scraper
Run the [`runner.ps1`](runner.ps1) file, on Windows PowerShell, with the following command-line arguments.
- Number of posts to _process_ (_process_ meaning to save the post (if all the data is available) or not save a post (due to various reasons))
- Maximum number of workers (during concurrency)
- Width of the resized image to be saved
- Height of the resized image to be saved
- Beautiful Soup parser

For example, running `.\runner.ps1 50 10 128 128 lxml` processes the first 50 posts (which are not already processed) concurrently, with a maximum of 10 workers. Beautiful Soup uses the "lxml" parser to find the required data from the page, and the image is resized to 128x128 and saved in the "images" folder.

The program can, on average, save more than **350 images per minute**.

### 2. CNN
See [the Python notebook](cnn.ipynb), which trains a CNN using [TensorFlow](https://www.tensorflow.org/). Both the training and test accuracies of the model are **75%**.

## Additional Resources
The scraped data of the first 131k posts can be found [here](scraped%20data).

## Note
- Running `.\reset.ps1` will delete
	- images
	- data.csv
	- did_not_save.csv
	- communication.txt
	- next_post_id.txt.
