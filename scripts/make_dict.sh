echo [make_dict.sh] : choose decoder {varbyte, simple9}
read decoder
echo $decoder > ../code/user_data/decoder.txt
python3 ../code/make_dict.py $decoder