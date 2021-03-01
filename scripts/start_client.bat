@ECHO OFF
cd ../
echo "Client started"
REM ARGUMENTS: MAP FILE PATH, NUMBER OF PARTS
python code/client.py resources/map.geojson 4
PAUSE