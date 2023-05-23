$(window).on("load", function () {
    nav = $("#side-nav")
    $(".profile-dropdown").on("click", function (e) {
        nav.toggleClass("disabled");
    });
});
