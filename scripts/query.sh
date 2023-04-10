echo [query.sh] : write query
read query
echo [query.sh] : show tree? {0, 1}
read show
echo $query > ../code/user_data/query.txt
python3 ../code/q-tree.py $show