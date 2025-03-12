@echo off
setlocal

:: Prompt for subreddit
set /p subreddit="Enter subreddit (default: askreddit): "
if "%subreddit%"=="" set subreddit=askreddit

:: Prompt for timeframe
set /p timeframe="Enter timeframe (default: day): "
if "%timeframe%"=="" set timeframe=day

:: Prompt for post count
set /p post_count="Enter number of posts to process (default: 1): "
if "%post_count%"=="" set post_count=1

:: Run the Python script with the provided options
python src/silent_video_creator.py --subreddit %subreddit% --timeframe %timeframe% --post_count %post_count%

endlocal
pause