#!/bin/zsh

echo "Press [ENTER] to start the stopwatch"
read

# Record the start time
start_time=$(date +%s)

echo "Stopwatch started. Press [ENTER] to stop."

# Loop to update the elapsed time
while true; do
  # Calculate elapsed time
  elapsed_time=$(( $(date +%s) - start_time ))
  
  # Convert elapsed time to hh:mm:ss format
  printf "\rElapsed time: %02d:%02d:%02d" $((elapsed_time / 3600)) $(((elapsed_time % 3600) / 60)) $((elapsed_time % 60))
  
  # Sleep for 1 second
  sleep 1
done &

# Wait for user to stop the stopwatch
read

# Kill the background process
kill $!

# Print the final elapsed time
elapsed_time=$(( $(date +%s) - start_time ))
printf "\nFinal elapsed time: %02d:%02d:%02d\n" $((elapsed_time / 3600)) $(((elapsed_time % 3600) / 60)) $((elapsed_time % 60))

