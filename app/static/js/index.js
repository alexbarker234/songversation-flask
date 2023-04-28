$(window).on('load', function() {
    if (window.location.pathname === '/index' || window.location.pathname === '') {
        loadTopArtists()
    }
})

function loadTopArtists() {
    $.getJSON('/topartists', function (data) {
        addArtists(data)
        })
}

function addArtists(data) {
    let artistDiv = $('#top-artists');
    let rank = 1;
    data.forEach(element => {
        artistDiv.append(`<div class="artist-box">#${rank}<img src="${element.image}" draggable="false">${element.name}</div>`)
        rank++;
    });
}