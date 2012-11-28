#!/bin/bash

# do we have a valid date
decdate=$(date --date "$1" +%d.%m.%Y) ;
dayOfMonth=$(date --date "$1" +%A) ; 

if [ "$dayOfMonth" == "Saturday" ] ; then
    exit 1 ;
fi

if [ "$dayOfMonth" == "Sunday" ] ; then
    exit 1 ;
fi

if [ ! -n $(echo "$decdate" | grep "invalid date") ] ; then
    exit 1 ;
fi

#get the URL
wgdate=$(date --date "$1" +%d-%b-%Y) ;
nprApiDate=$(date --date="$1" +%Y-%m-%d) ;
nprURL="http://api.npr.org/query?id=13&date="$nprApiDate"&dateType=story&output=NPRML&apiKey=MDA2OTgzNTcwMDEyOTc1NDg4NTNmMWI5Mg001" ;

# now make sure that the path has included within it location for metawrite

# now parse out the data on the URL -- its year, its artist, its
# comment, its title (track number not included). Then delete the
# source file
year=$(date --date "$1" +%Y) ;
titleDate=$(date --date "$1" "+%A, %B %d, %Y" ) ;
artist="Terry Gross" ;
comment="more info at : Fresh Air from WHYY and NPR Web site" ;
title="$titleDate" ;

touch freshair$wgdate.txt ;
rm -f freshair$wgdate.txt ;
curl "$nprURL" | grep \<title\> | grep CDATA | grep -v "Fresh Air from WHYY" | sed 's/.*CDATA\[//g' | sed 's/\]\]>.*//g' > freshair$wgdate.txt ;

for num in $(seq 1 $(cat freshair$wgdate.txt | wc -l )) ; do
    subtitle=$(cat freshair$wgdate.txt | head -n $num | tail -n 1) ;
    title=$(echo "$title""; "$num") ""$subtitle" ) ;
done
album="Fresh Air from WHYY and NPR: "$year ;
title=$(echo $title".") ;
rm -f freshair$wgdate.txt ;

# now download the URL files using NPR API, using mp3...
if [ $year -ge 2003 ] ; then
    nprApiDate=$(date --date="$1" +%Y-%m-%d) ;
    nprMp3Date=$(date --date="$1" +%Y%m%d) ;
    
    touch freshair$wgdate.txt ;
    rm -f freshair$wgdate.txt ;
    for file in $(curl "$nprURL" | grep m3u | sed 's/.*http/http/g' | \
	grep http | sed 's/\.m3u\?.*/\.m3u/g' ) ; do
	curl "$file" | grep http | sed 's/\.mp3<.*/\.mp3/g' >> freshair"$wgdate".txt ;
    done
    
    num=1
    for file in $(cat freshair$wgdate.txt | grep $nprMp3Date | sort | uniq ) ; do
	wget -c "$file" -O freshair."$decdate"."$num".mp3 ;
	num=$(( $num + 1)); 
    done
    rm -f freshair$wgdate.txt ;

# now concatenate mp3 files into one wav file, then delete mp3 files...
    (for file in freshair."$decdate".*.mp3 ; do sox $file -t cdr - ; done) | \
	sox -t cdr - freshair$wgdate.wav && rm -f freshair."$decdate".*.mp3 ;
else
# now download the URL files into wav files
    num=1
    for mmsurl in $(cat freshair."$decdate".asx | grep "mms://" | \
	sed 's/.*mms/mms/g' | sed 's/\.wma.*/\.wma/g') ; do
	echo "$mmsurl" ;
	mplayer -ao pcm:file=freshair."$decdate"."$num".wav \
	    -channels 2 -af resample=44100:0:0 $mmsurl ;
	num=$(( $num + 1)) ;
    done

# concatenate the wav file into one wav file, then convert into m4a,
# then add tagging information
    (for file in freshair."$decdate".*.wav ; do sox $file -t cdr - ; done) | \
	sox -t cdr - freshair$wgdate.wav && rm -f freshair."$decdate".*.wav ;
fi

# now convert the files into m4a
/usr/bin/avconv -y -i freshair$wgdate.wav -ar 44100 -ac 2 -aq 400 \
    -acodec libfaac NPR.FreshAir."$decdate".m4a ;

/usr/local/bin/metawrite -t "$title" -a "$artist" -A "$album" -y "$year" -c "$comment" \
    NPR.FreshAir."$decdate".m4a ;
/usr/bin/mp4tags -P /mnt/media/freshair/npr_freshair_image_300.png \
    NPR.FreshAir."$decdate".m4a ;
rm -f freshair$wgdate.wav freshair."$decdate".asx ;

if [ $# -ge 2 ] ; then
    /usr/bin/mp4tags -t "$2" NPR.FreshAir."$decdate".m4a ;
fi

if [ $# -ge 3 ] ; then
    /usr/bin/mp4tags -t "$2" -T "$3" NPR.FreshAir."$decdate".m4a ; 
fi
