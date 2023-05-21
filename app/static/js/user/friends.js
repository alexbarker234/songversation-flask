$(window).on("load", function () {
    $(document).on("click", ".add-friend", function (e) {
        addFriend($(e.target).parent(), $(e.target).closest(".user-result").data("id"));
    });
});

function searchUsers() {
    input = $("#user-search-input").first();
    $.getJSON(`/api/search-users?name=${input.val()}`).done((response) => {
        container = $("#user-search-results");
        container.empty();
        response.users.forEach((user) => {
            container.append(userResultComponent(user));
        });
    });
}

function addFriend(container, id) {
    if (!id) {
        container.empty();
        container.append("Error");
    } else {
        $.ajax({
            type: "POST",
            url: "/api/add-friend",
            data: JSON.stringify({ id: id }),
            contentType: "application/json",
        })
            .done((response) => {
                container.empty();
                container.append("Added");
            })
            .fail(function (jqxhr, textStatus, error) {
                container.empty();
                container.append("Error");
            });
    }
}
