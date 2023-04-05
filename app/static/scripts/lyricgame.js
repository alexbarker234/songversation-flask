let currentPlaylist = null;
let playlists = null;
let tracks = null;
/* 
    TODO: 
    - ensure only songs with lyrics can get selected
    - ensure playlists have songs on spotify 
    - remove local tracks
    - remove punctuation from autocomplete 
*/

$(window).on('load', function() {
    loadPlaylists();

    $(document).on("click", function(e) { setAutocompleteState(false) });
    $(document).on("click", ".playlist-box img" , function(e) {
        let platlistBox = e.target.parentNode;
        getPlaylistSongs(platlistBox.dataset.id).then(response => loadGameWithPlaylist(playlists[platlistBox.dataset.index], response))
    });

    $(document).on("click", ".autocomplete li" , selectAutocomplete);

    $(document).on("keyup", "#guess-input" , manageAutocomplete);
})
function loadPlaylists() {
    $.getJSON('/getplaylists', function (data) {
        addPlaylists(data)
        })
}
function getLyrics(trackID) {
    return $.getJSON(`https://spotify-lyric-api.herokuapp.com/?trackid=${trackID}`);
}
function processLyrics(data) {
    if (data.error)  return;

    lines = [];

    for (let i = 0; i < data.lines.length; i++) {
        const element = data.lines[i];
        if (!element || !element.words || element.words === '♪') continue;
        lines.push(element.words);
    }
    return lines;
}

function getPlaylistSongs(playlistID) {
    return $.getJSON(`/getplaylistsongs/${playlistID}`);
}


function addPlaylists(data) {
    let playlistDiv = $('#playlists');
    let url = window.location.href;
    playlists = data;
    let index = 0;
    data.forEach(element => {
        playlistDiv.append(createPlaylistBox(element, index))
        index++;
     });
}

function loadGameWithPlaylist(playlist, songs){
    tracks = songs;
    // delete playlist selector
    $('#playlists').remove()
    $('#title').remove();

    let gameDiv = $('#lyric-game');
    // playlist icon
    selectedPlaylist = createPlaylistBox(playlist);
    selectedPlaylist.classList.add('selected-playlist')
    gameDiv.append(selectedPlaylist)

    // add title
    gameDiv.append('<h2 id="title">Which song is this?</h2>')

    // add lyric display
    gameDiv.append('<div id="lyric-box"></div>')

    // input box
    const autocomplete = document.createElement("div");
    autocomplete.classList.add('autocomplete-container')

    const inputBox = document.createElement("input");
    inputBox.id = 'guess-input';
    inputBox.placeholder = "Guess here...";
    //inputBox.setAttribute('list', "playlist-tracks");

    const trackList = document.createElement("div");
    trackList.id = "track-list"
    trackList.classList.add('autocomplete-options')
    trackList.style.display = "none"
    songs.forEach(function(item){
        var option = document.createElement('li');
        option.innerHTML = item.name;
        trackList.appendChild(option);
     });

    // lame default autocomplete
    /*const trackList = document.createElement("datalist");
    trackList.id = "playlist-tracks"
    songs.forEach(function(item){
        var option = document.createElement('option');
        option.value = item.name;
        trackList.appendChild(option);
     });*/
     autocomplete.append(inputBox)
     autocomplete.append(trackList)
     gameDiv.append(autocomplete)

    // choose random song 
    const randomSong = songs[Math.floor(Math.random() * songs.length)];

    getLyrics(randomSong.id).then( response => 
        displayLyrics(processLyrics(response))
      );
}

function manageAutocomplete(e){
    console.log(e.target.value)
    setAutocompleteState(e.target.value != '');

    filter = e.target.value.toUpperCase();
    trackList = $("#track-list");
    a = trackList.find("li");
    for (i = 0; i < a.length; i++) {
      txtValue = a[i].textContent || a[i].innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
      } else {
        a[i].style.display = "none";
      }
    }
}

function setAutocompleteState(enabled) {
    $("#track-list").css("display", enabled ? '' : 'none');
}

function selectAutocomplete(e) {
    trackList = $("#guess-input");
    console.log(e.target.innerHTML)
    trackList.val(e.target.innerHTML);
}

function displayLyrics(lyrics) {
    let lineStart = randBetween(0, lyrics.length - 3)
    let lyricBox = $('#lyric-box')

    let lineCurrent = lineStart;
    let interval = setInterval(function() {
        lyricBox.append(`<div class="lyric-line">${lyrics[lineCurrent]}</div>`)
        lineCurrent++;
        if (lineCurrent - lineStart >= 3) clearInterval(interval);
    }, 3000)

}

function createPlaylistBox(playlistData, index){
    const playlistBox = document.createElement("div");
    playlistBox.classList.add("playlist-box")
    if (index) playlistBox.dataset.index = index;
    playlistBox.dataset.id = playlistData.id;

    const playlistImage = document.createElement("img");
    playlistImage.src = playlistData.image;
    playlistImage.draggable = false;

    playlistBox.append(playlistImage)
    playlistBox.append(playlistData.name)

    return playlistBox;
    //return `<div class="playlist-box" data-index=${index} data-id=${element.id}><img src="${element.image}" draggable="false">${element.name}</div>`
}


// min & max inclusive
function randBetween(min, max) { 
    return Math.floor(Math.random() * (max - min + 1) + min)
}