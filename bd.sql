--types
create type type_of_p as enum ('cash', 'card', 'deposit');
create type type_of_c as enum ('income', 'expense');

--drop tables
drop table if exists transactions_b_a cascade;
drop table if exists transactions cascade;
drop table if exists budgets cascade;
drop table if exists categories cascade;
drop table if exists accounts cascade;
drop table if exists users cascade;
drop table if exists logs cascade;

--tables
create table users (
    id serial primary key,
    username varchar(50) not null unique,
    email varchar(100) not null unique,
    password_hash varchar(255) not null,
    created_at timestamp default current_timestamp
);


create table accounts (
    id serial primary key,
    user_id int not null references users(id) on delete cascade,
    name varchar(100) not null,
    type type_of_p not null,
    balance decimal(12, 2) not null default 0.00,
    created_at timestamp default current_timestamp
);


create table categories (
    id serial primary key,
    user_id int not null references users(id) on delete cascade,
    name varchar(100) not null,
    type type_of_c not null,
    unique (user_id, name)
);


create table transactions (
    id serial primary key,
    account_id int not null references accounts(id) on delete restrict,
    category_id int not null references categories(id) on delete restrict,
    amount decimal(12, 2) not null check (amount > 0),
    description text,
    transaction_date date not null default current_date
);


create table transactions_b_a (
    id serial primary key,
    account_id_from int not null references accounts(id),
    account_id_to int not null references accounts(id),
    amount decimal(12, 2) not null check (amount > 0),
    description text,
    transaction_date date not null default current_date
);


create table budgets (
    id serial primary key,
    user_id int not null references users(id) on delete cascade,
    category_id int not null references categories(id) on delete cascade,
    amount_limit decimal(12, 2) not null check (amount_limit > 0),
    period_start date not null,
    period_end date not null check (period_end >= period_start),
    unique (user_id, category_id, period_start)
);

create table logs (
    log_id serial primary key,
    table_name text not null,
    record_id int not null,
    action varchar(10) not null check (action in ('insert', 'UPDATE', 'DELETE')),
    action_date timestamp not null default current_timestamp,
    old_data jsonb,
    new_data jsonb
);

--trigger function
create or replace function log_trg_func()
returns trigger as $$
declare
    pk_name text := TG_ARGV[0];
    record_id int;
begin
    if (TG_OP = 'insert') then
        record_id := (to_jsonb(NEW)->>pk_name)::int;

        insert into logs(table_name, record_id, action, action_date, new_data)
        values (TG_TABLE_NAME, record_id, 'insert', current_timestamp, to_jsonb(NEW));

        return NEW;

    elsif (TG_OP = 'UPDATE') then
        record_id := (to_jsonb(NEW)->>pk_name)::int;

        insert into logs(table_name, record_id, action, action_date, old_data, new_data)
        values (TG_TABLE_NAME, record_id, 'UPDATE', current_timestamp, to_jsonb(OLD), to_jsonb(NEW));

        return NEW;

    elsif (TG_OP = 'DELETE') then
        record_id := (to_jsonb(OLD)->>pk_name)::int;

        insert into logs(table_name, record_id, action, action_date, old_data)
        values (TG_TABLE_NAME, record_id, 'DELETE', current_timestamp, to_jsonb(OLD));

        return OLD;
    end if;

    return null;
end;
$$ language plpgsql;


--triggers
create trigger accounts_audit_trigger
after insert or update or delete on accounts
for each row execute function log_trg_func('id');

create trigger categories_audit_trigger
after insert or update or delete on categories
for each row execute function log_trg_func('id');

create trigger transactions_audit_trigger
after insert or update or delete on transactions
for each row execute function log_trg_func('id');

create trigger budgets_audit_trigger
after insert or update or delete on budgets
for each row execute function log_trg_func('id');

create trigger transactions_b_a_audit_trigger
after insert or update or delete on transactions_b_a
for each row execute function log_trg_func('id');


