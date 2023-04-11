$(window).on('load', function() {
    if (window.location.pathname === '/lyricgame') {
        loadPlaylists()
    }
})

function loadPlaylists() {
    $.getJSON('/getplaylists', function (data) {
        addPlaylists(data)
        })
}

function addPlaylists(data) {
    let playlistDiv = $('#playlists');
    //let url = window.location.href;
    playlistCache = data;
    let index = 0;
    data.forEach(element => {
        if (element.trackCount != 0) {
            playlistCache[element.id] = element;
            playlistBox = createPlaylistBox(element, index);
            playlistBox.css("animation", "fade-drop-in 1s")
            playlistBox.children('img').click(function(e) {
                let playlistBox = e.target.parentNode;
                //getPlaylistTracks(playlistBox.dataset.id).then(response => loadGameWithPlaylist(playlistCache[playlistBox.dataset.id], response))
                let newURL = window.location.href + `/playlist/${playlistBox.dataset.id}`
                window.location.replace(newURL)
            })
            playlistDiv.append(playlistBox)
            index++;
        }
     });
}