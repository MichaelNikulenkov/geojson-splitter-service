@ECHO OFF
cd ../
echo "Client started"
python code/client.py resources/map.geojson 4
PAUSE