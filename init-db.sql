create table if not exists game (
    game_id text primary key,
    winner text default null,
    game_start timestamp default current_timestamp
);

create table if not exists game_moves (
    game_id text,
    row integer,
    side text,
    piece text,
    turn integer,
    foreign key(game_id) references game(game_id)
);