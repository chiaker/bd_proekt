create type type_of_p as enum ('cash', 'card', 'deposit');
create type type_of_c as enum ('income', 'expense');

drop table if exists transactions_b_a cascade;
drop table if exists transactions cascade;
drop table if exists budgets cascade;
drop table if exists categories cascade;
drop table if exists accounts cascade;
drop table if exists users cascade;
drop table if exists logs cascade;


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
    action varchar(10) not null check (action in ('INSERT', 'UPDATE', 'DELETE')),
    old_data jsonb,
    new_data jsonb,
    changed_at timestamp not null default current_timestamp
);

create or replace function log_audit_changes()
returns trigger as $$
declare
    pk_name text := TG_ARGV[0];
    record_id int;
begin
    if (TG_OP = 'INSERT') then
        record_id := (to_jsonb(NEW)->>pk_name)::int;

        insert into logs(table_name, record_id, action, new_data)
        values (TG_TABLE_NAME, record_id, 'INSERT', to_jsonb(NEW));

        return NEW;

    elsif (TG_OP = 'UPDATE') then
        record_id := (to_jsonb(NEW)->>pk_name)::int;

        insert into logs(table_name, record_id, action, old_data, new_data)
        values (TG_TABLE_NAME, record_id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));

        return NEW;

    elsif (TG_OP = 'DELETE') then
        record_id := (to_jsonb(OLD)->>pk_name)::int;

        insert into logs(table_name, record_id, action, old_data)
        values (TG_TABLE_NAME, record_id, 'DELETE', to_jsonb(OLD));

        return OLD;
    end if;

    return null;
end;
$$ language plpgsql;



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

