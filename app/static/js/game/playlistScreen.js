$(window).on("load", function () {
    if (window.location.pathname === "/lyricgame") {
        loadPlaylists();
    }
});

function loadPlaylists() {
    loader = createLoader();
    loader.css("margin", "auto");
    $("#cover-art").append(loader);

    $.getJSON("/getplaylists", function (data) {
        addPlaylists(data);
        loader.remove();
    });
}

function addPlaylists(data) {
    let playlistDiv = $("#cover-art");
    //let url = window.location.href;
    playlistCache = data;
    let index = 0;
    data.forEach((element) => {
        if (element.trackCount != 0) {
            playlistCache[element.id] = element;
            playlistBox = createCoverArtBox(
                element,
                index,
                `lyricgame/playlist/${element.id}`
            );
            playlistBox.css({
                "opacity": "0",
                "animation": "fade-drop-in 1s forwards",
                "animation-delay": `${index * 0.05}s`,
            });
            /*playlistBox.children('img').click(function(e) {
                let playlistBox = e.target.parentNode;
                //getPlaylistTracks(playlistBox.dataset.id).then(response => loadGameWithPlaylist(playlistCache[playlistBox.dataset.id], response))
                let newURL = window.location.href + `/playlist/${playlistBox.dataset.id}`
                window.location.replace(newURL)
            })*/
            playlistDiv.append(playlistBox);
            index++;
        }
    });
}
