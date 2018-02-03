drop table if exists members;
drop table if exists users;
create table members (
  memberID integer primary key autoincrement,
  name text not null,
  email text not null,
  phone text not null
);
create table users (
  userID integer primary key autoincrement,
  username text not null,
  password text not null,
  access_rights integer default 0
);
INSERT INTO users (username, password, access_rights)
       VALUES ('nothing_user', 'password', 0);
INSERT INTO users (username, password, access_rights)
       VALUES ('get_user', 'password', 1);
INSERT INTO users (username, password, access_rights)
       VALUES ('getput_user', 'password', 2);
INSERT INTO users (username, password, access_rights)
       VALUES ('admin_user', 'password', 3);
