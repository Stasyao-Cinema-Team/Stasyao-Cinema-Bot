drop table Data;
drop table Actions;
drop table Events;
drop table Admins;
drop table Users;
drop table Ordering;

-- ------------------------------------------------------------------------------------------------------------------ --

CREATE TABLE Users
(
    id          INTEGER                             not null
        constraint "Users_pk"
            primary key autoincrement,
    tg_uname    TEXT unique                         not null,
    tg_id       INTEGER unique                      not null,
    create_time TIMESTAMP default CURRENT_TIMESTAMP not null
);

-- ------------------------------------------------------------------------------------------------------------------ --

CREATE TABLE Admins
(
    id          INTEGER                             not null
        constraint "Admins_pk"
            primary key autoincrement,
    user_id     INTEGER unique                      not null
        constraint "Admins.user_id-Users.id-fk"
            references Users (id),
    create_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    create_uid  INTEGER                             not null
        constraint "Admins.create_uid-Users.id-fk"
            references Users (id),
    update_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    update_uid  INTEGER                             not null
        constraint "Admins.update_uid-Users.id-fk"
            references Users (id),
    active      BOOLEAN   default FALSE             not null
);

-- ------------------------------------------------------------------------------------------------------------------ --

create table Events
(
    id          INTEGER                             not null
        constraint "Events_pk"
            primary key autoincrement,
    name        TEXT unique                         not null,
    create_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    create_uid  INTEGER                             not null
        constraint "Events.create_uid-Users.id-fk"
            references Users (id),
    update_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    update_uid  INTEGER                             not null
        constraint "Events.update_uid-Users.id-fk"
            references Users (id),
    active      BOOLEAN   default TRUE              not null
);

-- ------------------------------------------------------------------------------------------------------------------ --

create table Actions
(
    id          INTEGER                             not null
        constraint "Actions_pk"
            primary key autoincrement,
    name        TEXT unique                         not null,
    event_id    INTEGER                             not null
        constraint "Actions.event_id-event.id-fk"
            references Events (id),
    create_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    create_uid  INTEGER                             not null
        constraint "Events.create_uid-Users.id-fk"
            references Users (id),
    update_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    update_uid  INTEGER                             not null
        constraint "Events.update_uid-Users.id-fk"
            references Users (id),
    active      BOOLEAN   default TRUE              not null
);

-- ------------------------------------------------------------------------------------------------------------------ --

create table Ordering
(
    entity_id TEXT unique not null,
    `order`   TEXT        not null
);

-- ------------------------------------------------------------------------------------------------------------------ --

create table Data
(
    id          INTEGER                             not null
        constraint "Data_pk"
            primary key autoincrement,
    action_id   INTEGER                             not null
        constraint "Data.action_id-action.id-fk"
            references Events (id),
    create_time TIMESTAMP default CURRENT_TIMESTAMP not null,
    create_uid  INTEGER                             not null
        constraint "Data.create_uid-Users.id-fk"
            references Users (id),
    system      BOOLEAN   default FALSE             not null,
    type        TEXT                                not null,
    active      BOOLEAN   default TRUE              not null,
    value       TEXT                                not null
);

-- ------------------------------------------------------------------------------------------------------------------ --

insert into Users (id, tg_uname, tg_id, create_time)
values (0, 'system user', 0, datetime('1970-01-01 00:00:00'));

insert into Events (id, name, create_time, create_uid, update_time, update_uid, active)
values (0, 'Homepage/Домашняя страница', datetime('1970-01-01 00:00:00'), 0, datetime('1970-01-01 00:00:00'), 0, TRUE);

insert into Actions (id, name, event_id, create_time, create_uid, update_time, update_uid, active)
values (0, 'Greeting/Приветствие', 0, datetime('1970-01-01 00:00:00'), 0, datetime('1970-01-01 00:00:00'), 0, TRUE);

insert into Data (action_id, create_uid, system, type, active, value)
values (0, 0, TRUE, 'text', TRUE, 'Hello World!
Приветствую странник!');

-- ------------------------------------------------------------------------------------------------------------------ --

