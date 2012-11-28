#!/bin/bash

dayofweek=$(date --date="$1" +%A) ;

if [ "$dayofweek" != "Saturday" ] ; then
    echo "Error, day of week," "$dayofweek" "!= Saturday" ;
    exit 1 ;
fi

nprDateForm=$(date --date="$1" +%Y%m%d) ;
nprApiForm=$(date --date="$1" +%Y-%m-%d) ;
nprYear=$(date --date="$1" +%Y) ;
decdate=$(date --date="$1" +%d.%m.%Y) ;

# echo "$nprDateForm", "$dayofweek", "$nprApiForm" ;

# now start to download this file
waitwaitURL="http://api.npr.org/query?id=35&date="$nprApiForm"&dateType=story&output=NPRML&apiKey=MDA2OTgzNTcwMDEyOTc1NDg4NTNmMWI5Mg001" ;
curl "$waitwaitURL" > waitwaitnpr."$nprDateForm".txt ;

# now find m3u URLs
touch foo_"$nprDateForm".txt ;
rm -f foo_"$nprDateForm".txt ;
for file in $(cat waitwaitnpr."$nprDateForm".txt | grep m3u | sed 's/.*http/http/g' | grep http | sed 's/\.m3u\?.*/\.m3u/g') ; do
    curl "$file" | grep http | grep "$nprDateForm" | sed 's/\.mp3<.*/\.mp3/g'>> foo_"$nprDateForm".txt ;
done

nicedate=$(date --date="$1" +"%A, %b %d, %Y") ;
title="Wait Wait...Don't Tell Me! ""$nicedate" ;

touch title.waitwait."$nprDateForm".txt ;
rm -f title.waitwait."$nprDateForm".txt ;
cat waitwaitnpr."$nprDateForm".txt | grep \<title\> | \
    grep CDATA | grep -v "Wait Wait...Don't Tell Me" | \
    sed 's/.*CDATA\[//g' | sed 's/\]\].*//g' > \
    title.waitwait."$nprDateForm".txt ;

for num in $(seq 1 $(cat title.waitwait."$nprDateForm".txt | wc -l )) ; do
    subtitle=$(cat title.waitwait."$nprDateForm".txt | head -n $num | \
	tail -n 1 ) ;
    title="$title""; "$num") ""$subtitle" ;
done
title="$title". ;

rm -f title.waitwait."$nprDateForm".txt ;

# download mp3s corresponding to specific date
for file in $(cat foo_"$nprDateForm".txt | sort | uniq ) ; do
    wget -c "$file" ;
done

rm -f foo_"$nprDateForm".txt ;
rm -f waitwaitnpr."$nprDateForm".txt ;

album="Wait Wait...Don't Tell Me! ""$nprYear" ;

# now join into a single wav file using sox, from mp3 file
(for file in "$nprDateForm"_waitwait_*.mp3 ; do sox "$file" -t cdr - ; done ) | \
    sox -t cdr - waitwait_"$nprDateForm".wav && rm "$nprDateForm"_waitwait_*.mp3 ;

# convert using avconv into a single m4a file
/usr/bin/avconv -y -i waitwait_"$nprDateForm".wav \
    -ar 44100 -ac 2 -aq 400 \
    -acodec libfaac \
    NPR.WaitWait."$decdate".m4a ;
rm -rf waitwait_"$nprDateForm".wav ;

/usr/local/bin/metawrite -t "$title" -a "Carl Kassel And Peter Sagal" \
    -y "$nprYear" \
    -A "$album" NPR.WaitWait."$decdate".m4a ;

if [ $# -eq 2 ] ; then
    /usr/local/bin/metawrite -T "$2" NPR.WaitWait."$decdate".m4a ;
fi