FROM postgres:15-bookworm
LABEL authors="aeremin"
COPY schema.sql /schema.sql
COPY init-script.sh /docker-entrypoint-initdb.d/init-script.sh
COPY ./postgresql.conf /postgresql.conf
COPY ./pg_hba.conf /pg_hba.conf
RUN chmod +x /docker-entrypoint-initdb.d/init-script.sh
RUN mkdir -p /var/pg_data/archive/
RUN chown -R postgres:postgres /var/pg_data/
EXPOSE 5432
CMD ["postgres"]
