let currentPlaylist = null;

let playlistCache = {};
let availableTrackIDs = [];

let loadedTracks = new Map();
/** List of all trackIDs with lyrics */
let loadedLyrics = []; 

/** @type Track */
let currentTrack = null;
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
    - some lyric links return 404 - make sure thats fixed
    - make the autocomplete include artist names 
*/

$(window).on('load', function() {
    loadPlaylists();

    $(document).on("click", ".autocomplete-options li" , function(e) { selectAutocomplete(e.target.innerHTML) });

    // close autocomplete menu
    $(document).on("click", ".autocomplete-options" , function(e) { e.stopPropagation() }); // dont close when clicking this
    $(document).on("click", function(e) { setAutocompleteVisibility(e.target.id =="guess-input" && e.target.value != '') });
    
    $(document).on("click", ".playlist-box img" , function(e) {
        let platlistBox = e.target.parentNode;
        getPlaylistTracks(platlistBox.dataset.id).then(response => loadGameWithPlaylist(playlistCache[platlistBox.dataset.id], response))
    });


    $(document).on("keyup", "#guess-input" , manageAutocomplete);
    
    $(document).on("keydown", autocompleteKeyboard);
})
function loadPlaylists() {
    $.getJSON('/getplaylists', function (data) {
        addPlaylists(data)
        })
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

function getPlaylistTracks(playlistID) {
    return $.getJSON(`/getplaylisttracks/${playlistID}`);
}


function addPlaylists(data) {
    let playlistDiv = $('#playlists');
    //let url = window.location.href;
    playlistCache = data;
    let index = 0;
    data.forEach(element => {
        if (element.trackCount != 0) {
            playlistCache[element.id] = element;
            playlistDiv.append(createPlaylistBox(element, index))
            index++;
        }
     });
}

function loadGameWithPlaylist(playlist, tracks){
    loadedTracks = tracks.reduce(function(map, obj) {
        map[obj.id] = obj;
        return map;
    }, {});
    availableTrackIDs = tracks.map(function (obj) { return obj.id });
    availableTrackIDs = availableTrackIDs.filter(n => n).shuffle() // remove null track ids (local files) and shuffle

    // delete playlist selector
    $('#playlists').remove()
    $('#title').remove();

    let gameDiv = $('#lyric-game');
    // playlist icon
    selectedPlaylist = createPlaylistBox(playlist);
    selectedPlaylist.addClass('selected-playlist')
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
    tracks.forEach(function(track) {
        trackList.append($("<li>", { html: `${trackListDisplay(track)}` }));
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

    const loaderOverlay = $("<div>", {id: "loader-container"});
    loaderOverlay.append($("<div>", {id: "loader-overlay"}));
    loaderOverlay.append($("<div>", {id: "loader-spinner"}));
    gameDiv.append(loaderOverlay);

    // start game
    //chooseLyrics()
    //console.log(loadedTracks)
    loadLyrics(5, [...availableTrackIDs], true)
}

function trackListDisplay(track) {
    return `${track.name} - ${track.artists.join(', ')}`
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
    let options = autocompleteList.find("li");
    let enabled = options.toArray().filter(elem => elem.style.display != "none")
    let optionHeight = options.first().height() * 2; // TODO: find out why this is 2x

    if (e.keyCode == keyUp || e.keyCode == keyDown) {
        if (autocompleteList.css('display') == "none") return;

        if (e.keyCode == keyUp) {
            if (autocompleteSelected == -1) autocompleteSelected++; 
            autocompleteSelected = (autocompleteSelected - 1).mod(optionCount);
        }
        else if (e.keyCode == keyDown) {
            autocompleteSelected = (autocompleteSelected + 1).mod(optionCount);        
        }
        
        autocompleteList.scrollTop(autocompleteSelected * optionHeight);

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
        else if (autocompleteSelected != -1) selectAutocomplete(enabled[autocompleteSelected].innerHTML);     
    }
}


// BUTTONS
function skipButton() {
    roundsLeft--;
}
function checkButton() {
    input = $("#guess-input");
    if (input.val() == trackListDisplay(currentTrack)) {
        console.log("yay")
        chooseLyrics()
    }
    else {
        console.log("wrong")
    }
    roundsLeft--;
}
/** 
 * Will load all lyrics in order from the availableTrackIDs array into the loadedTracks map
 * First time loads of playlists with large amounts of lyric-less songs could be slow
 * @param {number} numToLoad - The amount of tracks to request lyrics for at once
 * @param {Array} tracksToLoad - A list of trackIDs to get lyrics for 
 * @param {boolean} startGame - Whether the game will start when finding suitable lyrics
 * */ 
function loadLyrics(numToLoad, tracksToLoad, startGame) {

    numToLoad = Math.min(numToLoad, tracksToLoad.length);
    toLoad = tracksToLoad.splice(tracksToLoad.length - numToLoad, numToLoad);

    $.getJSON('/gettracklyrics?track_ids=' + toLoad)
        .done(function(response) {
            console.log(response)
            for (const track_id in response.track_lyrics) {
                loadedTracks[track_id].lyrics = response.track_lyrics[track_id]
                if (response.track_lyrics[track_id].length > 0) loadedLyrics.push(track_id)
            }
            
            // will only be called on the first load
            if (loadedLyrics.length > 0 && startGame) 
            {
                chooseLyrics();
                loader = $('#loader-container')
                if (loader) loader.remove()
                startGame = false;
            }
            if (tracksToLoad.length != 0)  {
                loadLyrics(numToLoad, tracksToLoad, startGame);
            }
            else {
                console.log("finished loading lyrics")
                console.log(loadedLyrics)
            }
        })
}

function chooseLyrics(trackID){
    // choose random song 
    if (!trackID) trackID = loadedLyrics.pop()

    if (loadedLyrics.length == 0) {
        console.log("out of songs")
    }

    currentTrack = loadedTracks[trackID]
    displayLyrics(loadedTracks[trackID].lyrics, trackID)
}

function displayLyrics(lyrics, trackID) {
    // clear box from any previous attempts
    $('#lyric-box').empty();

    let startLine = randBetween(0, lyrics.length - 3)
    setTimeout(function() { displayLyricLine(lyrics, trackID, startLine, startLine)},500)
}

function displayLyricLine(lyrics, trackID, startLine, curLine) {
    // stop if the player has already guessed the song correctly
    if (trackID != currentTrack.id) return

    let lyricBox = $('#lyric-box')
    lyricBox.append(`<div class="lyric-line">${lyrics[curLine]}</div>`)
    curLine++;
    // call next if less than 3 lyrics have been displayed
    if (curLine - startLine < 3) setTimeout(function() { displayLyricLine(lyrics, trackID, startLine, curLine) }, 3000);
}

function createPlaylistBox(playlistData, index){
    const playlistBox = $("<div>", { class: "playlist-box" });
    playlistBox.attr( "data-id", playlistData.id )
    if (index) playlistBox.attr( "data-index", index )

    const playlistImage = $("<img>", { src: playlistData.image, draggable: false });

    playlistBox.append(playlistImage)
    playlistBox.append(playlistData.name)

    return playlistBox
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

Array.prototype.shuffle = function() {
    return this.sort(function() {
        return Math.random() - 0.5;
      });
}
