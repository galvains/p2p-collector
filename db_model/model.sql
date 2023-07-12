-- CREATE DATABASE collection_p2p_database;
CREATE TABLE TicketsTable (
    id bigserial primary key not null,
    nick_name varchar(80) not null,
    price numeric not null,
    orders numeric not null,
    available numeric not null,
    max_limit numeric not null,
    min_limit numeric not null,
    rate numeric not null,
    pay_methods text not null,
    currency varchar(5) not null,
    coin varchar(5) not null,
    trade_type varchar(5) not null,
    link text not null,
    time_create timestamp not null,
    exchange_id int references exchange_table (id) not null
)

