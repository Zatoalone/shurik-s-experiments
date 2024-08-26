--Version 6
DROP TABLE IF EXISTS emails;
DROP TABLE IF EXISTS phones;

CREATE USER mr_bot WITH PASSWORD '';
CREATE USER repl_user REPLICATION PASSWORD '';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE emails (ID SERIAL PRIMARY KEY, email VARCHAR (100) NOT NULL);
CREATE TABLE phone_numbers (ID SERIAL PRIMARY KEY, number VARCHAR (100) NOT NULL);

INSERT INTO emails(email) VALUES ('test1@example.ru');
INSERT INTO emails(email) VALUES ('test_2@example.ru');
INSERT INTO emails(email) VALUES ('test@yandex.ru');
INSERT INTO emails(email) VALUES ('masha23@example.com');

INSERT INTO phone_numbers(number) VALUES ('+7 (999) 888 77 66');
INSERT INTO phone_numbers(number) VALUES ('89998887766');
INSERT INTO phone_numbers(number) VALUES ('8-999-888-77-66');
INSERT INTO phone_numbers(number) VALUES ('+79998877665');


GRANT SELECT,INSERT ON TABLE emails TO mr_bot;
GRANT USAGE,UPDATE ON SEQUENCE emails_id_seq TO mr_bot;
GRANT SELECT,INSERT ON TABLE phone_numbers TO mr_bot;
GRANT USAGE,UPDATE ON SEQUENCE phone_numbers_id_seq TO mr_bot;
