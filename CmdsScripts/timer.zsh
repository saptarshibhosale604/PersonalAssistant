#!/bin/zsh

# e.g 
# timer.sh 1 sec
# timer.sh 2 min
# timer.sh 2        # sec default

# Check if the first argument is provided
if [[ -z "$1" ]]; then
  echo "Usage: $0 <countdown_time> [sec|min]"
  exit 1
fi

# Set the countdown time based on the first argument
countdown_time=$1

# Check the second argument for time unit
if [[ "$2" == "min" ]]; then
  countdown_time=$((countdown_time * 60))  # Convert minutes to seconds
elif [[ "$2" != "sec" && -n "$2" ]]; then
  echo "Invalid time unit. Use 'sec' for seconds or 'min' for minutes."
  exit 1
fi

# Use a Zsh-style countdown loop
for ((i = countdown_time; i >= 0; i--)); do
  # Calculate minutes and seconds
  minutes=$((i / 60))
  seconds=$((i % 60))
  
  # Print in mm:ss format
  printf "\rCountdown: %02d:%02d" "$minutes" "$seconds"
  sleep 1
done

printf "\rCountdown: Time's up!      \n"  # Print the final message

