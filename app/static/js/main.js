function createCoverArtBox(coverArtData, index){
    const coverArtBox = $("<div>", { class: "cover-art-box" });
    coverArtBox.attr( "data-id", coverArtData.id )
    if (index) coverArtBox.attr( "data-index", index )

    const coverArtImage = $("<img>", { src: coverArtData.image, draggable: false });

    coverArtBox.append(coverArtImage)
    coverArtBox.append(coverArtData.name)

    return coverArtBox
}
