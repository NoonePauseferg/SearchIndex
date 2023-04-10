Hi, im Vorobev Vadim and this is my search index project

to start:
    - run index.sh
    - run make_dict.sh, select decoder
    - run query.sh, write query, select output

Compressing:
    I have implemented two compressing algorithms :
        - varbyte
        - simple9

    on small data(only docs) this algos shows compression in:
        varbyte : 3.9 / (2.5 + 440 / 1024) = 1.3312
        simple9 : 3.9 / (2.6 + 440 / 1024) = 1.2872

    but on big data(docs with word tf in each doc):
        varbyte : 6.2 / (3.6 + 864 / 1024) = 1.3952
        simple9 : 6.2 / (3.2 + 863 / 1024) = 1.5336

    these results can be justified by the fact that simple9 is redundant for small data 
    due to granularity, but thanks to this granularity, we can read data faster

Tree:
    I tried to implement q-tree and balansed it as much as I can. I don reall have
    big experience with trees, so I implement it as described in file q-tree.py;

Conclusion:
    a. I learned a lot of new things about search index
    b. Improved my byte skills by implementing compression algos
    c. Improved my skills in trees by implementing q-tree and trying to balance it
