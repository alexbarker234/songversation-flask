function createPlaylistBox(playlistData, index){
    const playlistBox = $("<div>", { class: "playlist-box" });
    playlistBox.attr( "data-id", playlistData.id )
    if (index) playlistBox.attr( "data-index", index )

    const playlistImage = $("<img>", { src: playlistData.image, draggable: false });

    playlistBox.append(playlistImage)
    playlistBox.append(playlistData.name)

    return playlistBox
}
