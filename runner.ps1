$n = $args[0]
$threads = $args[1]

$sw = [Diagnostics.Stopwatch]::StartNew()

Start-Process -FilePath "py" -ArgumentList ".\concurrent_scraper.py $n $threads" -Wait

$saved = (Get-Content ".\data.csv").Length - 1
$not_saved = (Get-Content ".\did_not_save.csv").Length - 1
$nxt_post_id = Get-Content ".\id_counter.txt"

$sw.Elapsed

Write-Output "Total saved: $saved."
Write-Output "Total not saved: $not_saved."
Write-Output "Total attempted: $($saved + $not_saved)."
Write-Output "Next post id: $nxt_post_id."

if ($saved + $not_saved -ne $nxt_post_id - 1) {
	Write-Output "Something went wrong."
	Write-Output 0 > ".\communication.txt"
}

$sw.Stop()
