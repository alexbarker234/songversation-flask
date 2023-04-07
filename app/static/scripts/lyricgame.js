let currentPlaylist = null;
let playlists = null;
let tracks = null;
let currentSong = null;
let rounds = 5;
let roundsLeft = rounds;

let autocompleteSelected = -1;
let optionCount = 0;

const keyUp = 38, keyDown = 40, keyEnter = 13

/* 
    TODO: 
    - ensure only songs with lyrics can get selected
    - ensure playlists have songs on spotify 
    - remove local tracks
    - remove punctuation from autocomplete search
    - try and avoid putting the song title in the lyrics??
    - remove whole lyric lines like "ooh-ooh" and "yeah"
    - keyboard support - arrowkey autocomplete, enter to submit
*/

$(window).on('load', function() {
    loadPlaylists();

    $(document).on("click", ".autocomplete-options li" , function(e) { selectAutocomplete(e.target.innerHTML) });

    // close autocomplete menu
    $(document).on("click", ".autocomplete-options" , function(e) { e.stopPropagation() }); // dont close when clicking this
    $(document).on("click", function(e) { setAutocompleteVisibility(e.target.id =="guess-input" && e.target.value != '') });
    
    $(document).on("click", ".playlist-box img" , function(e) {
        let platlistBox = e.target.parentNode;
        getPlaylistSongs(platlistBox.dataset.id).then(response => loadGameWithPlaylist(playlists[platlistBox.dataset.index], response))
    });


    $(document).on("keyup", "#guess-input" , manageAutocomplete);
    
    $(document).on("keydown", autocompleteKeyboard);
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

    // input box & autocomplete
    const bottomBox = $("<div>", { class:"bottom-container" })

    const autocomplete = $("<div>", { class:"autocomplete-container" })

    const inputBox = document.createElement("input");
    inputBox.id = 'guess-input';
    inputBox.placeholder = "Guess here...";

    const trackList = $("<div>", { id: "track-list", class:"autocomplete-options" }).css("display", 'none');
    songs.forEach(function(item) {
        trackList.append($("<li>", { html: item.name }));
    });

    autocomplete.append(inputBox)
    autocomplete.append(trackList)
    bottomBox.append(autocomplete)
    
    // submit buttons
    const buttonContainer = $("<div>", {id: "button-container"});
    buttonContainer.append($("<button>", {id: "skip", "class": "button", html:"Skip"}))
    buttonContainer.append($("<button>", {id: "submit", "class": "button", html:"Submit", onclick:"checkButton()"}))
    bottomBox.append(buttonContainer)

    gameDiv.append(bottomBox);


    // start game
    chooseLyrics()
}

// AUTOCOMPLETE
function manageAutocomplete(e){
    if (e.keyCode == keyUp || e.keyCode == keyDown || e.keyCode == keyEnter) return;
 
    setAutocompleteVisibility(e.target.value != '');

    let filter = e.target.value.toUpperCase();
    let trackList = $("#track-list");
    let options = trackList.find("li");

    optionCount = 0;
    autocompleteSelected = -1;

    for (i = 0; i < options.length; i++) {
        txtValue = options[i].textContent || options[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            $(options[i]).css('display', '');
            optionCount++
        } 
        else {
            $(options[i]).css('display', 'none');
        }
        $(options[i]).removeClass("selected");
    }
}
function setAutocompleteVisibility(enabled) {
    $("#track-list").css("display", enabled ? '' : 'none');
}
function selectAutocomplete(value) {
    $("#guess-input").val(value);
    setAutocompleteVisibility(false);
}
function autocompleteKeyboard(e) {
    if (e.keyCode != keyUp && e.keyCode != keyDown && e.keyCode != keyEnter || optionCount == 0) return;
    e.preventDefault();

    let autocompleteList = $("#track-list");
    let enabled = autocompleteList.find("li").toArray().filter(elem => elem.style.display != "none")

    if (e.keyCode == keyUp || e.keyCode == keyDown) {
        if (autocompleteList.css('display') == "none") return;

        if (e.keyCode == keyUp) {
            if (autocompleteSelected == -1) autocompleteSelected++; 
            autocompleteSelected = (autocompleteSelected - 1).mod(optionCount);
        }
        else if (e.keyCode == keyDown) {
            autocompleteSelected = (autocompleteSelected + 1).mod(optionCount);
        }

        console.log(autocompleteSelected)
        // highlight selected
        for (i = 0; i < enabled.length; i++) {
            if (i == autocompleteSelected)
                $(enabled[i]).addClass("selected");
            else
                $(enabled[i]).removeClass("selected");
        }
    }
    else if (e.keyCode == keyEnter) {
        // submit
        if (autocompleteList.css('display') == "none") checkButton()
        // choose
        else selectAutocomplete(enabled[autocompleteSelected].innerHTML);     
    }
}


// BUTTONS
function skipButton() {
    roundsLeft--;
}
function checkButton() {
    input = $("#guess-input");
    if (input.val() == currentSong.name) {
        console.log("yay")
        chooseLyrics()
    }
    else {
        console.log("wrong")
    }
    roundsLeft--;
}

// lyric function

function chooseLyrics(){
    // choose random song 
    currentSong = tracks[Math.floor(Math.random() * tracks.length)];

    getLyrics(currentSong.id).then( response => 
        displayLyrics(processLyrics(response))
        );
}

function displayLyrics(lyrics) {
    let lineStart = randBetween(0, lyrics.length - 3)
    let lyricBox = $('#lyric-box')

    lyricBox.empty();

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


// interesting
// https://web.archive.org/web/20090717035140if_/javascript.about.com/od/problemsolving/a/modulobug.htm
Number.prototype.mod = function (n) {
    "use strict";
    return ((this % n) + n) % n;
  };
  