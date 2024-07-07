$n = $args[0] # total number of images to be processed
$max_workers = $args[1] # maximum number of workers
$width = $args[2] # width of the resized image
$height = $args[3] # height of the resized image
$parser = $args[4] # Beautiful Soup parser (such as lxml, lxml-xml, html.parser or html5lib)

$sw = [Diagnostics.Stopwatch]::StartNew() # start a stopwatch

Start-Process -FilePath "py" -ArgumentList ".\concurrent_scraper.py $n $max_workers $width $height $parser" -Wait # run the python program and wait for it to terminate

# get the counts
$saved = (Get-Content ".\data.csv").Length - 1 # stores the post id, hash code, rating and general tags
$not_saved = (Get-Content ".\did_not_save.csv").Length - 1 # stores the post id and reason for a post not being saved
$nxt_post_id = Get-Content ".\next_post_id.txt" # keeps track of the post id of the next post to be processed

$sw.Elapsed # print the time taken
$sw.Stop() # stop the stopwatch

Write-Output "Total saved: $saved."
Write-Output "Total not saved: $not_saved."
Write-Output "Total processed: $($saved + $not_saved)."
Write-Output "Next post id: $nxt_post_id."

# if the numbers don't match (perhaps due to a post not being processed), then update the file accordingly
if ($saved + $not_saved -ne $nxt_post_id - 1) { # if number of posts saved + number of posts not saved != number of posts processed == nxt_post_id - 1
	Write-Output "Something went wrong."
	Set-Content -Path ".\communication.txt" -Value "0" # for communication between this program and the python program ("0" iff there was an error in processing the previous posts, and "1" iff the next posts can be processed)
}

Write-Output "End of program."
