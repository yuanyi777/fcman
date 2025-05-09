SAVEIFS=$IFS
IFS=$'\n'

fileList=$(ls ~/.sbt/*.zip)
gameList=$(basename -s .zip $fileList)

for gameName in $gameList
do
    mv ~/.sbt/"$gameName.zip" .
    unzip "$gameName.zip"
    rm "$gameName.zip"

    fileName=$(ls "$gameName"*)

    python3 fccrc.py "$fileName"
done

mv *.nes ../fc/games 2>/dev/null
mv *.fds ../fc/games 2>/dev/null

IFS=$SAVEIFS
