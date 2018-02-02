drop table if exists members;
create table members (
    memberID integer primary key autoincrement,
    name text not null,
    email text not null,
    phone text not null
);
