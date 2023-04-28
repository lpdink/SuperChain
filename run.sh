# python group_server.py & 
python consensus_server.py &
sleep 2
python consensus_client.py
killall python
