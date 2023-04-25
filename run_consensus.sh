# for batch_size in 2 4 8 16
# do
#     python change_config.py --batch_size=$batch_size --node_nums=8
#     python consensus_server.py > /dev/null &
#     echo -e "\n$batch_size\t" >> tps.log
#     python consensus_client.py
#     killall -9 python
# done

for node_nums in 8 12 16 20 24 28 32
do
    python change_config.py --batch_size=512 --node_nums=$node_nums
    python consensus_server.py > /dev/null &
    echo -e "\n$node_nums\t" >> tps.log
    python consensus_client.py
    killall -9 python
done