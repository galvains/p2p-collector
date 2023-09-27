--CREATE DATABASE collector;
CREATE TABLE exchanges (
    id smallserial primary key not null,
    name varchar(10)
);

CREATE TABLE tickets (
    nick_name varchar(50) not null,
    price numeric not null,
    orders numeric not null,
    available numeric not null,
    max_limit numeric not null,
    min_limit numeric not null,
    rate numeric not null,
    pay_methods text not null,
    currency varchar(5) not null,
    coin varchar(5) not null,
    trade_type boolean not null,
    link text not null,
    time_create timestamp not null,
    exchange_id int references exchanges (id) not null
);

