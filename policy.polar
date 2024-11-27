actor System {}

actor User {}

resource Application {
    roles = [
        "anonymous",
        "user",
        "paid-user",
        "admin"
    ];
}

resource Bool {}

resource Movie {
    relations = {
        app: Application,
    };

    roles = [
        # system roles
        "free-movie",
        # user roles
        "anonymous",
        "user",
        "paid-user",
        "admin"
    ];

    permissions = [
        "view-partial",
        "view",
        "comment",
        "rate",
        "edit"
    ];
}

# generic
allow(actor: Actor, "view", movie: Movie) if
    allow(actor, "view-partial", movie);


# anonymous
has_role(_: Actor, "anonymous", _: Movie) if
    true;

allow(actor: Actor, "view-partial", movie: Movie) if
    has_role(actor, "anonymous", movie) and
    has_role(_, "free-movie", movie);


# user
allow(actor: Actor, "view-partial", movie: Movie) if
    has_role(actor, "user", movie) and
    has_role(_, "free-movie", movie);


# paid-user
has_role(actor: Actor, "user", movie: Movie) if
    has_role(actor, "paid-user", movie);

allow(actor: Actor, "view", movie: Movie) if
    has_role(actor, "paid-user", movie);

allow(actor: Actor, "comment", movie: Movie) if
    has_role(actor, "paid-user", movie);

allow(actor: Actor, "rate", movie: Movie) if
    has_role(actor, "paid-user", movie);



# admin
has_role(actor: Actor, "paid-user", movie: Movie) if
    has_role(actor, "admin", movie);

allow(actor: Actor, "edit", movie: Movie) if
    has_role(actor, "admin", movie);


# singleton application roles
has_relation(_: Movie, "app", _: Application) if
    true;

has_role(actor: Actor, "anonymous", movie: Movie) if
    app matches Application and
    has_role(actor, "anonymous", app) and
    has_relation(movie, "app", app);

has_role(actor: Actor, "user", movie: Movie) if
    app matches Application and
    has_role(actor, "user", app) and
    has_relation(movie, "app", app);

has_role(actor: Actor, "paid-user", movie: Movie) if
    app matches Application and
    has_role(actor, "paid-user", app) and
    has_relation(movie, "app", app);

has_role(actor: Actor, "admin", movie: Movie) if
    app matches Application and
    has_role(actor, "admin", app) and
    has_relation(movie, "app", app);
