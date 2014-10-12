first=0
declare -i sum
sum=0
declare -i total
total=0
min=1000
max=0
for dir in `find . -type d`
do
    if [ $first -eq 0 ]; then
      first=1
      continue
    fi
    echo $dir
    numfiles=`ls -1 $dir | wc -l`
    declare -i numfiles
    numfiles=$numfiles-2
    sum=$sum+$numfiles
    total=$total+1

    if [ $numfiles -gt $max ]; then
      max=$numfiles
    fi
    if [ $numfiles -lt $min ]; then
      min=$numfiles
    fi
done
declare -i avg
avg=$sum/$total
echo "Average: $avg"
echo "Min: $min"
echo "Max: $max"
