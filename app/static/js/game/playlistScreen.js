$(window).on("load", function () {
    if (window.location.pathname != "/lyricgame") return;

    loadPlaylists();
    $(".tracklist-selector").on("click", function (e) {
        if ($(e.target).hasClass("disabled")) return;
        let link = e.target.href;
        var fragment = link.split("#")[1];

        if (fragment === "playlist-selector") {
            selectorClick("playlists", loadPlaylists);
        } else if (fragment === "artist-selector") {
            selectorClick("artists", loadArtists);
        }
    });
});

function selectorClick(type, toLoad) {
    let selectors = $(".cover-art-selectors").first().children();
    selectors.css("display", "none");

    $("#title").html("Choose a" + (type == "artists" ? "n artist" : " playlist"));

    let selector = selectors.siblings(`#${type}`).first();
    selector.removeAttr("style");
    if (selector.children().length == 0) {
        toLoad();
    }
}

function loadArtists() {
    loader = loaderComponent();
    loader.css("margin", "auto");
    $("#artists").append(loader);

    $.getJSON("/api/get-artists", function (data) {
        loader.remove();
        // sort alphabetically
        data.sort((a, b) => (a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1));
        addArtSelectors(data, $("#artists"), "artist");
    });
}

function loadPlaylists() {
    loader = loaderComponent();
    loader.css("margin", "auto");
    $("#playlists").append(loader);

    $.getJSON("/api/get-playlists", function (data) {
        addArtSelectors(data, $("#playlists"), "playlist");
        loader.remove();
    });
}

function addArtSelectors(data, div, type) {
    //let url = window.location.href;
    let index = 0;
    data.forEach((element) => {
        if (element.trackCount != 0) {
            data[element.id] = element;
            let artBox = coverArtBoxComponent(element, index, `lyricgame/${type}/${element.id}`);
            artBox.css({
                opacity: "0",
                animation: "fade-drop-in 1s forwards",
                "animation-delay": `${index * 0.05}s`,
            });
            div.append(artBox);
            index++;
        }
    });
}
