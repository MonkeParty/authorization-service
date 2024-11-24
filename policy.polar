actor Actor {}

resource OnlineCinema {
    roles = ["user", "admin"];
    permissions = ["view", "edit"];

    "view" if "user";
    "user" if "admin";
    "edit" if "admin";
}

resource Movie {
    roles = [
        "unauthenticated",
        "user",
        "paid-user",
        "admin"
    ];
    permissions = [
        "view",
        "comment",
        "rate",
        "edit"
    ];
    relations = {
        movie_container: OnlineCinema
    };

    "view" if "user";
    "rate" if "user";
    "comment" if "user";

    "user" if "paid-user";

    "paid-user" if "admin";
    "edit" if "admin";
}