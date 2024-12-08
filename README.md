# sample_course_work

pip install -r .\requirements.txt

выполнить ddl.sql и dml.sql

streamlit run main.py

Если вы в vs code, то

launch.json
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python:Streamlit",
            "type": "debugpy",
            "request": "launch",
            "module": "streamlit",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "args": [
                "run",
                "${file}",
                "--server.port",
                "2000",
                "--server.runOnSave=false"
            ]
        }
    ]
}
```
