для запуска - streamlit run src/main.py  

для подключения к бд - docker exec -it postgres_container psql -U habrpguser -d habrdb

копирование данных в - docker cp /Users/admin/Desktop/MAI/Third/base/курсач/service_for_reservation_tennis_courts/migrations/ddl.sql postgres_container:/tmp/ddl.sql

неистово все сносим - DO $$ DECLARE
       r RECORD;
   BEGIN
       FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
           EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
       END LOOP;
   END $$;