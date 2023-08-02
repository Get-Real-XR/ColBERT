(make sure you have poetry installed)

```
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

poetry install
pip install torch torchvision torchaudio
poetry shell
```

move index folder into the default index root, /data/ColBERT/experiments/default/indexes/
and set .env accordingly, for instance, with
/data/ColBERT/experiments/default/indexes/wikipedia/07312023/<* index files>
we have .env as
```
INDEX_ROOT="wikipedia"
INDEX_NAME="07312023"
PORT="8893"
```
Now we can run
```
python server.py <collection path to csv>
```