--roles
drop role if exists db_admin;
drop role if exists app_user;
drop role if exists audit_user;

create role db_admin with login password '123' createdb;
create role app_user with login password '123';
create role audit_user with login password '123';

grant all privileges on database finance_db to db_admin;

grant usage on schema public to app_user, audit_user;
grant usage on type type_of_p to app_user;
grant usage on type type_of_c to app_user;
grant usage, select on all sequences in schema public to app_user;
grant select, insert, update, delete on users to app_user;
grant select, insert, update, delete on accounts to app_user;
grant select, insert, update, delete on categories to app_user;
grant select, insert, update, delete on transactions to app_user;
grant select, insert, update, delete on transactions_b_a to app_user;
grant select, insert, update, delete on budgets to app_user;
grant select on logs to app_user, audit_user;
grant execute on function get_user_total_balance(int) to app_user;
grant execute on function get_category_transactions_sum(int, date, date) to app_user;
grant execute on procedure add_transaction(int, int, decimal, text, date) to app_user;
grant execute on procedure transfer_between_accounts(int, int, decimal, text, date) to app_user;
grant select on user_accounts_summary to app_user, audit_user;
grant select on category_transactions_report to app_user, audit_user;

alter default privileges in schema public grant usage, select on sequences to app_user;
alter default privileges in schema public grant select, insert, update, delete on tables to app_user;
alter default privileges in schema public grant select on tables to audit_user;
alter default privileges in schema public grant usage on types to app_user;


--data

