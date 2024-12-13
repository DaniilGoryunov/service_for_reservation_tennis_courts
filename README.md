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

для запуска - streamlit run src/main.py  
для подключения к бд - docker exec -it postgres_container psql -U habrpguser -d habrdb
копирование данных в - docker cp /Users/admin/Desktop/MAI/Third/base/курсач/sample_course_work/migrations/ddl.sql postgres_container:/tmp/ddl.sql
неистово все сносим - DO $$ DECLARE
       r RECORD;
   BEGIN
       FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
           EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
       END LOOP;
   END $$;