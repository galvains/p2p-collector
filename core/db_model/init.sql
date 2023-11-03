CREATE TABLE app_exchangetable (
    id smallserial primary key not null,
    name varchar(10)
);

INSERT INTO app_exchangetable(id, name) VALUES (1, 'Binance');
INSERT INTO app_exchangetable(id, name) VALUES (2, 'Bybit');
INSERT INTO app_exchangetable(id, name) VALUES (3, 'Paxful');
INSERT INTO app_exchangetable(id, name) VALUES (4, 'OKX');

CREATE TABLE app_ticketstable (
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
    exchange_id int references app_exchangetable (id) not null
);
