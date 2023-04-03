let currentPlaylist = null;

$(window).on('load', function() {
    loadPlaylists();
})
function loadPlaylists() {
    $.getJSON('/getplaylists', function (data) {
        addPlaylists(data)
        })
}

function addPlaylists(data) {
    let artistDiv = $('#playlists');
    let url = window.location.href;
    data.forEach(element => {
        artistDiv.append(`<div class="playlist-box"><a href="${url + "/" + element.id}"></a><img src="${element.image}" draggable="false">${element.name}</div>`)
     });
}

function getLyrics() {

}