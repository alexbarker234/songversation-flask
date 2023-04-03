$(window).on('load', function() {
    getLyrics('4Ymo42ECcSJwS2fdG7zNPq')
})


function getLyrics(trackID) {
    $.ajax({
        type : "GET",
        url : `https://spotify-lyric-api.herokuapp.com/?trackid=${trackID}`,
        success: function (data) {
            processLyrics(data)
            }
        });
}
function processLyrics(data) {
    console.log(data)
    if (data.error)  return;

    lines = [];

    for (let i = 0; i < data.lines.length; i++) {
        const element = data.lines[i];
        if (!element || !element.words || element.words === '♪') continue;
        lines.push(element.words);
    }

    
    console.log(lines)
}