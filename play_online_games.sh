i=$1

if [ $# -eq 0 ]; then
    i=0
fi

while true; do
    echo "Running $i"
    python3 online_game_player.py > results/$i.txt 2> errors/$i.txt
    i=$[$i+1]
    sleep 1
done
