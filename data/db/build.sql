CREATE TABLE IF NOT EXISTS servers
(
    ServerID     integer PRIMARY KEY,
    ServerPrefix text DEFAULT ';'
);


CREATE TABLE IF NOT EXISTS users
(
    UserID         integer PRIMARY KEY,
    XP             integer DEFAULT 0,
    Level          integer DEFAULT 0,
    Primogems      integer DEFAULT 0,
    EventBanner    integer DEFAULT 0,
    WeaponBanner   integer DEFAULT 0,
    StandardBanner integer DEFAULT 0
);