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
        is_free: Bool
    };

    roles = [
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


# TODO: add a condition that a movie should be marked free in order to watch as anonymous/user
# anonymous
allow(actor: Actor, "view-partial", movie: Movie) if
    is_free matches Bool and
    has_relation(movie, "is_free", is_free) and
    has_role(actor, "anonymous", movie);

has_role(_: Actor, "anonymous", _: Movie) if
    true;


# user
allow(actor: Actor, "view-partial", movie: Movie) if
    is_free matches Bool and
    has_relation(movie, "is_free", is_free) and
    has_role(actor, "user", movie);

allow(actor: Actor, "comment", movie: Movie) if
    has_role(actor, "user", movie);

allow(actor: Actor, "rate", movie: Movie) if
    has_role(actor, "user", movie);


# paid-user
allow(actor: Actor, "view", movie: Movie) if
    has_role(actor, "paid-user", movie);

has_role(actor: Actor, "user", movie: Movie) if
    has_role(actor, "paid-user", movie);


# admin
allow(actor: Actor, "edit", movie: Movie) if
    has_role(actor, "admin", movie);

has_role(actor: Actor, "paid-user", movie: Movie) if
    has_role(actor, "admin", movie);


# singleton application roles
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

has_relation(_: Movie, "app", _: Application) if
    true;