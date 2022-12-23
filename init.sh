
if [ ! -d "venv" ]; then
    echo --------------------
    echo Creating virtualenv
    echo --------------------
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt 

export FLASK_APP=main.py
if [ ! -d "migrations" ]; then
    echo --------------------
    echo INIT THE migrations folder
    echo --------------------
    alembic init migrations
    export FLASK_APP=main.py;
fi
echo --------------------
echo Generating initial datas
echo --------------------
flask initial-data