insert into users (username, email, password_hash, created_at) VALUES
('ivanov', 'ivanov@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '2024-01-15 10:30:00'),
('petrov', 'petrov@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '2024-01-20 14:15:00'),
('sidorov', 'sidorov@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '2024-02-01 09:00:00'),
('smirnov', 'smirnov@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '2024-02-10 16:45:00'),
('kozlov', 'kozlov@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '2024-02-15 11:20:00');

insert into accounts (user_id, name, type, balance, created_at) VALUES
(1, 'Основной кошелек', 'cash', 15000.00, '2024-01-15 10:35:00'),
(1, 'Банковская карта', 'card', 50000.00, '2024-01-15 10:36:00'),
(1, 'Депозитный счет', 'deposit', 100000.00, '2024-01-15 10:37:00'),
(2, 'Наличные', 'cash', 8000.00, '2024-01-20 14:20:00'),
(2, 'Кредитная карта', 'card', 25000.00, '2024-01-20 14:21:00'),
(3, 'Кошелек', 'cash', 12000.00, '2024-02-01 09:05:00'),
(3, 'Дебетовая карта', 'card', 35000.00, '2024-02-01 09:06:00'),
(4, 'Наличка', 'cash', 5000.00, '2024-02-10 16:50:00'),
(4, 'Карта зарплатная', 'card', 60000.00, '2024-02-10 16:51:00'),
(5, 'Деньги дома', 'cash', 3000.00, '2024-02-15 11:25:00'),
(5, 'Основная карта', 'card', 40000.00, '2024-02-15 11:26:00'),
(5, 'Накопительный счет', 'deposit', 200000.00, '2024-02-15 11:27:00');

insert into categories (user_id, name, type) VALUES
(1, 'Зарплата', 'income'),
(1, 'Премия', 'income'),
(1, 'Подарки', 'income'),
(1, 'Продукты', 'expense'),
(1, 'Транспорт', 'expense'),
(1, 'Развлечения', 'expense'),
(1, 'Коммунальные услуги', 'expense'),
(2, 'Зарплата', 'income'),
(2, 'Подработка', 'income'),
(2, 'Еда', 'expense'),
(2, 'Одежда', 'expense'),
(2, 'Медицина', 'expense'),
(3, 'Доход от бизнеса', 'income'),
(3, 'Инвестиции', 'income'),
(3, 'Рестораны', 'expense'),
(3, 'Путешествия', 'expense'),
(4, 'Зарплата', 'income'),
(4, 'Аренда', 'expense'),
(4, 'Интернет и связь', 'expense'),
(5, 'Зарплата', 'income'),
(5, 'Дивиденды', 'income'),
(5, 'Образование', 'expense'),
(5, 'Спорт', 'expense');

insert into transactions (account_id, category_id, amount, description, transaction_date) VALUES
(1, 1, 50000.00, 'Зарплата за январь', '2024-01-31'),
(1, 4, 3500.00, 'Покупка продуктов в супермаркете', '2024-02-05'),
(2, 1, 50000.00, 'Зарплата на карту', '2024-01-31'),
(2, 5, 1200.00, 'Проездной на месяц', '2024-02-01'),
(2, 6, 2500.00, 'Поход в кино', '2024-02-10'),
(2, 7, 3500.00, 'Оплата коммунальных услуг', '2024-02-15'),
(4, 8, 45000.00, 'Зарплата', '2024-01-31'),
(4, 10, 2800.00, 'Обед в кафе', '2024-02-08'),
(5, 8, 45000.00, 'Зарплата', '2024-01-31'),
(5, 11, 5000.00, 'Покупка куртки', '2024-02-12'),
(6, 13, 80000.00, 'Доход от продажи', '2024-02-05'),
(6, 15, 4500.00, 'Ужин в ресторане', '2024-02-14'),
(7, 13, 80000.00, 'Доход от бизнеса', '2024-02-05'),
(7, 16, 15000.00, 'Билеты на отпуск', '2024-02-20'),
(8, 17, 55000.00, 'Зарплата', '2024-01-31'),
(8, 18, 20000.00, 'Аренда квартиры', '2024-02-01'),
(9, 17, 55000.00, 'Зарплата', '2024-01-31'),
(9, 19, 1500.00, 'Оплата интернета и мобильной связи', '2024-02-05'),
(10, 20, 60000.00, 'Зарплата', '2024-01-31'),
(10, 21, 5000.00, 'Дивиденды по акциям', '2024-02-10'),
(11, 20, 60000.00, 'Зарплата', '2024-01-31'),
(11, 22, 8000.00, 'Оплата курсов', '2024-02-15'),
(12, 20, 60000.00, 'Зарплата', '2024-01-31'),
(12, 23, 3000.00, 'Абонемент в спортзал', '2024-02-01');

insert into transactions_b_a (account_id_from, account_id_to, amount, description, transaction_date) VALUES
(1, 2, 10000.00, 'Перевод с кошелька на карту', '2024-02-01'),
(2, 3, 20000.00, 'Пополнение депозита', '2024-02-05'),
(4, 5, 5000.00, 'Перевод между счетами', '2024-02-10'),
(6, 7, 15000.00, 'Перевод на карту', '2024-02-08'),
(8, 9, 10000.00, 'Перевод с наличных на карту', '2024-02-12'),
(10, 11, 8000.00, 'Перевод между картами', '2024-02-15'),
(10, 12, 50000.00, 'Пополнение накопительного счета', '2024-02-20');

insert into budgets (user_id, category_id, amount_limit, period_start, period_end) VALUES
(1, 4, 10000.00, '2024-02-01', '2024-02-29'),
(1, 5, 5000.00, '2024-02-01', '2024-02-29'),
(1, 6, 8000.00, '2024-02-01', '2024-02-29'),
(1, 7, 5000.00, '2024-02-01', '2024-02-29'),
(2, 10, 8000.00, '2024-02-01', '2024-02-29'),
(2, 11, 10000.00, '2024-02-01', '2024-02-29'),
(2, 12, 5000.00, '2024-02-01', '2024-02-29'),
(3, 15, 12000.00, '2024-02-01', '2024-02-29'),
(3, 16, 30000.00, '2024-02-01', '2024-02-29'),
(4, 18, 20000.00, '2024-02-01', '2024-02-29'),
(4, 19, 2000.00, '2024-02-01', '2024-02-29'),
(5, 22, 10000.00, '2024-02-01', '2024-02-29'),
(5, 23, 5000.00, '2024-02-01', '2024-02-29');


--functions
create or replace function get_user_total_balance(p_user_id int)
returns decimal(12, 2) as $$
declare
    total_balance decimal(12, 2);
begin
    select coalesce(sum(balance), 0.00)
    into total_balance
    from accounts
    where user_id = p_user_id;
    
    return total_balance;
end;
$$ language plpgsql;

create or replace function get_category_transactions_sum(p_category_id int, p_start_date date, p_end_date date)
returns decimal(12, 2) as $$
declare
    total_amount decimal(12, 2);
begin
    select coalesce(sum(amount), 0.00)
    into total_amount
    from transactions
    where category_id = p_category_id
    and transaction_date between p_start_date and p_end_date;
    
    return total_amount;
end;
$$ language plpgsql;

--queries with functions
select 
    u.username,
    get_user_total_balance(u.id) as total_balance
from users u
where u.id = 1;

select 
    c.name as category_name,
    get_category_transactions_sum(c.id, '2024-02-01', '2024-02-29') as total_sum
from categories c
where c.id = 4;


--procedure
create or replace procedure add_transaction(
    p_account_id int,
    p_category_id int,
    p_amount decimal(12, 2),
    p_description text default null,
    p_transaction_date date default current_date
)
language plpgsql as $$
declare
    category_type type_of_c;
    balance_delta decimal(12, 2);
begin
    select type into category_type
    from categories
    where id = p_category_id;
    
    if not found then
        raise exception 'категория с id % не найдена', p_category_id;
    end if;
    
    if category_type = 'income' then
        balance_delta := p_amount;
    else
        balance_delta := -p_amount;
    end if;
    
    if category_type = 'expense' then
        if (select balance from accounts where id = p_account_id) + balance_delta < 0 then
            raise exception 'Недостаточно средств на счете';
        end if;
    end if;
    
    insert into transactions (account_id, category_id, amount, description, transaction_date)
    values (p_account_id, p_category_id, p_amount, p_description, p_transaction_date);
    
    update accounts
    set balance = balance + balance_delta
    where id = p_account_id;
end;
$$;

create or replace procedure transfer_between_accounts(
    p_account_id_from int,
    p_account_id_to int,
    p_amount decimal(12, 2),
    p_description text default null,
    p_transaction_date date default current_date
)
language plpgsql as $$
begin
    if p_account_id_from = p_account_id_to then
        raise exception 'Нельзя переводить средства на тот же счет';
    end if;
    
    if (select balance from accounts where id = p_account_id_from) < p_amount then
        raise exception 'Недостаточно средств на счете';
    end if;
    
    insert into transactions_b_a (account_id_from, account_id_to, amount, description, transaction_date)
    values (p_account_id_from, p_account_id_to, p_amount, p_description, p_transaction_date);
    
    update accounts
    set balance = balance - p_amount
    where id = p_account_id_from;
    
    update accounts
    set balance = balance + p_amount
    where id = p_account_id_to;
end;
$$;



create or replace view user_accounts_summary as
select 
    u.id as user_id,
    u.username,
    u.email,
    count(a.id) as total_accounts,
    coalesce(sum(a.balance), 0.00) as total_balance,
    min(a.created_at) as first_account_created
from users u
left join accounts a on u.id = a.user_id
group by u.id, u.username, u.email;

create or replace view category_transactions_report as
select 
    c.id as category_id,
    c.name as category_name,
    c.type as category_type,
    u.id as user_id,
    u.username,
    count(t.id) as transaction_count,
    coalesce(sum(t.amount), 0.00) as total_amount,
    coalesce(avg(t.amount), 0.00) as average_amount,
    min(t.transaction_date) as first_transaction_date,
    max(t.transaction_date) as last_transaction_date
from categories c
join users u on c.user_id = u.id
left join transactions t on c.id = t.category_id
group by c.id, c.name, c.type, u.id, u.username;



